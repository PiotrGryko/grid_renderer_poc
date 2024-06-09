import imgui


class BottomInfoBar:
    def __init__(self, config):
        self.config = config

    def render_bottom_info_bar(self):
        viewport = imgui.get_main_viewport()
        width = viewport.size.x
        height = viewport.size.y

        imgui.set_next_window_position(0, height - 30)
        imgui.set_next_window_size(width, 30)
        # imgui.set_next_window_bg_alpha(0.95)  # Transparent background

        if imgui.begin("##BottomInfoBar",
                       flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_SAVED_SETTINGS):
            imgui.text(self.config.bottom_bar_message)
        imgui.end()
