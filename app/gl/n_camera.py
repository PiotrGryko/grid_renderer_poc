import time


class CameraAnimation:
    def __init__(self, n_window, n_net):
        self.n_window = n_window
        self.n_net = n_net
        self.target_x = None
        self.target_y = None
        self.target_zoom = None

        self.start_x = None
        self.start_y = None
        self.start_zoom = None

        self.is_animating = False
        self.start_time = None
        self.duration = None
        self.left = None
        self.bottom = None

    def get_target_for_current_projection(self):
        difx, dify = self.n_window.projection.world_to_ndc_point(self.left, self.bottom)
        cx, cy = self.n_window.projection.get_translation()
        x = cx - difx
        y = cy - dify
        return x, y

    def animate_to_bounds(self, left, bottom, right, top, duration=1.0):
        # Calculate the target width and height in world coordinates
        world_w, world_h = right - left, top - bottom

        self.left = left + world_w / 2
        self.bottom = bottom + world_h / 2

        self.duration = duration
        self.start_zoom = self.n_window.zoom_factor
        self.target_x, self.target_y = self.get_target_for_current_projection()
        self.target_zoom = self.n_window.calculate_zoom_for_bounds(world_w, world_h)

        print("target", self.target_x, self.target_y, self.target_zoom)
        self.start_time = time.time()
        self.is_animating = True

    def animate_to_node(self, x, y, duration=2.0):
        # Calculate the target width and height in world coordinates

        self.left = x
        self.bottom = y

        self.duration = duration
        self.start_zoom = self.n_window.zoom_factor
        self.target_x, self.target_y = self.get_target_for_current_projection()
        self.target_zoom = 0.2

        print("target", self.target_x, self.target_y, self.target_zoom)
        self.start_time = time.time()
        self.is_animating = True

    def update_animation(self):
        if not self.is_animating:
            return

        delta_one = 0
        delta_two = 0
        t = (time.time() - self.start_time) / self.duration
        if 0 <= t < 0.5:
            stage = 1
            delta_one = t / 0.5  # Normalize t for Stage 1
        elif 0.5 <= t <= 1:
            stage = 2
            delta_one = 1
            delta_two = (t - 0.5) / 0.5  # Normalize t for Stage 2
        else:
            stage = None
        if t >= 1 and self.is_animating:
            print("animation finished")
            self.is_animating = False
        elif self.is_animating:
            if stage == 1:
                tx, ty = self.n_window.projection.get_translation()
                current_x = self.lerp(tx, self.target_x, delta_one)
                current_y = self.lerp(ty, self.target_y, delta_one)
                self.n_window.projection.translate_to(current_x, current_y)
            if stage == 2:
                zoom_out = self.lerp(self.start_zoom, self.target_zoom, delta_two)
                self.n_window.zoom_to_point(0, 0, zoom_out)

            self.n_window.on_viewport_updated()

    def lerp(self, start, end, t):
        return start + t * (end - start)
