import OpenGL.GL as gl
import numpy as np


class NQuad:
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

        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.w = 0
        self.h = 0

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

    def update_quad_position(self, x1, y1, x2, y2):
        if not self.created:
            return

        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.w = x2 - x1
        self.h = y2 - y1

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

    def update_second_texture_coordinates(self, tex_width, tex_height, current_quad, prev_quad):
        """
        Map tex coordinates from one quad to another quad
        Two quads can be different sizes and different positions
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
