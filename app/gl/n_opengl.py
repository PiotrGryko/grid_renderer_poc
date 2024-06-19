import os.path

import OpenGL.GL as gl
import glfw
from OpenGL.GL import *
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.ai.model_parser import ModelParser
from app.config.app_config import LittleConfig
from app.gl.c_color_theme import NColorTheme
from app.gl.n_camera import CameraAnimation
from app.gl.n_effects import NEffects
from app.gl.n_net import NNet, NetWrapper
from app.gl.n_scene_v2 import NSceneV2
from app.gl.n_viewport import NViewport
from app.gl.n_window import NWindow
from app.config.download_manager import DownloadManager
from app.gui.gui_config import GuiConfig
from app.gui.gui_pants import GuiPants
from app.utils import FancyUtilsClass


class OpenGLApplication:
    def __init__(self):

        # Default buffer size
        self.buffer_width = 2560
        self.buffer_height = 2560

        self.viewport_width = self.buffer_width / 2
        self.viewport_height = self.buffer_height / 2

        self.config = LittleConfig()
        self.config.load_config()

        self.n_window = NWindow()
        self.color_theme = NColorTheme()
        self.utils = FancyUtilsClass()
        self.download_manager = DownloadManager()
        self.n_net = NetWrapper(self.n_window, self.color_theme)

        self.camera_animation = CameraAnimation(self.n_window, self.n_net)

        self.n_viewport = NViewport(self.n_net, self.viewport_width, self.viewport_height)

        self.n_scene = NSceneV2(self.n_net,
                                self.n_viewport,
                                self.n_window,
                                self.buffer_width,
                                self.buffer_height)
        self.n_effects = NEffects(self.n_net, self.n_window)

        self.model_parser = ModelParser(self.n_effects)

        self.gui_config = GuiConfig(
            self.n_net,
            self.n_window,
            self.color_theme,
            self.utils,
            self.config,
            self,
            self.download_manager,
            self.camera_animation,
            self.n_effects,
            self.model_parser)

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
            self.config.color_name = self.color_theme.name

    def on_viewport_updated(self):
        viewport = self.n_window.viewport_to_world_cords()
        self.n_viewport.update_viewport(viewport)
        self.n_effects.on_viewport_changed(viewport)
        if self.n_viewport.visible_data is not None:
            self.n_net.update_visible_layers(self.n_viewport.visible_data)

    def reload_config(self):
        self.config.save_config()
        self.color_theme.load_by_name(self.config.color_name)

        if self.config.buffer_width != self.buffer_width or self.config.buffer_height != self.buffer_height:
            self.buffer_width = self.config.buffer_width
            self.buffer_height = self.config.buffer_height
            self.viewport_width = self.buffer_width / 2
            self.viewport_height = self.buffer_height / 2

            self.n_scene.destroy()
            self.n_scene = None
            self.n_scene = NSceneV2(self.n_net,
                                    self.n_viewport,
                                    self.n_window,
                                    self.buffer_width,
                                    self.buffer_height)
            self.n_viewport.viewport_w = self.viewport_width
            self.n_viewport.viewport_h = self.viewport_height

        self.n_scene.enable_blending = self.config.enable_blend
        self.n_viewport.power_of_two = self.config.power_of_two

    def load_model(self,
                   model=None,
                   model_directory=None,
                   save_mem_file=False,
                   load_mem_file=False):

        if load_mem_file:
            self.n_net.weights_net.init_from_last_memory_files()
        elif model is not None:
            self.n_net.weights_net.init_from_tensors(list(model.named_parameters()), save_to_memfile=save_mem_file)
        elif model_directory is not None and os.path.exists(model_directory):

            model = AutoModelForCausalLM.from_pretrained(model_directory, local_files_only=True)
            self.n_net.weights_net.init_from_tensors(list(model.named_parameters()), save_to_memfile=save_mem_file)
            self.config.model_directory = model_directory
            self.config.save_config()
        elif self.config.model_directory is not None and os.path.exists(self.config.model_directory):
            model = AutoModelForCausalLM.from_pretrained(self.config.model_directory, local_files_only=True)
            self.n_net.weights_net.init_from_tensors(list(model.named_parameters()), save_to_memfile=save_mem_file)
        if model is None:
            print("No model to load!", "Showing welcome message")
            # welcome_message = self.utils.create_welcome_message()
            welcome_message = self.utils.create_logo_message()
            self.n_net.weights_net.init_from_np_arrays([welcome_message], ["welcome_layer"])

        if model is not None:
            index = 0
            tokenizer = AutoTokenizer.from_pretrained(model.name_or_path, local_files_only=True)
            self.model_parser.load_hg_model(model, tokenizer)
            # parser.register_hooks()
            # parser.perform_forward_pass("Hi?")
            self.n_net.neurons_net.init_from_model_parser(self.model_parser)
            # ModelParser().extract_layers_info(model.named_parameters())
            # for name, t in model.named_parameters():
            #     print(index, "name", name, "shape", t.shape)
            #     index += 1
            self.config.model_name = model.name_or_path
        else:
            self.config.model_name = None
        self.config.save_config()

        self.n_scene.destroy()
        self.n_scene = None
        self.n_scene = NSceneV2(self.n_net,
                                self.n_viewport,
                                self.n_window,
                                self.buffer_width,
                                self.buffer_height)
        self.utils.print_memory_usage()
        self.reload_view()

    def reload_view(self):
        # update tree size and depth using grid size
        self.n_viewport.set_grid_size(self.n_net.total_width, self.n_net.total_height)
        # calculate min zoom using grid size
        self.n_window.calculate_min_zoom(self.n_net)
        # start render loop
        self.n_window.reset_to_center(self.n_net)

    def start(self,
              model=None,
              model_directory=None,
              save_mem_file=False,
              load_mem_file=False):
        self.reload_config()
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

        self.load_model(model, model_directory, save_mem_file, load_mem_file)
        # self.n_effects.init()
        print("Main loop")
        self.n_window.start_main_loop()
        glfw.terminate()

        gl.glDeleteProgram(self.n_window.n_color_map_v2_texture_shader.shader_program)
        gl.glDeleteProgram(self.n_window.n_billboards_from_texture_shader.shader_program)
        gl.glDeleteProgram(self.n_window.n_effects_shader.shader_program)

        self.gui.remove_gui()
