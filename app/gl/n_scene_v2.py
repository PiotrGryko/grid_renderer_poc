import gc
import math
import time

import numpy as np

import OpenGL.GL as gl


class Quad:
    def __init__(self):
        self.tex_vbo = None
        self.vao = None
        self.ebo = None
        self.vbo = None
        self.indices = None
        self.tex_coords = None
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
            0.0, 0.0,  # Bottom-left becomes Top-left
            1.0, 0.0,  # Bottom-right becomes Top-right
            1.0, 1.0,  # Top-right becomes Bottom-right
            0.0, 1.0  # Top-left becomes Bottom-left
        ], dtype=np.float32)
        # Define the indices to form two triangles
        self.indices = np.array([
            0, 1, 2,  # Triangle 1
            0, 2, 3  # Triangle 2
        ], dtype=np.uint32)

        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, gl.GL_DYNAMIC_DRAW)

        #
        self.tex_vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.tex_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.tex_coords.nbytes, self.tex_coords, gl.GL_STATIC_DRAW)

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

        # Create and bind the element buffer object (EBO)
        self.ebo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, gl.GL_STATIC_DRAW)
        self.created = True

    def update_quad_position(self, x1, y1, x2, y2):
        if not self.created:
            return
        self.vertices = np.array([
            x1, y1,  # Bottom-left
            x2, y1,  # Bottom-right
            x2, y2,  # Top-right
            x1, y2  # Top-left
        ], dtype=np.float32)
        # Bind the VBO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        # Update the buffer data
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, 0, self.vertices.nbytes, self.vertices)

    def draw(self):
        if not self.created:
            return
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, len(self.indices), gl.GL_UNSIGNED_INT, None)


class EntityV2:
    def __init__(self):
        self.ebo = None
        self.tex_coords = None
        self.indices = None
        self.tex_vbo = None
        self.node_circle_vbo = None
        self.node_quad_vbo = None
        self.vao = None
        self.pbo = None
        self.texture = None

        self.empty_img = None
        self.created = False

        self.width = 0
        self.height = 0
        self.num_instances = 0
        self.radius = 0.2
        self.num_segments = 20

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
            0.0, 0.0,  # Bottom-left becomes Top-left
            1.0, 0.0,  # Bottom-right becomes Top-right
            1.0, 1.0,  # Top-right becomes Bottom-right
            0.0, 1.0  # Top-left becomes Bottom-left
        ], dtype=np.float32)
        return tex_coords

    def create_data_container_texture(self, width, height):
        self.texture = gl.glGenTextures(1)
        self.width = width
        self.height = height
        self.empty_img = np.empty((self.width, self.height), dtype=np.float32)
        self.num_instances = self.width * self.height

        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R32F, self.width, self.height, 0, gl.GL_RED, gl.GL_FLOAT, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
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
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, gl.GL_RED, gl.GL_FLOAT, self.empty_img)
        for c, d in zip(chunks, dimensions):
            cx1, cy1, cx2, cy2 = d
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, cx1, cy1, cx2 - cx1, cy2 - cy1, gl.GL_RED, gl.GL_FLOAT, c)

        #print("View data updated", (time.time() - start_time) * 1000, "ms")

    def draw_points(self, count):
        if not self.created:
            return

        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_POINTS, 0, 1, count)

    def draw_nodes(self, count, detail):
        if not self.created:
            return
        count = min([count, self.num_instances])
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        segments_count = min([self.num_segments, math.ceil(detail * self.num_segments)])
        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLE_FAN, 0,
                                 segments_count, count)

    def draw_billboards(self, count, detail):
        if not self.created:
            return
        count = min([count, self.num_instances])
        gl.glActiveTexture(gl.GL_TEXTURE2)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        segments_count = min([self.num_segments, math.ceil(detail * self.num_segments)])
        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLE_STRIP, 0,
                                 segments_count, count)


class NSceneV2:
    def __init__(self, n_net, n_viewport, buffer_w, buffer_h):
        self.n_net = n_net
        self.n_viewport = n_viewport

        self.visible_grid_part = None
        self.current_details_level = None

        self.current_width = buffer_w * 2
        self.current_height = buffer_h * 2

        self.quad = Quad()
        self.entity = EntityV2()
        self.current_size = 0

    def set_node_radius(self, radius):
        self.entity.update_node_radius(radius)

    # @profile
    def update_scene_entities(self):

        if self.n_viewport.visible_data is None:
            return
        should_update = False

        if self.visible_grid_part != self.n_viewport.visible_data:
            self.visible_grid_part = self.n_viewport.visible_data
            should_update = True

        if should_update:
            self.current_size = int(self.visible_grid_part.w * self.visible_grid_part.h)
            chunks, dimensions = self.n_net.get_subgrid_chunks_grid_dimensions(
                self.visible_grid_part.x1,
                self.visible_grid_part.y1,
                self.visible_grid_part.x2,
                self.visible_grid_part.y2,
                self.visible_grid_part.factor)
            self.quad.update_quad_position(
                0,
                0,
                self.current_width,
                self.current_height,
            )
            self.entity.update_data(
                chunks,
                dimensions)

    def draw_scene(self,
                   n_color_map_v2_texture_shader,
                   n_instances_from_texture_shader,
                   n_billboards_from_texture_shader
                   ):

        if not self.entity.created:
            self.entity.create_data_container_texture(
                self.current_width,
                self.current_height
            )
        if not self.quad.created:
            self.quad.create_quad()

        # Update
        self.update_scene_entities()

        size = self.visible_grid_part.w * self.visible_grid_part.h

        max_points_count = 1500000
        max_nodes_count = 500000

        if size >= max_points_count:
            n_color_map_v2_texture_shader.use()
            n_color_map_v2_texture_shader.update_texture_width(self.current_width)
            n_color_map_v2_texture_shader.update_texture_height(self.current_height)
            n_color_map_v2_texture_shader.update_details_factor(self.visible_grid_part.factor)
            n_color_map_v2_texture_shader.update_position_offset(self.visible_grid_part.offset_x,
                                                                 self.visible_grid_part.offset_y)
            self.quad.draw()
        else:
            if  True:#size < max_nodes_count:
                #self.entity.draw_nodes(size, 1)

                n_billboards_from_texture_shader.use()
                n_billboards_from_texture_shader.update_texture_width(self.current_width)
                n_billboards_from_texture_shader.update_texture_height(self.current_height)
                n_billboards_from_texture_shader.update_target_width(self.visible_grid_part.w)
                n_billboards_from_texture_shader.update_target_height(self.visible_grid_part.h)
                n_billboards_from_texture_shader.update_details_factor(self.visible_grid_part.factor)
                n_billboards_from_texture_shader.update_position_offset(self.visible_grid_part.offset_x,
                                                                        self.visible_grid_part.offset_y)
                self.entity.draw_billboards(size, 1)

            elif size < max_points_count:
                n_instances_from_texture_shader.use()
                n_instances_from_texture_shader.update_texture_width(self.current_width)
                n_instances_from_texture_shader.update_texture_height(self.current_height)
                n_instances_from_texture_shader.update_target_width(self.visible_grid_part.w)
                n_instances_from_texture_shader.update_target_height(self.visible_grid_part.h)
                n_instances_from_texture_shader.update_details_factor(self.visible_grid_part.factor)
                n_instances_from_texture_shader.update_position_offset(self.visible_grid_part.offset_x,
                                                                       self.visible_grid_part.offset_y)
                self.entity.draw_points(size)


