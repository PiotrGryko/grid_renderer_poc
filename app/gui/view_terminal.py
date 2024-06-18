import code
import io
import sys
import imgui

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


class ScienceBasedTerminal(Widget):
    def __init__(self, config):
        super().__init__("Terminal")
        self.config = config
        self.history = []
        self.input_buffer = ""
        self.output = ""
        self.cmd_wrapper = TerminalCommandsWrapper(config.app, config.n_net)
        self.console = code.InteractiveConsole(locals={"app": self.cmd_wrapper})
        self.input_changed = False
        self.last_length = 0
        self.inserted = False

    def execute(self, command):
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            self.console.push(command)
        except Exception as e:
            print(f"Error: {e}")

        self.output += f"{command}\n"
        self.output += sys.stdout.getvalue()
        self.output += sys.stderr.getvalue()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    def execute_script(self, script_path):
        try:
            with open(script_path, 'r') as script_file:
                script_content = script_file.read()
                self.console.runsource(script_content, script_path)
        except Exception as e:
            self.output += f"Error loading script: {e}\n"

    def _on_visibility_changed(self):
        self.config.show_terminal_view = self.opened

    def _update_visibility(self):
        self.opened = self.config.show_terminal_view

    def attach_media_button(self):
        # Set cursor position with padding for the attach media button
        imgui.begin_child("buttonattach", width=45, height=100, border=False)
        imgui.set_cursor_position((10, 90 - 25))
        if imgui.button("📎", width=25, height=25):
            print("Attach media button pressed")
        # Reset cursor position to after the button
        imgui.end_child()

    def send_button(self):
        # Set cursor position with padding for the send button
        imgui.begin_child("sendbutton", width=70, height=100, border=False)
        imgui.set_cursor_position((10, 90 - 25))
        if imgui.button("Send", width=50, height=25):
            print("Send button pressed")
        imgui.end_child()

    def input_box(self):
        width = imgui.get_content_region_available_width() - 70
        height = 100

        def input_callback(data):
            if self.last_length != data.buffer_text_length and not self.inserted:
                text = self.wrap_text(data.buffer, width)
                data.delete_chars(0, data.buffer_text_length)
                data.insert_chars(0, text)
                self.last_length = data.buffer_text_length

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (10, 10))

        imgui.begin_child("ScrollingRegion", width, height,
                          border=True,
                          flags=imgui.WINDOW_NO_SCROLLBAR)

        imgui.push_style_var(imgui.STYLE_SCROLLBAR_SIZE, 1)
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (0, 0))
        imgui.push_style_var(imgui.STYLE_CELL_PADDING, (10, 10))
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0, 0, 0, 0)
        # Input Text Box
        (changed, value) = imgui.input_text_multiline(
            "##input_text", self.input_buffer, -1,
            width=width - 20,
            height=height - 20,
            callback=input_callback,
            flags=imgui.INPUT_TEXT_CALLBACK_ALWAYS | imgui.INPUT_TEXT_NO_HORIZONTAL_SCROLL | imgui.INPUT_TEXT_ENTER_RETURNS_TRUE | imgui.INPUT_TEXT_CTRL_ENTER_FOR_NEW_LINE
        )
        imgui.pop_style_color()
        imgui.pop_style_var(3)

        self.input_changed = changed
        if self.input_changed:
            self.input_buffer = value
            imgui.set_keyboard_focus_here()

        imgui.end_child()
        imgui.pop_style_var(1)

    def wrap_text(self, text, max_width):
        wrapped_lines = []
        current_line = ""

        for char in text:
            if imgui.calc_text_size(current_line + char)[0] < max_width - 20:
                current_line += char
            else:
                wrapped_lines.append(current_line)
                current_line = char

        # Append the last line
        if current_line:
            wrapped_lines.append(current_line)

        return '\n'.join(wrapped_lines)

    def _content(self):

        input_height = 100
        button_height = 25
        padding = 10
        available_height = imgui.get_content_region_available()[1] - (input_height + button_height + 2 * padding)
        available_width = imgui.get_content_region_available()[0] - 2 * padding

        imgui.set_cursor_pos((padding, padding))

        # Render the output field
        imgui.begin_child("OutputField", width=available_width, height=available_height, border=True)
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (10, 10))
        imgui.text_unformatted(self.output)
        imgui.pop_style_var()
        imgui.end_child()
        imgui.set_cursor_pos_y(imgui.get_cursor_pos_y() + padding)

        imgui.begin_group()
        self.attach_media_button()
        imgui.same_line(spacing=0)
        self.input_box()

        if self.input_changed:
            self.history.append(self.input_buffer)
            if self.input_buffer.startswith('load_script '):
                script_path = self.input_buffer[len('load_script '):]
                self.execute_script(script_path)
            else:
                self.execute(self.input_buffer)
            self.input_buffer = ""

        imgui.same_line(spacing=0)
        self.send_button()
        imgui.end_group()