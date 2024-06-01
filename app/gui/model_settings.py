import math
import os
import threading
import time

import imgui
from huggingface_hub import HfApi, ModelFilter

from app.gui.file_dialog import FileDialog


class ModelSettingsPage:
    def __init__(self, download_manager, config):
        self.api = HfApi()
        self.models = []
        self.selected_model = None
        self.search_text = ""
        self.loading = False  # Flag to indicate loading state
        self.load_thread = None
        self.loaded = False
        self.file_dialog = FileDialog(config)
        self.download_manager = download_manager

    def start_loading_models(self):

        self.loading = True
        # if self.load_thread is not None and self.load_thread.is_alive():
        #     self.load_thread.join()
        self.load_thread = threading.Thread(target=self.load_models_list, args=(self.search_text,))
        self.load_thread.start()

    def load_models_list(self, query):
        print("loading models list...", self.search_text)

        if len(self.search_text) > 1:
            models = self.api.list_models(limit=50, sort="downloads", search=self.search_text)
        else:
            models = self.api.list_models(limit=50, sort="downloads")
        models = list(models)
        if self.search_text == query:
            self.models = models
            self.loading = False
            self.loaded = True
            print("Models loaded ", query, self.search_text)

    def render_spinner(self, center, radius, thickness):
        draw_list = imgui.get_window_draw_list()
        num_segments = 30
        start_angle = time.time() * 2.0  # Rotate speed

        for i in range(num_segments):
            angle = start_angle + (i * 2 * math.pi / num_segments)
            x = center[0] + math.cos(angle) * radius
            y = center[1] + math.sin(angle) * radius
            color = imgui.get_color_u32_rgba(1.0, 1.0, 1.0, 1.0 * (i / num_segments))
            draw_list.add_circle_filled(x, y, thickness, color)

    def render(self):

        window_expanded, window_opened = imgui.begin("Downloads manager", flags=imgui.WINDOW_NO_RESIZE, closable=True)
        if not self.loaded and not self.loading:
            self.start_loading_models()

        # Left column: Search bar and model list
        imgui.begin_child("left_column", width=300, height=400, border=True)

        changed, new_query = imgui.input_text("Search", self.search_text, 256)
        if changed:
            self.search_text = new_query
            self.start_loading_models()

        if self.loading:
            imgui.same_line()
            spinner_pos = imgui.get_cursor_screen_pos()
            self.render_spinner((spinner_pos[0] + 10, spinner_pos[1] + 10), radius=8, thickness=2)
            imgui.new_line()

        if imgui.begin_list_box("##models_list", width=280, height=350):
            for model in self.models:
                is_selected = (model == self.selected_model)
                opened, clicked = imgui.selectable(model.modelId, width=250, selected=is_selected)
                if clicked and not is_selected:
                    print("model clicked")
                    self.selected_model = model
            imgui.end_list_box()

        imgui.end_child()

        imgui.same_line()

        # Right column: Model settings
        imgui.begin_child("right_column", width=400, height=400, border=True)

        if self.selected_model:
            model_info = self.selected_model
            imgui.text(f"Model Name: {model_info.modelId}")
            imgui.text_wrapped(f"Model ID: {model_info.id}")
            imgui.text_wrapped(f"Author: {model_info.author}")
            imgui.text_wrapped(f"SHA: {model_info.sha}")
            imgui.text_wrapped(f"Created At: {model_info.created_at}")
            imgui.text_wrapped(f"Last Modified: {model_info.last_modified}")
            imgui.text_wrapped(f"Private: {model_info.private}")
            imgui.text_wrapped(f"Gated: {model_info.gated}")
            imgui.text_wrapped(f"Downloads: {model_info.downloads}")
            imgui.text_wrapped(f"Likes: {model_info.likes}")
            imgui.text_wrapped(f"Library Name: {model_info.library_name}")
            imgui.text_wrapped(f"Pipeline Tag: {model_info.pipeline_tag}")

            # Display tags as a single wrapped string
            tags_string = ", ".join(model_info.tags)
            imgui.text("Tags:")
            imgui.push_text_wrap_pos(imgui.get_window_size()[0] - 20)  # Set wrap position
            imgui.text_colored(tags_string, 1.0, 0.5, 0.0, 1.0)
            imgui.pop_text_wrap_pos()

            imgui.separator()
            if model_info.siblings:
                imgui.text("Files:")
                for sibling in model_info.siblings:
                    imgui.text_wrapped(f"- {sibling.rfilename}")

            imgui.separator()
            status = self.download_manager.get_download_status(model_info.modelId)
            imgui.text_wrapped(f"Download status: {status}")

            imgui.separator()
            imgui.text("Download Model")

            # Local path selection
            if imgui.button("Select Path"):
                print("button")
                self.file_dialog.open()

            imgui.same_line()
            imgui.text_wrapped(f"Path: {self.file_dialog.selected_path}")
            self.file_dialog.render()

            if imgui.button("Download"):
                updated_path = self.file_dialog.selected_path + "/" + self.selected_model.modelId.replace("/", "_")
                self.download_manager.download_model(self.selected_model.modelId, updated_path)

        imgui.end_child()

        imgui.end()
        return window_opened
