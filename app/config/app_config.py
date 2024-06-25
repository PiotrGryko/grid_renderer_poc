import json
import os


class LittleConfig:
    def __init__(self):
        self.color_name = None
        self.buffer_width = None
        self.buffer_height = None
        self.enable_blend = None
        self.power_of_two = None
        self.last_directory = None
        self.model_directory = None
        self.gui_state_config = None
        self.window_width = None
        self.window_height = None
        self.show_weights = True
        self.filename = "config.json"

    def load_config(self):

        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, self.filename)

        try:
            with open(file_path, 'r') as file:
                config_data = json.load(file)
                self.color_name = config_data.get('color_name')
                self.buffer_width = config_data.get('buffer_width')
                self.buffer_height = config_data.get('buffer_height')
                self.enable_blend = config_data.get('enable_blend')
                self.power_of_two = config_data.get('power_of_two')
                self.last_directory = config_data.get('last_directory')
                self.model_directory = config_data.get('model_directory')
                self.gui_state_config = config_data.get('gui_state_config')
                self.window_width = config_data.get('window_width')
                self.window_height = config_data.get('window_height')
                self.show_weights = config_data.get('show_weights')

        except FileNotFoundError:
            print(f"Error: {file_path} not found.")
        except json.JSONDecodeError:
            print(f"Error: Failed to parse {file_path}.")

    def save_config(self):
        config_data = {
            'color_name': self.color_name,
            'buffer_width': self.buffer_width,
            'buffer_height': self.buffer_height,
            'enable_blend': self.enable_blend,
            'power_of_two': self.power_of_two,
            'last_directory': self.last_directory,
            'model_directory': self.model_directory,
            'gui_state_config': self.gui_state_config,
            'window_width': self.window_width,
            'window_height': self.window_height,
            'show_weights': self.show_weights

        }
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, self.filename)
        try:
            with open(file_path, 'w') as file:
                json.dump(config_data, file, indent=4)
        except IOError as e:
            print(f"Error: Failed to write to {file_path}. {e}")

    # Shortcuts for easier managment
    def set_model_directory(self, model_directory):
        self.model_directory = model_directory
        self.save_config()

    def set_last_directory(self, last_directory):
        self.last_directory = last_directory
        self.save_config()

    def set_graphics_settings(self, buffer_width, buffer_height, power_of_two, enable_blend):
        self.buffer_width = buffer_width
        self.buffer_height = buffer_height
        self.power_of_two = power_of_two
        self.enable_blend = enable_blend
        self.save_config()

    def set_show_weights(self, show_weights):
        self.show_weights = show_weights
        self.save_config()
