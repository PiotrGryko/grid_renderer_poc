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
    TEXT_ENCODING = "text-encoding"
    TIME_SERIES_CLASSIFICATION = "time-series-classification"
    TIME_SERIES_REGRESSION = "time-series-regression"
    KEYPOINT_DETECTION = "keypoint-detection"
    BACKBONE = "backbone"
    AUDIO_XVECTOR = "audio-xvector"
    AUDIO_FRAME_CLASSIFICATION = "audio-frame-classification"
    CTC = "ctc"

    def get_parameters(self):
        return TASK_PIPELINE_PARAMETERS[self]

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

    def has_context_parameter(self):
        return self.is_question_answering()

    def has_audio_input(self):
        return self.is_audio_classification() or self.is_automatic_speech_recognition()


TASK_PIPELINE_PARAMETERS_DESCRIPTION = {
    TaskType.AUDIO_CLASSIFICATION: '''inputs (np.ndarray or bytes or str or dict) — The inputs is either :
str that is the filename of the audio file, the file will be read at the correct sampling rate to get the waveform using ffmpeg. This requires ffmpeg to be installed on the system.
bytes it is supposed to be the content of an audio file and is interpreted by ffmpeg in the same way.
(np.ndarray of shape (n, ) of type np.float32 or np.float64) Raw audio at the correct sampling rate (no further check will be done)
dict form can be used to pass raw audio sampled at arbitrary sampling_rate and let this pipeline do the resampling. The dict must be either be in the format {"sampling_rate": int, "raw": np.array}, or {"sampling_rate": int, "array": np.array}, where the key "raw" or "array" is used to denote the raw audio waveform.
top_k (int, optional, defaults to None) — The number of top labels that will be returned by the pipeline. If the provided number is None or higher than the number of labels available in the model configuration, it will default to the number of labels.''',
    TaskType.AUTOMATIC_SPEECH_RECOGNITION: '''inputs (np.ndarray or bytes or str or dict) — The inputs is either :
str that is either the filename of a local audio file, or a public URL address to download the audio file. The file will be read at the correct sampling rate to get the waveform using ffmpeg. This requires ffmpeg to be installed on the system.
bytes it is supposed to be the content of an audio file and is interpreted by ffmpeg in the same way.
(np.ndarray of shape (n, ) of type np.float32 or np.float64) Raw audio at the correct sampling rate (no further check will be done)
dict form can be used to pass raw audio sampled at arbitrary sampling_rate and let this pipeline do the resampling. The dict must be in the format {"sampling_rate": int, "raw": np.array} with optionally a "stride": (left: int, right: int) than can ask the pipeline to treat the first left samples and last right samples to be ignored in decoding (but used at inference to provide more context to the model). Only use stride with CTC models.
return_timestamps (optional, str or bool) — Only available for pure CTC models (Wav2Vec2, HuBERT, etc) and the Whisper model. Not available for other sequence-to-sequence models.
For CTC models, timestamps can take one of two formats:

"char": the pipeline will return timestamps along the text for every character in the text. For instance, if you get [{"text": "h", "timestamp": (0.5, 0.6)}, {"text": "i", "timestamp": (0.7, 0.9)}], then it means the model predicts that the letter “h” was spoken after 0.5 and before 0.6 seconds.
"word": the pipeline will return timestamps along the text for every word in the text. For instance, if you get [{"text": "hi ", "timestamp": (0.5, 0.9)}, {"text": "there", "timestamp": (1.0, 1.5)}], then it means the model predicts that the word “hi” was spoken after 0.5 and before 0.9 seconds.
For the Whisper model, timestamps can take one of two formats:

"word": same as above for word-level CTC timestamps. Word-level timestamps are predicted through the dynamic-time warping (DTW) algorithm, an approximation to word-level timestamps by inspecting the cross-attention weights.
True: the pipeline will return timestamps along the text for segments of words in the text. For instance, if you get [{"text": " Hi there!", "timestamp": (0.5, 1.5)}], then it means the model predicts that the segment “Hi there!” was spoken after 0.5 and before 1.5 seconds. Note that a segment of text refers to a sequence of one or more words, rather than individual words as with word-level timestamps.
generate_kwargs (dict, optional) — The dictionary of ad-hoc parametrization of generate_config to be used for the generation call. For a complete overview of generate, check the following guide.
max_new_tokens (int, optional) — The maximum numbers of tokens to generate, ignoring the number of tokens in the prompt.''',
    TaskType.TEXT_TO_AUDIO: '''text_inputs (str or List[str]) — The text(s) to generate.
forward_params (dict, optional) — Parameters passed to the model generation/forward method. forward_params are always passed to the underlying model.
generate_kwargs (dict, optional) — The dictionary of ad-hoc parametrization of generate_config to be used for the generation call. For a complete overview of generate, check the following guide. generate_kwargs are only passed to the underlying model if the latter is a generative model.''',
    TaskType.ZERO_SHOT_AUDIO_CLASSIFICATION: '''audios (str, List[str], np.array or List[np.array]) — The pipeline handles three types of inputs:
A string containing a http link pointing to an audio
A string containing a local path to an audio
An audio loaded in numpy
candidate_labels (List[str]) — The candidate labels for this audio
hypothesis_template (str, optional, defaults to "This is a sound of {}") — The sentence used in cunjunction with candidate_labels to attempt the audio classification by replacing the placeholder with the candidate_labels. Then likelihood is estimated by using logits_per_audio''',
    TaskType.DEPTH_ESTIMATION: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing a http link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images, which must then be passed as a string. Images in a batch must all be in the same format: all as http links, all as local paths, or all as PIL images.

timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.IMAGE_CLASSIFICATION: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing a http link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images, which must then be passed as a string. Images in a batch must all be in the same format: all as http links, all as local paths, or all as PIL images.

function_to_apply (str, optional, defaults to "default") — The function to apply to the model outputs in order to retrieve the scores. Accepts four different values:
If this argument is not specified, then it will apply the following functions according to the number of labels:

If the model has a single label, will apply the sigmoid function on the output.
If the model has several labels, will apply the softmax function on the output.
Possible values are:

"sigmoid": Applies the sigmoid function on the output.
"softmax": Applies the softmax function on the output.
"none": Does not apply any function on the output.
top_k (int, optional, defaults to 5) — The number of top labels that will be returned by the pipeline. If the provided number is higher than the number of labels available in the model configuration, it will default to the number of labels.
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.IMAGE_SEGMENTATION: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing an HTTP(S) link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images. Images in a batch must all be in the same format: all as HTTP(S) links, all as local paths, or all as PIL images.

subtask (str, optional) — Segmentation task to be performed, choose [semantic, instance and panoptic] depending on model capabilities. If not set, the pipeline will attempt tp resolve in the following order: panoptic, instance, semantic.
threshold (float, optional, defaults to 0.9) — Probability threshold to filter out predicted masks.
mask_threshold (float, optional, defaults to 0.5) — Threshold to use when turning the predicted masks into binary values.
overlap_mask_area_threshold (float, optional, defaults to 0.5) — Mask overlap threshold to eliminate small, disconnected segments.
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.IMAGE_TO_IMAGE: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing a http link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images, which must then be passed as a string. Images in a batch must all be in the same format: all as http links, all as local paths, or all as PIL images.

timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is used and the call may block forever.""",

    TaskType.OBJECT_DETECTION: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing an HTTP(S) link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images. Images in a batch must all be in the same format: all as HTTP(S) links, all as local paths, or all as PIL images.

threshold (float, optional, defaults to 0.5) — The probability necessary to make a prediction.
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.VIDEO_CLASSIFICATION: """videos (str, List[str]) — The pipeline handles three types of videos:
A string containing a http link pointing to a video
A string containing a local path to a video
The pipeline accepts either a single video or a batch of videos, which must then be passed as a string. Videos in a batch must all be in the same format: all as http links or all as local paths.

top_k (int, optional, defaults to 5) — The number of top labels that will be returned by the pipeline. If the provided number is higher than the number of labels available in the model configuration, it will default to the number of labels.
num_frames (int, optional, defaults to self.model.config.num_frames) — The number of frames sampled from the video to run the classification on. If not provided, will default to the number of frames specified in the model configuration.
frame_sampling_rate (int, optional, defaults to 1) — The sampling rate used to select frames from the video. If not provided, will default to 1, i.e. every frame will be used.""",

    TaskType.ZERO_SHOT_IMAGE_CLASSIFICATION: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing a http link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
candidate_labels (List[str]) — The candidate labels for this image
hypothesis_template (str, optional, defaults to "This is a photo of {}") — The sentence used in cunjunction with candidate_labels to attempt the image classification by replacing the placeholder with the candidate_labels. Then likelihood is estimated by using logits_per_image
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.ZERO_SHOT_OBJECT_DETECTION: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing a http link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
candidate_labels (List[str]) — The candidate labels for this image
hypothesis_template (str, optional, defaults to "This is a photo of {}") — The sentence used in cunjunction with candidate_labels to attempt the image classification by replacing the placeholder with the candidate_labels. Then likelihood is estimated by using logits_per_image
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.CONVERSATIONAL: """conversations (a Conversation or a list of Conversation) — Conversation to generate responses for. Inputs can also be passed as a list of dictionaries with role and content keys - in this case, they will be converted to Conversation objects automatically. Multiple conversations in either format may be passed as a list.
clean_up_tokenization_spaces (bool, optional, defaults to True) — Whether or not to clean up the potential extra spaces in the text output. generate_kwargs — Additional keyword arguments to pass along to the generate method of the model (see the generate method corresponding to your framework here).""",

    TaskType.FILL_MASK: """args (str or List[str]) — One or several texts (or one list of prompts) with masked tokens.
    targets (str or List[str], optional) — When passed, the model will limit the scores to the passed targets instead of looking up in the whole vocab. If the provided targets are not in the model vocab, they will be tokenized and the first resulting token will be used (with a warning, and that might be slower).
    top_k (int, optional) — When passed, overrides the number of predictions to return.""",

    TaskType.QUESTION_ANSWERING: """args (SquadExample or a list of SquadExample) — One or several SquadExample containing the question and context.
X (SquadExample or a list of SquadExample, optional) — One or several SquadExample containing the question and context (will be treated the same way as if passed as the first positional argument).
data (SquadExample or a list of SquadExample, optional) — One or several SquadExample containing the question and context (will be treated the same way as if passed as the first positional argument).
question (str or List[str]) — One or several question(s) (must be used in conjunction with the context argument).
context (str or List[str]) — One or several context(s) associated with the question(s) (must be used in conjunction with the question argument).
topk (int, optional, defaults to 1) — The number of answers to return (will be chosen by order of likelihood). Note that we return less than topk answers if there are not enough options available within the context.
doc_stride (int, optional, defaults to 128) — If the context is too long to fit with the question for the model, it will be split in several chunks with some overlap. This argument controls the size of that overlap.
max_answer_len (int, optional, defaults to 15) — The maximum length of predicted answers (e.g., only answers with a shorter length are considered).
max_seq_len (int, optional, defaults to 384) — The maximum length of the total sentence (context + question) in tokens of each chunk passed to the model. The context will be split in several chunks (using doc_stride as overlap) if needed.
max_question_len (int, optional, defaults to 64) — The maximum length of the question after tokenization. It will be truncated if needed.
handle_impossible_answer (bool, optional, defaults to False) — Whether or not we accept impossible as an answer.
align_to_words (bool, optional, defaults to True) — Attempts to align the answer to real words. Improves quality on space separated langages. Might hurt on non-space-separated languages (like Japanese or Chinese)""",

    TaskType.SUMMARIZATION: """documents (str or List[str]) — One or several articles (or one list of articles) to summarize.
return_text (bool, optional, defaults to True) — Whether or not to include the decoded texts in the outputs
return_tensors (bool, optional, defaults to False) — Whether or not to include the tensors of predictions (as token indices) in the outputs.
clean_up_tokenization_spaces (bool, optional, defaults to False) — Whether or not to clean up the potential extra spaces in the text output. generate_kwargs — Additional keyword arguments to pass along to the generate method of the model (see the generate method corresponding to your framework here).""",

    TaskType.TABLE_QUESTION_ANSWERING: '''table (pd.DataFrame or Dict) — Pandas DataFrame or dictionary that will be converted to a DataFrame containing all the table values. See above for an example of dictionary.
query (str or List[str]) — Query or list of queries that will be sent to the model alongside the table.
sequential (bool, optional, defaults to False) — Whether to do inference sequentially or as a batch. Batching is faster, but models like SQA require the inference to be done sequentially to extract relations within sequences, given their conversational nature.
padding (bool, str or PaddingStrategy, optional, defaults to False) — Activates and controls padding. Accepts the following values:
True or 'longest': Pad to the longest sequence in the batch (or no padding if only a single sequence if provided).
'max_length': Pad to a maximum length specified with the argument max_length or to the maximum acceptable input length for the model if that argument is not provided.
False or 'do_not_pad' (default): No padding (i.e., can output a batch with sequences of different lengths).
truncation (bool, str or TapasTruncationStrategy, optional, defaults to False) — Activates and controls truncation. Accepts the following values:
True or 'drop_rows_to_fit': Truncate to a maximum length specified with the argument max_length or to the maximum acceptable input length for the model if that argument is not provided. This will truncate row by row, removing rows from the table.
False or 'do_not_truncate' (default): No truncation (i.e., can output batch with sequence lengths greater than the model maximum admissible input size).''',

    TaskType.TEXT_CLASSIFICATION: """inputs (str or List[str] or Dict[str], or List[Dict[str]]) — One or several texts to classify. In order to use text pairs for your classification, you can send a dictionary containing {"text", "text_pair"} keys, or a list of those.
top_k (int, optional, defaults to 1) — How many results to return.
function_to_apply (str, optional, defaults to "default") — The function to apply to the model outputs in order to retrieve the scores. Accepts four different values:
If this argument is not specified, then it will apply the following functions according to the number of labels:

If the model has a single label, will apply the sigmoid function on the output.
If the model has several labels, will apply the softmax function on the output.
Possible values are:

"sigmoid": Applies the sigmoid function on the output.
"softmax": Applies the softmax function on the output.
"none": Does not apply any function on the output.""",

    TaskType.TEXT_GENERATION: """text_inputs (str, List[str], List[Dict[str, str]], or List[List[Dict[str, str]]]) — One or several prompts (or one list of prompts) to complete. If strings or a list of string are passed, this pipeline will continue each prompt. Alternatively, a “chat”, in the form of a list of dicts with “role” and “content” keys, can be passed, or a list of such chats. When chats are passed, the model’s chat template will be used to format them before passing them to the model.
return_tensors (bool, optional, defaults to False) — Whether or not to return the tensors of predictions (as token indices) in the outputs. If set to True, the decoded text is not returned.
return_text (bool, optional, defaults to True) — Whether or not to return the decoded texts in the outputs.
return_full_text (bool, optional, defaults to True) — If set to False only added text is returned, otherwise the full text is returned. Only meaningful if return_text is set to True.
clean_up_tokenization_spaces (bool, optional, defaults to True) — Whether or not to clean up the potential extra spaces in the text output.
prefix (str, optional) — Prefix added to prompt.
handle_long_generation (str, optional) — By default, this pipelines does not handle long generation (ones that exceed in one form or the other the model maximum length). There is no perfect way to adress this (more info :https://github.com/huggingface/transformers/issues/14033#issuecomment-948385227). This provides common strategies to work around that problem depending on your use case.
None : default strategy where nothing in particular happens
"hole": Truncates left of input, and leaves a gap wide enough to let generation happen (might truncate a lot of the prompt and not suitable when generation exceed the model capacity)
generate_kwargs (dict, optional) — Additional keyword arguments to pass along to the generate method of the model (see the generate method corresponding to your framework here).""",

    TaskType.TEXT2TEXT_GENERATION: """args (str or List[str]) — Input text for the encoder.
return_tensors (bool, optional, defaults to False) — Whether or not to include the tensors of predictions (as token indices) in the outputs.
return_text (bool, optional, defaults to True) — Whether or not to include the decoded texts in the outputs.
clean_up_tokenization_spaces (bool, optional, defaults to False) — Whether or not to clean up the potential extra spaces in the text output.
truncation (TruncationStrategy, optional, defaults to TruncationStrategy.DO_NOT_TRUNCATE) — The truncation strategy for the tokenization within the pipeline. TruncationStrategy.DO_NOT_TRUNCATE (default) will never truncate, but it is sometimes desirable to truncate the input to fit the model’s max_length instead of throwing an error down the line. generate_kwargs — Additional keyword arguments to pass along to the generate method of the model (see the generate method corresponding to your framework here).""",

    TaskType.TOKEN_CLASSIFICATION: """inputs (str or List[str]) — One or several texts (or one list of texts) for token classification.""",

    TaskType.TRANSLATION: """args (str or List[str]) — Texts to be translated.
return_tensors (bool, optional, defaults to False) — Whether or not to include the tensors of predictions (as token indices) in the outputs.
return_text (bool, optional, defaults to True) — Whether or not to include the decoded texts in the outputs.
clean_up_tokenization_spaces (bool, optional, defaults to False) — Whether or not to clean up the potential extra spaces in the text output.
src_lang (str, optional) — The language of the input. Might be required for multilingual models. Will not have any effect for single pair translation models
tgt_lang (str, optional) — The language of the desired output. Might be required for multilingual models. Will not have any effect for single pair translation models generate_kwargs — Additional keyword arguments to pass along to the generate method of the model (see the generate method corresponding to your framework here).

""",

    TaskType.ZERO_SHOT_CLASSIFICATION: """sequences (str or List[str]) — The sequence(s) to classify, will be truncated if the model input is too large.
candidate_labels (str or List[str]) — The set of possible class labels to classify each sequence into. Can be a single label, a string of comma-separated labels, or a list of labels.
hypothesis_template (str, optional, defaults to "This example is {}.") — The template used to turn each label into an NLI-style hypothesis. This template must include a {} or similar syntax for the candidate label to be inserted into the template. For example, the default template is "This example is {}." With the candidate label "sports", this would be fed into the model like "<cls> sequence to classify <sep> This example is sports . <sep>". The default template works well in many cases, but it may be worthwhile to experiment with different templates depending on the task setting.
multi_label (bool, optional, defaults to False) — Whether or not multiple candidate labels can be true. If False, the scores are normalized such that the sum of the label likelihoods for each sequence is 1. If True, the labels are considered independent and probabilities are normalized for each candidate by doing a softmax of the entailment score vs. the contradiction score.""",

    TaskType.DOCUMENT_QUESTION_ANSWERING: """image (str or Image) — The pipeline handles three types of images:
A string containing a http link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images. If given a single image, it can be broadcasted to multiple questions.

question (str) — A question to ask of the document.
word_boxes (List[str, Tuple[float, float, float, float]], optional) — A list of words and bounding boxes (normalized 0->1000). If you provide this optional input, then the pipeline will use these words and boxes instead of running OCR on the image to derive them for models that need them (e.g. LayoutLM). This allows you to reuse OCR’d results across many invocations of the pipeline without having to re-run it each time.
top_k (int, optional, defaults to 1) — The number of answers to return (will be chosen by order of likelihood). Note that we return less than top_k answers if there are not enough options available within the context.
doc_stride (int, optional, defaults to 128) — If the words in the document are too long to fit with the question for the model, it will be split in several chunks with some overlap. This argument controls the size of that overlap.
max_answer_len (int, optional, defaults to 15) — The maximum length of predicted answers (e.g., only answers with a shorter length are considered).
max_seq_len (int, optional, defaults to 384) — The maximum length of the total sentence (context + question) in tokens of each chunk passed to the model. The context will be split in several chunks (using doc_stride as overlap) if needed.
max_question_len (int, optional, defaults to 64) — The maximum length of the question after tokenization. It will be truncated if needed.
handle_impossible_answer (bool, optional, defaults to False) — Whether or not we accept impossible as an answer.
lang (str, optional) — Language to use while running OCR. Defaults to english.
tesseract_config (str, optional) — Additional flags to pass to tesseract while running OCR.
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.FEATURE_EXTRACTION: """args (str or List[str]) — One or several texts (or one list of texts) to get the features of.""",
    TaskType.IMAGE_FEATURE_EXTRACTION: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing a http link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images, which must then be passed as a string. Images in a batch must all be in the same format: all as http links, all as local paths, or all as PIL images.

timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is used and the call may block forever.""",

    TaskType.IMAGE_TO_TEXT: """images (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
A string containing a HTTP(s) link pointing to an image
A string containing a local path to an image
An image loaded in PIL directly
The pipeline accepts either a single image or a batch of images.

max_new_tokens (int, optional) — The amount of maximum tokens to generate. By default it will use generate default.
generate_kwargs (Dict, optional) — Pass it to send all of these arguments directly to generate allowing full control of this function.
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.MASK_GENERATION: """inputs (np.ndarray or bytes or str or dict) — Image or list of images.
mask_threshold (float, optional, defaults to 0.0) — Threshold to use when turning the predicted masks into binary values.
pred_iou_thresh (float, optional, defaults to 0.88) — A filtering threshold in [0,1] applied on the model’s predicted mask quality.
stability_score_thresh (float, optional, defaults to 0.95) — A filtering threshold in [0,1], using the stability of the mask under changes to the cutoff used to binarize the model’s mask predictions.
stability_score_offset (int, optional, defaults to 1) — The amount to shift the cutoff when calculated the stability score.
crops_nms_thresh (float, optional, defaults to 0.7) — The box IoU cutoff used by non-maximal suppression to filter duplicate masks.
crops_n_layers (int, optional, defaults to 0) — If crops_n_layers>0, mask prediction will be run again on crops of the image. Sets the number of layers to run, where each layer has 2**i_layer number of image crops.
crop_overlap_ratio (float, optional, defaults to 512 / 1500) — Sets the degree to which crops overlap. In the first crop layer, crops will overlap by this fraction of the image length. Later layers with more crops scale down this overlap.
crop_n_points_downscale_factor (int, optional, defaults to 1) — The number of points-per-side sampled in layer n is scaled down by crop_n_points_downscale_factor**n.
timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever.""",

    TaskType.VISUAL_QUESTION_ANSWERING: """image (str, List[str], Image or List[Image]) — The pipeline handles three types of images:
    A string containing a http link pointing to an image
    A string containing a local path to an image
    An image loaded in PIL directly
    The pipeline accepts either a single image or a batch of images. If given a single image, it can be broadcasted to multiple questions.

    question (str, List[str]) — The question(s) asked. If given a single question, it can be broadcasted to multiple images.
    top_k (int, optional, defaults to 5) — The number of top labels that will be returned by the pipeline. If the provided number is higher than the number of labels available in the model configuration, it will default to the number of labels.
    timeout (float, optional, defaults to None) — The maximum time in seconds to wait for fetching images from the web. If None, no timeout is set and the call may block forever."""

}

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
