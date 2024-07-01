import os.path

import OpenGL.GL as gl
import glfw
from OpenGL.GL import *

from app.ai.model_parser import ModelParser
from app.config.app_config import LittleConfig
from app.gl.c_color_theme import NColorTheme
from app.gl.n_camera import CameraAnimation
from app.gl.n_effects import NEffects
from app.gl.n_frame_producer import NFrameProducer
from app.gl.n_net import  NNet
from app.gl.n_scene_v2 import NSceneV2
from app.gl.n_viewport import NViewport
from app.gl.n_window import NWindow
from app.config.download_manager import DownloadManager
from app.gui.gui_config import GuiConfig
from app.gui.gui_pants import GuiPants
from app.gui.managers.image_loader import ImageLoader
from app.utils import FancyUtilsClass


class ScreenBuffer:
    def __init__(self, width, height):
        self.buffer_width = width
        self.buffer_height = height
        self.viewport_width = self.buffer_width / 2
        self.viewport_height = self.buffer_height / 2

    def update(self, width, height):
        self.buffer_width = width
        self.buffer_height = height
        self.viewport_width = self.buffer_width / 2
        self.viewport_height = self.buffer_height / 2

    def different(self, width, height):
        return self.buffer_width != width or self.buffer_height != height


class OpenGLApplication:
    def __init__(self):

        # Default buffer size

        self.app_config = LittleConfig()
        self.app_config.load_config()

        self.n_buffer = ScreenBuffer(self.app_config.buffer_width, self.app_config.buffer_height)

        self.n_window = NWindow()
        self.n_window.update_size(
            self.app_config.window_width,
            self.app_config.window_height
        )

        self.n_frame_producer = NFrameProducer(self.n_buffer)
        self.color_theme = NColorTheme()
        self.color_theme.load_by_name(self.app_config.color_name)

        self.utils = FancyUtilsClass()
        self.download_manager = DownloadManager()

        self.n_net = NNet(self.n_window, self.color_theme)

        self.camera_animation = CameraAnimation(self.n_window, self.n_net)
        self.n_viewport = NViewport(self.n_net, self.n_buffer, self.n_frame_producer)
        self.n_effects = NEffects(self.n_net, self.n_window)
        self.model_parser = ModelParser(self.n_effects)

        self.n_scene = NSceneV2(self.n_net,
                                self.n_viewport,
                                self.n_window,
                                self.n_buffer)
        self.n_scene.enable_blending = self.app_config.enable_blend
        self.n_viewport.power_of_two = self.app_config.power_of_two

        self.image_loader = ImageLoader()
        self.gui_config = GuiConfig(
            self.n_net,
            self.n_window,
            self.color_theme,
            self.utils,
            self.app_config,
            self,
            self.download_manager,
            self.camera_animation,
            self.n_effects,
            self.model_parser,
            self.image_loader)

        self.gui = GuiPants(self.gui_config)

        self.mouse_x_world = None
        self.mouse_y_world = None

    def render(self):

        r, g, b, a = self.color_theme.color_low
        gl.glClearColor(r, g, b, a)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

        mouse_x_world, mouse_y_world = self.n_window.window_to_world_cords(
            self.n_window.last_mouse_x,
            self.n_window.last_mouse_y
        )
        if self.mouse_x_world != mouse_x_world or self.mouse_y_world != mouse_y_world:
            self.mouse_x_world = mouse_x_world
            self.mouse_y_world = mouse_y_world
            self.on_mouse_position_changed()
        self.n_window.n_color_map_v2_texture_shader.use()
        self.n_window.n_color_map_v2_texture_shader.update_projection(self.n_window.get_projection_matrix())
        self.n_window.n_color_map_v2_texture_shader.update_mouse_position(self.mouse_x_world,
                                                                          self.mouse_y_world)
        self.n_window.n_color_map_v2_texture_shader.update_color_map(self.color_theme.name,
                                                                     self.color_theme.color_array)

        self.n_window.n_billboards_from_texture_shader.use()
        self.n_window.n_billboards_from_texture_shader.update_projection(self.n_window.get_projection_matrix())
        self.n_window.n_billboards_from_texture_shader.update_cell_billboard()
        self.n_window.n_billboards_from_texture_shader.update_mouse_position(self.mouse_x_world,
                                                                             self.mouse_y_world)
        self.n_window.n_billboards_from_texture_shader.update_color_map(self.color_theme.name,
                                                                        self.color_theme.color_array)

        self.n_window.n_effects_shader.use()
        self.n_window.n_effects_shader.update_projection(self.n_window.get_projection_matrix())

        self.n_scene.draw_scene(
            self.n_window.n_color_map_v2_texture_shader,
            self.n_window.n_billboards_from_texture_shader
        )
        self.n_effects.draw(self.n_window.n_effects_shader)
        self.gui.render_fancy_pants()
        self.camera_animation.update_animation()
        glfw.swap_buffers(self.n_window.window)
        self.utils.print_memory_usage()

    def on_mouse_clicked(self):
        x = int(self.mouse_x_world)
        y = int(self.mouse_y_world)
        value, layer_meta = self.n_net.get_point_data(x, y)
        if value is not None and layer_meta is not None and value != -1:
            self.gui.show_popup(value, layer_meta, (x + 0.5, y + 0.5))
        else:
            self.gui.hide_popup()

    def on_mouse_position_changed(self):
        if self.gui.wants_mouse():
            return
        x = int(self.mouse_x_world)
        y = int(self.mouse_y_world)
        value, layer_meta = self.n_net.get_point_data(x, y)
        if value is not None and layer_meta is not None and value != -1:
            self.gui_config.publish_layer_position_message(self.mouse_x_world, self.mouse_y_world, layer_meta)
        else:
            self.gui_config.publish_position_message(self.mouse_x_world, self.mouse_y_world)

    def on_key_pressed(self, key):
        print("key pressed", key)
        if key == glfw.KEY_UP:
            self.n_window.mouse_scroll_callback(None, None, -0.1)
        if key == glfw.KEY_DOWN:
            self.n_window.mouse_scroll_callback(None, None, 0.1)
        if key == glfw.KEY_C:
            self.color_theme.next()
            self.app_config.color_name = self.color_theme.name

    def on_viewport_updated(self):
        viewport = self.n_window.viewport_to_world_cords()
        self.n_viewport.update_viewport(viewport)
        self.n_effects.on_viewport_changed(viewport)
        if self.n_viewport.visible_data is not None:
            self.n_net.update_visible_layers(self.n_viewport.visible_data)

    def reload_graphics_settings(self):
        self.color_theme.load_by_name(self.app_config.color_name)
        self.n_buffer.update(self.app_config.buffer_width, self.app_config.buffer_height)
        self.n_scene.enable_blending = self.app_config.enable_blend
        self.n_viewport.power_of_two = self.app_config.power_of_two
        self.on_viewport_updated()

    def reload_view(self):
        # update tree size and depth using grid size
        self.n_viewport.set_grid_size(self.n_net.total_width, self.n_net.total_height)
        # calculate min zoom using grid size
        self.n_window.calculate_min_zoom(self.n_net)
        # start render loop
        self.n_window.reset_to_center(self.n_net)

    def clear(self):
        self.app_config.model_directory = None
        self.app_config.save_config()
        # self.model_parser.clear()
        self.n_net.clear()
        self.load_model()

    def load_model(self,
                   model=None,
                   model_directory=None):
        print("Load model", "Model=", model, "Model directory=", model_directory)
        if model is None and model_directory is None and self.app_config.model_directory is not None and os.path.exists(
                self.app_config.model_directory):
            model_directory = self.app_config.model_directory

        if model is not None:
            self.model_parser.set_model(model)
            self.model_parser.parse_loaded_model()
            self.n_net.init_from_model_parser(self.model_parser)
        elif model_directory is not None and os.path.exists(model_directory):
            self.model_parser.load_model_from_path(model_directory)
            self.model_parser.load_tokenizer_from_path(model_directory)
            self.model_parser.load_image_processor_from_path(model_directory)
            self.model_parser.load_feature_extractor_from_path(model_directory)
            self.app_config.model_directory = model_directory
            self.model_parser.parse_loaded_model()
            self.n_net.init_from_model_parser(self.model_parser)
            #
            # self.n_net.weights_net.init_from_tensors(self.model_parser.named_parameters(),
            #                                          save_to_memfile=save_mem_file)
        if self.model_parser.model is None:
            print("No model to load!", "Showing welcome message")
            welcome_message = self.utils.create_logo_message()
            self.n_net.init_from_np_arrays([welcome_message], ["welcome_layer"])
        # else:
        #     self.model_parser.parse_loaded_model()
        #     self.n_net.neurons_net.init_from_model_parser(self.model_parser)

        self.app_config.save_config()

        self.utils.print_memory_usage()
        self.reload_view()

    def start(self,
              model=None,
              model_directory=None):
        # self.reload_config()
        self.n_window.create_window()
        # self.n_window.set_callbacks()

        self.gui.attach_fancy_gui()
        self.gui.set_callbacks()
        self.n_window.set_render_func(self.render)
        self.n_window.set_key_repeat_func(self.on_key_pressed)
        self.n_window.set_key_pressed_func(self.on_key_pressed)
        self.n_window.set_on_click_func(self.on_mouse_clicked)
        self.n_window.set_viewport_updated_func(self.on_viewport_updated)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_MULTISAMPLE)
        version = glGetString(GL_VERSION)

        print(f"OpenGL version: {version.decode('utf-8')}")

        self.n_window.n_color_map_v2_texture_shader.compile_color_map_v2_texture_program()
        self.n_window.n_billboards_from_texture_shader.compile_billboards_v2_program()
        self.n_window.n_effects_shader.compile_effects_program()

        self.utils.print_memory_usage()

        self.load_model(model, model_directory)
        # self.n_effects.init()
        print("Main loop")
        self.n_window.start_main_loop()

        glfw.terminate()
        gl.glDeleteProgram(self.n_window.n_color_map_v2_texture_shader.shader_program)
        gl.glDeleteProgram(self.n_window.n_billboards_from_texture_shader.shader_program)
        gl.glDeleteProgram(self.n_window.n_effects_shader.shader_program)

        self.app_config.window_width = self.n_window.width
        self.app_config.window_height = self.n_window.height
        self.gui.remove_gui()
