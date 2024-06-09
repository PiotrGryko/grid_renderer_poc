import imgui

from app.gui.widget import Widget


class LayersView(Widget):
    def __init__(self, config):
        super().__init__("Layers")
        self.config = config
        self.expanded = []
        self.layers = []
        self.n_net = config.n_net
        self.hover_index = -1
        self.width = 250
        self.camera_animation = config.camera_animation

    def _on_visibility_changed(self):
        self.config.show_layers_view = self.opened

    def _update_visibility(self):
        self.opened = self.config.show_layers_view

    def _content(self):
        if len(self.expanded) != len(self.n_net.layers):
            self.expanded = [False] * len(self.n_net.layers)

        hovering = False
        for i, layer in enumerate(self.n_net.layers):
            expanded, _ = imgui.collapsing_header(
                f"{layer.name}",
                flags=imgui.TREE_NODE_DEFAULT_OPEN if self.expanded[i] else 0)
            self.expanded[i] = expanded

            if expanded:
                imgui.text(f"Size: {layer.columns_count}x{layer.rows_count} {layer.size} elements")
                if imgui.button(f"Jump##{i}"):
                    bounds = layer.meta.bounds
                    print(f"jump pressed {bounds}")
                    left, bottom, right, top = bounds
                    self.camera_animation.animate_to_bounds(left, bottom, right, top)

            if imgui.is_item_hovered():
                hovering = True
                if self.hover_index != i:
                    self.hover_index = i

        if not hovering and self.hover_index != -1:
            self.hover_index = -1
