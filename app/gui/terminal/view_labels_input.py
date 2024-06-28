import uuid

import imgui


class LabelsInput:
    def __init__(self):
        self.last_length = 0
        self.inserted = False
        self.input_height = 35
        self.input_width = None
        self.buffer = None
        self.input_id = uuid.uuid4()
        self.labels = []
        self.input_text = ""

    def clear_input(self):
        self.buffer = None

    def _refresh_size(self):
        if len(self.labels) > 0:
            self.input_height = 70
        else:
            self.input_height = 35

    def render(self):
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (10, 10))

        imgui.begin_child(f"##LabelsInput_{self.input_id}", 0, self.input_height,
                          border=True,
                          flags=imgui.WINDOW_NO_SCROLLBAR)

        imgui.push_style_var(imgui.STYLE_SCROLLBAR_SIZE, 1)
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (0, 0))
        imgui.push_style_var(imgui.STYLE_CELL_PADDING, (10, 10))
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0, 0, 0, 0)
        if len(self.labels) > 0:
            for label in self.labels:
                imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.5, 0.2, 1.0)  # Change the background color
                imgui.push_style_var(imgui.STYLE_FRAME_PADDING, imgui.Vec2(10, 5))  # Add padding around the text
                if imgui.button(label):
                    self.labels.remove(label)
                    self._refresh_size()
                imgui.pop_style_var()
                imgui.pop_style_color()
                imgui.same_line()

            imgui.new_line()
            imgui.spacing()

        changed, self.input_text = imgui.input_text_with_hint("##input",
                                                              "Add new label and press Enter",
                                                              self.input_text,
                                                              128,
                                                              flags=imgui.INPUT_TEXT_ENTER_RETURNS_TRUE)
        imgui.same_line()
        if changed:
            if self.input_text.strip():
                self.labels.append(self.input_text.strip())
                self.input_text = ""
                self._refresh_size()

        imgui.pop_style_color()
        imgui.pop_style_var(3)

        if changed:
            print("changed !! ", self.buffer)
            imgui.set_keyboard_focus_here()

        imgui.end_child()
        imgui.pop_style_var(1)
