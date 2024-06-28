import imgui


class FileInput:
    def __init__(self, config):
        self.input_height = 35
        self.input_changed = False
        self.files = []

    def clear_input(self):
        self.files = []

    def has_files(self):
        return len(self.files) > 0

    def render(self, hint=None):
        if hint is None:
            hint = "Drag and drop files"
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (10, 10))

        imgui.begin_child("##FileInputView", 0, self.input_height,
                          border=True,
                          flags=imgui.WINDOW_NO_SCROLLBAR)

        imgui.push_style_var(imgui.STYLE_SCROLLBAR_SIZE, 1)
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (0, 0))
        imgui.push_style_var(imgui.STYLE_CELL_PADDING, (10, 10))
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0, 0, 0, 0)
        # Input Text Box
        if len(self.files) == 0:
            self.input_height = 35
            imgui.text_wrapped(hint)
        else:
            height = 0
            for index, f in enumerate(self.files):
                imgui.text(f)
                height += 35 if index == 0 else 20
            self.input_height = height

        imgui.pop_style_color()
        imgui.pop_style_var(3)
        imgui.end_child()
        imgui.pop_style_var(1)

    def load_file(self, file_path, max_size=130):
        self.files.append(file_path)
