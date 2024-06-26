import time

import OpenGL.GL as gl
import glfw
import imgui
import numpy as np

from app.gl.n_projection import Projection
from app.gl.n_shader import NShader


class NWindow:
    def __init__(self):
        self.window = None
        self.dragging = False
        self.mouse_press_pos = None
        self.width = 1280
        self.height = 1280
        self.last_mouse_x = 0.0
        self.last_mouse_y = 0.0
        self.zoom_factor = 1.0
        self.min_zoom = 0.01
        self.max_zoom = 1
        self.zoom_step = 0.01
        self.aspect_ratio = self.width / self.height
        self.projection = Projection()
        self.render_func = None
        self.on_click_func = None
        self.viewport_updated_func = None
        self.key_pressed_func = None
        self.key_repeat_func = None
        self.zoom_percent = 0
        self.formatted_zoom = None

        self.n_billboards_from_texture_shader = NShader()
        self.n_color_map_v2_texture_shader = NShader()
        self.n_effects_shader = NShader()

    def calculate_min_zoom(self, n_net):
        content_width, content_height = n_net.total_width, n_net.total_height
        w, h = self.window_to_viewport_cords(self.width, self.height)
        min_zoom_x = w / content_width / 1.2
        min_zoom_y = h / content_height / 1.2
        self.min_zoom = min_zoom_x if min_zoom_x < min_zoom_y else min_zoom_y
        self.zoom_factor = self.min_zoom  # current zoom value
        self.zoom_step = (self.max_zoom - self.min_zoom) / 100  # zoom step change on every mouse wheel scroll
        self.mouse_scroll_callback(self.window, 1, 1)
        print(w, h, content_width, content_height)
        print("Min zoom calculated:", self.min_zoom, self.max_zoom, self.zoom_step)

    def calculate_zoom_for_bounds(self, content_width, content_height):
        w, h = self.window_to_viewport_cords(self.width, self.height)
        min_zoom_x = w / content_width / 1.2
        min_zoom_y = h / content_height / 1.2
        return min(min_zoom_x, min_zoom_y)

    def create_window(self):
        # Initialize OpenGL and create a window
        glfw.init()

        # Set GLFW context hints
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.SAMPLES, 4)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.RESIZABLE, gl.GL_TRUE)

        # Create a GLFW window
        self.window = glfw.create_window(self.width, self.height, "Hello World", None, None)
        # Make the created window's context current

        glfw.make_context_current(self.window)

        # Check if window creation succeeded
        if not self.window:
            glfw.terminate()
            raise ValueError("Failed to create GLFW window")

    def set_callbacks(self):
        glfw.set_framebuffer_size_callback(self.window, self.frame_buffer_size_callback)
        glfw.set_scroll_callback(self.window, self.mouse_scroll_callback)
        glfw.set_cursor_pos_callback(self.window, self.mouse_position_callback)
        glfw.set_mouse_button_callback(self.window, self.mouse_button_callback)
        glfw.set_window_refresh_callback(self.window, self.window_refresh_callback)
        glfw.set_key_callback(self.window, self.window_key_callback)

    def start_main_loop(self):
        while not glfw.window_should_close(self.window):
            if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
                glfw.set_window_should_close(self.window, True)

            if self.render_func:
                self.render_func()
            glfw.poll_events()

    def close_window(self):
        glfw.set_window_should_close(self.window, True)

    def destroy_window(self):
        glfw.terminate()

    def set_render_func(self, render_func):
        self.render_func = render_func

    def set_on_click_func(self, on_click_func):
        self.on_click_func = on_click_func

    def set_key_pressed_func(self, key_pressed_func):
        self.key_pressed_func = key_pressed_func

    def set_key_repeat_func(self, key_repeat_func):
        self.key_repeat_func = key_repeat_func

    def set_viewport_updated_func(self, viewport_updated_func):
        self.viewport_updated_func = viewport_updated_func

    def get_projection_matrix(self):
        return self.projection.matrix

    def window_to_viewport_cords(self, x, y):
        """
        window space (1280x1280) to viewport coords [0-2] with [1,1] at the center
        :param x:
        :param y:
        :return:
        """
        sx = x / self.width * 2.0
        sy = y / self.height * 2.0
        return sx, sy

    def window_to_ndc_cords(self, x, y):
        """
        window space (1280x1280) to NDC [-1,1] with [0,0] at the center
        :param x:
        :param y:
        :return:
        """
        sx = (2.0 * x) / self.width - 1.0
        sy = (2.0 * y) / self.height - 1
        return sx, sy

    def window_to_world_cords(self, x, y):
        """
        window space (1280x1280) to WORLD cordinates (0,0, - W,H)
        :param x:
        :param y:
        :return:
        """
        sx = (2.0 * x) / self.width - 1.0
        sy = (2.0 * y) / self.height - 1
        wx, wy = self.projection.ndc_to_world_point(sx, sy)
        return wx, wy

    def viewport_to_world_cords(self):
        '''
        :return: current viewport in world coordinates
        '''
        # Window bottom left
        x1, y1 = self.projection.ndc_to_world_point(-1, -1)
        # Window top right
        x2, y2 = self.projection.ndc_to_world_point(1, 1)
        w, h = x2 - x1, y2 - y1
        return (x1, y1, w, h, self.zoom_factor)

    def world_to_ndc_cords(self, x1, y1, x2, y2):
        '''
        :return: world coordinates (for example x5400:y1300) to ndc cords (-1, -1 top left corner, 1,1 top right corner)
        '''
        # Window bottom left
        sx1, sy1 = self.projection.world_to_ndc_point(x1, y1)
        # Window top right
        sx2, sy2 = self.projection.world_to_ndc_point(x2, y2)

        return (sx1, sy1, sx2, sy2, self.zoom_factor)

    def ndc_to_window_cords(self, x1, y1, x2, y2):
        '''
        :return:  ndc coordinates (-1, -1 top left corner, 1,1 top right corner) to window coordinates (0,0 top left, 1280,1280 top right)
        '''
        sx1 = (x1 + 1) * self.width / 2.0
        sy1 = (y1 + 1) * self.height / 2.0
        sx2 = (x2 + 1) * self.width / 2.0
        sy2 = (y2 + 1) * self.height / 2.0
        return (sx1, sy1, sx2, sy2)

    def world_to_window_cords(self, x1, y1, x2, y2):
        '''
        :return:  WORLD coordinates  (for example x5400:y1300) to window coordinates (0,0 top left, 1280,1280 top right)
        '''
        (sx1, sy1, sx2, sy2, zoom_factor) = self.world_to_ndc_cords(
            x1,
            y1,
            x2,
            y2)
        (wx1, wy1, wx2, wy2) = self.ndc_to_window_cords(sx1, -sy1, sx2, -sy2)
        return (wx1, wy1, wx2, wy2)

    def on_viewport_updated(self):
        if self.viewport_updated_func:
            self.viewport_updated_func()

    def window_key_callback(self, window, key, scancode, action, mods):
        io = imgui.get_io()
        if io.want_capture_keyboard:
            return
        if action == glfw.PRESS:
            if self.key_pressed_func:
                self.key_pressed_func(key)

        if action == glfw.REPEAT:
            if self.key_repeat_func:
                self.key_repeat_func(key)

    def window_refresh_callback(self, window):
        if self.render_func:
            self.render_func()

    def frame_buffer_size_callback(self, window, w, h):
        self.update_size(w,h)
        self.on_viewport_updated()

    def update_size(self, w, h):
        self.width, self.height = w, h
        self.aspect_ratio = w / h
        self.projection.set_aspect_ratio(self.aspect_ratio)
        print('resize', self.width, self.height)


    def zoom_to_point(self, zoom_x, zoom_y, new_zoom):
        self.zoom_factor = new_zoom

        if self.zoom_factor <= self.min_zoom:
            self.zoom_factor = self.min_zoom
        if self.zoom_factor >= self.max_zoom:
            self.zoom_factor = self.max_zoom

        self.projection.zoom(zoom_x, zoom_y, self.zoom_factor)
        self.on_viewport_updated()

        self.zoom_percent = self.zoom_factor / self.max_zoom
        formatted = "{:.0%}".format(self.zoom_percent)
        if self.formatted_zoom != formatted:
            self.formatted_zoom = formatted
            print("zoom: ", formatted)

    def mouse_scroll_callback(self, window, x_offset, y_offset):
        io = imgui.get_io()
        if io.want_capture_mouse:
            return

        zoom_x, zoom_y = self.window_to_ndc_cords(self.last_mouse_x, self.last_mouse_y)
        # print("zoom xy",zoom_x,zoom_y)
        delta = - y_offset * self.zoom_step
        new_zoom = np.log(self.zoom_factor) + delta  # Logarithmically adjust zoom
        new_zoom = np.exp(new_zoom)  # Convert logarithmic scale back to linear scale
        self.zoom_to_point(zoom_x, zoom_y, new_zoom)

    def mouse_button_callback(self, window, button, action, mods):
        io = imgui.get_io()
        if io.want_capture_mouse:
            return
        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                pass
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.mouse_press_pos = glfw.get_cursor_pos(window)
                self.dragging = True
            elif action == glfw.RELEASE:
                mouse_release_pos = glfw.get_cursor_pos(window)
                if self.mouse_press_pos and self._is_click(self.mouse_press_pos, mouse_release_pos):
                    if self.on_click_func is not None:
                        self.on_click_func()
                self.dragging = False

    def mouse_position_callback(self, window, xpos, ypos):
        io = imgui.get_io()
        if io.want_capture_mouse:
            return
        xpos, ypos = xpos, self.height - ypos
        if not self.dragging:
            self.last_mouse_x = xpos
            self.last_mouse_y = ypos
            return

        # Calculate the translation offset based on mouse movement
        dx = xpos - self.last_mouse_x
        dy = ypos - self.last_mouse_y
        dx = dx / self.width * 2.0
        dy = dy / self.height * 2.0

        self.projection.translate_by(dx, dy)
        self.last_mouse_x = xpos
        self.last_mouse_y = ypos
        self.on_viewport_updated()

    def reset_to_center(self, n_net):

        self.projection.translate_to(-1, -1)
        self.projection.zoom_to(self.min_zoom)
        self.projection.set_aspect_ratio(self.aspect_ratio)

        world_w, world_h = self.projection.world_to_ndc_point(n_net.total_width, n_net.total_height)
        # by default world is positioned (0,0) in the bottom left corner
        dx = self.width / 2
        dy = self.height / 2
        dx = dx / self.width * 2.0
        dx = dx - world_w - (dx - world_w) / 2
        dy = dy / self.height * 2.0
        dy = dy - world_h - (dy - world_h) / 2
        # self.projection.translate_by(dx, dy)
        print(dx, dy)
        self.projection.translate_to(-(1 - dx), -(1 - dy))
        self.on_viewport_updated()

    def cancel_drag(self):
        self.dragging = False

    def _is_click(self, press_pos, release_pos, threshold=5.0):
        dx = release_pos[0] - press_pos[0]
        dy = release_pos[1] - press_pos[1]
        return (dx * dx + dy * dy) <= (threshold * threshold)
