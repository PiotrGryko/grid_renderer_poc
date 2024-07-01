import uuid

import imgui

from app.gui.widget import Widget


class LayerItem:
    def __init__(self, net_layer):
        self.name = net_layer.name
        self.display_name = self.name.rsplit('.', 1)[-1]
        self.bounds = net_layer.bounds
        self.children = []
        self.id = uuid.uuid4()

        self.expanded = False
        self.hovered = False
        self.clicked = False

        self.collapsed_height = 25
        self.expanded_height = 70

        self.hover_bounds = None

    @staticmethod
    def from_net_layer(net_layer):
        item = LayerItem(net_layer)
        for s in net_layer.sub_layers:
            item.children.append(LayerItem.from_net_layer(s))
        return item

    def __repr__(self):
        return f"{self.name} {self.bounds} {self.children}"

    def _render(self, on_hover, on_hover_end, on_jump, full_name=True, active_layer_name=None, level=0):
        layer = self
        if self.hover_bounds is not None and active_layer_name is not None and layer.name in active_layer_name:
            draw_list = imgui.get_window_draw_list()
            hover_color = imgui.get_color_u32_rgba(1, 0.4, 0.0, 0.5)  # semi-transparent blue
            draw_list.add_rect_filled(self.hover_bounds[0], self.hover_bounds[1], self.hover_bounds[2],
                                      self.hover_bounds[3],
                                      hover_color)

        elif self.hovered and self.hover_bounds is not None:
            draw_list = imgui.get_window_draw_list()
            hover_color = imgui.get_color_u32_rgba(0.2, 0.4, 0.8, 0.5)  # semi-transparent blue
            draw_list.add_rect_filled(self.hover_bounds[0], self.hover_bounds[1], self.hover_bounds[2],
                                      self.hover_bounds[3],
                                      hover_color)

        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (0, 1))
        start_pos = imgui.get_cursor_screen_pos()
        for i in range(level):
            imgui.indent()
        name = layer.name if full_name else layer.display_name
        self.expanded, _ = imgui.collapsing_header(
            f"{name}##{layer.id}",
            flags=imgui.TREE_NODE_DEFAULT_OPEN if self.expanded else 0)

        if self.expanded:
            imgui.indent()
            imgui.dummy(0, 5)
            imgui.dummy(0, 5)
            if imgui.button(f"Jump##{layer.id}"):
                on_jump(self)
            imgui.dummy(0, 5)
            imgui.unindent()
        for i in range(level):
            imgui.unindent()
        imgui.pop_style_var(1)

        end_pos = imgui.get_cursor_screen_pos()
        window_pos = imgui.get_window_position()
        window_width = imgui.get_window_size()[0]
        item_rect_min = (window_pos[0], start_pos[1])
        item_rect_max = (window_pos[0] + window_width, end_pos[1])

        bounds = [item_rect_min[0], item_rect_min[1], item_rect_max[0], item_rect_max[1]]
        if self.hover_bounds != bounds:
            self.hover_bounds = bounds

        hovered = False
        # Check if the mouse is hovering within the bounds
        if imgui.is_mouse_hovering_rect(item_rect_min[0], item_rect_min[1], item_rect_max[0], item_rect_max[1]):
            hovered = True

        if self.expanded:
            for index, c in enumerate(layer.children):
                c._render(on_hover, on_hover_end, on_jump, False, level=level + 1, active_layer_name=active_layer_name)

        if hovered is False and self.hovered:
            # print("hover end", self.name, self.clicked)
            on_hover_end(self)
        elif hovered and not self.hovered:
            # print("hover start", self.name)
            on_hover(self)
        self.hovered = hovered


class LayersView(Widget):
    def __init__(self, config):
        super().__init__("Layers", config)
        self.config = config
        self.expanded = {}
        self.n_net = config.n_net
        self.hover_id = None
        self.width = 250
        self.camera_animation = config.camera_animation

        self.hovering = False

        self.layers = []

        self.current_weights_id = None
        self.current_model_id = None

    def _load_layers(self):
        self.layers.clear()
        for net_layer in self.n_net.net_layers:
            self.layers.append(LayerItem.from_net_layer(net_layer))

    def on_hover(self, layer):
        if self.hover_id != layer.name:
            self.hover_id = layer.name
            self.config.effects.show_quad(layer.name)
            self.config.publish_hover_message(layer)

    def on_hover_end(self, layer):
        self.hover_id = None
        self.config.effects.hide(layer.name)

    def on_jump(self, layer):
        bounds = layer.bounds
        print(f"jump pressed {bounds}")
        left, bottom, right, top = bounds
        self.camera_animation.animate_to_bounds(left, bottom, right, top)

    def _content(self):
        self.hovering = False
        if self.current_model_id != self.config.model_parser.current_model_name:
            self.current_model_id = self.config.model_parser.current_model_name
            self._load_layers()

        for l in self.layers:
            l._render(
                self.on_hover,
                self.on_hover_end,
                self.on_jump,
                active_layer_name=self.config.effects.raw_id
            )
