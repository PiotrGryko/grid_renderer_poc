import time

import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw


class GuiPants:
    def __init__(self, n_window, color_theme, utils):
        self.fps = 0
        self.color_theme = color_theme
        self.start_time = time.time()
        self.frame_count = 0
        self.n_window = n_window
        self.impl = None
        self.utils = utils

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

        def mouse_callback_wrapper(window, x_offset, y_offset):
            self.n_window.mouse_scroll_callback(window, x_offset, y_offset)
            self.impl.scroll_callback(window, x_offset, y_offset)

        glfw.set_key_callback(self.n_window.window, key_callback_wrapper)
        glfw.set_scroll_callback(self.n_window.window, mouse_callback_wrapper)



    def render_fancy_pants(self):
        self.impl.process_inputs()

        # Update frame count
        self.frame_count += 1
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Open")[0]:
                    print("Open selected")
                if imgui.menu_item("Save")[0]:
                    print("Save selected")
                if imgui.menu_item("Exit")[0]:
                    self.n_window.close_window()
                imgui.end_menu()
            if imgui.begin_menu("Color"):
                imgui.begin_child("ColorMenuChild", width=220, height=250)
                for color in self.color_theme.cmap_options:
                    selected = self.color_theme.name == color
                    if imgui.menu_item(color, selected=selected)[0]:
                        print(color, "selected")
                        self.color_theme.load_by_name(color)
                imgui.end_child()
                imgui.end_menu()
            imgui.end_main_menu_bar()

            # Create a floating window with input fields
        imgui.begin("Floating Input Window")

        # Text input field
        changed, text_value = imgui.input_text("Text Input", "Default Text", 256)
        if changed:
            print("Text Input Changed:", text_value)
        imgui.end()

        # Create a floating window docked to the top

        imgui.set_next_window_bg_alpha(0.0)  # Make background transparent
        imgui.set_next_window_position(0, imgui.get_frame_height(), imgui.ONCE)
        imgui.set_next_window_size(175, 70, imgui.ONCE)
        imgui.begin("Fps",
                    flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE)
        r, g, b, a = self.color_theme.color_high
        imgui.push_style_color(imgui.COLOR_TEXT, r,g,b,a)  # Red color
        imgui.text(f"FPS: {self.fps:.2f}")
        imgui.text(f"Color: {self.color_theme.name}")
        imgui.text(self.utils.get_memory_message())
        imgui.pop_style_color()

        imgui.end()
        # Your GUI code here
        # imgui.begin("Hello, World!")
        # imgui.text("This is some useful text.")
        # imgui.end()

        # Rendering
        imgui.render()
        self.impl.render(imgui.get_draw_data())

    def remove_gui(self):
        self.impl.shutdown()
