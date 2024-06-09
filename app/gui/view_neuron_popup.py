import imgui


class NeuronPopup:
    def __init__(self, config):
        self.visible = False
        self.world_position = (0, 0)
        self.value = ""
        self.layer_meta = None
        self.config = config

    def show(self, position, value, layer_meta):
        self.visible = True
        self.world_position = position
        self.value = value
        self.layer_meta = layer_meta

    def render(self):
        if not self.visible:
            return

        w_x, w_y = self.world_position
        x, y, w, z = self.config.n_window.world_to_window_cords(w_x, w_y, 1, 1)

        x_within_layer = int(w_x - 0.5 - self.layer_meta.column_offset)
        y_within_layer = int(w_y - 0.5 - self.layer_meta.row_offset)

        window_width = 250
        window_height = 100
        radius = 10

        # Set the window position and size
        imgui.set_next_window_position(x - window_width / 2, y - window_height - radius, condition=imgui.ALWAYS)
        imgui.set_next_window_size(window_width, window_height)
        imgui.set_next_window_bg_alpha(0.75)  # Set the background alpha to make it transparent

        # Display the popup with text fields
        imgui.begin("Neuron Info",
                    flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        imgui.text(f"Value: {self.value}")
        imgui.text_wrapped(f"Layer: {self.layer_meta.name}")
        imgui.text(f"Position x:{x_within_layer} y:{y_within_layer}")
        if imgui.button("Close"):
            self.visible = False
        imgui.same_line()
        if imgui.button("Jump"):
            self.config.camera_animation.animate_to_node(w_x, w_y)

        imgui.end()

        # Draw a triangle below the window
        draw_list = imgui.get_foreground_draw_list()
        window_min_x, window_min_y = x - window_width / 2, y - window_height - radius
        draw_list.add_triangle_filled(x, y, x - radius, window_min_y + window_height, x + radius,
                                      window_min_y + window_height, imgui.get_color_u32_rgba(0.2, 0.6, 1.0, 1.0))
