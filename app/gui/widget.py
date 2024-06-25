from enum import Enum

import imgui


class ViewType(Enum):
    FLOATING = 0
    DOCK_LEFT = 1
    DOCK_RIGHT = 2
    DOCK_BOTTOM = 3


class Widget:
    def __init__(self, name, gui_config):
        self.gui_config = gui_config
        self.window_name = name
        self.config_id = self.window_name
        self.view_type = ViewType.FLOATING
        self.context = None
        self.opened = True
        self.detached = False
        self.selected = False

        self.width = 300
        self.height = 400

        self.load_from_config()

    def on_config_save(self, config):
        pass

    def on_config_load(self, config):
        pass

    def save_config(self):
        widget_config = {
            'opened': self.opened,
            'width': self.width,
            'height': self.height,
            'view_type': self.view_type.value
        }
        self.on_config_save(widget_config)
        self.gui_config.app_config.gui_state_config[self.config_id] = widget_config
        self.gui_config.app_config.save_config()

    def load_from_config(self):
        widget_config = self.gui_config.app_config.gui_state_config.get(self.config_id)
        if widget_config:
            self.opened = widget_config['opened']
            self.width = widget_config['width']
            self.height = widget_config['height']
            self.view_type = ViewType(widget_config['view_type'])
            self.on_config_load(widget_config)

    # Override this to render custom content
    def _content(self):
        pass

    def _attached_title_bar(self):
        if self.selected:
            imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.2, 0.4, 0.8, 1.0)

        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (0, 0))
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (5, 5))
        imgui.begin_child("TitleBar", height=30, border=True)

        imgui.text(self.window_name)
        imgui.same_line(imgui.get_window_width() - 145)

        imgui.same_line(imgui.get_window_width() - 90)
        if imgui.begin_popup_context_item("DockPopup"):
            if imgui.selectable("Float")[1]:
                self.view_type = ViewType.FLOATING
                self.calculate_window_size()
                print("Dock Left selected")
            if imgui.selectable("Dock Left")[1]:
                self.view_type = ViewType.DOCK_LEFT
                self.calculate_window_size()
                print("Dock Left selected")
            if imgui.selectable("Dock Right")[1]:
                self.view_type = ViewType.DOCK_RIGHT
                self.calculate_window_size()
                print("Dock Right selected")
            if imgui.selectable("Dock Bottom")[1]:
                self.view_type = ViewType.DOCK_BOTTOM
                self.calculate_window_size()
                print("Dock Bottom selected")
            imgui.end_popup()
        if imgui.button("Dock"):
            imgui.open_popup("DockPopup")
        imgui.same_line(imgui.get_window_width() - 50)
        if imgui.button("Close"):
            self.opened = False
            print("Close button pressed")

        imgui.end_child()
        imgui.pop_style_var(2)
        if self.selected:
            imgui.pop_style_color()

    def calculate_window_size(self):
        w = imgui.get_io().display_size[0]
        h = imgui.get_io().display_size[1]
        if self.view_type == ViewType.FLOATING:
            self.width = min(self.width, w - 10)
            self.height = min(self.height, h - 10)
        elif self.view_type == ViewType.DOCK_LEFT:
            self.width = min(self.width, w / 4)
            self.height = h
        elif self.view_type == ViewType.DOCK_RIGHT:
            self.width = min(self.width, w / 4)
            self.height = h
        elif self.view_type == ViewType.DOCK_BOTTOM:
            self.width = w
            self.height = min(self.height, h / 4)

    def render(self):
        bottom_bar = 30
        top_bar = 18
        scene_buttons = 20
        if self.opened:
            if self.view_type == ViewType.FLOATING:
                pass
            elif self.view_type == ViewType.DOCK_LEFT:
                imgui.set_next_window_size(self.width, imgui.get_io().display_size[1] - top_bar - bottom_bar)
                imgui.set_next_window_position(0, top_bar)
            elif self.view_type == ViewType.DOCK_RIGHT:
                imgui.set_next_window_size(self.width, imgui.get_io().display_size[1] - top_bar - bottom_bar- scene_buttons)
                imgui.set_next_window_position(imgui.get_io().display_size[0] - self.width, top_bar + scene_buttons)
            elif self.view_type == ViewType.DOCK_BOTTOM:
                imgui.set_next_window_size(imgui.get_io().display_size[0], self.height)
                imgui.set_next_window_position(0, imgui.get_io().display_size[1] - self.height - bottom_bar)

            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))

            flags = imgui.WINDOW_NO_TITLE_BAR if self.view_type == ViewType.FLOATING else imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE

            expanded, opened = imgui.begin(self.window_name, flags=flags)

            if opened != self.opened:
                self.opened = opened

            if expanded:
                self._attached_title_bar()

                imgui.begin_child("Content", width=0, height=0, border=False)
                self.selected = imgui.is_window_focused()

                self._content()
                imgui.end_child()

            io = imgui.get_io()
            display_size = io.display_size
            mouse_pos = imgui.get_mouse_pos()
            window_pos = imgui.get_window_position()
            window_size = imgui.get_window_size()

            is_hovered = False
            draw_list = imgui.get_window_draw_list()

            hover_size = 10

            if (self.view_type == ViewType.DOCK_LEFT
                    and mouse_pos[0] < window_pos[0] + window_size[0]
                    and mouse_pos[0] > window_pos[0] + window_size[0] - hover_size):
                is_hovered = True
                imgui.set_mouse_cursor(imgui.MOUSE_CURSOR_RESIZE_EW)
                if imgui.is_mouse_down(imgui.MOUSE_BUTTON_LEFT):
                    self.resizing = True

            if (self.view_type == ViewType.DOCK_RIGHT
                    and mouse_pos[0] > window_pos[0]
                    and mouse_pos[0] < window_pos[0] + hover_size):
                is_hovered = True
                imgui.set_mouse_cursor(imgui.MOUSE_CURSOR_RESIZE_EW)
                if imgui.is_mouse_down(imgui.MOUSE_BUTTON_LEFT):
                    self.resizing = True

            if (self.view_type == ViewType.DOCK_BOTTOM
                    and mouse_pos[1] > window_pos[1]
                    and mouse_pos[1] < window_pos[1] + hover_size):
                imgui.set_mouse_cursor(imgui.MOUSE_CURSOR_RESIZE_NS)
                is_hovered = True
                if imgui.is_mouse_down(imgui.MOUSE_BUTTON_LEFT):
                    self.resizing = True
                    print("self. resizing", self.resizing)

            if not imgui.is_mouse_down(imgui.MOUSE_BUTTON_LEFT):
                self.resizing = False

            if self.resizing:
                if self.view_type == ViewType.DOCK_LEFT:
                    self.width = int(mouse_pos[0])
                elif self.view_type == ViewType.DOCK_RIGHT:
                    self.width = int(display_size[0] - mouse_pos[0])
                elif self.view_type == ViewType.DOCK_BOTTOM:
                    self.height = int(display_size[1] - mouse_pos[1] - bottom_bar)

            if self.view_type == ViewType.FLOATING:
                w, h = imgui.get_window_size()
                self.width = int(w)
                self.height = int(h)

            if is_hovered or self.resizing:
                color = imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0)  # Blue color
            else:
                color = imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 0.0)

            if self.view_type == ViewType.DOCK_LEFT:
                draw_list.add_line(window_pos[0] + window_size[0] - 5, window_pos[1],
                                   window_pos[0] + window_size[0] - 5, window_pos[1] + window_size[1], color)
            elif self.view_type == ViewType.DOCK_RIGHT:
                draw_list.add_line(window_pos[0] + 1, window_pos[1], window_pos[0] + 1,
                                   window_pos[1] + window_size[1],
                                   color)
            elif self.view_type == ViewType.DOCK_BOTTOM:
                draw_list.add_line(window_pos[0], window_pos[1] + 1, window_pos[0] + window_size[0],
                                   window_pos[1] + 1,
                                   color)

            if self.view_type == ViewType.FLOATING:
                w, h = imgui.get_window_size()
                self.width = int(w)
                self.height = int(h)

            imgui.end()
            imgui.pop_style_var(1)
