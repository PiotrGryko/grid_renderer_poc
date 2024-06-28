from io import BytesIO

import numpy as np
import requests
from PIL import Image, ImageDraw

from app.ai.task_type import TaskType


class OutputLine:
    def __init__(self, text=None, image=None, audio_data=None, sampling_rate=None):
        self.text = text
        self.image = image
        self.audio_data = audio_data
        self.sampling_rate = sampling_rate


class BasePipeResult:
    def __init__(self, task, input, output, success=True):
        self.task = task
        self.input = input
        self.output = output
        self.success = success
        self.lines = []

    def draw_boxes_on_image(self, image_path, detections):
        # Open the image file
        print("draw boxes", image_path, detections)
        if image_path.startswith('http://') or image_path.startswith('https://'):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            # Open the image file
            image = Image.open(image_path)

        draw = ImageDraw.Draw(image)

        # Loop through the detections and draw boxes
        for detection in detections:
            box = detection['box']
            label = detection['label']
            score = detection['score']

            # Define the bounding box
            xmin, ymin, xmax, ymax = box['xmin'], box['ymin'], box['xmax'], box['ymax']
            draw.rectangle([xmin, ymin, xmax, ymax], outline="red", width=3)

            # Draw label and score
            draw.text((xmin, ymin), f"{label} ({score:.2f})", fill="red")

        return image

    def load_image(self, image_path):
        print("load image ", image_path)
        if image_path.startswith('http://') or image_path.startswith('https://'):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            # Open the image file
            image = Image.open(image_path)
        return image


class ErrorResult(BasePipeResult):
    def __init__(self, task, input, error):
        super().__init__(task, input, error, success=False)
        self.lines = [OutputLine(text=error)]


class UnknownPipeResult(BasePipeResult):
    def __init__(self, task, input, output):
        super().__init__(task, input, output)
        self.lines = [OutputLine(text=output)]


class AudioClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.AUDIO_CLASSIFICATION, input, output)
        self.lines = [OutputLine(text=output)]


class AutomaticSpeechRecognitionPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.AUTOMATIC_SPEECH_RECOGNITION, input, output)
        for o in self.output:
            self.lines.append(OutputLine(text=o['text']))


class TextGenerationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TEXT_GENERATION, input, output)
        for o in self.output:
            self.lines.append(OutputLine(text=o['generated_text']))


class Text2TextGenerationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TEXT2TEXT_GENERATION, input, output)
        for o in self.output:
            self.lines.append(OutputLine(text=o['generated_text']))


class SummarizationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.SUMMARIZATION, input, output)
        for o in self.output:
            self.lines.append(OutputLine(text=o['summary_text']))


class TranslationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TRANSLATION, input, output)
        for o in self.output:
            self.lines.append(OutputLine(text=o['translation_text']))


class FillMaskPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.FILL_MASK, input, output)
        self.lines = [OutputLine(text=self.output)]


class TokenClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TOKEN_CLASSIFICATION, input, output)
        self.lines = [OutputLine(text=self.output)]


class TextClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TEXT_CLASSIFICATION, input, output)
        highest_score_element = max(self.output, key=lambda x: x['score'])
        self.lines = [
            OutputLine(text=f"Label: {highest_score_element['label']},"
                            f" Score: {highest_score_element['score']}")]


class ZeroShotClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.ZERO_SHOT_CLASSIFICATION, input, output)
        sequence = self.output['sequence']
        labels = self.output['labels']
        scores = self.output['scores']
        labels_scores = zip(labels, scores)

        highest_score_element = max(labels_scores, key=lambda x: x[1])
        self.lines = [
            OutputLine(text=f"Label: {highest_score_element[0]},"
                            f" Score: {highest_score_element[1]}")]


class ZeroShotAudioClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.ZERO_SHOT_AUDIO_CLASSIFICATION, input, output)
        highest_score_element = max(self.output[0], key=lambda x: x['score'])
        self.lines = [
            OutputLine(text=f"Label: {highest_score_element['label']},"
                            f" Score: {highest_score_element['score']}")]


class ObjectDetectionPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.OBJECT_DETECTION, input, output)
        if type(self.input) is str and len(self.output) > 0:
            self.lines.append(OutputLine(text=self.output, image=self.draw_boxes_on_image(self.input, self.output)))
        elif type(self.input) is list:
            for i, o in zip(self.input, self.output):
                self.lines.append(OutputLine(
                    text=o,
                    image=self.draw_boxes_on_image(i, o)
                ))


class TextToAudioPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TEXT_TO_AUDIO, input, output)
        self.audio_data = self.output['audio']
        self.sampling_rate = self.output['sampling_rate']
        self.lines = [
            OutputLine(
                audio_data=self.output['audio'],
                sampling_rate=self.output['sampling_rate'])]


class TextToSpeechPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TEXT_TO_SPEECH, input, output)
        self.audio_data = self.output['audio']
        self.sampling_rate = self.output['sampling_rate']
        self.lines = [
            OutputLine(
                audio_data=self.output['audio'],
                sampling_rate=self.output['sampling_rate'])]


class QuestionAnsweringPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.QUESTION_ANSWERING, input, output)
        self.lines.append(
            OutputLine(text=f"Answer: {self.output['answer']},"
                            f" Score: {self.output['score']}"))


class VisualQuestionAnsweringPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.QUESTION_ANSWERING, input, output)
        highest_score_element = max(self.output, key=lambda x: x['score'])
        self.lines.append(
            OutputLine(text=f"Answer: {highest_score_element['answer']},"
                            f" Score: {highest_score_element['score']}"))


class DepthEstimationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.DEPTH_ESTIMATION, input, output)
        if type(self.input) is str and len(self.output) > 0:
            self.lines.append(OutputLine(text=self.output, image=self.output["depth"]))
        elif type(self.input) is list:
            for i, o in zip(self.input, self.output):
                self.lines.append(OutputLine(text=o, image=o["depth"]))


class ImageClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.IMAGE_CLASSIFICATION, input, output)
        if type(self.input) is str and len(self.output) > 0:
            self.lines.append(OutputLine(text=self.output, image=self.load_image(self.input)))
        elif type(self.input) is list:
            for i, o in zip(self.input, self.output):
                self.lines.append(OutputLine(text=o, image=self.load_image(i)))


class ImageSegmentationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.IMAGE_SEGMENTATION, input, output)
        if type(self.input) is str and len(self.output) > 0:
            for out in self.output:
                self.lines.append(OutputLine(text=out, image=out['mask']))
        elif type(self.input) is list:
            for i, out in zip(self.input, self.output):
                for o in out:
                    self.lines.append(OutputLine(text=o, image=o['mask']))


class ImageToImagePipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.IMAGE_TO_IMAGE, input, output)
        if type(self.input) is str:
            self.lines.append(OutputLine(image=self.output))
        elif type(self.input) is list:
            for i, out in zip(self.input, self.output):
                self.lines.append(OutputLine(image=out))


class VideoClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.VIDEO_CLASSIFICATION, input, output)
        self.lines = [OutputLine(text=output)]


class ZeroShotImageClassificationPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.ZERO_SHOT_IMAGE_CLASSIFICATION, input, output)
        if type(self.input) is str:
            self.lines = [OutputLine(text=self.output, image=self.load_image(self.input))]
        elif type(self.input) is list:
            for i, o in zip(self.input, self.output):
                self.lines.append(OutputLine(
                    text=o,
                    image=self.load_image(i)
                ))


class ZeroShotObjectDetectionPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.ZERO_SHOT_OBJECT_DETECTION, input, output)
        if type(self.input) is str and len(self.output) > 0:
            self.lines.append(OutputLine(text=self.output, image=self.draw_boxes_on_image(self.input, self.output)))
        elif type(self.input) is list:
            for i, o in zip(self.input, self.output):
                self.lines.append(OutputLine(
                    text=o,
                    image=self.draw_boxes_on_image(i, o)
                ))


class ImageToTextPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.IMAGE_TO_TEXT, input, output)
        if type(self.input) is str and len(self.output) > 0:
            self.lines.append(OutputLine(text=self.output[0]['generated_text'], image=self.load_image(self.input)))
        elif type(self.input) is list:
            for i, o in zip(self.input, self.output):
                self.lines.append(OutputLine(
                    text=o[0]['generated_text'],
                    image=self.load_image(i)
                ))


class ImageFeatureExtractionPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.IMAGE_FEATURE_EXTRACTION, input, output)
        np_array = np.array(output)

        self.lines.append(OutputLine(text=f"Numpy array of a shape {np_array.shape}"))


class FeatureExtractionPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.FEATURE_EXTRACTION, input, output)
        np_array = np.array(output)

        self.lines.append(OutputLine(text=f"Numpy array of a shape {np_array.shape}"))


class TableQuestionAnsweringPipeResult(BasePipeResult):
    def __init__(self, input, output):
        super().__init__(TaskType.TABLE_QUESTION_ANSWERING, input, output)
        self.lines.append(OutputLine(text=output))


def create_pipe_error_result(task_type, input, error):
    return ErrorResult(task_type, input, error)


def create_pipe_success_result(task_type, input, output):
    if task_type == TaskType.AUDIO_CLASSIFICATION:
        return AudioClassificationPipeResult(input, output)
    elif task_type == TaskType.AUTOMATIC_SPEECH_RECOGNITION:
        return AutomaticSpeechRecognitionPipeResult(input, output)
    elif task_type == TaskType.TEXT_GENERATION:
        return TextGenerationPipeResult(input, output)
    elif task_type == TaskType.FILL_MASK:
        return FillMaskPipeResult(input, output)
    elif task_type == TaskType.TOKEN_CLASSIFICATION:
        return TokenClassificationPipeResult(input, output)
    elif task_type == TaskType.OBJECT_DETECTION:
        return ObjectDetectionPipeResult(input, output)
    elif task_type == TaskType.TEXT_TO_AUDIO:
        return TextToAudioPipeResult(input, output)
    elif task_type == TaskType.TEXT_TO_SPEECH:
        return TextToSpeechPipeResult(input, output)
    elif task_type == TaskType.QUESTION_ANSWERING:
        return QuestionAnsweringPipeResult(input, output)
    elif task_type == TaskType.DEPTH_ESTIMATION:
        return DepthEstimationPipeResult(input, output)
    elif task_type == TaskType.IMAGE_CLASSIFICATION:
        return ImageClassificationPipeResult(input, output)
    elif task_type == TaskType.IMAGE_SEGMENTATION:
        return ImageSegmentationPipeResult(input, output)
    elif task_type == TaskType.IMAGE_TO_IMAGE:
        return ImageToImagePipeResult(input, output)
    elif task_type == TaskType.VIDEO_CLASSIFICATION:
        return VideoClassificationPipeResult(input, output)
    elif task_type == TaskType.ZERO_SHOT_IMAGE_CLASSIFICATION:
        return ZeroShotImageClassificationPipeResult(input, output)
    elif task_type == TaskType.ZERO_SHOT_OBJECT_DETECTION:
        return ZeroShotObjectDetectionPipeResult(input, output)
    elif task_type == TaskType.TEXT2TEXT_GENERATION:
        return Text2TextGenerationPipeResult(input, output)
    elif task_type == TaskType.IMAGE_TO_TEXT:
        return ImageToTextPipeResult(input, output)
    elif task_type == TaskType.SUMMARIZATION:
        return SummarizationPipeResult(input, output)
    elif task_type == TaskType.TRANSLATION:
        return TranslationPipeResult(input, output)
    elif task_type == TaskType.TEXT_CLASSIFICATION:
        return TextClassificationPipeResult(input, output)
    elif task_type == TaskType.ZERO_SHOT_CLASSIFICATION:
        return ZeroShotClassificationPipeResult(input, output)
    elif task_type == TaskType.ZERO_SHOT_AUDIO_CLASSIFICATION:
        return ZeroShotAudioClassificationPipeResult(input, output)
    elif task_type == TaskType.IMAGE_FEATURE_EXTRACTION:
        return ImageFeatureExtractionPipeResult(input, output)
    elif task_type == TaskType.FEATURE_EXTRACTION:
        return FeatureExtractionPipeResult(input, output)
    elif task_type == TaskType.VISUAL_QUESTION_ANSWERING:
        return VisualQuestionAnsweringPipeResult(input, output)
    elif task_type == TaskType.TABLE_QUESTION_ANSWERING:
        return TableQuestionAnsweringPipeResult(input, output)
    else:
        return UnknownPipeResult(task_type, input, output)


SUPPORTED_PIPELINES = [
    "text-generation",
    "text2text-generation",
    "summarization",
    "translation",

    "audio-classification",
    "token-classification",
    "text-classification",
    "video-classification",
    "image-classification",
    "zero-shot-classification",
    "zero-shot-image-classification",
    "zero-shot-object-detection",
    "zero-shot-audio-classification",

    "fill-mask",
    "automatic-speech-recognition",
    "object-detection",
    "question-answering",
    "depth-estimation",
    "image-segmentation",
    "image-feature-extraction",
    "visual-question-answering",
    "table-question-answering",
    "feature-extraction",

    "text-to-audio",
    "text-to-speech",
    "image-to-image",
    "image-to-text"

]
