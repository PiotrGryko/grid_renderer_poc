import os
import threading

import numpy as np
import torch
from torch import nn


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
        print("update activations", self.name, type(output))
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
        self.parsed_model = None
        self.hooks_registered = False

        self.last_result = None

    def _register_hooks(self):
        if self.hooks_registered:
            return
        self.parsed_model.register_hooks(self.n_effects)
        self.hooks_registered = True

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

    def perform_forward_pass(self, input_text):
        thread = threading.Thread(target=self._perform_forward_pass_internal, args=(input_text,))
        thread.start()
        return thread

    def pool_forward_pass_result(self):
        if self.last_result is not None:
            r = self.last_result
            self.last_result = None
            return r
        else:
            return None

    def _perform_forward_pass_internal(self, input_text):
        self._register_hooks()
        inputs = self.tokenizer(input_text, return_tensors="pt")
        output = self.model.generate(**inputs, max_new_tokens=100, do_sample=False)
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)

        print("Input: ", input_text)
        print("Output: ", generated_text)
        self.last_result = generated_text

    def load_hg_model(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        _, module = list(self.model.named_modules())[0]
        name = os.path.basename(self.model.name_or_path)
        parsed_model = self._parse_module(module, name)
        parsed_model.update_names()

        self.parsed_model = parsed_model

        return parsed_model
