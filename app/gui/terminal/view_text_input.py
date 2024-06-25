import uuid

import imgui


class TextInput:
    def __init__(self, hint=None):
        self.input_changed = False
        self.last_length = 0
        self.inserted = False
        self.input_height = 50
        self.input_width = None
        self.buffer = None
        self.hint = hint
        self.input_id = uuid.uuid4()

    def clear_input(self):
        self.buffer = None

    def render(self):
        self.input_width = imgui.get_content_region_available_width()

        def input_callback(data):
            if self.last_length != data.buffer_text_length and not self.inserted:
                text = self.wrap_text(data.buffer, self.input_width)
                data.delete_chars(0, data.buffer_text_length)
                data.insert_chars(0, text)
                self.last_length = data.buffer_text_length

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (10, 10))

        imgui.begin_child(f"##TextInputView_{self.input_id}", 0, self.input_height,
                          border=True,
                          flags=imgui.WINDOW_NO_SCROLLBAR)

        imgui.push_style_var(imgui.STYLE_SCROLLBAR_SIZE, 1)
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (0, 0))
        imgui.push_style_var(imgui.STYLE_CELL_PADDING, (10, 10))
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0, 0, 0, 0)

        cursor_pos_x = imgui.get_cursor_pos_x()
        if not self.buffer and self.hint:
            imgui.push_style_color(imgui.COLOR_TEXT, 0.7, 0.7, 0.7, 1.0)  # Set hint color to gray
            imgui.set_cursor_pos_x(cursor_pos_x)  # Move cursor to the beginning of the line
            imgui.text(self.hint)
            imgui.pop_style_color()
            imgui.same_line()
            imgui.set_cursor_pos_x(cursor_pos_x)  # Move cursor to the beginning of the line again

        # Input Text Box
        (changed, self.buffer) = imgui.input_text_multiline(
            "##input_text",
            self.buffer if self.buffer else "",
            -1,
            width=0,
            height=self.input_height - 20,
            callback=input_callback,
            flags=imgui.INPUT_TEXT_CALLBACK_ALWAYS | imgui.INPUT_TEXT_NO_HORIZONTAL_SCROLL | imgui.INPUT_TEXT_ENTER_RETURNS_TRUE | imgui.INPUT_TEXT_CTRL_ENTER_FOR_NEW_LINE
        )
        imgui.pop_style_color()
        imgui.pop_style_var(3)
        self.input_changed = changed
        if self.input_changed:
            print("changed !! ", self.buffer)
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
