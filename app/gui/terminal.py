import code
import io
import sys
import imgui


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


class ScienceBasedTerminal:
    def __init__(self, app, n_net):
        self.history = []
        self.input_buffer = ""
        self.output = ""
        self.cmd_wrapper = TerminalCommandsWrapper(app,n_net)
        self.console = code.InteractiveConsole(locals={"app": self.cmd_wrapper})


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

    def render(self):
        imgui.begin("Terminal")

        imgui.text("Output:")
        imgui.begin_child("output", height=200, width=0)
        imgui.text_unformatted(self.output)
        imgui.end_child()

        imgui.separator()

        imgui.text("Input:")
        # imgui.set_keyboard_focus_here()
        changed, self.input_buffer = imgui.input_text("", self.input_buffer, 256, imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
        # imgui.set_keyboard_focus_here()
        if changed:
            self.history.append(self.input_buffer)
            if self.input_buffer.startswith('load_script '):
                script_path = self.input_buffer[len('load_script '):]
                self.execute_script(script_path)
            else:
                self.execute(self.input_buffer)
            self.input_buffer = ""
        imgui.end()
