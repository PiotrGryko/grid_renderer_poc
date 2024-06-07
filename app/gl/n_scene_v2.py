import math
import time
from enum import Enum

import OpenGL.GL as gl
import numpy as np

from app.gl.n_blend_calculator import NBlendCalculator


class Quad:
    def __init__(self):
        self.vao = None
        self.ebo = None
        self.vbo = None
        self.indices = None
        self.tex_vbo = None
        self.tex_coords = None

        self.prev_tex_vbo = None
        self.prev_tex_coords = None

        self.vertices = None
        self.created = False

    def create_quad(self):
        self.vertices = np.array([
            0, 0,  # Bottom-left
            1, 0,  # Bottom-right
            1, 1,  # Top-right
            0, 1  # Top-left
        ], dtype=np.float32)

        self.tex_coords = np.array([
            0.0, 0.0,  # Bottom-left
            1.0, 0.0,  # Bottom-right
            1.0, 1.0,  # Top-right
            0.0, 1.0  # Top-left
        ], dtype=np.float32)

        self.prev_tex_coords = np.array([
            0.0, 0.0,  # Bottom-left
            1.0, 0.0,  # Bottom-right
            1.0, 1.0,  # Top-right
            0.0, 1.0  # Top-left
        ], dtype=np.float32)

        # Define the indices to form two triangles
        self.indices = np.array([
            0, 1, 2,
            2, 3, 0
        ], dtype=np.uint32)

        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_DYNAMIC_DRAW)

        #
        self.tex_vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.tex_coords.nbytes, self.tex_coords, gl.GL_STATIC_DRAW)

        self.prev_tex_vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.prev_tex_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.prev_tex_coords.nbytes, self.prev_tex_coords, gl.GL_STATIC_DRAW)

        # Create and bind the vertex array object (VAO)
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        # Bind the vertex buffer object (VBO) for vertices
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # # Bind the texture
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_vbo)
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # # Bind the texture
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.prev_tex_vbo)
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # Create and bind the element buffer object (EBO)
        self.ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, gl.GL_STATIC_DRAW)
        self.created = True

    def destroy(self):
        if self.created:
            gl.glDeleteBuffers(1, [self.vbo])
            gl.glDeleteBuffers(1, [self.tex_vbo])
            gl.glDeleteBuffers(1, [self.prev_tex_vbo])
            gl.glDeleteBuffers(1, [self.ebo])
            gl.glDeleteVertexArrays(1, [self.vao])
            self.created = False

    # def update_quad_position(self, x1, y1, x2, y2, offset_x, offset_y, factor):
    #     if not self.created:
    #         return
    #     # The quad x1,y1,x2,y2 is always 0,0,width,height
    #     # The position of the quad in the world is offset + size * factor
    #
    #     x1 = offset_x + x1 * factor
    #     x2 = offset_x + x2 * factor
    #     y1 = offset_y + y1 * factor
    #     y2 = offset_y + y2 * factor
    #     self.vertices = np.array([
    #         x1, y1,  # Bottom-left
    #         x2, y1,  # Bottom-right
    #         x2, y2,  # Top-right
    #         x1, y2,  # Top-left
    #     ], dtype=np.float32)
    #     # Bind the VBO
    #     gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
    #
    #     # Update the buffer data
    #     gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)

    def update_quad_position_old(self, x1, y1, x2, y2):
        if not self.created:
            return
        self.vertices = np.array([
            x1, y1,  # Bottom-left
            x2, y1,  # Bottom-right
            x2, y2,  # Top-right
            x1, y2,  # Top-left
        ], dtype=np.float32)
        # Bind the VBO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        # Update the buffer data
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)

    def update_second_texture_coordinates(self, tex_width, tex_height, current_quad, prev_quad, n_window):
        """
        Map tex coordinates from one quad to another quad
        Two quads can be different sized and different positions
        Both quads have [0-1] tex coordinates in their own space
        This method maps prev_quad on current_quad and calculates
        prev_quad tex coordinates (prev_tex_coords) in current quad space (tex coordinates [0-1])
        :param tex_width:
        :param tex_height:
        :param current_quad:
        :param prev_quad:
        :param n_window:
        :return:
        """
        if not self.created:
            return

        factor_delta = prev_quad.factor / current_quad.factor
        w = tex_width
        h = tex_height

        diff_x1 = (current_quad.fx1 - prev_quad.fx1 * factor_delta) / w / factor_delta
        diff_y1 = (current_quad.fy1 - prev_quad.fy1 * factor_delta) / h / factor_delta

        x1 = 0
        x2 = 1 / factor_delta
        y1 = 0
        y2 = 1 / factor_delta

        dify = diff_y1
        difx = diff_x1

        y1 = y1 + dify
        y2 = y2 + dify
        x1 = x1 + difx
        x2 = x2 + difx
        # print("tex width", w)
        # print("tex height", h)
        #
        # print("prev quad", prev_quad.fx1, prev_quad.fx2, prev_quad.fy1, prev_quad.fy2)
        # print("current quad", current_quad.fx1, current_quad.fx2, current_quad.fy1, current_quad.fy2)
        # print("prev factor ", prev_quad.factor, "current factor", current_quad.factor, "delta", factor_delta)
        # print("height current", current_h, "prev h", prev_h)
        # print("diff", diff_x1, diff_y1)
        # print("x1 x2", x1, x2)
        # print("y1 y2", y1, y2)

        self.prev_tex_coords = np.array([
            x1, y1,  # Bottom-left
            x2, y1,  # Bottom-right
            x2, y2,  # Top-right
            x1, y2  # Top-left
        ], dtype=np.float32)

        # Bind the VBO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.prev_tex_vbo)
        # Update the buffer data
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.prev_tex_coords.nbytes, self.prev_tex_coords)

    def draw(self):
        if not self.created:
            return
        gl.glBindVertexArray(self.vao)
        # gl.glDrawElementsInstanced(gl.GL_TRIANGLES, len(self.indices), gl.GL_UNSIGNED_INT, None, 1)
        gl.glDrawElements(gl.GL_TRIANGLES, len(self.indices), gl.GL_UNSIGNED_INT, None)


class EntityV2:
    def __init__(self, gl_texture_unit=gl.GL_TEXTURE2):
        self.ebo = None
        self.tex_coords = None
        self.indices = None
        self.tex_vbo = None
        self.node_circle_vbo = None
        self.node_quad_vbo = None
        self.vao = None
        self.pbo = None

        self.empty_img = None
        self.created = False

        self.width = 0
        self.height = 0
        self.num_instances = 0
        self.radius = 0.2
        self.num_segments = 20

        self.texture = None
        self.gl_texture_unit = gl_texture_unit

        self.visible_grid_part = None
        self.quad = Quad()

        # Track the detail level of the second texture (used in blending mode)
        self.second_texture_factor = None
        self.current_texture_factor = None

    def build_node_vertices(self):
        vertices = []
        for i in range(self.num_segments):
            theta = 2.0 * math.pi * float(i) / float(self.num_segments)
            x = self.radius * math.cos(theta)
            y = self.radius * math.sin(theta)
            vertices.extend([x, y])
        vertices = np.array(vertices, dtype=np.float32)
        return vertices

    def build_quad_vertices(self):
        vertices = np.array([
            0, 0,  # Bottom-left
            1, 0,  # Bottom-right
            1, 1,  # Top-right
            0, 1  # Top-left
        ], dtype=np.float32)
        vertices = np.array(vertices, dtype=np.float32)
        return vertices

    def build_text_coords(self):
        tex_coords = np.array([
            0.0, 0.0,  # Bottom-left
            1.0, 0.0,  # Bottom-right
            1.0, 1.0,  # Top-right
            0.0, 1.0  # Top-left
        ], dtype=np.float32)
        return tex_coords

    def create_data_container_texture(self, width, height):
        self.width = width
        self.height = height
        self.empty_img = np.full((self.width, self.height), fill_value=-1, dtype=np.float32)
        self.num_instances = self.width * self.height

        self.texture = gl.glGenTextures(1)
        gl.glActiveTexture(self.gl_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R32F, width, height, 0, gl.GL_RED, gl.GL_FLOAT, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        error = gl.glGetError()
        if error != gl.GL_NO_ERROR:
            print(f"Error loading texture: {error}")

        vertices = self.build_node_vertices()
        quads = self.build_quad_vertices()
        self.tex_coords = self.build_text_coords()
        # Define the indices to form two triangles
        self.indices = np.array([
            0, 1, 2,  # Triangle 1
            0, 2, 3  # Triangle 2
        ], dtype=np.uint32)

        # Instance data for multiple triangles
        self.node_circle_vbo = gl.glGenBuffers(1)
        # Bind the vertex buffer and upload vertex data
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.node_circle_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_DYNAMIC_DRAW)

        # Instance data for multiple triangles
        self.node_quad_vbo = gl.glGenBuffers(1)
        # Bind the vertex buffer and upload vertex data
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.node_quad_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, quads.nbytes, quads, gl.GL_DYNAMIC_DRAW)

        self.tex_vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.tex_coords.nbytes, self.tex_coords, gl.GL_STATIC_DRAW)

        # Create vertex array object (VAO)
        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        # Bind the vertex buffer to the VAO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.node_circle_vbo)
        gl.glEnableVertexAttribArray(0)
        gl.glVertexAttribPointer(0, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # Bind the vertex buffer to the VAO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.node_quad_vbo)
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # # Bind the texture
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_vbo)
        gl.glEnableVertexAttribArray(2)
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        # Create and bind the element buffer object (EBO)
        self.ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, gl.GL_STATIC_DRAW)
        self.created = True

        error = gl.glGetError()
        if error != gl.GL_NO_ERROR:
            print(f"Error loading texture: {error}")

        self.created = True

    def destroy(self):
        if self.created:
            self.quad.destroy()
            gl.glDeleteBuffers(1, [self.node_circle_vbo])
            gl.glDeleteBuffers(1, [self.node_quad_vbo])
            gl.glDeleteBuffers(1, [self.tex_vbo])
            gl.glDeleteBuffers(1, [self.ebo])
            gl.glDeleteVertexArrays(1, [self.vao])
            gl.glDeleteTextures(1, [self.texture])
            self.created = False

    def update_data(self, chunks, dimensions):
        if not self.created:
            return
        start_time = time.time()
        gl.glActiveTexture(self.gl_texture_unit)
        # Clear previous state
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, gl.GL_RED, gl.GL_FLOAT, self.empty_img)
        for c, d in zip(chunks, dimensions):
            cx1, cy1, cx2, cy2 = d
            width = cx2 - cx1
            height = cy2 - cy1
            if cx1 + width > self.width or cy1 + height > self.height:
                print("Data outside the texture bounds!! Did you update the buffer size?")
                continue
            # print("dx dy", cx1, cy1, cx2 - cx1, cy2 - cy1)

            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, cx1, cy1, cx2 - cx1, cy2 - cy1, gl.GL_RED, gl.GL_FLOAT, c)

        # print("View data updated", (time.time() - start_time) * 1000, "ms")

    def update_entity(self, visible_grid_part):
        self.visible_grid_part = visible_grid_part
        self.current_texture_factor = self.visible_grid_part.factor
        chunks, dimensions = visible_grid_part.grab_visible_data()
        self.update_data(
            chunks,
            dimensions)

    def update_quad_position(self, buffer_w, buffer_h):
        if self.visible_grid_part is None:
            print("Missing grid bounds!")
            return
        x1, y1, x2, y2 = self.visible_grid_part.get_quad_position(buffer_w, buffer_h)
        self.quad.update_quad_position_old(x1, y1, x2, y2)

    def draw_points(self, count):
        if not self.created:
            return

        gl.glActiveTexture(self.gl_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_POINTS, 0, 1, count)

    def draw_nodes(self, count, detail):
        if not self.created:
            return
        count = min([count, self.num_instances])
        gl.glActiveTexture(self.gl_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        segments_count = min([self.num_segments, math.ceil(detail * self.num_segments)])
        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLE_FAN, 0,
                                 segments_count, count)

    def draw_billboards(self, count, detail):
        if not self.created:
            return
        count = min([count, self.num_instances])
        gl.glActiveTexture(self.gl_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        segments_count = min([self.num_segments, math.ceil(detail * self.num_segments)])
        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLE_STRIP, 0,
                                 6, count)

    def create_quad(self):
        if not self.quad.created:
            self.quad.create_quad()

    def draw_texture(self):
        self.create_quad()
        self.quad.draw()


class NSceneV2:
    def __init__(self, n_net, n_viewport, n_window, buffer_w, buffer_h):
        self.n_net = n_net
        self.n_viewport = n_viewport
        self.n_window = n_window

        self.current_width = buffer_w
        self.current_height = buffer_h

        self.entity1 = EntityV2(gl.GL_TEXTURE2)
        self.entity2 = EntityV2(gl.GL_TEXTURE3)

        self.should_update_entity2 = False

        self.current_entity = None

        self.enable_blending = True
        self.dragged = False

        self.blend_calculator = NBlendCalculator()

    def destroy(self):
        self.entity1.destroy()
        self.entity2.destroy()

    # @profile
    def update_scene_entities(self):

        if self.n_viewport.visible_data is None:
            return

        current_quad = self.n_viewport.visible_data
        should_update = True

        if self.entity1.visible_grid_part == current_quad:
            should_update = False
        if self.entity2.visible_grid_part == current_quad:
            should_update = False

        if should_update:

            if self.current_entity is not None and self.current_entity.visible_grid_part.zoom == current_quad.zoom:
                self.dragged = True
            else:
                self.dragged = False

            # Update entity2 if its current and the detail factor didn't change
            if self.current_entity == self.entity2 and self.entity2.visible_grid_part.factor == current_quad.factor:
                self.should_update_entity2 = True
            # Update entity2 if the current is entity1 and the detail factor changed.
            if self.current_entity == self.entity1 and self.entity1.visible_grid_part.factor != current_quad.factor:
                self.should_update_entity2 = True
            # Skip entity 2 if blending is disabled
            if self.should_update_entity2 and self.enable_blending:
                self.should_update_entity2 = False
                self.entity2.update_entity(current_quad)
                self.entity2.update_quad_position(self.current_width, self.current_height)

                if self.entity1.visible_grid_part is not None:
                    self.entity2.quad.update_second_texture_coordinates(
                        self.current_width,
                        self.current_height,
                        self.entity2.visible_grid_part,
                        self.entity1.visible_grid_part,
                        self.n_window
                    )
                    self.entity2.second_texture_factor = self.entity1.visible_grid_part.factor
                self.current_entity = self.entity2
                print("update entity2 ",
                      "current factor", self.entity2.current_texture_factor,
                      "prev factor", self.entity2.second_texture_factor)
            else:
                self.entity1.update_entity(current_quad)
                self.entity1.update_quad_position(self.current_width, self.current_height)

                if self.entity2.visible_grid_part is not None:
                    self.entity1.quad.update_second_texture_coordinates(
                        self.current_width,
                        self.current_height,
                        self.entity1.visible_grid_part,
                        self.entity2.visible_grid_part,
                        self.n_window
                    )
                    self.entity1.second_texture_factor = self.entity2.visible_grid_part.factor
                self.current_entity = self.entity1

                if self.entity2.visible_grid_part is not None:
                    print("update entity1 ",
                          "current factor", self.entity1.current_texture_factor,
                          "prev factor", self.entity1.second_texture_factor)
                else:
                    print("update entity 1")

    def draw_textures(self, n_color_map_v2_texture_shader, alpha_factor):
        # factor = self.n_viewport.current_factor
        factor_delta = self.n_viewport.current_factor_delta
        # mix_factor = factor_delta if self.zooming_in else 1 - factor_delta

        mix_factor = self.blend_calculator.get_second_texture_mix_factor(
            current_level=self.current_entity.current_texture_factor,
            prev_level=self.current_entity.second_texture_factor,
            delta=factor_delta,
            reached_min_zoom=self.n_window.zoom_factor == self.n_window.min_zoom,
            dragged=self.dragged)

        n_color_map_v2_texture_shader.use()
        if not self.enable_blending:
            mix_factor = 0
        if self.current_entity == self.entity2:
            n_color_map_v2_texture_shader.select_texture(1)
            n_color_map_v2_texture_shader.mix_textures(mix_factor)
            n_color_map_v2_texture_shader.update_fading_factor(alpha_factor)
            gl.glActiveTexture(self.entity2.gl_texture_unit)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.entity2.texture)
            self.entity2.draw_texture()
        else:
            n_color_map_v2_texture_shader.select_texture(0)
            n_color_map_v2_texture_shader.mix_textures(mix_factor)
            n_color_map_v2_texture_shader.update_fading_factor(alpha_factor)
            gl.glActiveTexture(self.entity1.gl_texture_unit)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.entity1.texture)
            self.entity1.draw_texture()

    def draw_points(self, n_instances_from_texture_shader, size):
        n_instances_from_texture_shader.use()
        n_instances_from_texture_shader.update_texture_width(self.current_width)
        n_instances_from_texture_shader.update_texture_height(self.current_height)
        n_instances_from_texture_shader.update_target_width(self.current_entity.visible_grid_part.w)
        n_instances_from_texture_shader.update_target_height(self.current_entity.visible_grid_part.h)
        n_instances_from_texture_shader.update_details_factor(self.current_entity.visible_grid_part.factor)
        n_instances_from_texture_shader.update_position_offset(self.current_entity.visible_grid_part.offset_x,
                                                               self.current_entity.visible_grid_part.offset_y)

        if self.current_entity == self.entity2:
            n_instances_from_texture_shader.select_texture(1)
            self.entity2.draw_points(size)
        else:
            n_instances_from_texture_shader.select_texture(0)
            self.entity1.draw_points(size)

    def draw_billboards(self, n_billboards_from_texture_shader, size):
        n_billboards_from_texture_shader.use()
        n_billboards_from_texture_shader.update_texture_width(self.current_width)
        n_billboards_from_texture_shader.update_texture_height(self.current_height)
        n_billboards_from_texture_shader.update_target_width(self.current_entity.visible_grid_part.w)
        n_billboards_from_texture_shader.update_target_height(self.current_entity.visible_grid_part.h)
        n_billboards_from_texture_shader.update_details_factor(self.current_entity.visible_grid_part.factor)
        n_billboards_from_texture_shader.update_position_offset(self.current_entity.visible_grid_part.offset_x,
                                                                self.current_entity.visible_grid_part.offset_y)
        if self.current_entity == self.entity2:
            n_billboards_from_texture_shader.select_texture(1)
            self.entity2.draw_billboards(size, 1)
        else:
            n_billboards_from_texture_shader.select_texture(0)
            self.entity1.draw_billboards(size, 1)

    def draw_scene(self,
                   n_color_map_v2_texture_shader,
                   n_instances_from_texture_shader,
                   n_billboards_from_texture_shader,
                   n_color_billboards_texture_shader
                   ):

        if not self.entity1.created:
            self.entity1.create_data_container_texture(
                self.current_width,
                self.current_height
            )
            self.entity1.quad.create_quad()
        if not self.entity2.created:
            self.entity2.create_data_container_texture(
                self.current_width,
                self.current_height
            )
            self.entity2.quad.create_quad()

        self.update_scene_entities()

        max_points_count = 1500000
        max_nodes_count = 500000

        size = self.current_entity.visible_grid_part.w * self.current_entity.visible_grid_part.h

        if self.n_viewport.current_factor_half_delta < 1:
            # print(self.n_viewport.current_factor, self.n_viewport.current_factor_half_delta)
            self.draw_billboards(n_billboards_from_texture_shader, size)
            # self.draw_textures(n_color_billboards_texture_shader, 1)

        self.draw_textures(n_color_map_v2_texture_shader, self.n_viewport.current_factor_half_delta)
