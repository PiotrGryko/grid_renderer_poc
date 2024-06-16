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

    def _render(self, on_hover, on_hover_end, on_jump, level=0):
        layer = self
        hovered = False
        height = self.expanded_height if self.expanded else self.collapsed_height

        if self.hovered:
            imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0.2, 0.4, 0.8, 0.5)  # Blue background

        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (0, 0))

        imgui.begin_child(f"child_{layer.id}", width=0, height=height, border=False)

        for i in range(level):
            imgui.indent()

        self.expanded, _ = imgui.collapsing_header(
            layer.name,
            flags=imgui.TREE_NODE_DEFAULT_OPEN if self.expanded else 0)
        if imgui.is_item_hovered() and imgui.is_mouse_clicked(imgui.MOUSE_BUTTON_LEFT):
            print(f"Child {layer.id} clicked")
            self.clicked = True
        imgui.indent()

        if self.expanded:
            imgui.dummy(0,5)
            imgui.text(layer.description)
            imgui.dummy(0,5)
            if imgui.button(f"Jump##{layer.id}"):
                on_jump(self)

        imgui.end_child()
        imgui.pop_style_var(1)

        if self.hovered:
            imgui.pop_style_color()

        if imgui.is_item_hovered() and imgui.is_mouse_clicked(imgui.MOUSE_BUTTON_LEFT):
            print(f"Child {layer.id} clicked")
            self.clicked = True

        if imgui.is_item_hovered():
            hovered = True

        if self.clicked:
            hovered = True

        if imgui.is_mouse_released(imgui.MOUSE_BUTTON_LEFT):
            if self.clicked:
                print(f"Child {layer.id} released")
            self.clicked = False

        if self.expanded:
            for index, c in enumerate(layer.children):
                c._render(on_hover, on_hover_end, on_jump, level=level + 1)

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
                # self._render_layer(layer, i)
        else:
            if self.tree_item is None:
                self._create_tree_items()
            self.tree_item._render(
                self.on_hover,
                self.on_hover_end,
                self.on_jump
            )
            # self._render_layer(self.tree_item, 0)

        # if not self.hovering and self.hover_id is not None:
        #     self.on_hover_end()
