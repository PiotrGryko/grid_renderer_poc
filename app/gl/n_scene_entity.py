import math
import time

import OpenGL.GL as gl
import numpy as np

from app.gl.n_quad import NQuad


class EntityV2:
    def __init__(self):
        self.ebo = None
        self.tex_coords = None
        self.indices = None
        self.tex_vbo = None

        self.node_quad_vbo = None
        self.vao = None
        self.pbo = None

        self.frame_data = None
        self.created = False

        self.width = 0
        self.height = 0
        self.num_instances = 0
        self.radius = 0.2
        self.num_segments = 20

        self.base_texture = None
        self.gl_base_texture_unit = gl.GL_TEXTURE2

        # previous frame
        self.prev_texture = None
        self.gl_prev_texture_unit = gl.GL_TEXTURE3

        self.active_texture = None
        self.active_texture_index = 0  # 0 or 1
        self.gl_active_texture_unit = self.gl_base_texture_unit

        self.visible_grid_part = None
        self.quad = NQuad()

        # Track the detail level of the second texture (used in blending mode)
        self.second_texture_factor = None
        self.current_texture_factor = None

        self.pbo_id = None

        self.scheduled = False

        self.fade_duration = 300
        self.start_time = None
        self.is_fading = False
        self.locked = False

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
        self.frame_data = np.full((self.width, self.height), fill_value=-1, dtype=np.float32)
        self.num_instances = self.width * self.height

        # base texture
        self.base_texture = gl.glGenTextures(1)
        gl.glActiveTexture(self.gl_base_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.base_texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R32F, width, height, 0, gl.GL_RED, gl.GL_FLOAT, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        error = gl.glGetError()
        if error != gl.GL_NO_ERROR:
            print(f"Error loading texture: {error}")

        self.active_texture = self.base_texture
        # previous texture for smooth updates
        self.prev_texture = gl.glGenTextures(1)
        gl.glActiveTexture(self.gl_prev_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.prev_texture)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_R32F, width, height, 0, gl.GL_RED, gl.GL_FLOAT, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        error = gl.glGetError()
        if error != gl.GL_NO_ERROR:
            print(f"Error loading texture: {error}")

        # vertices = self.build_node_vertices()
        quads = self.build_quad_vertices()
        self.tex_coords = self.build_text_coords()
        # Define the indices to form two triangles
        self.indices = np.array([
            0, 1, 2,  # Triangle 1
            0, 2, 3  # Triangle 2
        ], dtype=np.uint32)

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
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.node_quad_vbo)
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

        error = gl.glGetError()
        if error != gl.GL_NO_ERROR:
            print(f"Error loading texture: {error}")

        self.created = True

    def destroy(self):
        if self.created:
            self.quad.destroy()
            # gl.glDeleteBuffers(1, [self.node_circle_vbo])
            gl.glDeleteBuffers(1, [self.node_quad_vbo])
            gl.glDeleteBuffers(1, [self.tex_vbo])
            gl.glDeleteBuffers(1, [self.ebo])
            gl.glDeleteVertexArrays(1, [self.vao])
            gl.glDeleteTextures(1, [self.base_texture])
            self.created = False

    def update_entity(self, current_frame, buffer_w, buffer_h):
        start_time = time.time()
        frame_data = current_frame.data

        if buffer_w != self.width or buffer_h != self.height:
            print("Buffer mismatch!")
            return

        prev_quad = self.visible_grid_part

        self.visible_grid_part = current_frame.visible_grid_part
        self.current_texture_factor = self.visible_grid_part.factor

        if self.active_texture_index == 0:
            self.active_texture_index = 1
            self.gl_active_texture_unit = self.gl_prev_texture_unit
            self.active_texture = self.prev_texture
        else:
            self.active_texture_index = 0
            self.gl_active_texture_unit = self.gl_base_texture_unit
            self.active_texture = self.base_texture

        gl.glActiveTexture(self.gl_active_texture_unit)
        gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 0, 0, self.width, self.height, gl.GL_RED, gl.GL_FLOAT,
                           frame_data)
        print("Updated entity", (time.time() - start_time) * 1000, "ms")

        x1, y1, x2, y2 = self.visible_grid_part.get_quad_position(buffer_w, buffer_h)
        self.quad.update_quad_position(x1, y1, x2, y2)

        if prev_quad is not None:
            self.second_texture_factor = prev_quad.factor
            self.quad.update_second_texture_coordinates(
                buffer_w,
                buffer_h,
                self.visible_grid_part,
                prev_quad
            )

            if self.visible_grid_part.factor != prev_quad.factor:
                self.start_time = time.time()
                self.is_fading = True
                if self.visible_grid_part.zoom > prev_quad.zoom:
                    self.locked = True

    def get_fade_progress(self):
        if self.start_time is None:
            return 0

        elapsed_time = (time.time() - self.start_time) * 1000  # Convert to milliseconds
        progress = (elapsed_time % self.fade_duration) / self.fade_duration

        # Check if the interval has completed
        if elapsed_time >= self.fade_duration:
            progress = 1
            self.is_fading = False
            self.locked = False
            self.start_time = None
        return 1 - progress

    def draw_points(self, count):
        if not self.created:
            return

        gl.glActiveTexture(self.gl_active_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.active_texture)

        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_POINTS, 0, 1, count)

    def draw_nodes(self, count, detail):
        if not self.created:
            return
        count = min([count, self.num_instances])
        gl.glActiveTexture(self.gl_active_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.active_texture)
        segments_count = min([self.num_segments, math.ceil(detail * self.num_segments)])
        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLE_FAN, 0,
                                 segments_count, count)

    def draw_billboards(self, count, detail):
        if not self.created:
            return
        count = min([count, self.num_instances])
        gl.glActiveTexture(self.gl_active_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.active_texture)
        segments_count = min([self.num_segments, math.ceil(detail * self.num_segments)])
        gl.glBindVertexArray(self.vao)
        gl.glDrawArraysInstanced(gl.GL_TRIANGLE_STRIP, 0,
                                 6, count)

    def create_quad(self):
        if not self.quad.created:
            self.quad.create_quad()

    def draw_texture(self):
        gl.glActiveTexture(self.gl_active_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.active_texture)
        self.create_quad()
        self.quad.draw()
