import os

import numpy as np
import torch
from torch import nn


class LayerMeta:
    def __init__(self, name, layer_type, shape=None, probability=None):
        self.name = name
        self.layer_type = layer_type
        self.shape = shape
        self.probability = probability
        self.components = []

    def add_component(self, component):
        self.components.append(component)

    def update_names(self, parent_name=None):
        if parent_name is not None:
            self.name = parent_name + "." + self.name
        for c in self.components:
            c.update_names(self.name)

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
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.layers_info = []
        self.parsed_model = None

    def flatten_output(self, output):
        flat_list = []
        if isinstance(output, tuple):
            for item in output:
                flat_list.extend(self.flatten_output(item))
        elif isinstance(output, torch.Tensor):
            flat_list.append(output)
        elif hasattr(output, '__dict__'):  # For objects like BaseModelOutputWithPast
            for value in output.__dict__.values():
                flat_list.extend(self.flatten_output(value))
        return flat_list

    def save_activation(self, info):
        def hook(module, input, output):
            print("update activations", info.name, type(output))
            flattened_output = self.flatten_output(output)
            activation = [o.detach().cpu().numpy() for o in flattened_output if o is not None]
            activation = [a.reshape(a.shape[0], -1) if len(a.shape) > 2 else a for a in activation]

            info.activation = activation[0] if len(activation) == 1 else activation
            info.size_x, info.size_y = info.activation.shape if isinstance(info.activation, np.ndarray) else (
                None, None)

        return hook

    def register_hooks(self):
        for info in self.layers_info:
            info.module.register_forward_hook(self.save_activation(info))

    def perform_forward_pass(self, input_text):
        inputs = self.tokenizer(input_text, return_tensors="pt")
        output = self.model.generate(**inputs, max_new_tokens=10, do_sample=False)
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)

        for info in self.layers_info:
            if info.activation is not None:
                activation = info.activation
                if isinstance(activation, list):
                    activation = activation[0]
                if len(activation.shape) == 2:
                    info.size_x, info.size_y = activation.shape

        print(generated_text)
        return generated_text

    def parse_module(self, module, name):
        if isinstance(module, nn.Embedding):
            layer_meta = LayerMeta(name, module.__class__.__name__,
                                   [module.num_embeddings, module.embedding_dim])
        elif isinstance(module, nn.Linear):
            layer_meta = LayerMeta(name, module.__class__.__name__, [module.in_features, module.out_features])
        elif isinstance(module, nn.LayerNorm):
            layer_meta = LayerMeta(name, module.__class__.__name__, [module.normalized_shape[0], 1])
        elif isinstance(module, nn.Dropout):
            layer_meta = LayerMeta(name, module.__class__.__name__, [1, 1], probability=module.p)
        elif hasattr(module, 'children') and list(module.children()):
            layer_meta = LayerMeta(name, module.__class__.__name__, )
            for i, (child_name, child_module) in enumerate(module.named_children()):
                child_parsed = self.parse_module(child_module, child_name)
                layer_meta.add_component(child_parsed)
        else:
            layer_meta = LayerMeta(name, module.__class__.__name__,[1, 1])
        return layer_meta

    def model_to_json(self):
        _, module = list(self.model.named_modules())[0]
        name = os.path.basename(self.model.name_or_path)
        parsed_model = self.parse_module(module, name)
        parsed_model.update_names()
        # parsed_model.calculate_bounds()
        # parsed_model.count_layers()
        # parsed_model.calculate_offsets(gap_between_layers=parsed_model.layers_count)
        self.parsed_model = parsed_model
        # offset_model = self.calculate_offsets(parsed_model)
        # json_output = json.dumps(offset_model, indent=2)
        return parsed_model
