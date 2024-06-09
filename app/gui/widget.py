import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer

from enum import Enum


class ViewType(Enum):
    FLOATING = 0
    DOCK_LEFT = 1
    DOCK_RIGHT = 2
    DOCK_BOTTOM = 3


class Widget:
    def __init__(self, name):
        self.window_name = name
        self.view_type = ViewType.FLOATING
        self.detached_window = None
        self.detached_impl = None
        self.context = None
        self.opened = True
        self.detached = False
        self.selected = False

        self.window_width = 300
        self.window_height = 400

    # Override this to render custom content
    def _content(self):
        pass

    # On visibility changed, called on self.opened change
    def _on_visibility_changed(self):
        pass

    # Set visibility from config
    def _update_visibility(self):
        pass

    def _attached_title_bar(self):
        if self.selected:
            imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.2, 0.4, 0.8, 1.0)

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (5, 5))
        imgui.begin_child("TitleBar", height=30, border=True)
        imgui.text(self.window_name)
        imgui.same_line(imgui.get_window_width() - 145)
        if imgui.button("Detach"):
            print("Close button pressed")
            self.detached = True

        imgui.same_line(imgui.get_window_width() - 90)
        if imgui.begin_popup_context_item("DockPopup"):
            if imgui.selectable("Float")[1]:
                self.view_type = ViewType.FLOATING
                print("Dock Left selected")
            if imgui.selectable("Dock Left")[1]:
                self.view_type = ViewType.DOCK_LEFT
                print("Dock Left selected")
            if imgui.selectable("Dock Right")[1]:
                self.view_type = ViewType.DOCK_RIGHT
                print("Dock Right selected")
            if imgui.selectable("Dock Bottom")[1]:
                self.view_type = ViewType.DOCK_BOTTOM
                print("Dock Bottom selected")
            imgui.end_popup()
        if imgui.button("Dock"):
            imgui.open_popup("DockPopup")
        imgui.same_line(imgui.get_window_width() - 50)
        if imgui.button("Close"):
            self.opened = False
            self._on_visibility_changed()
            # Handle detaching logic here
            print("Close button pressed")

        imgui.end_child()
        imgui.pop_style_var()
        if self.selected:
            imgui.pop_style_color()

    def _detached_title_bar(self):
        if self.selected:
            imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.2, 0.4, 0.8, 1.0)  # Blue background

            # Push padding style for the custom title bar
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (5, 5))
        # Custom title bar
        imgui.begin_child("TitleBar", height=30, border=True)
        imgui.text(self.window_name)
        imgui.same_line(imgui.get_window_width() - 55)
        if imgui.button("Attach"):
            self.detached = False
            self.opened = True
            self._on_visibility_changed()
            glfw.set_window_should_close(self.detached_window, True)
            print("Attach button pressed")
        imgui.end_child()
        imgui.pop_style_var()
        if self.selected:
            imgui.pop_style_color()

    def render(self):
        self._update_visibility()

        if not self.opened and self.detached_window is not None:
            glfw.set_window_should_close(self.detached_window, True)

        if self.detached:
            return
        self._attached()

    def render_detached(self, context, n_window):
        self._activate_detached_context()
        self._detached()
        self.close()

        glfw.make_context_current(n_window.window)
        imgui.set_current_context(context)

    def _attached(self):
        if self.opened:
            # Update the position and size based on the current view type
            if self.view_type == ViewType.FLOATING:
                pass
                # imgui.set_next_window_size(self.window_width, self.window_height)
                # imgui.set_next_window_position(50, 50)
            elif self.view_type == ViewType.DOCK_LEFT:
                imgui.set_next_window_size(300, imgui.get_io().display_size[1])
                imgui.set_next_window_position(0, 0)
            elif self.view_type == ViewType.DOCK_RIGHT:
                imgui.set_next_window_size(300, imgui.get_io().display_size[1])
                imgui.set_next_window_position(imgui.get_io().display_size[0] - 300, 0)
            elif self.view_type == ViewType.DOCK_BOTTOM:
                imgui.set_next_window_size(imgui.get_io().display_size[0], 200)
                imgui.set_next_window_position(0, imgui.get_io().display_size[1] - 200)

            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
            expanded, opened = imgui.begin(self.window_name, flags=imgui.WINDOW_NO_TITLE_BAR)

            if opened != self.opened:
                self.opened = opened
                self._on_visibility_changed()

            if expanded:
                self._attached_title_bar()

                imgui.begin_child("Content", width=0, height=0, border=False)
                self.selected = imgui.is_window_focused()

                self._content()
                imgui.end_child()
            imgui.end()
            imgui.pop_style_var(1)  # This should match the number of push_style_var calls

    def _framebuffer_size_callback(self, window, width, height):
        self.window_width = width
        self.window_height = height
        self.detached_impl.io.display_size = width, height

    def _window_refresh_callback(self, window):
        self._detached()

    def _activate_detached_context(self):
        if not self.detached:
            return

        if self.detached_window is None:

            self.detached_window = glfw.create_window(self.window_width,
                                                      self.window_height,
                                                      "Detached " + self.window_name,
                                                      None,
                                                      None)
            glfw.make_context_current(self.detached_window)
            self.context = imgui.create_context()
            imgui.set_current_context(self.context)
            self.detached_impl = GlfwRenderer(self.detached_window)
            glfw.set_window_size_callback(self.detached_window, self._framebuffer_size_callback)
            glfw.set_window_refresh_callback(self.detached_window, self._window_refresh_callback)
        else:
            glfw.make_context_current(self.detached_window)
            imgui.set_current_context(self.context)

    def _detached(self):

        if self.detached_window is not None and not glfw.window_should_close(self.detached_window):
            glfw.poll_events()
            self.detached_impl.process_inputs()
            imgui.new_frame()
            imgui.set_next_window_position(0, 0, condition=imgui.ALWAYS)
            imgui.set_next_window_size(self.window_width, self.window_height, condition=imgui.ALWAYS)
            imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
            imgui.begin(
                self.window_name,
                flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
            self.selected = imgui.is_window_focused()
            self._detached_title_bar()
            self._content()

            imgui.end()
            imgui.pop_style_var(1)  # This should match the number of push_style_var calls
            imgui.render()
            self.detached_impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.detached_window)

    def close(self):
        if self.detached_window is not None and glfw.window_should_close(self.detached_window):
            print("window closed")
            self.detached_impl.shutdown()
            glfw.destroy_window(self.detached_window)
            self.detached_window = None
            self.detached = False
