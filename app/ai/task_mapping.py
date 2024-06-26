import inspect

from transformers import (
    AutoConfig,
    MODEL_FOR_SPEECH_SEQ_2_SEQ_MAPPING,
    MODEL_MAPPING,
    MODEL_FOR_IMAGE_TO_IMAGE_MAPPING,
    MODEL_FOR_TIME_SERIES_REGRESSION_MAPPING,
    MODEL_FOR_TIME_SERIES_CLASSIFICATION_MAPPING,
    MODEL_FOR_TEXT_ENCODING_MAPPING,
    MODEL_FOR_KEYPOINT_DETECTION_MAPPING,
    MODEL_FOR_MASK_GENERATION_MAPPING,
    MODEL_FOR_BACKBONE_MAPPING,
    MODEL_FOR_TEXT_TO_WAVEFORM_MAPPING,
    MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING,
    MODEL_FOR_AUDIO_XVECTOR_MAPPING,
    MODEL_FOR_AUDIO_FRAME_CLASSIFICATION_MAPPING,
    MODEL_FOR_CTC_MAPPING,
    MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING,
    MODEL_FOR_NEXT_SENTENCE_PREDICTION_MAPPING,
    MODEL_FOR_MULTIPLE_CHOICE_MAPPING,
    MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING,
    MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING,
    MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING,
    MODEL_FOR_DEPTH_ESTIMATION_MAPPING,
    MODEL_FOR_ZERO_SHOT_OBJECT_DETECTION_MAPPING,
    MODEL_FOR_OBJECT_DETECTION_MAPPING,
    MODEL_FOR_MASKED_IMAGE_MODELING_MAPPING,
    MODEL_FOR_IMAGE_MAPPING,
    MODEL_FOR_MASKED_LM_MAPPING,
    MODEL_FOR_VISUAL_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_DOCUMENT_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_VISION_2_SEQ_MAPPING,
    MODEL_FOR_VIDEO_CLASSIFICATION_MAPPING,
    MODEL_FOR_UNIVERSAL_SEGMENTATION_MAPPING,
    MODEL_FOR_INSTANCE_SEGMENTATION_MAPPING,
    MODEL_FOR_SEMANTIC_SEGMENTATION_MAPPING,
    MODEL_FOR_IMAGE_SEGMENTATION_MAPPING,
    MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING,
    MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING,
    MODEL_FOR_CAUSAL_IMAGE_MODELING_MAPPING,
    MODEL_FOR_PRETRAINING_MAPPING,
    MODEL_FOR_CAUSAL_LM_MAPPING,
    MODEL_WITH_LM_HEAD_MAPPING
)
from transformers.models.auto.configuration_auto import config_class_to_model_type

from app.ai.task_type import TaskType

DEFAULT_MODEL_CLASS_MAPPING = [MODEL_MAPPING]

MODEL_CLASS_MAPPINGS = [
    MODEL_FOR_PRETRAINING_MAPPING,
    MODEL_WITH_LM_HEAD_MAPPING,
    MODEL_FOR_CAUSAL_LM_MAPPING,
    MODEL_FOR_CAUSAL_IMAGE_MODELING_MAPPING,
    MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING,
    MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING,
    MODEL_FOR_IMAGE_SEGMENTATION_MAPPING,
    MODEL_FOR_SEMANTIC_SEGMENTATION_MAPPING,
    MODEL_FOR_INSTANCE_SEGMENTATION_MAPPING,
    MODEL_FOR_UNIVERSAL_SEGMENTATION_MAPPING,
    MODEL_FOR_VIDEO_CLASSIFICATION_MAPPING,
    MODEL_FOR_VISION_2_SEQ_MAPPING,
    MODEL_FOR_VISUAL_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_DOCUMENT_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_MASKED_LM_MAPPING,
    MODEL_FOR_IMAGE_MAPPING,
    MODEL_FOR_MASKED_IMAGE_MODELING_MAPPING,
    MODEL_FOR_OBJECT_DETECTION_MAPPING,
    MODEL_FOR_ZERO_SHOT_OBJECT_DETECTION_MAPPING,
    MODEL_FOR_DEPTH_ESTIMATION_MAPPING,
    MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING,
    MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING,
    MODEL_FOR_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING,
    MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING,
    MODEL_FOR_MULTIPLE_CHOICE_MAPPING,
    MODEL_FOR_NEXT_SENTENCE_PREDICTION_MAPPING,
    MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING,
    MODEL_FOR_CTC_MAPPING,
    MODEL_FOR_SPEECH_SEQ_2_SEQ_MAPPING,
    MODEL_FOR_AUDIO_FRAME_CLASSIFICATION_MAPPING,
    MODEL_FOR_AUDIO_XVECTOR_MAPPING,
    MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING,
    MODEL_FOR_TEXT_TO_WAVEFORM_MAPPING,
    MODEL_FOR_BACKBONE_MAPPING,
    MODEL_FOR_MASK_GENERATION_MAPPING,
    MODEL_FOR_KEYPOINT_DETECTION_MAPPING,
    MODEL_FOR_TEXT_ENCODING_MAPPING,
    MODEL_FOR_TIME_SERIES_CLASSIFICATION_MAPPING,
    MODEL_FOR_TIME_SERIES_REGRESSION_MAPPING,
    MODEL_FOR_IMAGE_TO_IMAGE_MAPPING
]

MAPPING_TO_TASK = {
    TaskType.TEXT_CLASSIFICATION: MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING,
    TaskType.TOKEN_CLASSIFICATION: MODEL_FOR_TOKEN_CLASSIFICATION_MAPPING,
    TaskType.QUESTION_ANSWERING: MODEL_FOR_QUESTION_ANSWERING_MAPPING,
    TaskType.TABLE_QUESTION_ANSWERING: MODEL_FOR_TABLE_QUESTION_ANSWERING_MAPPING,
    TaskType.VISUAL_QUESTION_ANSWERING: MODEL_FOR_VISUAL_QUESTION_ANSWERING_MAPPING,
    TaskType.DOCUMENT_QUESTION_ANSWERING: MODEL_FOR_DOCUMENT_QUESTION_ANSWERING_MAPPING,
    TaskType.AUTOMATIC_SPEECH_RECOGNITION: MODEL_FOR_SPEECH_SEQ_2_SEQ_MAPPING,
    TaskType.IMAGE_TO_IMAGE: MODEL_FOR_IMAGE_TO_IMAGE_MAPPING,
    TaskType.TIME_SERIES_REGRESSION: MODEL_FOR_TIME_SERIES_REGRESSION_MAPPING,
    TaskType.TIME_SERIES_CLASSIFICATION: MODEL_FOR_TIME_SERIES_CLASSIFICATION_MAPPING,
    TaskType.FEATURE_EXTRACTION: MODEL_FOR_TEXT_ENCODING_MAPPING,
    TaskType.KEYPOINT_DETECTION: MODEL_FOR_KEYPOINT_DETECTION_MAPPING,
    TaskType.MASK_GENERATION: MODEL_FOR_MASK_GENERATION_MAPPING,
    TaskType.BACKBONE: MODEL_FOR_BACKBONE_MAPPING,
    TaskType.TEXT_TO_SPEECH: MODEL_FOR_TEXT_TO_WAVEFORM_MAPPING,
    TaskType.TEXT_TO_AUDIO: MODEL_FOR_TEXT_TO_SPECTROGRAM_MAPPING,
    TaskType.AUDIO_XVECTOR: MODEL_FOR_AUDIO_XVECTOR_MAPPING,
    TaskType.AUDIO_FRAME_CLASSIFICATION: MODEL_FOR_AUDIO_FRAME_CLASSIFICATION_MAPPING,
    TaskType.CTC: MODEL_FOR_CTC_MAPPING,
    TaskType.AUDIO_CLASSIFICATION: MODEL_FOR_AUDIO_CLASSIFICATION_MAPPING,
    TaskType.TEXT_GENERATION: MODEL_FOR_CAUSAL_LM_MAPPING,
    TaskType.TEXT2TEXT_GENERATION: MODEL_FOR_SEQ_TO_SEQ_CAUSAL_LM_MAPPING,
    TaskType.DEPTH_ESTIMATION: MODEL_FOR_DEPTH_ESTIMATION_MAPPING,
    TaskType.ZERO_SHOT_OBJECT_DETECTION: MODEL_FOR_ZERO_SHOT_OBJECT_DETECTION_MAPPING,
    TaskType.OBJECT_DETECTION: MODEL_FOR_OBJECT_DETECTION_MAPPING,
    TaskType.FILL_MASK: MODEL_FOR_MASKED_LM_MAPPING,
    TaskType.VIDEO_CLASSIFICATION: MODEL_FOR_VIDEO_CLASSIFICATION_MAPPING,
    TaskType.IMAGE_SEGMENTATION: MODEL_FOR_IMAGE_SEGMENTATION_MAPPING,
    TaskType.ZERO_SHOT_IMAGE_CLASSIFICATION: MODEL_FOR_ZERO_SHOT_IMAGE_CLASSIFICATION_MAPPING,
    TaskType.IMAGE_CLASSIFICATION: MODEL_FOR_IMAGE_CLASSIFICATION_MAPPING,
    TaskType.IMAGE_TO_TEXT: MODEL_FOR_VISION_2_SEQ_MAPPING,
    TaskType.IMAGE_FEATURE_EXTRACTION: MODEL_FOR_IMAGE_MAPPING

    # TaskType.CAUSAL_IMAGE_MODELING: MODEL_FOR_CAUSAL_IMAGE_MODELING_MAPPING,
    # TaskType.PRETRAINING: MODEL_FOR_PRETRAINING_MAPPING,
    # TaskType.LANGUAGE_MODELING: MODEL_WITH_LM_HEAD_MAPPING,
    # TaskType.MULTIPLE_CHOICE: MODEL_FOR_MULTIPLE_CHOICE_MAPPING,
    # TaskType.NEXT_SENTENCE_PREDICTION: MODEL_FOR_NEXT_SENTENCE_PREDICTION_MAPPING,
    # TaskType.IMAGE: MODEL_FOR_IMAGE_MAPPING,
    # TaskType.UNIVERSAL_SEGMENTATION: MODEL_FOR_UNIVERSAL_SEGMENTATION_MAPPING,
    # TaskType.INSTANCE_SEGMENTATION: MODEL_FOR_INSTANCE_SEGMENTATION_MAPPING,
    # TaskType.SEMANTIC_SEGMENTATION: MODEL_FOR_SEMANTIC_SEGMENTATION_MAPPING,

}


def get_model_pipeline_task(model):
    config = model.config
    model_class = get_model_class_from_config(config)
    for task, mapping in MAPPING_TO_TASK.items():
        if model_class in mapping.values():
            return task
    return TaskType.NONE


def get_model_pipeline_task_from_path(path):
    model_class = get_model_class_from_path(path)
    for task, mapping in MAPPING_TO_TASK.items():
        if model_class in mapping.values():
            return task
    return TaskType.NONE


def get_model_class_from_path(path):
    print("Get model class from path ", path)
    config = AutoConfig.from_pretrained(path)
    return get_model_class_from_config(config)


def get_model_class_from_config(config):
    model_class_name = config_class_to_model_type(type(config).__name__)
    possible_classes = []
    mappings = MODEL_CLASS_MAPPINGS + DEFAULT_MODEL_CLASS_MAPPING
    for m in mappings:
        clas_from_mapping = m.get(type(config), None)
        if clas_from_mapping:
            possible_classes.append(clas_from_mapping)

    architectures = config.architectures

    print("Get class from config", model_class_name,
          "\npossible classes:", possible_classes,
          "\narchitectures", architectures)
    first_arch = architectures[0]
    for pc in possible_classes:
        if first_arch in pc.__name__:
            print("Selected model class:", pc, )
            return pc
    print(f"Didn't find the class for architecture {first_arch}")
    if len(possible_classes) > 0:
        print(f"Returning first possible class {possible_classes[0]}")
        return possible_classes[0]
    return None
