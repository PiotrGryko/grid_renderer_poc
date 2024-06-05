import imgui


class LayersView:
    def __init__(self, n_net, camera_animation):
        self.expanded = []
        self.layers = []
        self.n_net = n_net
        self.hover_index = -1
        self.width = 250
        self.camera_animation = camera_animation

    def render(self):
        if len(self.expanded) != len(self.n_net.layers):
            self.expanded = [False] * len(self.n_net.layers)  # Track expansion state of each layer

        # window_width, window_height = imgui.get_io().display_size
        # imgui.set_next_window_position(window_width - self.width, 0)
        # imgui.set_next_window_size(self.width, window_height/2)
        imgui.begin("Layers", closable=True)

        hovering = False
        for i, layer in enumerate(self.n_net.layers):
            # Create a collapsible header for each layer
            expanded, _ = imgui.collapsing_header(f"{layer.name}",
                                                  flags=imgui.TREE_NODE_DEFAULT_OPEN if self.expanded[i] else 0)
            self.expanded[i] = expanded

            if expanded:
                imgui.text(f"Size: {layer.columns_count}x{layer.rows_count} {layer.size} elements")

                if imgui.button(f"Jump##{i}"):
                    print(f"jump pressed {layer.bounds}")
                    left, bottom, right, top = layer.bounds
                    self.camera_animation.animate_to_bounds(left, bottom, right, top)

            if imgui.is_item_hovered():
                # Callback for hovering over the element
                hovering = True
                if self.hover_index != i:
                    print(f"Hovering over {layer.name}")
                    self.hover_index = i

        if not hovering and self.hover_index != -1:
            self.hover_index = -1
            print(f"Hovering end")

        imgui.end()
