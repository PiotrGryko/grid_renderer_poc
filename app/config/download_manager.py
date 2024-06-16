import threading
from huggingface_hub import hf_hub_download, HfApi

from transformers import (
    AutoModelForCausalLM, AutoModelForSequenceClassification, AutoModelForImageClassification,
    AutoModelForTokenClassification,
    AutoModelForQuestionAnswering, AutoModelForSeq2SeqLM, AutoModelForMaskedLM, AutoModelForVision2Seq,
    AutoModelForImageSegmentation,
    AutoModelForSpeechSeq2Seq, AutoModelForAudioClassification, AutoModelForMultipleChoice,
    AutoModelForNextSentencePrediction,
    AutoModelForVideoClassification, AutoModelForDocumentQuestionAnswering, AutoModelForTableQuestionAnswering,
    BlipForConditionalGeneration, Speech2TextForConditionalGeneration, VisionEncoderDecoderModel, AutoTokenizer
)


class DownloadManager:
    def __init__(self):
        self.download_threads = {}
        self.download_status = {}
        self.api = HfApi()

        self.MODEL_CLASS_MAPPING = {
            "text-generation": AutoModelForCausalLM,
            "text-classification": AutoModelForSequenceClassification,
            "image-classification": AutoModelForImageClassification,
            "token-classification": AutoModelForTokenClassification,
            "question-answering": AutoModelForQuestionAnswering,
            "translation": AutoModelForSeq2SeqLM,
            "summarization": AutoModelForSeq2SeqLM,
            "fill-mask": AutoModelForMaskedLM,
            "vision-to-text": AutoModelForVision2Seq,
            "image-segmentation": AutoModelForImageSegmentation,
            "speech-seq2seq": AutoModelForSpeechSeq2Seq,
            "audio-classification": AutoModelForAudioClassification,
            "multiple-choice": AutoModelForMultipleChoice,
            "next-sentence-prediction": AutoModelForNextSentencePrediction,
            "video-classification": AutoModelForVideoClassification,
            "document-question-answering": AutoModelForDocumentQuestionAnswering,
            "table-question-answering": AutoModelForTableQuestionAnswering,
            "text-to-image": BlipForConditionalGeneration,
            "image-to-text": VisionEncoderDecoderModel,
            "image-to-speech": Speech2TextForConditionalGeneration
        }

    def get_model_class(self, model_id):
        model_info = self.api.model_info(model_id)
        task = model_info.pipeline_tag
        print(f"Model ID: {model_id}")
        print(f"Detected Task: {task}")
        return self.MODEL_CLASS_MAPPING.get(task, AutoModelForCausalLM)

    def download_model(self, model_id, path):
        if model_id in self.download_threads:
            print(f"Download for {model_id} is already in progress.")
            return

        self.download_status[model_id] = "Downloading"
        thread = threading.Thread(target=self._download_model_thread, args=(model_id, path))
        self.download_threads[model_id] = thread
        thread.start()

    def _download_model_thread(self, model_id, path):
        print("download model thread ", model_id, path)
        try:
            model_class = self.get_model_class(model_id)
            model = model_class.from_pretrained(model_id, local_files_only=False)
            tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=False)
            model.save_pretrained(path)
            tokenizer.save_pretrained(path)
            self.download_status[model_id] = "Completed"
        except Exception as e:
            self.download_status[model_id] = f"Error: {str(e)}"
        finally:
            del self.download_threads[model_id]

    def get_download_status(self, model_id):
        return self.download_status.get(model_id, "Not started")

    def get_all_download_statuses(self):
        return self.download_status

    def cancel_download(self, model_id):
        # Implement cancellation logic if needed
        pass
