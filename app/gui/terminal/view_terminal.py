import code
import io
import json
import sys
from enum import Enum

import imgui

from app.ai.pipeline_task import TaskInput
from app.ai.task_mapping import TaskType
from app.gui.terminal.view_file_input import FileInput
from app.gui.terminal.view_image_input import ImageInput
from app.gui.terminal.view_labels_input import LabelsInput
from app.gui.terminal.view_output import TerminalOutputView, OutputBuffer, SystemMessageLevel
from app.gui.terminal.view_parameters_popup import ParametersPopup
from app.gui.terminal.view_text_input import TextInput
from app.gui.widget import Widget


class TerminalCommandsWrapper:
    def __init__(self, app, n_net):
        self.app = app
        self.n_net = n_net

    def load_numpy(self, layers):
        names = []
        for index, l in enumerate(layers):
            names.append(f"layer{index}")
        self.n_net.init_from_np_arrays(
            all_layers=layers,
            names=names
        )
        self.app.reload_view()


class TerminalType(Enum):
    PYTHON = 0
    MODEL = 1

    @staticmethod
    def from_value(value):
        print("from string terminal", value)
        if value == 0:
            return TerminalType.PYTHON
        else:
            return TerminalType.MODEL


class ScienceBasedTerminal(Widget):
    def __init__(self, config):
        self.config = config
        self.python_buffer = OutputBuffer()
        self.model_buffer = OutputBuffer()
        self.cmd_wrapper = TerminalCommandsWrapper(config.app, config.n_net)
        self.console = code.InteractiveConsole(locals={"app": self.cmd_wrapper})
        self.parameters_popup = ParametersPopup(config)
        self.last_length = 0
        self.inserted = False

        self.terminal_Type = TerminalType.PYTHON
        self.pipeline_task_type = TaskType.NONE

        self.text_input = TextInput()
        self.context_input = TextInput()
        self.image_input = ImageInput(config)
        self.file_input = FileInput(config)
        self.labels_input = LabelsInput()
        self.output_view = TerminalOutputView(config)

        self.total_input_height = self.text_input.input_height
        self.input_width = None
        self.left_column_width = 50
        self.right_column_width = 70
        self.padding = 10
        self.current_model_name = None
        super().__init__("Terminal", config)

    def on_config_save(self, config):
        config['type'] = self.terminal_Type.value
        print("saving terminal", self.terminal_Type, self.terminal_Type.value)

    def on_config_load(self, config):
        print("config", config)
        self.terminal_Type = TerminalType.from_value(config.get('type', 0))
        print("loaded terminal", self.terminal_Type)

    def on_file_dropped(self, path):
        print("terminal on file dropped", path)
        if self.should_render_file_input():
            self.file_input.load_file(path)
        else:
            self.image_input.load_image(path)

    def should_render_context_input(self):
        return self.terminal_Type is TerminalType.MODEL and self.pipeline_task_type.has_context_input

    def should_render_labels_input(self):
        return self.terminal_Type is TerminalType.MODEL and self.pipeline_task_type.has_zero_shot_label_input

    def should_render_file_input(self):
        return self.terminal_Type is TerminalType.MODEL and self.pipeline_task_type.has_file_input

    def attach_media_button(self):
        # Set cursor position with padding for the attach media button
        imgui.begin_child("buttonattach", width=45, height=self.total_input_height, border=False)
        imgui.set_cursor_position((10, self.total_input_height - 25))
        if imgui.button("📎", width=25, height=25):
            print("Attach media button pressed")
        # Reset cursor position to after the button
        imgui.end_child()

    def send_button(self):
        # Set cursor position with padding for the send button
        imgui.begin_child("sendbutton", width=70, height=self.total_input_height, border=False)
        imgui.set_cursor_position((10, self.total_input_height - 25))
        if imgui.button("Send", width=50, height=25):
            print("Send button pressed")
            self._send_data()

        imgui.end_child()

    def _send_data(self):

        if self.terminal_Type is TerminalType.PYTHON:
            self.execute_python_command(self.text_input.buffer)
            return

        context_message = self.context_input.buffer
        zero_shot_labels = self.labels_input.labels

        task_input = TaskInput(
            text=self.text_input.buffer,
            images=self.image_input.images,
            files=self.file_input.files,
            context=context_message,
            labels=zero_shot_labels
        )
        validation_error = task_input.validate(self.pipeline_task_type)
        if validation_error is not None:
            self.model_buffer.send_system_message(validation_error, SystemMessageLevel.WARNING)
            return

        self.execute_model_pipeline(task_input=task_input)
        self.text_input.clear_input()
        self.image_input.clear_input()
        self.file_input.clear_input()

    def type_buttons(self):
        # imgui.begin_child("type_buttons", height=25, border=False)
        active = self.terminal_Type == TerminalType.PYTHON
        if active:
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 1.0)
        if imgui.button("Python", width=50, height=25):
            self.terminal_Type = TerminalType.PYTHON
        if active:
            imgui.pop_style_color()

        imgui.same_line()

        active = self.terminal_Type == TerminalType.MODEL
        if active:
            imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 1.0)
        if imgui.button("Model", width=50, height=25):
            self.terminal_Type = TerminalType.MODEL

        if active:
            imgui.pop_style_color()

    #  imgui.end_child()

    def pipeline_selector(self):
        if self.terminal_Type == TerminalType.MODEL:
            if self.config.model_parser.model is None:
                self.window_name = "No model detected"
            else:
                self.window_name = f"Model: {self.config.model_parser.parsed_model.name}"
            imgui.text(f"Pipeline:")
            imgui.same_line()
            imgui.push_item_width(250)
            changed = imgui.begin_combo("", self.pipeline_task_type.value)

            if changed:
                for item in TaskType:
                    selected, opened = imgui.selectable(item.value, item is self.pipeline_task_type)
                    if selected:
                        self.config.model_parser.pipeline_task.change_task(item)
                imgui.end_combo()
            imgui.pop_item_width()
        else:
            self.window_name = "Terminal"

    def _content(self):

        if self.config.model_parser.current_model_name != self.current_model_name:
            self.current_model_name = self.config.model_parser.current_model_name
            self.model_buffer.send_system_message(f"Model loaded: {self.current_model_name}")
            self.python_buffer.send_system_message(f"Model loaded: {self.current_model_name}")

        self.pipeline_task_type = self.config.model_parser.pipeline_task.task
        self.input_width = imgui.get_content_region_available_width() - self.left_column_width - self.right_column_width
        self.total_input_height = self.text_input.input_height
        if self.should_render_labels_input():
            self.total_input_height += self.labels_input.input_height
        if self.should_render_context_input():
            self.total_input_height += self.context_input.input_height
        if self.should_render_file_input():
            self.total_input_height += self.file_input.input_height
        else:
            self.total_input_height += self.image_input.input_height

        self.output_view.calculate_size(self.total_input_height)
        self.type_buttons()
        imgui.same_line()
        self.pipeline_selector()
        imgui.same_line()
        self.parameters_popup.render()

        imgui.begin_child("##content")
        imgui.set_cursor_pos((self.padding, self.padding))

        if self.terminal_Type == TerminalType.PYTHON:
            self.output_view.render(self.python_buffer)
        else:
            self.output_view.render(self.model_buffer)

        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + self.padding)

        imgui.begin_group()
        self.attach_media_button()
        imgui.same_line(spacing=0)

        imgui.begin_child("##input_container",
                          height=self.total_input_height + 2 * self.padding,
                          width=self.input_width)
        if self.should_render_context_input():
            self.context_input.render(self.pipeline_task_type.context_input_hint)
        if self.should_render_labels_input():
            self.labels_input.render()
        if self.should_render_file_input():
            self.file_input.render(self.pipeline_task_type.file_input_hint)
        else:
            self.image_input.render(self.pipeline_task_type.image_input_hint,
                                    self.pipeline_task_type.media_accepts_single_file)
        self.text_input.render(self.pipeline_task_type.text_input_hint)
        imgui.end_child()
        #
        if self.text_input.input_changed:
            self._send_data()

        last_result = self.config.model_parser.get_run_result()
        if last_result is not None:
            print("Received result", last_result)
            self.model_buffer.send_pipeline_result_message(last_result)
            self.output_view.scroll_to_bottom()

        imgui.same_line(spacing=0)
        self.send_button()
        imgui.end_group()
        imgui.end_child()

    def validate(self, command=None, images=None, files=None, context_message=None, zero_shot_labels=None):
        empty_command = command is None
        empty_images = images is None or len(images) == 0
        empty_files = files is None or len(files) == 0
        empty_context_message = context_message is None or context_message == ""
        empty_labels = zero_shot_labels is None or len(zero_shot_labels) == 0

        if empty_command and empty_images and empty_files:
            print("No data")
            self.model_buffer.send_system_message("No input data", SystemMessageLevel.WARNING)
            return False
        if self.pipeline_task_type.is_none():
            print("No task detected")
            self.model_buffer.send_system_message("No pipeline task detected", SystemMessageLevel.WARNING)
            return False
        elif self.pipeline_task_type.has_zero_shot_label_input and empty_labels:
            self.model_buffer.send_system_message(f"You must add candidate labels", SystemMessageLevel.WARNING)
            return False
        elif self.pipeline_task_type.has_context_input and empty_context_message:
            self.model_buffer.send_system_message(f"You must add context message", SystemMessageLevel.WARNING)
            return False
        elif self.pipeline_task_type.has_image_input and empty_images:
            self.model_buffer.send_system_message(f"{self.pipeline_task_type.value} pipeline requires image input",
                                                  SystemMessageLevel.WARNING)
            return False
        elif self.pipeline_task_type.has_audio_input and empty_files:
            self.model_buffer.send_system_message(f"{self.pipeline_task_type.value} pipeline requires audio input",
                                                  SystemMessageLevel.WARNING)
            return False
        elif self.pipeline_task_type.has_video_input and empty_files:
            self.model_buffer.send_system_message(f"{self.pipeline_task_type.value} pipeline requires video input",
                                                  SystemMessageLevel.WARNING)
            return False
        return True

    def execute_python_command(self, command):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            self.console.push(command)
        except Exception as e:
            print(f"Error: {e}")

        self.python_buffer.send_user_message(command)
        self.python_buffer.send_user_message(sys.stdout.getvalue())
        self.python_buffer.send_user_message(sys.stderr.getvalue())
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        return True

    def execute_model_pipeline(self,
                               task_input):
        print("execute")
        self.model_buffer.send_user_message(task_input.get_input_message())
        self.config.model_parser.run_model(task_input=task_input)

    def execute_script(self, script_path):
        try:
            with open(script_path, 'r') as script_file:
                script_content = script_file.read()
                self.console.runsource(script_content, script_path)
        except Exception as e:
            self.python_buffer.send_user_message(f"Error loading script: {e}\n")
