import hashlib

import OpenGL.GL as gl
import imgui
from PIL import Image


class ImageData:
    def __init__(self, tex_id, tex_w, tex_h, image, path):
        self.input_texture_id = tex_id
        self.input_texture_width = tex_w
        self.input_texture_height = tex_h
        self.image = image
        self.path = path


class ImageLoader:

    def __init__(self):
        self.images = {}

    def clear_input(self):
        self.images = {}

    def load_image_from_path(self, file_path, max_size=130):
        if file_path in self.images:
            return self.images[file_path]

        image = Image.open(file_path)
        img = self._load_gl_image(image, max_size)
        self.images[file_path] = img
        return img

    def load_image(self, image, max_size=130):
        image_key = hashlib.sha256(image.tobytes()).hexdigest()

        if image_key in self.images:
            return self.images[image_key]

        img = self._load_gl_image(image, max_size)
        self.images[image_key] = img
        return img

    def _load_gl_image(self, image, max_size=130):
        image = image.convert("RGBA")
        width, height = image.size

        if width > height:
            if width > max_size:
                height = int((max_size / width) * height)
                width = max_size
        else:
            if height > max_size:
                width = int((max_size / height) * width)
                height = max_size

        image = image.resize((width, height))
        image_data = image.tobytes()

        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_data)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        return ImageData(
            tex_id=texture_id,
            tex_w=width,
            tex_h=height,
            image=image,
            path=None
        )

    def render_from_PIL_image(self, image, max_size=130):
        img = self.load_image(image, max_size)
        if img:
            imgui.image(int(img.input_texture_id), int(img.input_texture_width), int(img.input_texture_height))
            return (img.input_texture_width, img.input_texture_height)
        else:
            return None

    def render_from_path(self, image, max_size=130):
        img = self.load_image_from_path(image, max_size)
        if img:
            imgui.image(int(img.input_texture_id), int(img.input_texture_width), int(img.input_texture_height))
            return (img.input_texture_width, img.input_texture_height)
        else:
            return None
