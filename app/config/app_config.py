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
            'last_directory': self.last_directory
        }
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, self.filename)
        try:
            with open(file_path, 'w') as file:
                json.dump(config_data, file, indent=4)
        except IOError as e:
            print(f"Error: Failed to write to {file_path}. {e}")
