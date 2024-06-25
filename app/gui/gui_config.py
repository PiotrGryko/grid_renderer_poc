class GuiConfig:
    def __init__(self, n_net, n_window, color_theme, utils, config, app, download_manager, camera_animation, effects, model_parser, image_loader):
        self.top_bar_height = 30
        self.bottom_bar_height = 30

        self.n_net = n_net
        self.n_window = n_window
        self.color_theme = color_theme
        self.utils = utils
        self.app_config = config
        self.app = app
        self.download_manager = download_manager
        self.camera_animation = camera_animation
        self.effects = effects
        self.model_parser = model_parser
        self.image_loader = image_loader

        self.bottom_bar_message = "Welcome"

    def publish_message(self, message):
        self.bottom_bar_message = message

    def publish_position_message(self, mouse_x, mouse_y):
        self.bottom_bar_message = f"x:{int(mouse_x)} y:{int(mouse_y)}"

    def publish_hover_message(self, layer_meta):
        self.bottom_bar_message = f"Layer: {layer_meta.name}"

    def publish_layer_position_message(self, mouse_x, mouse_y, layer_meta):
        x_within_layer = int(mouse_x - layer_meta.column_offset)
        y_within_layer = int(mouse_y - layer_meta.row_offset)
        self.bottom_bar_message = (f"x:{int(mouse_x)}"
                                   f"y:{int(mouse_y)}, "
                                   f"Layer: {layer_meta.name}, "
                                   f"pos: {x_within_layer}:{y_within_layer}")
