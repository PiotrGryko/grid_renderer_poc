import os

from torch import nn
from transformers import AutoTokenizer, AutoImageProcessor, AutoFeatureExtractor

from app.ai.pipeline_task import PipelineTask
from app.ai.task_mapping import get_model_class_from_path


class LayerMeta:
    def __init__(self, module, name, layer_type, shape=None, probability=None):
        self.module = module
        self.name = name
        self.layer_type = layer_type
        self.shape = shape
        self.probability = probability
        self.components = []
        self.n_effects = None

    def add_component(self, component):
        self.components.append(component)

    def update_names(self, parent_name=None):
        if parent_name is not None:
            self.name = parent_name + "." + self.name
        for c in self.components:
            c.update_names(self.name)

    def hook(self, module, input, output):
        # print("update activations", self.name, type(output))
        self.n_effects.show_quad_raw(self.name)

    def register_hooks(self, n_effects):
        self.n_effects = n_effects
        self.module.register_forward_hook(self.hook)
        for c in self.components:
            c.register_hooks(n_effects)

    def __repr__(self, level=0):
        indent = "  " * level
        repr_str = (f"{indent}LayerMeta(name={self.name}, layer_type={self.layer_type}, "
                    f"shape={self.shape}, probability={self.probability},\n"
                    f"{indent}components=[\n")
        for component in self.components:
            repr_str += component.__repr__(level + 1) + ",\n"
        repr_str += f"{indent}])"
        return repr_str


class ModelParser:
    def __init__(self, n_effects):
        self.n_effects = n_effects
        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.feature_extractor = None

        self.parsed_model = None
        self.current_model_name = None
        self.hooked_model_name = None
        self.last_result = None
        self.pipeline_task = PipelineTask()

    def clear(self):
        self.model = None
        self.tokenizer = None
        self.feature_extractor = None
        self.image_processor = None
        self.parsed_model = None
        self.current_model_name = None
        self.hooked_model_name = None
        self.pipeline_task.clear()

    def _register_hooks(self):
        print("register hooks")
        if self.hooked_model_name == self.parsed_model.name:
            print("register hooks skipped")
            return
        self.parsed_model.register_hooks(self.n_effects)
        self.hooked_model_name = self.parsed_model.name

    def _parse_module(self, module, name):
        if isinstance(module, nn.Embedding):
            layer_meta = LayerMeta(module, name, module.__class__.__name__,
                                   [module.num_embeddings, module.embedding_dim])
        elif isinstance(module, nn.Linear):
            layer_meta = LayerMeta(module, name, module.__class__.__name__, [module.in_features, module.out_features])
        elif isinstance(module, nn.LayerNorm):
            layer_meta = LayerMeta(module, name, module.__class__.__name__, [module.normalized_shape[0], 1])
        elif isinstance(module, nn.Dropout):
            layer_meta = LayerMeta(module, name, module.__class__.__name__, [1, 1], probability=module.p)
        elif hasattr(module, 'children') and list(module.children()):
            layer_meta = LayerMeta(module, name, module.__class__.__name__, )
            for i, (child_name, child_module) in enumerate(module.named_children()):
                child_parsed = self._parse_module(child_module, child_name)
                layer_meta.add_component(child_parsed)
        else:
            layer_meta = LayerMeta(module, name, module.__class__.__name__, [1, 1])
        return layer_meta

    def run_model(self, input_text=None, images=None, context_message=None):
        self._register_hooks()
        self.pipeline_task.run_pipeline(input_text, images, context_message)

    def get_run_result(self):
        return self.pipeline_task.pool_forward_pass_result()

    def named_parameters(self):
        if self.model is None:
            return []
        else:
            return list(self.model.named_parameters())

    def set_model(self, model):
        self.model = model

    def set_tokenizer(self, tokenizer):
        self.tokenizer = tokenizer

    def set_image_processor(self, image_processor):
        self.image_processor = image_processor

    def set_feature_extractor(self, feature_extractor):
        self.feature_extractor = feature_extractor

    def load_model_from_path(self, path, task=None):
        model = None
        # model_class = None
        # if task is None:
        #     task = get_model_pipeline_task_from_path(path)
        #
        # if task is not None:
        #     model_class = TASK_TO_CLASS.get(task, None)

        # config = AutoConfig.from_pretrained(path)
        # print(config)
        # print("config:")
       # print(config.replace_list_option_in_docstrings())
        model_class = get_model_class_from_path(path)
        #model_class = Speech2TextModel
        print("loading model",model_class)
        if model_class is not None:
            model = model_class.from_pretrained(path, local_files_only=True)
            print(f"Successfully loaded model for task: {task}", model_class)
        # else:
        #     for task, model_class in TASK_TO_CLASS.items():
        #         try:
        #             # print(f"Trying to load model for task: {task}")
        #             model = model_class.from_pretrained(path, local_files_only=True)
        #             print(f"Successfully loaded model for task: {task}", model_class)
        #             break
        #         except Exception as e:
        #             pass
                    # print(f"Failed to load model for task: {task} with error: {e}")
        self.model = model

    def load_tokenizer_from_path(self, path):
        try:
            print(f"Trying to load tokenizer")
            self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True, config=self.model.config)
            print(f"Successfully loaded tokenizer")
        except Exception as e:
            print(f"Failed to load tokenizer with error: {e}")
            self.tokenizer = None

    def load_image_processor_from_path(self, path):
        try:
            print(f"Trying to load image processor")
            self.image_processor = AutoImageProcessor.from_pretrained(path, local_files_only=True)
            print(f"Successfully loaded image processor")
        except Exception as e:
            print(f"Failed to load image processor with error: {e}")
            self.image_processor = None

    def load_feature_extractor_from_path(self, path):
        try:
            print(f"Trying to load feature extractor")
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(path, local_files_only=True)
            print(f"Successfully loaded feature extractor")
        except Exception as e:
            print(f"Failed to load feature extractor with error: {e}")
            self.feature_extractor = None

    def parse_loaded_model(self):
        self.pipeline_task.load_from_model(self.model, self.tokenizer, self.image_processor, self.feature_extractor)
        _, module = list(self.model.named_modules())[0]
        name = os.path.basename(self.model.name_or_path)
        parsed_model = self._parse_module(module, name)
        parsed_model.update_names()
        self.parsed_model = parsed_model
        self.current_model_name = self.parsed_model.name

    # def load_transformers_model(self, model, tokenizer):
    #     self.model = model
    #     self.tokenizer = tokenizer
    #     self.pipeline_task.load_from_model(self.model, self.tokenizer)
    #     _, module = list(self.model.named_modules())[0]
    #     name = os.path.basename(self.model.name_or_path)
    #     parsed_model = self._parse_module(module, name)
    #     parsed_model.update_names()
    #
    #     self.parsed_model = parsed_model
    #     self.current_model_name = self.parsed_model.name
