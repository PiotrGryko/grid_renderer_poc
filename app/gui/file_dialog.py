import os

import imgui


class FileDialog:
    def __init__(self, config):
        self.opened = False
        self.new_dir_name = ""
        self.config = config

        self.current_path = os.path.expanduser("~") if self.config.last_directory is None else self.config.last_directory
        self.selected_path = None

    def open(self):
        print("open dialog")
        self.opened = True

    def render(self):
        if not self.opened:
            return
        opened, self.opened = imgui.begin("Select Path", True)
        if opened:

            # Show current path
            imgui.text(f"Current Path: {self.current_path}")
            imgui.separator()

            # Navigation buttons
            if imgui.button("Up"):
                self.current_path = os.path.dirname(self.current_path)
            imgui.same_line()
            if imgui.button("Select"):
                self.selected_path = self.current_path
                self.config.last_directory = self.selected_path
                self.config.save_config()
                self.opened = False

            imgui.push_item_width(200)  # Set the width of the input text field
            changed, self.new_dir_name = imgui.input_text("New Dir Name", self.new_dir_name, 256)
            imgui.pop_item_width()
            imgui.same_line()
            if imgui.button("Create New Dir"):
                self.create_new_directory()

            imgui.separator()

            # Directory contents
            self.draw_directory_contents(self.current_path)
            imgui.end()

    def draw_directory_contents(self, path):
        try:
            for item in os.listdir(path):
                if item.startswith('.'):
                    continue
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    opened, selected = imgui.selectable(f"[DIR] {item}")
                    if opened:
                        self.current_path = item_path
        except Exception as e:
            print(e)

    def create_new_directory(self):
        if self.new_dir_name:
            new_dir_path = os.path.join(self.current_path, self.new_dir_name)
            try:
                os.makedirs(new_dir_path, exist_ok=True)
                self.current_path = new_dir_path
                self.new_dir_name = ""  # Clear the input field after creation
            except Exception as e:
                print(f"Error creating directory: {e}")
