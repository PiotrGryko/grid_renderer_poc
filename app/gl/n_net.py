import json
import math
import os
import re
import time

import numpy as np

from app.grid.n_grid import create_grid, create_layer


class NetWrapper:
    def __init__(self, n_window, color_theme):
        self.weights_net = NNet(n_window, color_theme)
        self.neurons_net = NNet(n_window, color_theme)

        self.show_weights = True

    def clear(self):
        self.show_weights = True
        self.weights_net.clear()
        self.neurons_net.clear()

    def set_weights_net_active(self):
        self.show_weights = True

    def set_neurons_net_active(self):
        self.show_weights = False

    @property
    def loaded_data_id(self):
        if self.show_weights:
            return self.weights_net.loaded_data_id
        else:
            return self.neurons_net.loaded_data_id

    @property
    def total_width(self):
        if self.show_weights:
            return self.weights_net.total_width
        else:
            return self.neurons_net.total_width

    @property
    def total_height(self):
        if self.show_weights:
            return self.weights_net.total_height
        else:
            return self.neurons_net.total_height

    @property
    def layers(self):
        if self.show_weights:
            return self.weights_net.layers
        else:
            return self.neurons_net.layers

    def update_visible_layers(self, bounds):
        if self.show_weights:
            self.weights_net.update_visible_layers(bounds)
        else:
            self.neurons_net.update_visible_layers(bounds)

    def get_subgrid_chunks_grid_dimensions(self, col_min, row_min, col_max, row_max, factor):
        if self.show_weights:
            return self.weights_net.get_subgrid_chunks_grid_dimensions(col_min, row_min, col_max, row_max, factor)
        else:
            return self.neurons_net.get_subgrid_chunks_grid_dimensions(col_min, row_min, col_max, row_max, factor)

    def get_point_data(self, x, y):
        if self.show_weights:
            return self.weights_net.get_point_data(x, y)
        else:
            return self.neurons_net.get_point_data(x, y)


class NNet:
    def __init__(self, n_window, color_theme):
        self.n_window = n_window
        self.color_theme = color_theme
        self.layers = []
        self.layers_names = []
        self.grid_columns_count = 0
        self.grid_rows_count = 0
        self.total_width = 0
        self.total_height = 0
        self.total_size = 0
        self.grid = create_grid()
        self.visible_layers = []

        # Unique for each load
        self.loaded_data_id = None

    def clear(self):
        self.layers = []
        self.layers_names = []
        self.grid_columns_count = 0
        self.grid_rows_count = 0
        self.total_width = 0
        self.total_height = 0
        self.total_size = 0
        self.visible_layers = []
        self.loaded_data_id = None


    def init_from_model_parser(self, model_parser):
        print("Init net from activations parser")
        layers = []
        names = []
        components = []

        def parse_component(component, start=True):
            if component.shape is not None:
                s = component.shape
                layer_grid = np.random.uniform(0, 1, (s[0], s[1])).astype(np.float32)
                names.append(component.name)
                layers.append(layer_grid)
                components.append(component)

            for c in component.components:
                parse_component(c, False)

        parse_component(model_parser.parsed_model)
        self.create_layers(layers, names)
        self.init_grid()
        self.loaded_data_id = model_parser.parsed_model.name

    def init_from_size(self, all_layers_sizes):
        print("Init net from sizes")
        layers = []
        names = []
        print("Generating layers data")
        for index, size in enumerate(all_layers_sizes):
            size_x = math.ceil(math.sqrt(size))
            size_y = size_x
            calculated_size = [size_x, size_y]
            rows_count, columns_count = calculated_size[0], calculated_size[1]
            layer_grid = np.random.uniform(0, 1, (rows_count, columns_count)).astype(np.float32)
            layers.append(layer_grid)
            names.append(f"basic_layer_{index}")
        print("Creating layers")
        self.create_layers(layers, names)
        self.init_grid()
        self.loaded_data_id = f"init_from_size_{time.time()}"

    def init_from_np_arrays(self, all_layers, names):
        print("Init net from np arrays")
        if len(all_layers) != len(names):
            print("layers size doenst match names size")
            return
        layers = []
        print("Generating layers data")
        for index, layer_grid in enumerate(all_layers):
            layers.append(layer_grid)
        print("Creating layers")
        self.create_layers(layers, names)
        self.init_grid()
        self.loaded_data_id = f"init_from_np_arrays_{time.time()}"

    def init_from_last_memory_files(self):
        layers = []
        names = []
        files = os.listdir("memfile")

        def numerical_sort_key(value):
            # Find all sequences of digits in the string and convert the first one to an integer
            numbers = re.findall(r'\d+', value)
            return int(numbers[0]) if numbers else 0

        files.sort(key=numerical_sort_key)
        for index, file_name in enumerate(files):
            print(f"\rParsing memfile: {int(100 * index / len(files))}%", end="")
            if file_name.endswith(".dat"):
                file_name = f"memfile/{file_name}"
                print(file_name)
                metadata_file_name = f"{file_name}.json"
                with open(metadata_file_name, 'r') as meta_file:
                    metadata = json.load(meta_file)

                shape = tuple(metadata["shape"])
                dtype = np.dtype(metadata["dtype"])
                memmap = np.memmap(file_name, dtype=dtype, mode='r', shape=shape)
                layers.append(memmap)
                names.append(file_name)
        self.create_layers(layers, names)
        self.init_grid()
        self.loaded_data_id = f"init_from_last_memory_files_{time.time()}"

    def init_from_tensors(self, names_parameters, save_to_memfile=False):
        print("Init net from tensors")
        start_time = time.time()
        size = len(names_parameters)
        layers = []
        names = []
        print("")

        for index, (name, tensor) in enumerate(names_parameters):
            print(f"\rDetaching tensors: {int(100 * index / size)}%", end="")
            tensor_numpy = tensor.detach().numpy()
            layers.append(tensor_numpy)
            names.append(name)

            if save_to_memfile:
                # Create a memory-mapped file
                file_name = f"memfile/tensor{index}.dat"
                os.makedirs("memfile", exist_ok=True)
                memmap = np.memmap(file_name, dtype=tensor_numpy.dtype, mode='w+', shape=tensor_numpy.shape)
                # Write the tensor data to the memory-mapped file
                memmap[:] = tensor_numpy[:]
                # Flush changes to disk
                memmap.flush()

                metadata_file_name = f"{file_name}.json"
                metadata = {
                    "shape": tensor_numpy.shape,
                    "dtype": str(tensor_numpy.dtype)
                }
                with open(metadata_file_name, 'w') as meta_file:
                    json.dump(metadata, meta_file)

        print(f"\rDetaching tensors: 100%", time.time() - start_time, "s", end="")
        print("")
        self.create_layers(layers, names)
        self.init_grid()
        self.loaded_data_id = f"init_from_tensors_{time.time()}"

    def create_layers(self, all_layers, all_names):
        start_time = time.time()
        self.layers = []
        print("Creating layers", len(all_layers))
        for index, layer_data in enumerate(all_layers):
            name = all_names[index]
            grid_layer = create_layer(layer_data, name)
            self.layers.append(grid_layer)
        print(f"Layers created", time.time() - start_time, "s")

    def init_grid(self):
        start_time = time.time()
        print(f"Init net, layers count:", len(self.layers))
        if len(self.layers) == 0:
            return
        max_row_count = max(l.rows_count for l in self.layers)
        gap_between_layers = len(self.layers)
        print("Loading offsets")
        for index, grid_layer in enumerate(self.layers):
            column_offset = sum([l.columns_count for l in self.layers[:index]])
            layer_offset = index * gap_between_layers
            current_row_count = grid_layer.rows_count
            row_offset = 0
            if current_row_count < max_row_count:
                row_offset = int((max_row_count - current_row_count) / 2)
            grid_layer.define_layer_offset(column_offset + layer_offset, row_offset)
            print(f"\rLoading offsets: {int(100 * index / len(self.layers))}%", end="")
        print(f"\rLoading offsets: 100%", end="")
        print("")
        self.grid_columns_count = sum([l.columns_count for l in self.layers]) + gap_between_layers * len(self.layers)
        self.grid_rows_count = max([l.rows_count for l in self.layers])
        self.total_width = self.grid_columns_count
        self.total_height = self.grid_rows_count
        self.total_size = sum([l.size for l in self.layers])
        print(f"Grid dimensions: {self.grid_rows_count}x{self.grid_columns_count}")
        self.grid.add_layers(self.layers)
        print("Net initialized", time.time() - start_time, "s",
              "total size: ", self.total_size
              )

    def update_visible_layers(self, bounds):
        col_min = bounds.x1
        row_min = bounds.y1
        col_max = bounds.x2
        row_max = bounds.y2
        visible = self.grid.get_visible_layers(col_min, row_min, col_max, row_max)

        if visible != self.visible_layers:
            self.visible_layers = visible

    def get_subgrid_chunks_grid_dimensions(self, col_min, row_min, col_max, row_max, factor):
        start_time = time.time()
        chunks, dimensions, = self.grid.get_visible_data_chunks(col_min, row_min, col_max, row_max,
                                                                factor,
                                                                factor,
                                                                True)

        print("Get grid chunks", (time.time() - start_time) * 1000, "ms", "factor:", factor, "count", len(chunks))
        return chunks, dimensions

    def get_point_data(self, x, y):
        return self.grid.get_point_data(x, y)
