import threading

from huggingface_hub import HfApi
from transformers import (
    AutoTokenizer, AutoImageProcessor, AutoFeatureExtractor, AutoModel
)

from app.ai.task_mapping import get_model_class_from_path


class DownloadStatus:
    def __init__(self, message, completed, model_directory=None):
        self.message = message
        self.completed = completed
        self.model_directory = model_directory


class DownloadManager:
    def __init__(self):
        self.download_threads = {}
        self.download_status = {}
        self.api = HfApi()

    # def get_model_class(self, model_id):
    #     model_info = self.api.model_info(model_id)
    #     task = model_info.pipeline_tag
    #     print("Get class from task", task)
    #
    #     task_class = TASK_TO_CLASS.get(task, AutoModelForCausalLM)
    #     print(f"Model ID: {model_id}")
    #     print(f"Detected Task: {task}")
    #     print(f"Task class: {task_class}")
    #     return task_class

    def download_model(self, model_info, path):
        model_id = model_info.modelId
        if model_id in self.download_threads:
            print(f"Download for {model_id} is already in progress.")
            return

        self.download_status[model_id] = DownloadStatus(
            "Downloading",
            False
        )
        thread = threading.Thread(target=self._download_model_thread, args=(model_info, path))
        self.download_threads[model_id] = thread
        thread.start()

    def _download_model_thread(self, model_info, path):
        model_id = model_info.modelId
        library_name = model_info.library_name
        model = None
        print("download model thread ", model_id, path, "library:", library_name)
        try:
            if library_name == "transformers":
                try:
                    #model_class = self.get_model_class(model_id)
                    model_class = get_model_class_from_path(model_id)
                    #model_class = AutoModel
                    print("Downloading model", model_class)
                    model = model_class.from_pretrained(model_id, local_files_only=False)
                    print("Saving model")
                    model.save_pretrained(path)
                except Exception as e:
                    raise e
                try:
                    print("Downloading tokenizer", model_class)
                    tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=False)
                    print("Saving tokenizer")
                    tokenizer.save_pretrained(path)
                    print("Saved tokenizer")
                except Exception as e:
                    print("tokenizer Exception", e)

                try:
                    print("Downloading image processor", model_class)
                    image_processor = AutoImageProcessor.from_pretrained(model_id, local_files_only=False)
                    print("Saving image processor")
                    image_processor.save_pretrained(path)
                    print("Saved image processor")
                except Exception as e:
                    print("image processor Exception", e)

                try:
                    print("Downloading feature extractor", model_class)
                    image_processor = AutoFeatureExtractor.from_pretrained(model_id, local_files_only=False)
                    print("Saving feature extractor")
                    image_processor.save_pretrained(path)
                    print("Saved feature extractor")
                except Exception as e:
                    print("feature extractor Exception", e)

                print("Completed")
                self.download_status[model_id] = DownloadStatus(
                    "Completed",
                    True,
                    model_directory=path
                )
            else:
                raise f"Unsupported model library {library_name}"
        except Exception as e:
            print("Exception:", e)
            self.download_status[model_id] = DownloadStatus(
                f"Error: {str(e)}",
                False
            )
        finally:
            del self.download_threads[model_id]

    def get_download_status(self, model_id):
        return self.download_status.get(model_id, DownloadStatus(
            "Not started",
            False
        ))

    def get_all_download_statuses(self):
        return self.download_status

    def cancel_download(self, model_id):
        # Implement cancellation logic if needed
        pass
