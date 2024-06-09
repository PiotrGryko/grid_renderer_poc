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

    def _content(self):

        window_height = imgui.get_window_height()
        input_height = 20
        padding = 5

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (5, 5))
        imgui.text("Output:")
        imgui.begin_child("output", height=window_height - input_height - 40, width=0, border=False)

        imgui.text_unformatted(self.output)
        if self.input_changed:
            imgui.set_scroll_here_y(1.0)  # Scroll to bottom if the child window is active

        imgui.end_child()
        imgui.pop_style_var()

        imgui.separator()

        # Input section
        imgui.set_cursor_pos_y(window_height - input_height - padding)  # Position input at the bottom
        imgui.set_cursor_pos_x(padding)
        imgui.text("Input:")
        imgui.same_line()
        imgui.push_item_width(-1 - padding * 2)  # Make input field fill the remaining width
        self.input_changed, self.input_buffer = imgui.input_text("", self.input_buffer, 256,
                                                                 imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
        imgui.pop_item_width()

        if self.input_changed:
            self.history.append(self.input_buffer)
            if self.input_buffer.startswith('load_script '):
                script_path = self.input_buffer[len('load_script '):]
                self.execute_script(script_path)
            else:
                self.execute(self.input_buffer)
            self.input_buffer = ""
            imgui.set_keyboard_focus_here()  # Keep focus on the input box
