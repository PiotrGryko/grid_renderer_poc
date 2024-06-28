from enum import Enum

import numpy as np
from PIL import Image


class TaskType(Enum):
    NONE = "NONE"
    AUDIO_CLASSIFICATION = "audio-classification"
    AUTOMATIC_SPEECH_RECOGNITION = "automatic-speech-recognition"
    TEXT_TO_AUDIO = "text-to-audio"
    TEXT_TO_SPEECH = "text-to-speech"
    ZERO_SHOT_AUDIO_CLASSIFICATION = "zero-shot-audio-classification"
    DEPTH_ESTIMATION = "depth-estimation"
    IMAGE_CLASSIFICATION = "image-classification"
    IMAGE_SEGMENTATION = "image-segmentation"
    IMAGE_TO_IMAGE = "image-to-image"
    OBJECT_DETECTION = "object-detection"
    VIDEO_CLASSIFICATION = "video-classification"
    ZERO_SHOT_IMAGE_CLASSIFICATION = "zero-shot-image-classification"
    ZERO_SHOT_OBJECT_DETECTION = "zero-shot-object-detection"
    CONVERSATIONAL = "conversational"
    FILL_MASK = "fill-mask"
    QUESTION_ANSWERING = "question-answering"
    SUMMARIZATION = "summarization"
    TABLE_QUESTION_ANSWERING = "table-question-answering"
    TEXT_CLASSIFICATION = "text-classification"
    TEXT_GENERATION = "text-generation"
    TEXT2TEXT_GENERATION = "text2text-generation"
    TOKEN_CLASSIFICATION = "token-classification"
    TRANSLATION = "translation"
    ZERO_SHOT_CLASSIFICATION = "zero-shot-classification"
    DOCUMENT_QUESTION_ANSWERING = "document-question-answering"
    FEATURE_EXTRACTION = "feature-extraction"
    IMAGE_FEATURE_EXTRACTION = "image-feature-extraction"
    IMAGE_TO_TEXT = "image-to-text"
    MASK_GENERATION = "mask-generation"
    VISUAL_QUESTION_ANSWERING = "visual-question-answering"
    TIME_SERIES_CLASSIFICATION = "time-series-classification"
    TIME_SERIES_REGRESSION = "time-series-regression"
    KEYPOINT_DETECTION = "keypoint-detection"
    BACKBONE = "backbone"
    AUDIO_XVECTOR = "audio-xvector"
    AUDIO_FRAME_CLASSIFICATION = "audio-frame-classification"
    CTC = "ctc"

    def __init__(self, value):
        super().__init__()
        self.has_context_input = None
        self.has_zero_shot_label_input = None
        self.has_image_input = None
        self.has_audio_input = None
        self.has_video_input = None
        self.has_file_input = None

        self.text_input_hint = None
        self.context_input_hint = None
        self.image_input_hint = None
        self.file_input_hint = None

        self.parameters = None

        self.media_accepts_single_file = None

    # Meeehh ;/
    def fill(self):
        self.parameters = TASK_PIPELINE_PARAMETERS[self]
        self.has_zero_shot_label_input = (self.is_zero_shot_object_detection()
                                          or self.is_zero_shot_audio_classification()
                                          or self.is_zero_shot_image_classification()
                                          or self.is_zero_shot_classification())
        self.has_context_input = self.is_question_answering() or self.is_table_question_answering()

        self.has_image_input = (self.is_image_to_image()
                                or self.is_object_detection()
                                or self.is_zero_shot_object_detection()
                                or self.is_image_segmentation()
                                or self.is_image_to_text()
                                or self.is_image_classification()
                                or self.is_zero_shot_image_classification()
                                or self.is_image_feature_extraction()
                                or self.is_visual_question_answering())

        self.has_audio_input = (self.is_audio_classification()
                                or self.is_automatic_speech_recognition()
                                or self.is_zero_shot_audio_classification())

        self.has_video_input = self.is_video_classification()
        self.has_file_input = self.has_video_input or self.has_audio_input

        self.media_accepts_single_file = self.is_zero_shot_object_detection() or self.is_visual_question_answering()

        self.text_input_hint = "Type your message"
        self.context_input_hint = "Add context message"
        self.image_input_hint = "Drag and drop images"
        self.file_input_hint = "Drag and drop files"

        if self.is_table_question_answering():
            self.context_input_hint = "Paste table dict"

        if self.has_video_input:
            self.file_input_hint = "Drag and drop video files"
            # self.text_input_hint = "Type video URL"
        if self.has_audio_input:
            self.file_input_hint = "Drag and drop audio files"
            # self.text_input_hint = "Type audio URL"
        # if self.has_image_input:
        # self.text_input_hint = "Type image URL"

    @staticmethod
    def from_string(task_string):
        for name, member in TaskType.__members__.items():
            if member.value == task_string:
                return member
        raise ValueError(f"'{task_string}' is not a valid Task")

    def is_none(self):
        return self == TaskType.NONE

    def is_audio_classification(self):
        return self == TaskType.AUDIO_CLASSIFICATION

    def is_automatic_speech_recognition(self):
        return self == TaskType.AUTOMATIC_SPEECH_RECOGNITION

    def is_text_to_audio(self):
        return self == TaskType.TEXT_TO_AUDIO or self == TaskType.TEXT_TO_SPEECH

    def is_zero_shot_audio_classification(self):
        return self == TaskType.ZERO_SHOT_AUDIO_CLASSIFICATION

    def is_depth_estimation(self):
        return self == TaskType.DEPTH_ESTIMATION

    def is_image_classification(self):
        return self == TaskType.IMAGE_CLASSIFICATION

    def is_image_segmentation(self):
        return self == TaskType.IMAGE_SEGMENTATION

    def is_image_to_image(self):
        return self == TaskType.IMAGE_TO_IMAGE

    def is_object_detection(self):
        return self == TaskType.OBJECT_DETECTION

    def is_video_classification(self):
        return self == TaskType.VIDEO_CLASSIFICATION

    def is_zero_shot_image_classification(self):
        return self == TaskType.ZERO_SHOT_IMAGE_CLASSIFICATION

    def is_zero_shot_object_detection(self):
        return self == TaskType.ZERO_SHOT_OBJECT_DETECTION

    def is_conversational(self):
        return self == TaskType.CONVERSATIONAL

    def is_fill_mask(self):
        return self == TaskType.FILL_MASK

    def is_question_answering(self):
        return self == TaskType.QUESTION_ANSWERING

    def is_summarization(self):
        return self == TaskType.SUMMARIZATION

    def is_table_question_answering(self):
        return self == TaskType.TABLE_QUESTION_ANSWERING

    def is_text_classification(self):
        return self == TaskType.TEXT_CLASSIFICATION

    def is_text_generation(self):
        return self == TaskType.TEXT_GENERATION

    def is_text2text_generation(self):
        return self == TaskType.TEXT2TEXT_GENERATION

    def is_token_classification(self):
        return self == TaskType.TOKEN_CLASSIFICATION

    def is_translation(self):
        return self == TaskType.TRANSLATION

    def is_zero_shot_classification(self):
        return self == TaskType.ZERO_SHOT_CLASSIFICATION

    def is_document_question_answering(self):
        return self == TaskType.DOCUMENT_QUESTION_ANSWERING

    def is_feature_extraction(self):
        return self == TaskType.FEATURE_EXTRACTION

    def is_image_feature_extraction(self):
        return self == TaskType.IMAGE_FEATURE_EXTRACTION

    def is_image_to_text(self):
        return self == TaskType.IMAGE_TO_TEXT

    def is_mask_generation(self):
        return self == TaskType.MASK_GENERATION

    def is_visual_question_answering(self):
        return self == TaskType.VISUAL_QUESTION_ANSWERING


TASK_PIPELINE_PARAMETERS = {
    TaskType.NONE: {},
    TaskType.AUDIO_CLASSIFICATION: {
        "inputs": {"type": (np.ndarray, bytes, str, dict), "optional": False, "default": None},
        "top_k": {"type": int, "optional": True, "default": None}
    },
    TaskType.AUTOMATIC_SPEECH_RECOGNITION: {
        "inputs": {"type": (np.ndarray, bytes, str, dict), "optional": False, "default": None},
        "return_timestamps": {"type": (str, bool), "optional": True, "default": None},
        "generate_kwargs": {"type": dict, "optional": True, "default": None},
        "max_new_tokens": {"type": int, "optional": True, "default": None}
    },
    TaskType.TEXT_TO_AUDIO: {
        "text_inputs": {"type": (str, list), "optional": False, "default": None},
        "forward_params": {"type": dict, "optional": True, "default": None},
        "generate_kwargs": {"type": dict, "optional": True, "default": None}
    },
    TaskType.TEXT_TO_SPEECH: {
        "text_inputs": {"type": (str, list), "optional": False, "default": None},
        "forward_params": {"type": dict, "optional": True, "default": None},
        "generate_kwargs": {"type": dict, "optional": True, "default": None}
    },
    TaskType.ZERO_SHOT_AUDIO_CLASSIFICATION: {
        "audios": {"type": (str, list, np.ndarray), "optional": False, "default": None},
        "candidate_labels": {"type": list, "optional": False, "default": None},
        "hypothesis_template": {"type": str, "optional": True, "default": "This is a sound of {}"}
    },
    TaskType.DEPTH_ESTIMATION: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.IMAGE_CLASSIFICATION: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "function_to_apply": {"type": str, "optional": True, "default": "default"},
        "top_k": {"type": int, "optional": True, "default": 5},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.IMAGE_SEGMENTATION: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "subtask": {"type": str, "optional": True, "default": None},
        "threshold": {"type": float, "optional": True, "default": 0.9},
        "mask_threshold": {"type": float, "optional": True, "default": 0.5},
        "overlap_mask_area_threshold": {"type": float, "optional": True, "default": 0.5},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.IMAGE_TO_IMAGE: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.OBJECT_DETECTION: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "threshold": {"type": float, "optional": True, "default": 0.5},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.VIDEO_CLASSIFICATION: {
        "videos": {"type": (str, list), "optional": False, "default": None},
        "top_k": {"type": int, "optional": True, "default": 5},
        "num_frames": {"type": int, "optional": True, "default": None},
        "frame_sampling_rate": {"type": int, "optional": True, "default": 1}
    },
    TaskType.ZERO_SHOT_IMAGE_CLASSIFICATION: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "candidate_labels": {"type": list, "optional": False, "default": None},
        "hypothesis_template": {"type": str, "optional": True, "default": "This is a photo of {}"},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.ZERO_SHOT_OBJECT_DETECTION: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "candidate_labels": {"type": list, "optional": False, "default": None},
        "hypothesis_template": {"type": str, "optional": True, "default": "This is a photo of {}"},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.CONVERSATIONAL: {
        "conversations": {"type": (str, list), "optional": False, "default": None},
        "clean_up_tokenization_spaces": {"type": bool, "optional": True, "default": True},
        "generate_kwargs": {"type": dict, "optional": True, "default": None}
    },
    TaskType.FILL_MASK: {
        "args": {"type": (str, list), "optional": False, "default": None},
        "targets": {"type": (str, list), "optional": True, "default": None},
        "top_k": {"type": int, "optional": True, "default": 5}
    },
    TaskType.QUESTION_ANSWERING: {
        "args": {"type": (str, list), "optional": False, "default": None},
        "X": {"type": (str, list), "optional": True, "default": None},
        "data": {"type": (str, list), "optional": True, "default": None},
        "question": {"type": (str, list), "optional": False, "default": None},
        "context": {"type": (str, list), "optional": False, "default": None},
        "topk": {"type": int, "optional": True, "default": 1},
        "doc_stride": {"type": int, "optional": True, "default": 128},
        "max_answer_len": {"type": int, "optional": True, "default": 15},
        "max_seq_len": {"type": int, "optional": True, "default": 384},
        "max_question_len": {"type": int, "optional": True, "default": 64},
        "handle_impossible_answer": {"type": bool, "optional": True, "default": False},
        "align_to_words": {"type": bool, "optional": True, "default": True}
    },
    TaskType.SUMMARIZATION: {
        "documents": {"type": (str, list), "optional": False, "default": None},
        "return_text": {"type": bool, "optional": True, "default": True},
        "return_tensors": {"type": bool, "optional": True, "default": False},
        "clean_up_tokenization_spaces": {"type": bool, "optional": True, "default": False},
        "generate_kwargs": {"type": dict, "optional": True, "default": None}
    },
    TaskType.TABLE_QUESTION_ANSWERING: {
        "table": {"type": ("DataFrame", dict), "optional": False, "default": None},
        "query": {"type": (str, list), "optional": False, "default": None},
        "sequential": {"type": bool, "optional": True, "default": False},
        "padding": {"type": (bool, str), "optional": True, "default": False},
        "truncation": {"type": (bool, str), "optional": True, "default": False}
    },
    TaskType.TEXT_CLASSIFICATION: {
        "inputs": {"type": (str, list, dict), "optional": False, "default": None},
        "top_k": {"type": int, "optional": True, "default": 1},
        "function_to_apply": {"type": str, "optional": True, "default": "default"}
    },
    TaskType.TEXT_GENERATION: {
        "text_inputs": {"type": (str, list), "optional": False, "default": None},
        "return_tensors": {"type": bool, "optional": True, "default": False},
        "return_text": {"type": bool, "optional": True, "default": True},
        "return_full_text": {"type": bool, "optional": True, "default": True},
        "clean_up_tokenization_spaces": {"type": bool, "optional": True, "default": True},
        "prefix": {"type": str, "optional": True, "default": None},
        "handle_long_generation": {"type": str, "optional": True, "default": None},
        "generate_kwargs": {"type": dict, "optional": True, "default": None}
    },
    TaskType.TEXT2TEXT_GENERATION: {
        "args": {"type": (str, list), "optional": False, "default": None},
        "return_tensors": {"type": bool, "optional": True, "default": False},
        "return_text": {"type": bool, "optional": True, "default": True},
        "clean_up_tokenization_spaces": {"type": bool, "optional": True, "default": False},
        "truncation": {"type": str, "optional": True, "default": "do_not_truncate"},
        "generate_kwargs": {"type": dict, "optional": True, "default": None}
    },
    TaskType.TOKEN_CLASSIFICATION: {
        "inputs": {"type": (str, list), "optional": False, "default": None}
    },
    TaskType.TRANSLATION: {
        "args": {"type": (str, list), "optional": False, "default": None},
        "return_tensors": {"type": bool, "optional": True, "default": False},
        "return_text": {"type": bool, "optional": True, "default": True},
        "clean_up_tokenization_spaces": {"type": bool, "optional": True, "default": False},
        "src_lang": {"type": str, "optional": True, "default": None},
        "tgt_lang": {"type": str, "optional": True, "default": None},
        "generate_kwargs": {"type": dict, "optional": True, "default": None}
    },
    TaskType.ZERO_SHOT_CLASSIFICATION: {
        "sequences": {"type": (str, list), "optional": False, "default": None},
        "candidate_labels": {"type": (str, list), "optional": False, "default": None},
        "hypothesis_template": {"type": str, "optional": True, "default": "This example is {}."},
        "multi_label": {"type": bool, "optional": True, "default": False}
    },
    TaskType.DOCUMENT_QUESTION_ANSWERING: {
        "image": {"type": (str, Image), "optional": False, "default": None},
        "question": {"type": str, "optional": False, "default": None},
        "word_boxes": {"type": (list, tuple), "optional": True, "default": None},
        "top_k": {"type": int, "optional": True, "default": 1},
        "doc_stride": {"type": int, "optional": True, "default": 128},
        "max_answer_len": {"type": int, "optional": True, "default": 15},
        "max_seq_len": {"type": int, "optional": True, "default": 384},
        "max_question_len": {"type": int, "optional": True, "default": 64},
        "handle_impossible_answer": {"type": bool, "optional": True, "default": False},
        "lang": {"type": str, "optional": True, "default": "english"},
        "tesseract_config": {"type": str, "optional": True, "default": None},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.FEATURE_EXTRACTION: {
        "args": {"type": (str, list), "optional": False, "default": None}
    },
    TaskType.IMAGE_FEATURE_EXTRACTION: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.IMAGE_TO_TEXT: {
        "images": {"type": (str, list, Image), "optional": False, "default": None},
        "max_new_tokens": {"type": int, "optional": True, "default": None},
        "generate_kwargs": {"type": dict, "optional": True, "default": None},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.MASK_GENERATION: {
        "inputs": {"type": (np.ndarray, bytes, str, dict), "optional": False, "default": None},
        "mask_threshold": {"type": float, "optional": True, "default": 0.0},
        "pred_iou_thresh": {"type": float, "optional": True, "default": 0.88},
        "stability_score_thresh": {"type": float, "optional": True, "default": 0.95},
        "stability_score_offset": {"type": int, "optional": True, "default": 1},
        "crops_nms_thresh": {"type": float, "optional": True, "default": 0.7},
        "crops_n_layers": {"type": int, "optional": True, "default": 0},
        "crop_overlap_ratio": {"type": float, "optional": True, "default": 512 / 1500},
        "crop_n_points_downscale_factor": {"type": int, "optional": True, "default": 1},
        "timeout": {"type": float, "optional": True, "default": None}
    },
    TaskType.VISUAL_QUESTION_ANSWERING: {
        "image": {"type": (str, list, Image), "optional": False, "default": None},
        "question": {"type": (str, list), "optional": False, "default": None},
        "top_k": {"type": int, "optional": True, "default": 5},
        "timeout": {"type": float, "optional": True, "default": None}
    }
}
