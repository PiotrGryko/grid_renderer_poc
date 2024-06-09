import time

import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer

from app.gui.view_bottom_info_bar import BottomInfoBar
from app.gui.gui_config import GuiConfig
from app.gui.view_layers import LayersView
from app.gui.view_download_manager import DownloadManagerPage
from app.gui.view_neuron_popup import NeuronPopup
from app.gui.view_terminal import ScienceBasedTerminal
from app.gui.view_top_menu import TopMenu


class GuiPants:
    def __init__(self, config):
        self.fps = 0
        self.start_time = time.time()
        self.frame_count = 0
        self.impl = None

        self.config = config
        self.n_window = self.config.n_window
        self.color_theme = self.config.color_theme

        self.top_menu = TopMenu(self.config)
        self.layers_view = LayersView(self.config)
        self.model_settings_page = DownloadManagerPage(self.config)
        self.terminal = ScienceBasedTerminal(self.config)
        self.bottom_info_bar = BottomInfoBar(self.config)
        self.neuron_popup = NeuronPopup(self.config)
        self.context = None

    def show_popup(self, value, layer_meta, world_position):
        self.neuron_popup.show(world_position, value, layer_meta)

    def hide_popup(self):
        self.neuron_popup.visible = False

    def attach_fancy_gui(self):
        self.context = imgui.create_context()
        self.impl = GlfwRenderer(self.n_window.window, attach_callbacks=False)

    def set_callbacks(self):
        glfw.set_framebuffer_size_callback(self.n_window.window, self.n_window.frame_buffer_size_callback)
        glfw.set_cursor_pos_callback(self.n_window.window, self.n_window.mouse_position_callback)
        glfw.set_window_refresh_callback(self.n_window.window, self.n_window.window_refresh_callback)

        def key_callback_wrapper(window, key, scancode, action, mods):
            self.n_window.window_key_callback(window, key, scancode, action, mods)
            self.impl.keyboard_callback(window, key, scancode, action, mods)

        def char_callback_wrapper(window, char):
            self.impl.char_callback(window, char)

        def mouse_scroll_callback_wrapper(window, x_offset, y_offset):
            self.n_window.mouse_scroll_callback(window, x_offset, y_offset)
            self.impl.scroll_callback(window, x_offset, y_offset)

        def mouse_input_wrapper(window, button, action, mods):
            io = imgui.get_io()
            if not io.want_capture_mouse:
                self.n_window.mouse_button_callback(window, button, action, mods)
            else:
                # Reset dragging state
                self.n_window.cancel_drag()

        glfw.set_mouse_button_callback(self.n_window.window, mouse_input_wrapper)
        glfw.set_key_callback(self.n_window.window, key_callback_wrapper)
        glfw.set_char_callback(self.n_window.window, char_callback_wrapper)
        glfw.set_scroll_callback(self.n_window.window, mouse_scroll_callback_wrapper)

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
        imgui.set_next_window_size(500, 100, imgui.ONCE)
        imgui.begin("Fps",
                    flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)
        r, g, b, a = self.color_theme.color_high
        imgui.push_style_color(imgui.COLOR_TEXT, r, g, b, a)  # Red color
        imgui.text(f"{self.config.app_config.model_name}")
        imgui.text(f"FPS: {self.fps:.2f}")
        imgui.text(f"Color: {self.color_theme.name}")
        imgui.text(f"Buffer: {self.config.app_config.buffer_width}x{self.config.app_config.buffer_height}")
        imgui.text(self.config.utils.get_memory_message())
        imgui.pop_style_color()

        imgui.end()

    def render_fancy_pants(self):

        # imgui.set_current_context(self.context)
        self.impl.process_inputs()

        imgui.new_frame()

        self.top_menu.render_top_menu()
        self.bottom_info_bar.render_bottom_info_bar()
        self.neuron_popup.render()
        self.render_config_box()
        self.layers_view.render()
        self.model_settings_page.render()

        self.terminal.render()
        # Rendering
        imgui.render()
        self.impl.render(imgui.get_draw_data())

        self.layers_view.render_detached(self.context, self.n_window)
        self.terminal.render_detached(self.context, self.n_window)
        self.model_settings_page.render_detached(self.context, self.n_window)

    def remove_gui(self):
        self.impl.shutdown()
