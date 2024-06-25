from app.gl.n_quad import NQuad


class LayerEffect:
    def __init__(self):
        self.id = None
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.w = 0
        self.h = 0
        self.updated = False
        self.quad = None
        self.bounds = None
        self.visible = False

        self.padding = 20
        self.min_size = 40

    def refit_quad(self, n_window):
        min_w, min_h = n_window.window_to_world_cords(0, 0)
        max_w, max_h = n_window.window_to_world_cords(self.min_size, self.min_size)
        w = max_w - min_w
        h = max_h - min_h
        min_size = w

        x1 = self.x1
        x2 = self.x2
        y1 = self.y1
        y2 = self.y2
        dif_x = 0
        dif_y = 0
        if self.w < min_size:
            dif_x = (min_size - self.w) / 2
        if self.h < min_size:
            dif_y = (min_size - self.h) / 2

        dif = max(dif_x, dif_y)
        if dif > 0:
            x1 = self.x1 - dif
            x2 = self.x2 + dif
            y1 = self.y1 - dif
            y2 = self.y2 + dif
            self.radius = dif
        else:
            self.radius = self.padding
        # print("updated size ", min_size, self.w, self.h)
        # print("final size", x2 - x1, y2 - y1, y2, y1)
        self.quad.update_quad_position(x1, y1, x2, y2)

    def create_quad(self):
        if self.quad is None:
            self.quad = NQuad()
            self.quad.create_quad()

    def update_quad(self, n_window):
        if not self.updated and self.visible:
            self.refit_quad(n_window)
            self.updated = True

    def show_quad(self, id, bounds):
        self.id = id
        self.bounds = bounds
        x1, y1, x2, y2 = self.bounds
        self.padding = min(x2 - x1, y2 - y1) * 0.1
        self.x1 = x1 - self.padding
        self.y1 = y1 - self.padding
        self.x2 = x2 + self.padding
        self.y2 = y2 + self.padding
        self.w = self.x2 - self.x1
        self.h = self.y2 - self.y1
        self.updated = False
        self.visible = True

    def draw(self, effects_shader, n_window):
        effects_shader.use()
        if self.visible:
            self.create_quad()
            self.update_quad(n_window)
            effects_shader.update_radius(self.radius)
            effects_shader.update_quad_size(self.quad.w, self.quad.h)
            self.quad.draw()


class NEffects:
    def __init__(self, n_net, n_window):
        self.n_net = n_net
        self.n_window = n_window
        self.layer_effect = None
        self.zoom = 0
        self.id = None
        self.raw_id = None

    def on_viewport_changed(self, viewport):
        x, y, w, h, zoom = viewport
        if self.layer_effect is not None and self.zoom != zoom:
            self.zoom = zoom
            self.layer_effect.updated = False

    def show_quad(self, id, bounds):
        if self.layer_effect is None:
            self.layer_effect = LayerEffect()
        self.id = id
        self.layer_effect.show_quad(id, bounds)

    def show_quad_raw(self, id):
        if self.layer_effect is None:
            self.layer_effect = LayerEffect()
        self.id = id
        self.raw_id = id
        bounds = None
        for l in self.n_net.layers:
            if self.id == l.name:
                bounds = l.meta.bounds
                break
        if bounds is not None:
            self.layer_effect.show_quad(id, bounds)

    def hide(self, id):
        if self.layer_effect is not None and self.id == id:
            self.layer_effect.visible = False

    def draw(self, effects_shader):
        if self.layer_effect is not None:
            self.layer_effect.draw(effects_shader, self.n_window)
