import time

import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw

from app.gui.layers_view import LayersView
from app.gui.model_settings import ModelSettingsPage
from app.gui.terminal import ScienceBasedTerminal
from app.gui.top_menu import TopMenu


class GuiPants:
    def __init__(self, n_net, n_window, color_theme, utils, config, app, download_manager, camera_animation):
        self.fps = 0
        self.color_theme = color_theme
        self.start_time = time.time()
        self.frame_count = 0
        self.n_window = n_window
        self.impl = None
        self.utils = utils
        self.config = config
        self.app = app
        self.n_net = n_net
        self.top_menu = TopMenu(self.config, self.n_window, self.color_theme, self.app)
        self.layers_view = LayersView(self.n_net, camera_animation)
        self.model_settings_page = ModelSettingsPage(download_manager, self.config)
        self.terminal = ScienceBasedTerminal(self.app, self.n_net)

    def attach_fancy_gui(self):
        imgui.create_context()
        self.impl = GlfwRenderer(self.n_window.window, attach_callbacks=False)

    def set_callbacks(self):
        glfw.set_framebuffer_size_callback(self.n_window.window, self.n_window.frame_buffer_size_callback)
        glfw.set_cursor_pos_callback(self.n_window.window, self.n_window.mouse_position_callback)
        glfw.set_mouse_button_callback(self.n_window.window, self.n_window.mouse_button_callback)
        glfw.set_window_refresh_callback(self.n_window.window, self.n_window.window_refresh_callback)

        def key_callback_wrapper(window, key, scancode, action, mods):
            self.n_window.window_key_callback(window, key, scancode, action, mods)
            self.impl.keyboard_callback(window, key, scancode, action, mods)

        def char_callback_wrapper(window, char):
            self.impl.char_callback(window, char)

        def mouse_callback_wrapper(window, x_offset, y_offset):
            self.n_window.mouse_scroll_callback(window, x_offset, y_offset)
            self.impl.scroll_callback(window, x_offset, y_offset)

        glfw.set_key_callback(self.n_window.window, key_callback_wrapper)
        glfw.set_char_callback(self.n_window.window, char_callback_wrapper)
        glfw.set_scroll_callback(self.n_window.window, mouse_callback_wrapper)

    def render_config_box(self):
        '''
        Debug info
        :return:
        '''
        # Update frame count
        self.frame_count += 1
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()

        imgui.set_next_window_bg_alpha(0.0)  # Make background transparent
        imgui.set_next_window_position(0, imgui.get_frame_height(), imgui.ONCE)
        imgui.set_next_window_size(175, 80, imgui.ONCE)
        imgui.begin("Fps",
                    flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)
        r, g, b, a = self.color_theme.color_high
        imgui.push_style_color(imgui.COLOR_TEXT, r, g, b, a)  # Red color
        imgui.text(f"FPS: {self.fps:.2f}")
        imgui.text(f"Color: {self.color_theme.name}")
        imgui.text(f"Buffer: {self.config.buffer_width}x{self.config.buffer_height}")
        imgui.text(self.utils.get_memory_message())
        imgui.pop_style_color()

        imgui.end()

    def render_fancy_pants(self):
        self.impl.process_inputs()

        imgui.new_frame()

        self.top_menu.render_top_menu()
        self.render_config_box()
        self.layers_view.render()
        if self.top_menu.show_model_settings:
            self.top_menu.show_model_settings = self.model_settings_page.render()

        self.terminal.render()
        # Rendering
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def remove_gui(self):
        self.impl.shutdown()
