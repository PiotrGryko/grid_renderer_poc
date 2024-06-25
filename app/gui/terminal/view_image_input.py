import imgui


class ImageInput:
    def __init__(self, config):
        self.input_height = 35
        self.input_changed = False
        self.image_loader = config.image_loader
        self.images = []

    def clear_input(self):
        self.images = []

    def has_images(self):
        return len(self.images) > 0

    def render(self, vertical=True):

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (10, 10))

        imgui.begin_child("##ImageInputView", 0, self.input_height,
                          border=True,
                          flags=imgui.WINDOW_NO_SCROLLBAR)

        imgui.push_style_var(imgui.STYLE_SCROLLBAR_SIZE, 1)
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (0, 0))
        imgui.push_style_var(imgui.STYLE_CELL_PADDING, (10, 10))
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0, 0, 0, 0)
        # Input Text Box
        if len(self.images) == 0:
            self.input_height = 35
            imgui.text_wrapped("Drag and drop images")
        else:
            height = 0
            for index, image in enumerate(self.images):
                if index > 0 and vertical:
                    imgui.same_line()
                (img_w, img_h) = self.image_loader.render_from_path(image)
                if img_h > height:
                    height = img_h
            self.input_height = height + 20

        imgui.pop_style_color()
        imgui.pop_style_var(3)
        imgui.end_child()
        imgui.pop_style_var(1)

    def load_image(self, file_path, max_size=130):
        self.images.append(file_path)
        self.input_height = 150
