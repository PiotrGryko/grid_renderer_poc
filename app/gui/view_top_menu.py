import imgui

from app.gui.file_dialog import FileDialog


class TopMenu:
    def __init__(self, gui_config, layers_view, terminal_view, model_manager_view):
        self.gui_config = gui_config
        self.layers_view = layers_view
        self.terminal_view = terminal_view
        self.model_manager_view = model_manager_view

        self.buffer_width = self.gui_config.app_config.buffer_width
        self.buffer_height = self.gui_config.app_config.buffer_height
        self.enable_blend = self.gui_config.app_config.enable_blend
        self.power_of_two = self.gui_config.app_config.power_of_two
        self.file_dialog = FileDialog(self.gui_config.app_config)

        self.selected_directory = None

    def render_top_menu(self):
        self.file_dialog.render()

        if self.selected_directory != self.file_dialog.selected_path:
            print("selected new path ", self.file_dialog.selected_path)
            self.selected_directory = self.file_dialog.selected_path
            self.gui_config.app.load_model(model_directory=self.selected_directory)
            self.file_dialog.selected_path = None

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Open")[0]:
                    print("Open selected")
                    self.file_dialog.open()
                if imgui.menu_item("Clear")[0]:
                    print("Clear selected")
                    self.gui_config.app_config.model_directory = None
                    self.gui_config.app_config.save_config()
                    self.gui_config.model_parser.clear()
                    self.gui_config.n_net.clear()
                    self.gui_config.app.load_model()
                if imgui.menu_item("Exit")[0]:
                    self.gui_config.n_window.close_window()
                imgui.end_menu()
            if imgui.begin_menu("Color"):
                imgui.begin_child("ColorMenuChild", width=220, height=250)
                for color in self.gui_config.color_theme.cmap_options:
                    selected = self.gui_config.color_theme.name == color
                    if imgui.menu_item(color, selected=selected)[0]:
                        print(color, "selected")
                        self.gui_config.color_name = color
                        #self.gui_config.app.reload_config()
                imgui.end_child()
                imgui.end_menu()
            if imgui.begin_menu("Settings"):
                imgui.separator()

                # Example custom elements
                changed, bw = imgui.input_int("Buffer Width", self.buffer_width)
                if changed:
                    self.buffer_width = bw
                changed, bh = imgui.input_int("Buffer Height", self.buffer_height)
                if changed:
                    self.buffer_height = bh
                changed, enable_b = imgui.checkbox("Enable Blend", self.enable_blend)
                if changed:
                    self.enable_blend = enable_b
                changed, pwr_of_two = imgui.checkbox("Power of Two", self.power_of_two)
                if changed:
                    self.power_of_two = pwr_of_two

                if imgui.button("Save Settings"):
                    self.gui_config.app_config.buffer_width = self.buffer_width
                    self.gui_config.app_config.buffer_height = self.buffer_height
                    self.gui_config.app_config.power_of_two = self.power_of_two
                    self.gui_config.app_config.enable_blend = self.enable_blend
                    self.gui_config.app.reload_graphics_settings()
                    imgui.close_current_popup()  # Close the settings menu
                imgui.end_menu()
            if imgui.begin_menu("View"):
                if imgui.menu_item("Layers View", selected=self.layers_view.opened)[0]:
                    self.layers_view.opened = not self.layers_view.opened
                if imgui.menu_item("Terminal", selected=self.terminal_view.opened)[0]:
                    self.terminal_view.opened = not self.terminal_view.opened
                if imgui.menu_item("Downloads manager", selected=self.model_manager_view.opened)[0]:
                    self.model_manager_view.opened = not self.model_manager_view.opened
                imgui.end_menu()
            imgui.end_main_menu_bar()
