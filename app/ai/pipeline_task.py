import threading
from io import BytesIO

import requests
from PIL import Image, ImageDraw
from transformers import pipeline

from app.ai.task_mapping import get_model_pipeline_task, TaskType, get_forward_params


class PipelineResult:
    def __init__(self, task, input, output, success):
        self.task = task
        self.input = input
        self.output = output
        self.formatted_output = output
        self.images = []
        self.success = success
        self.audio_data = None
        self.sampling_rate = None

    def __repr__(self):
        return (f"{self.__class__.__name__}(task={self.task!r}, "
                f"input={self.input!r},"
                f" output={self.output!r}, "
                f" images={self.images!r})")

    def process_result(self):
        if not self.success:
            self.formatted_output = f"OUTPUT:{self.output}"
        elif self.task.is_object_detection():
            if type(self.input) is str and len(self.output) > 0:
                self.images.append(self.draw_boxes_on_image(self.input, self.output))
            elif type(self.input) is list:
                for i, o in zip(self.input, self.output):
                    self.images.append(self.draw_boxes_on_image(i, o))
        elif self.task.is_image_classification():
            if type(self.input) is str and len(self.output) > 0:
                self.images.append(self.load_image(self.input))
            elif type(self.input) is list:
                for i in self.input:
                    self.images.append(self.load_image(i))
        elif self.task.is_depth_estimation():
            if type(self.input) is str and len(self.output) > 0:
                self.images.append(self.output['depth'])
            elif type(self.input) is list:
                for i, o in zip(self.input, self.output):
                    self.images.append(o['depth'])
        elif self.task.is_image_segmentation():
            if type(self.input) is str and len(self.output) > 0:
                for out in self.output:
                    self.images.append(out['mask'])
            elif type(self.input) is list:
                for i, out in zip(self.input, self.output):
                    for o in out:
                        self.images.append(o['mask'])
        elif self.task.is_text_to_audio():
            self.audio_data = self.output['audio']
            self.sampling_rate = self.output['sampling_rate']
            self.formatted_output = f"OUTPUT:"
        elif self.task.is_text_generation():
            self.formatted_output = f"OUTPUT:{self.output[0]['generated_text']}"
        else:
            self.formatted_output = f"OUTPUT:{self.output}"

    def load_image(self, image_path):
        print("load image ", image_path)
        if image_path.startswith('http://') or image_path.startswith('https://'):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            # Open the image file
            image = Image.open(image_path)
        return image

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


class PipelineTask:
    def __init__(self):
        self.task = TaskType.NONE
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.feature_extractor = None
        self.last_result = None
        self.forward_pass_parameters = None

    def clear(self):
        self.task = TaskType.NONE
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.feature_extractor = None
        self.last_result = None
        self.forward_pass_parameters = None

    def load_from_model(self, model, tokenizer=None, image_processor=None, feature_extractor=None):
        self.model = model
        self.tokenizer = tokenizer
        self.image_processor = image_processor
        self.feature_extractor = feature_extractor

        self.task = get_model_pipeline_task(self.model)
        if self.model:
            self.forward_pass_parameters = get_forward_params(self.model.__class__)
        print("detected pipeline", self.task)

    def get_model_forward_parameters(self):
        if self.model:
            return get_forward_params(self.model.__class__)
        else:
            return None

    def run_pipeline(self, input_text=None, images=None, context_message=None):
        thread = threading.Thread(target=self._run_pipeline_internal,
                                  args=(self.task,
                                        input_text,
                                        images,
                                        context_message))
        thread.start()
        return thread

    def _run_pipeline_internal(self, task, input_text, images, context_message):
        print("Run pipeline", task, input_text,
              "\nhas model", self.model is not None,
              "\nhas tokenizer", self.tokenizer is not None,
              "\nhas image processor", self.image_processor is not None,
              "\nhas feature extractor", self.feature_extractor is not None)
        input_value = images if images is not None else input_text

        try:
            if task.is_text_generation():
                pipe = pipeline(task=task.value,
                                model=self.model,
                                tokenizer=self.tokenizer,
                                image_processor=self.image_processor,
                                feature_extractor=self.feature_extractor,
                                do_sample=False,
                                num_return_sequences=1,
                                max_length=50,
                                return_full_text=False
                                )
            elif task.is_text_classification():
                pipe = pipeline(task=task.value,
                                model=self.model,
                                tokenizer=self.tokenizer,
                                image_processor=self.image_processor,
                                feature_extractor=self.feature_extractor
                                )
            else:
                pipe = pipeline(task=task.value,
                                model=self.model,
                                tokenizer=self.tokenizer,
                                image_processor=self.image_processor,
                                feature_extractor=self.feature_extractor
                                )

            if task.is_question_answering():
                output = pipe(question=input_value, context=context_message)
            else:
                output = pipe(input_value)
            print("Input: ", input_value)
            print("Output: ", output)
            self.last_result = PipelineResult(
                task=task,
                input=input_value,
                output=output,
                success=True
            )
            self.last_result.process_result()
        except Exception as e:
            print("Input: ", input_value)
            print("Exception: ", e)
            self.last_result = PipelineResult(
                task=task,
                input=input_value,
                output=str(e),
                success=False
            )
            self.last_result.process_result()

    def pool_forward_pass_result(self):
        if self.last_result is not None:
            r = self.last_result
            self.last_result = None
            return r
        else:
            return None
