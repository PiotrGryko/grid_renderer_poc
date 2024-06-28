import json
import threading

from transformers import pipeline

from app.ai.task_mapping import get_model_pipeline_task, TaskType
from app.ai.task_result import create_pipe_success_result, create_pipe_error_result


class TaskInput:
    def __init__(self, text, images, files, context, labels):
        self.text = text
        self.images = images
        self.files = files
        self.context = context
        self.labels = labels

    def get_table(self):
        try:
            table = json.loads(self.context)
            return table
        except Exception as e:
            print("Table exception", e)
            return {}

    def validate(self, task):
        empty_command = self.text is None
        empty_images = self.images is None or len(self.images) == 0
        empty_files = self.files is None or len(self.files) == 0
        empty_context_message = self.context is None or self.context == ""
        empty_labels = self.labels is None or len(self.labels) == 0

        if empty_command and empty_images and empty_files:
            return "No data"
        if task.is_none():
            return "No pipeline task detected"
        elif task.has_zero_shot_label_input and empty_labels:
            return "You must add candidate labels"
        elif task.has_context_input and empty_context_message:
            return "You must add context message"
        elif task.has_image_input and empty_images:
            return f"{task.value} pipeline requires image input"
        elif task.has_audio_input and empty_files:

            return f"{task.value} pipeline requires audio input"
        elif task.has_video_input and empty_files:
            return f"{task.value} pipeline requires video input"
        return None

    def get_input_message(self):
        user_msg = ""
        if self.files:
            user_msg += str(self.files)
            user_msg += "\n"
        if self.images:
            user_msg += str(self.images)
            user_msg += "\n"
        if self.text:
            user_msg += self.text
        return user_msg


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

    def load_from_model(self, model, tokenizer=None, image_processor=None, feature_extractor=None):
        self.model = model
        self.tokenizer = tokenizer
        self.image_processor = image_processor
        self.feature_extractor = feature_extractor

        self.task = get_model_pipeline_task(self.model)
        self.task.fill()
        print("detected pipeline", self.task)

    def change_task(self, task):
        self.task = task
        self.task.fill()

    def run_pipeline(self, task_input):
        thread = threading.Thread(target=self._run_pipeline_internal,
                                  args=(self.task,
                                        task_input))
        thread.start()
        return thread

    def _run_pipeline_internal(self, task, task_input):
        input_text = task_input.text
        images = task_input.images
        files = task_input.files
        context_message = task_input.context
        zero_shot_labels = task_input.labels

        print("Run pipeline", task, input_text,
              "\nhas model", self.model is not None,
              "\nhas tokenizer", self.tokenizer is not None,
              "\nhas image processor", self.image_processor is not None,
              "\nhas feature extractor", self.feature_extractor is not None)

        if images is None:
            images = []
        if files is None:
            files = []

        if task.is_zero_shot_object_detection() and len(files) > 0:
            input_value = files[0]
        elif len(files) > 0:
            input_value = files if files is not None else input_text
        elif len(images) > 0:
            input_value = images
        else:
            input_value = input_text

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
            else:
                pipe = pipeline(task=task.value,
                                model=self.model,
                                tokenizer=self.tokenizer,
                                image_processor=self.image_processor,
                                feature_extractor=self.feature_extractor
                                )
            print("Task attempt:", task, input_value, context_message, zero_shot_labels)

            if task.has_zero_shot_label_input:
                output = pipe(input_value, candidate_labels=zero_shot_labels)
            elif task.is_question_answering():
                output = pipe(question=input_value, context=context_message)
            elif task.is_visual_question_answering():
                output = pipe(question=input_text, image=images[0])
            elif task.is_table_question_answering():
                output = pipe(query=input_text, table=task_input.get_table())
            elif task.is_image_to_text():
                print("image to text", images, input_text)
                output = pipe(images, prompt=input_text)
            else:
                output = pipe(input_value)
            if zero_shot_labels:
                print("Labels", zero_shot_labels)
            if context_message:
                print("Context", context_message)
            print("Input: ", input_value)
            print("Output: ", output)
            self.last_result = create_pipe_success_result(
                task_type=task,
                input=input_value,
                output=output
            )
        except Exception as e:
            print("Input: ", input_value)
            print("Exception: ", e)
            self.last_result = create_pipe_error_result(
                task_type=task,
                input=input_value,
                error=str(e)
            )

    def pool_forward_pass_result(self):
        if self.last_result is not None:
            r = self.last_result
            self.last_result = None
            return r
        else:
            return None
