from enum import Enum

import imgui

from app.ai.task_result import BasePipeResult
from app.gui.managers.audio_player import AudioPlayer, PlaybackState


class SystemMessageLevel(Enum):
    SUCCESS = 0
    WARNING = 1
    ERROR = 2


class MessageTypeSystemEvent:
    def __init__(self, text, level):
        self.text = text
        self.level = level


class MessageTypeUserInput:
    def __init__(self, text):
        self.text = text


class MessageTypePipelineResult:
    def __init__(self, pipeline_result):
        self.result = pipeline_result


class OutputBuffer:
    def __init__(self):
        self.lines = []

    def send_user_message(self, text):
        self.lines.append(MessageTypeUserInput(text))

    def send_system_message(self, text, level=SystemMessageLevel.SUCCESS):
        self.lines.append(MessageTypeSystemEvent(text, level))

    def send_pipeline_result_message(self, result):
        self.lines.append(MessageTypePipelineResult(result))


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
        for index, line in enumerate(buffer.lines):
            if isinstance(line, MessageTypeUserInput):
                imgui.text_wrapped("INPUT:")
                imgui.same_line()
                imgui.text_wrapped(line.text)
            if isinstance(line, MessageTypeSystemEvent):
                imgui.text_wrapped("SYSTEM:")
                imgui.same_line()
                if line.level is SystemMessageLevel.WARNING:
                    imgui.text_colored(line.text, 1, 1, 0)
                else:
                    imgui.text_colored(line.text, 0, 1, 0)
            if isinstance(line, MessageTypePipelineResult):
                pipe_result = line.result
                imgui.text_wrapped("OUTPUT:")
                imgui.same_line()
                if not pipe_result.success:
                    imgui.push_style_color(imgui.COLOR_TEXT, 1, 0, 0)
                    for l in pipe_result.lines:
                        imgui.text_wrapped(str(l.text))
                    imgui.pop_style_color()
                else:
                    for l in pipe_result.lines:
                        ## has audio
                        if l.audio_data is not None:
                            state = self.audio_player.get_state(index)

                            if state == PlaybackState.PLAYING:
                                imgui.text("Playing...")
                            else:
                                if imgui.button(f"Play##{index}"):
                                    audio_data = l.audio_data.flatten()
                                    sampling_rate = l.sampling_rate
                                    self.audio_player.play(index, audio_data, sampling_rate)
                        ## has image
                        if l.image:
                            self.image_loader.render_from_PIL_image(l.image, 300)
                        ## has text
                        if l.text:
                            imgui.text_wrapped(str(l.text))

        if self.refresh_scroll:
            imgui.set_scroll_here_y(1.0)
            self.refresh_scroll = False
        imgui.end_child()
        imgui.pop_style_var(1)
