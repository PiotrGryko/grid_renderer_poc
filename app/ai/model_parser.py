import os

import numpy as np
import torch
from torch import nn
from transformers import AutoTokenizer, AutoImageProcessor, AutoFeatureExtractor

from app.ai.pipeline_task import PipelineTask
from app.ai.task_mapping import get_model_class_from_path


class ModuleMeta:
    def __init__(self, module, name, is_parameter=False):
        self.module = module
        self.name = name
        self.components = []
        self.n_effects = None
        self.is_parameter = is_parameter

    def get_data(self):
        if isinstance(self.module, nn.Parameter):
            return self.module.detach().numpy()
        elif self.is_parameter:
            return np.ones([2, 2])
        else:
            return None

    def add_component(self, component):
        self.components.append(component)

    def hook(self, module, input, output):
        self.flash(self.n_effects)

    def flash(self, n_effects):
        if self.is_parameter:
            n_effects.show_quad(self.name)
        else:
            for c in self.components:
                c.flash(n_effects)

    def register_hooks(self, n_effects):
        if isinstance(self.module, nn.Parameter):
            return
        self.n_effects = n_effects
        self.module.register_forward_hook(self.hook)
        for c in self.components:
            c.register_hooks(n_effects)

    def __repr__(self, level=0):
        indent = "  " * level
        repr_str = (f"{indent}LayerMeta(name={self.name}"
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
        print(type(module), module)
        module_meta = ModuleMeta(module, name)
        named_children = list(module.named_children())
        if len(named_children) > 0:
            for i, (child_name, child_module) in enumerate(named_children):
                child_parsed = self._parse_module(child_module, f"{name}.{child_name}")
                module_meta.add_component(child_parsed)
        else:
            parameters = list(module.named_parameters())
            if len(parameters) > 0:
                for n, p in parameters:
                    parameter = ModuleMeta(p, f"{name}.{n}", True)
                    module_meta.add_component(parameter)
            else:
                module_meta.is_parameter = True

        return module_meta

    def run_model(self, task_input):
        self._register_hooks()
        self.pipeline_task.run_pipeline(task_input)

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

    def load_model_from_path(self, path):
        model = None
        model_class = get_model_class_from_path(path)
        print("loading model", model_class, path)
        if model_class is not None:
            model = model_class.from_pretrained(path, local_files_only=True)
            print(f"Successfully loaded model from path", model_class)
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

        self.parsed_model = parsed_model
        self.current_model_name = self.parsed_model.name
