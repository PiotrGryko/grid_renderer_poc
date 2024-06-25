import imgui
from PIL import Image, ImageDraw
import sounddevice as sd

from app.ai.pipeline_task import PipelineResult
from app.gui.managers.audio_player import AudioPlayer, PlaybackState


class TerminalOutputView:
    def __init__(self, config):
        self.available_height = None
        self.available_width = None
        self.image_loader = config.image_loader
        self.refresh_scroll = False
        self.audio_player = AudioPlayer()

    def scroll_to_bottom(self):
        self.refresh_scroll = True

    def calculate_size(self, input_height):
        padding = 10
        title_bar = 30
        type_buttons = 30
        self.available_height = imgui.get_content_region_available()[1] - (
                input_height + title_bar + type_buttons + 2 * padding)
        self.available_width = imgui.get_content_region_available()[0] - 2 * padding

    def render(self, buffer):
        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (10, 10))

        imgui.begin_child("##OutputField", width=self.available_width, height=self.available_height, border=True)
        for index, line in enumerate(buffer.output):
            if type(line) is str:
                imgui.text_wrapped(line)
            if type(line) is PipelineResult:
                if not line.success:
                    imgui.push_style_color(imgui.COLOR_TEXT, 1, 0, 0)
                    imgui.text_wrapped(str(line.formatted_output))
                    imgui.pop_style_color()
                elif line.task.is_object_detection():
                    for img in line.images:
                        self.image_loader.render_from_PIL_image(img, 300)
                        imgui.text_wrapped(str(line.output))
                elif line.task.is_image_classification():
                    for img in line.images:
                        self.image_loader.render_from_PIL_image(img, 300)
                    imgui.text_wrapped(str(line.output))
                elif line.task.is_depth_estimation():
                    for img in line.images:
                        self.image_loader.render_from_PIL_image(img, 300)
                    imgui.text_wrapped(str(line.output))
                elif line.task.is_image_segmentation():
                    for img in line.images:
                        self.image_loader.render_from_PIL_image(img, 300)
                    imgui.text_wrapped(str(line.output))
                elif line.task.is_text_to_audio():
                    imgui.text_wrapped(str(line.formatted_output))
                    imgui.same_line()
                    state = self.audio_player.get_state(index)

                    if state == PlaybackState.PLAYING:
                        imgui.same_line()
                        imgui.text("Playing...")
                    else:
                        if imgui.button(f"Play##{index}"):
                            audio_data = line.audio_data.flatten()
                            sampling_rate = line.sampling_rate
                            self.audio_player.play(index, audio_data, sampling_rate)

                else:
                    imgui.text_wrapped(str(line.formatted_output))

        if self.refresh_scroll:
            imgui.set_scroll_here_y(1.0)
            self.refresh_scroll = False
        imgui.end_child()
        imgui.pop_style_var(1)
