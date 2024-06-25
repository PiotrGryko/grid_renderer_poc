import code
import io
import sys
from enum import Enum

import imgui

from app.ai.task_mapping import TaskType
from app.gui.terminal.view_file_input import FileInput
from app.gui.terminal.view_image_input import ImageInput
from app.gui.terminal.view_output import TerminalOutputView
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


class BufferContainer:
    def __init__(self):
        self.output = []


class ScienceBasedTerminal(Widget):
    def __init__(self, config):
        self.config = config
        self.python_buffer = BufferContainer()
        self.model_buffer = BufferContainer()
        self.cmd_wrapper = TerminalCommandsWrapper(config.app, config.n_net)
        self.console = code.InteractiveConsole(locals={"app": self.cmd_wrapper})
        self.parameters_popup = ParametersPopup(config)
        self.last_length = 0
        self.inserted = False

        self.terminal_Type = TerminalType.PYTHON
        self.pipeline_task_type = TaskType.NONE

        self.text_input = TextInput("Type your message")
        self.context_input = TextInput("Context message")
        self.image_input = ImageInput(config)
        self.file_input = FileInput(config)
        self.output_view = TerminalOutputView(config)

        self.total_input_height = self.text_input.input_height
        self.input_width = None
        self.left_column_width = 50
        self.right_column_width = 70
        self.padding = 10
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
        return self.terminal_Type is TerminalType.MODEL and self.pipeline_task_type.has_context_parameter()

    def should_render_file_input(self):
        return self.terminal_Type is TerminalType.MODEL and self.pipeline_task_type.has_audio_input()

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
        context_message = self.context_input.buffer
        if self.text_input.buffer:
            print("Text input ", self.text_input.buffer)
            self.execute(command=self.text_input.buffer, context_message=context_message)
        elif self.image_input.has_images():
            print("Image input", self.image_input.images)
            self.execute(images=self.image_input.images, context_message=context_message)
        elif self.file_input.has_files():
            print("File input", self.file_input.files)
            self.execute(images=self.file_input.files, context_message=context_message)
        else:
            print("No data")
        self.text_input.clear_input()
        self.image_input.clear_input()
        self.file_input.clear_input()

    def type_buttons(self):
        imgui.begin_child("type_buttons", height=25, border=False)
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

        imgui.same_line()

        if self.terminal_Type == TerminalType.MODEL:
            if self.config.model_parser.model is None:
                self.window_name = "No model detected"
            else:
                self.window_name = f"Model: {self.config.model_parser.parsed_model.name}"
            imgui.text(f"Pipeline: {self.pipeline_task_type.value}")
            imgui.same_line()
            self.parameters_popup.render()

        else:
            self.window_name = "Terminal"
        imgui.end_child()

    def _content(self):

        self.pipeline_task_type = self.config.model_parser.pipeline_task.task
        self.input_width = imgui.get_content_region_available_width() - self.left_column_width - self.right_column_width
        self.total_input_height = self.text_input.input_height
        if self.should_render_context_input():
            self.total_input_height += self.context_input.input_height
        if self.should_render_file_input():
            self.total_input_height += self.file_input.input_height
        else:
            self.total_input_height += self.image_input.input_height

        self.output_view.calculate_size(self.total_input_height)
        self.type_buttons()

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
            self.context_input.render()
        if self.should_render_file_input():
            self.file_input.render()
        else:
            self.image_input.render()
        self.text_input.render()
        imgui.end_child()
        #
        if self.text_input.input_changed:
            self._send_data()

        last_result = self.config.model_parser.get_run_result()
        if last_result is not None:
            print("Received result", last_result)
            self.model_buffer.output.append(last_result)
            self.output_view.scroll_to_bottom()

        imgui.same_line(spacing=0)
        self.send_button()
        imgui.end_group()
        imgui.end_child()

    def execute(self, command=None, images=None, context_message=None):
        print("execute")
        if self.terminal_Type is TerminalType.PYTHON:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()

            try:
                self.console.push(command)
            except Exception as e:
                print(f"Error: {e}")

            self.python_buffer.output.append(command)
            self.python_buffer.output.append(sys.stdout.getvalue())
            self.python_buffer.output.append(sys.stderr.getvalue())
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        else:
            if self.pipeline_task_type.is_none():
                print("No task detected")
                self.model_buffer.output.append("No pipeline task detected")
            else:
                self.model_buffer.output.append(f"INPUT: {str(images) if images else str(command)}")
                self.config.model_parser.run_model(input_text=command, images=images, context_message=context_message)

    def execute_script(self, script_path):
        try:
            with open(script_path, 'r') as script_file:
                script_content = script_file.read()
                self.console.runsource(script_content, script_path)
        except Exception as e:
            self.python_buffer.output.append(f"Error loading script: {e}\n")
