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
from app.gui.gui_pants import GuiPants
from app.utils import FancyUtilsClass


class OpenGLApplication:
    def __init__(self):

        self.buffer_width = 1280
        self.buffer_height = 1280

        self.n_window = NWindow()
        self.color_theme = NColorTheme()
        self.utils = FancyUtilsClass()

        self.n_net = NNet(self.n_window, self.color_theme)
        self.n_tree = NTree(0)
        self.n_viewport = NViewport(self.n_tree, self.n_net, self.buffer_width, self.buffer_height)
        self.n_scene = NSceneV2(self.n_net, self.n_viewport, self.n_window, self.buffer_width, self.buffer_height)
        self.gui = GuiPants(self.n_window, self.color_theme, self.utils)

        self.node_radius = 0.2
        self.node_gap = 1.0

    def render(self):

        r, g, b, a = self.color_theme.color_low
        gl.glClearColor(r, g, b, a)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        mouse_x_ndc, mouse_y_ndc = self.n_window.window_to_world_cords(
            self.n_window.last_mouse_x,
            self.n_window.last_mouse_y
        )
        # print(
        #     mouse_x_ndc, mouse_y_ndc
        # )
        self.n_window.n_color_map_v2_texture_shader.use()
        self.n_window.n_color_map_v2_texture_shader.update_projection(self.n_window.get_projection_matrix())
        self.n_window.n_color_map_v2_texture_shader.update_mouse_position(mouse_x_ndc,
                                                                          mouse_y_ndc)
        self.n_window.n_color_map_v2_texture_shader.update_color_map(self.color_theme.name,
                                                                     self.color_theme.color_array)

        self.n_window.n_color_billboards_texture_shader.use()
        self.n_window.n_color_billboards_texture_shader.update_projection(self.n_window.get_projection_matrix())
        self.n_window.n_color_billboards_texture_shader.update_mouse_position(mouse_x_ndc,
                                                                              mouse_y_ndc)
        self.n_window.n_color_billboards_texture_shader.update_color_map(self.color_theme.name,
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
            self.n_window.n_billboards_from_texture_shader,
            self.n_window.n_color_billboards_texture_shader
        )
        self.gui.render_fancy_pants()

        glfw.swap_buffers(self.n_window.window)
        self.utils.print_memory_usage()

    def set_node_radius(self, radius):
        self.node_radius = radius
        self.n_scene.set_node_radius(self.node_radius)
        print("node radius", self.node_radius)

    def on_key_pressed(self, key):
        print("key pressed", key)
        # if key == glfw.KEY_Q:
        #     pass
        #     self.node_gap = self.node_gap + 0.01
        # if key == glfw.KEY_W:
        #     pass
        #     self.node_gap = max(self.node_gap - 0.01, 0.1)
        if key == glfw.KEY_UP:
            for i in range(20):
                # time.sleep(0.001)
                self.n_window.mouse_scroll_callback(None, None, -0.1)
        if key == glfw.KEY_DOWN:
            self.n_window.mouse_scroll_callback(None, None, 1)
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

    def start(self, model, save_mem_file=False, load_mem_file=False):
        self.n_window.create_window()
        # self.n_window.set_callbacks()

        self.gui.attach_fancy_gui()
        self.gui.set_callbacks()

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
        self.n_window.n_color_billboards_texture_shader.compile_billboards_v3_program()

        self.utils.print_memory_usage()
        if load_mem_file:
            self.n_net.init_from_last_memory_files()
        else:
            self.n_net.init_from_tensors([tensor for name, tensor in list(model.named_parameters())[:1]],
                                         save_to_memfile=save_mem_file)
        self.utils.print_memory_usage()
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
        gl.glDeleteProgram(self.n_window.n_color_billboards_texture_shader.shader_program)
        self.gui.remove_gui()
