import gc
import math
import time

import numpy as np

import OpenGL.GL as gl

from app.gl.n_viewport import VisibleGrid


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

    def update_quad_position(self, x1, y1, x2, y2, offset_x, offset_y, factor):
        if not self.created:
            return
        # The quad x1,y1,x2,y2 is always 0,0,width,height
        # The position of the quad in the world is offset + size * factor
        x1 = offset_x + x1 * factor
        x2 = offset_x + x2 * factor
        y1 = offset_y + y1 * factor
        y2 = offset_y + y2 * factor
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
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R32F, self.width, self.height, 0, gl.GL_RED, gl.GL_FLOAT, None)
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

    def update_node_radius(self, radius):
        if not self.created:
            return
        self.radius = radius
        vertices = self.build_node_vertices()

        # Bind the vertex buffer and upload vertex data
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.node_circle_vbo)
        # Update the buffer data
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)

    def update_data(self, chunks, dimensions):
        if not self.created:
            return
        start_time = time.time()
        gl.glActiveTexture(self.gl_texture_unit)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, gl.GL_RED, gl.GL_FLOAT, self.empty_img)
        for c, d in zip(chunks, dimensions):
            cx1, cy1, cx2, cy2 = d
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, cx1, cy1, cx2 - cx1, cy2 - cy1, gl.GL_RED, gl.GL_FLOAT, c)

        # print("View data updated", (time.time() - start_time) * 1000, "ms")

    def update_entity(self, n_net, visible_grid_part, factor):
        self.visible_grid_part = visible_grid_part
        chunks, dimensions = n_net.get_subgrid_chunks_grid_dimensions(
            self.visible_grid_part.x1,
            self.visible_grid_part.y1,
            self.visible_grid_part.x2,
            self.visible_grid_part.y2,
            factor)
        self.update_data(
            chunks,
            dimensions)

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

        self.current_width = buffer_w * 2
        self.current_height = buffer_h * 2

        self.entity1 = EntityV2(gl.GL_TEXTURE2)
        self.entity2 = EntityV2(gl.GL_TEXTURE3)

        self.should_update_prev = False
        self.updated = False

        self.current_entity = None
        self.zooming_in = True

    def set_node_radius(self, radius):
        self.entity1.update_node_radius(radius)

    def switch_unit(self):
        self.should_update_prev = True

    # @profile
    def update_scene_entities(self):

        if self.n_viewport.visible_data is None:
            return

        current_quad = self.n_viewport.visible_data

        prev_quad = None
        should_update = True

        if self.entity1.visible_grid_part == current_quad:
            should_update = False
        if self.entity2.visible_grid_part == current_quad:
            should_update = False

        if should_update:
            print("should update")
            if self.current_entity == self.entity1:
                self.should_update_prev = True

            if self.should_update_prev:
                print("update entity 2 ")
                self.should_update_prev = False
                self.entity2.update_entity(self.n_net,
                                           current_quad,
                                           current_quad.factor)
                self.entity2.quad.update_quad_position(
                    0, 0,
                    self.current_width,
                    self.current_height,
                    self.entity2.visible_grid_part.offset_x,
                    self.entity2.visible_grid_part.offset_y,
                    self.entity2.visible_grid_part.factor
                )
                self.current_entity = self.entity2
                self.zooming_in = self.entity2.visible_grid_part.zoom > self.entity1.visible_grid_part.zoom

            else:
                print("update entity 1")
                self.updated = True
                self.entity1.update_entity(self.n_net, current_quad, current_quad.factor)

                self.entity1.quad.update_quad_position(
                    0, 0,
                    self.current_width,
                    self.current_height,
                    self.entity1.visible_grid_part.offset_x,
                    self.entity1.visible_grid_part.offset_y,
                    self.entity1.visible_grid_part.factor
                )
                self.current_entity = self.entity1
                if self.entity2.visible_grid_part is not None:
                    self.zooming_in = self.entity1.visible_grid_part.zoom > self.entity2.visible_grid_part.zoom
                # if self.entity2.visible_grid_part is not None:
                #     self.entity1.quad.update_second_texture_coordinates(
                #         self.current_width,
                #         self.current_height,
                #         self.entity1.visible_grid_part,
                #         self.entity2.visible_grid_part,
                #         self.n_window
                #     )
                # self.entity2.quad.update_second_texture_coordinates(
                #     self.current_width,
                #     self.current_height,
                #     self.entity2.visible_grid_part,
                #     self.entity1.visible_grid_part,
                #     self.n_window
                # )

                print(self.zooming_in)

    def draw_textures(self, n_color_map_v2_texture_shader):
        factor = self.n_viewport.current_factor
        factor_delta = self.n_viewport.current_factor_delta

        n_color_map_v2_texture_shader.use()
        current_alpha = factor_delta if factor == 1 else 1 # if self.zooming_in else factor_delta
        prev_alpha = 0 if not self.zooming_in else factor_delta if factor == 1 else factor_delta

        if self.current_entity == self.entity2:

            n_color_map_v2_texture_shader.select_texture(1)
            n_color_map_v2_texture_shader.update_fading_factor(current_alpha)
            gl.glActiveTexture(self.entity2.gl_texture_unit)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.entity2.texture)
            self.entity2.draw_texture()

            n_color_map_v2_texture_shader.select_texture(0)
            n_color_map_v2_texture_shader.update_fading_factor(prev_alpha)
            gl.glActiveTexture(self.entity1.gl_texture_unit)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.entity1.texture)
            self.entity1.draw_texture()

        else:

            n_color_map_v2_texture_shader.select_texture(0)
            n_color_map_v2_texture_shader.update_fading_factor(current_alpha)
            gl.glActiveTexture(self.entity1.gl_texture_unit)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.entity1.texture)
            self.entity1.draw_texture()
            #
            n_color_map_v2_texture_shader.select_texture(1)
            n_color_map_v2_texture_shader.update_fading_factor(prev_alpha)
            gl.glActiveTexture(self.entity2.gl_texture_unit)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.entity2.texture)
            self.entity2.draw_texture()

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
                   n_billboards_from_texture_shader
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

        # Update
        self.update_scene_entities()

        size = self.current_entity.visible_grid_part.w * self.current_entity.visible_grid_part.h

        max_points_count = 1500000
        max_nodes_count = 500000
        factor = self.n_viewport.current_factor

        if size < max_nodes_count:
            self.draw_billboards(n_billboards_from_texture_shader, size)

        self.draw_textures(n_color_map_v2_texture_shader)
