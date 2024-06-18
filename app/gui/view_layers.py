import uuid

import imgui

from app.gui.widget import Widget


class LayerItem:
    def __init__(self, name, bounds, rows_count, columns_count, size, description):
        self.name = name
        self.display_name = self.name.rsplit('.', 1)[-1]
        self.bounds = bounds
        self.rows_count = rows_count
        self.columns_count = columns_count
        self.size = size
        self.description = description
        self.children = []
        self.id = uuid.uuid4()

        self.expanded = False
        self.hovered = False
        self.clicked = False

        self.collapsed_height = 25
        self.expanded_height = 70

        self.hover_bounds = None

    def calculate_bounds(self):
        all_bounds = []
        if self.bounds is None:
            if len(self.children) == 0:
                return None

            for c in self.children:
                child_bounds = c.calculate_bounds()
                if child_bounds is not None:
                    all_bounds.append(child_bounds)
            col_min = min(item[0] for item in all_bounds)
            row_min = min(item[1] for item in all_bounds)
            col_max = max(item[2] for item in all_bounds)
            row_max = max(item[3] for item in all_bounds)

            self.bounds = [col_min, row_min, col_max, row_max]
            self.description = f"Size: {col_max - col_min}x{row_max - row_min}"
        return self.bounds

    def _render(self, on_hover, on_hover_end, on_jump, full_name=True, level=0):
        layer = self
        if self.hovered and self.hover_bounds is not None:
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
            imgui.text(layer.description)
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
                c._render(on_hover, on_hover_end, on_jump, False, level=level + 1)

        if hovered is False and self.hovered:
            print("hover end", self.name, self.clicked)
            on_hover_end(self)
        elif hovered and not self.hovered:
            print("hover start", self.name)
            on_hover(self)
        self.hovered = hovered


class LayersView(Widget):
    def __init__(self, config):
        super().__init__("Layers")
        self.config = config
        self.expanded = {}
        self.n_net = config.n_net
        self.hover_id = None
        self.width = 250
        self.camera_animation = config.camera_animation
        self.flat_items = []
        self.tree_item = None
        self.hovering = False

    def _create_flat_items(self):
        for l in self.n_net.layers:
            self.flat_items.append(LayerItem(
                name=l.name,
                bounds=l.meta.bounds,
                rows_count=l.meta.rows_count,
                columns_count=l.meta.columns_count,
                size=l.meta.size,
                description=f"Size: {l.columns_count}x{l.rows_count} {l.size} elements"
            ))

    def _create_tree_items(self):
        def fill_leaf(layer_item, component):
            for c in component.components:
                l = next((item for item in self.n_net.layers if item.name == c.name), None)
                if l is None:
                    item = LayerItem(
                        name=c.name,
                        bounds=None,
                        rows_count=0,
                        columns_count=0,
                        size=None,
                        description=None
                    )
                else:
                    print("layer name ", l.name)
                    item = LayerItem(
                        name=l.name,
                        bounds=l.meta.bounds,
                        rows_count=l.meta.rows_count,
                        columns_count=l.meta.columns_count,
                        size=l.meta.size,
                        description=f"Size: {l.columns_count}x{l.rows_count} {l.size} elements"
                    )
                layer_item.children.append(item)
                fill_leaf(item, c)

        tree = self.n_net.layers_tree
        top_item = LayerItem(
            name=tree.name,
            bounds=None,
            rows_count=0,
            columns_count=0,
            size=None,
            description=None
        )
        fill_leaf(top_item, tree)
        top_item.calculate_bounds()
        self.tree_item = top_item

    def _on_visibility_changed(self):
        self.config.show_layers_view = self.opened

    def _update_visibility(self):
        self.opened = self.config.show_layers_view

    def on_hover(self, layer):
        if self.hover_id != layer.name:
            print("hovering true ", layer.name)
            self.hover_id = layer.name
            self.config.effects.show_quad(layer.name, layer.bounds)
            self.config.publish_hover_message(layer)

    def on_hover_end(self, layer):
        self.hover_id = None
        self.config.effects.hide(layer.name)

        print("hovering false", layer.name)

    def on_jump(self, layer):
        bounds = layer.bounds
        print(f"jump pressed {bounds}")
        left, bottom, right, top = bounds
        self.camera_animation.animate_to_bounds(left, bottom, right, top)

    def _content(self):
        self.hovering = False
        if self.n_net.layers_tree is None:
            if len(self.flat_items) == 0:
                self._create_flat_items()

            if len(self.expanded) != len(self.flat_items):
                self.expanded = {}

            for i, layer in enumerate(self.flat_items):
                layer._render(
                    self.on_hover,
                    self.on_hover_end,
                    self.on_jump
                )
        else:
            if self.tree_item is None:
                self._create_tree_items()
            self.tree_item._render(
                self.on_hover,
                self.on_hover_end,
                self.on_jump
            )
