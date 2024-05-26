import os
import time

import OpenGL.GL as gl
import glfw
import psutil
from OpenGL.GL import *

from app.gl.c_color_theme import NColorTheme
from app.gl.n_net import NNet
from app.gl.n_scene_v2 import NSceneV2
from app.gl.n_tree import NTree
from app.gl.n_viewport import NViewport
from app.gl.n_window import NWindow


class OpenGLApplication:
    def __init__(self):

        self.buffer_width = 1280
        self.buffer_height = 1280

        self.n_window = NWindow()
        self.color_theme = NColorTheme()

        self.n_net = NNet(self.n_window, self.color_theme)
        self.n_tree = NTree(0)
        self.n_viewport = NViewport(self.n_tree, self.n_net, self.buffer_width, self.buffer_height)
        self.n_scene = NSceneV2(self.n_net, self.n_viewport, self.n_window, self.buffer_width, self.buffer_height)

        self.process = psutil.Process(os.getpid())
        self.memory_usage = 0
        self.virtual_memory_usage = 0
        self.frame_count = 0
        self.start_time = 0
        self.DEBUG = False

        self.node_radius = 0.2
        self.node_gap = 1.0

    def print_memory_usage(self):
        mem_info = self.process.memory_info()
        usage = f"{mem_info.rss / (1024 * 1024 * 1024):.2f}"
        if self.memory_usage != usage:
            self.memory_usage = usage
            print(f"Memory usage: {self.memory_usage} GB (Resident Set Size)")

    def render(self):

        r, g, b, a = self.color_theme.color_low
        gl.glClearColor(r, g, b, a)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        # Update frame count
        self.frame_count += 1
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1.0:  # Update FPS every second
            fps = self.frame_count / elapsed_time
            if self.DEBUG:
                fps_text = f"FPS: {fps:.2f}"
                self.frame_count = 0
                self.start_time = time.time()
                print(fps_text)

        mouse_x_ndc, mouse_y_ndc = self.n_window.window_to_world_cords(
            self.n_window.last_mouse_x,
            self.n_window.last_mouse_y
        )
        # print(
        #     mouse_x_ndc, mouse_y_ndc
        # )
        self.n_window.n_color_map_v2_texture_shader.use()
        self.n_window.n_color_map_v2_texture_shader.update_projection(self.n_window.get_projection_matrix())
        self.n_window.n_color_map_v2_texture_shader.update_quad_matrix(self.n_window.get_quad_projection_matrix())
        self.n_window.n_color_map_v2_texture_shader.update_mouse_position(mouse_x_ndc,
                                                                          mouse_y_ndc)
        self.n_window.n_color_map_v2_texture_shader.update_color_map(self.color_theme.name,
                                                                     self.color_theme.color_array)

        self.n_window.n_instances_from_texture_shader.use()
        self.n_window.n_instances_from_texture_shader.update_projection(self.n_window.get_projection_matrix())
        self.n_window.n_instances_from_texture_shader.update_mouse_position(mouse_x_ndc,
                                                                            mouse_y_ndc)
        self.n_window.n_instances_from_texture_shader.update_cell_billboard()
        self.n_window.n_instances_from_texture_shader.update_color_map(self.color_theme.name,
                                                                       self.color_theme.color_array)

        self.n_window.n_billboards_from_texture_shader.use()
        self.n_window.n_billboards_from_texture_shader.update_projection(self.n_window.get_projection_matrix())
        self.n_window.n_billboards_from_texture_shader.update_cell_billboard()
        self.n_window.n_billboards_from_texture_shader.update_mouse_position(mouse_x_ndc,
                                                                             mouse_y_ndc)
        self.n_window.n_billboards_from_texture_shader.update_color_map(self.color_theme.name,
                                                                        self.color_theme.color_array)

        self.n_scene.draw_scene(
            self.n_window.n_color_map_v2_texture_shader,
            self.n_window.n_instances_from_texture_shader,
            self.n_window.n_billboards_from_texture_shader
        )
        glfw.swap_buffers(self.n_window.window)
        self.print_memory_usage()

    def set_node_radius(self, radius):
        self.node_radius = radius
        self.n_scene.set_node_radius(self.node_radius)
        print("node radius", self.node_radius)

    def on_key_pressed(self, key):
        #print("key pressed", key)
        # if key == glfw.KEY_Q:
        #     pass
        #     self.node_gap = self.node_gap + 0.01
        # if key == glfw.KEY_W:
        #     pass
        #     self.node_gap = max(self.node_gap - 0.01, 0.1)
        if key == glfw.KEY_UP:
            for i in range(20):
                #time.sleep(0.001)
                self.n_window.mouse_scroll_callback(None,None,-0.1)
        if key == glfw.KEY_DOWN:
            self.n_window.mouse_scroll_callback(None,None,1)
        if key == glfw.KEY_C:
            self.color_theme.next()
        if key == glfw.KEY_E:
            self.set_node_radius(self.node_radius + 0.1)
        if key == glfw.KEY_R:
            self.set_node_radius(max(self.node_radius - 0.1, 0.1))
        if key == glfw.KEY_Z:
            self.n_scene.switch_unit()


    def on_viewport_updated(self):
        viewport = self.n_window.viewport_to_world_cords()

        self.n_viewport.update_viewport(viewport)
        if self.n_viewport.visible_data is not None:
            self.n_net.update_visible_layers(self.n_viewport.visible_data)

    def start(self, model):
        self.n_window.create_window()
        self.n_window.set_render_func(self.render)
        self.n_window.set_key_repeat_func(self.on_key_pressed)
        self.n_window.set_key_pressed_func(self.on_key_pressed)
        self.n_window.set_viewport_updated_func(self.on_viewport_updated)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_MULTISAMPLE)
        version = glGetString(GL_VERSION)

        print(f"OpenGL version: {version.decode('utf-8')}")

        self.n_window.n_color_map_v2_texture_shader.compile_color_map_v2_texture_program()
        self.n_window.n_instances_from_texture_shader.compile_instances_v2_program()
        self.n_window.n_billboards_from_texture_shader.compile_billboards_v2_program()

        self.print_memory_usage()
        self.n_net.init_from_tensors([tensor for name, tensor in list(model.named_parameters())])
        self.print_memory_usage()
        # update tree size and depth using grid size
        self.n_viewport.set_grid_size(self.n_net.total_width, self.n_net.total_height)
        # calculate min zoom using grid size
        self.n_window.calculate_min_zoom(self.n_net)
        # start render loop
        self.n_window.reset_to_center(self.n_net)
        print("Main loop")
        self.n_window.start_main_loop()
        glfw.terminate()

        gl.glDeleteProgram(self.n_window.n_color_map_v2_texture_shader.shader_program)
        gl.glDeleteProgram(self.n_window.n_instances_from_texture_shader.shader_program)
        gl.glDeleteProgram(self.n_window.n_billboards_from_texture_shader.shader_program)
