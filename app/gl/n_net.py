import math
import time

import numpy as np

from app.grid.n_grid import create_grid, create_layer


class NetLayerMeta:
    def __init__(self, name, bounds):
        self.name = name
        self.bounds = bounds


class NetLayer:
    def __init__(self):
        self.name = None
        # nested NetLayers
        self.sub_layers = []
        # Layers drawn on the screen
        self.grid_layer = None
        # Total layer bounds
        self.bounds = None

    # Used by Gui
    def get_metadata(self):
        return NetLayerMeta(self.name, self.bounds)

    def flatten_meta_data(self):
        result = [self.get_metadata()]
        for s in self.sub_layers:
            result += s.flatten_meta_data()
        return result

    def get_grid_layers(self):
        result = []
        if self.grid_layer is not None:
            result.append(self.grid_layer)
        for s in self.sub_layers:
            result += s.get_grid_layers()
        return result

    def calculate_bounds(self):
        all_bounds = []
        if self.grid_layer is None:
            if len(self.sub_layers) == 0:
                return None

            for c in self.sub_layers:
                child_bounds = c.calculate_bounds()
                if child_bounds is not None:
                    all_bounds.append(child_bounds)

            col_min = min(item[0] for item in all_bounds)
            row_min = min(item[1] for item in all_bounds)
            col_max = max(item[2] for item in all_bounds)
            row_max = max(item[3] for item in all_bounds)

            self.bounds = [col_min, row_min, col_max, row_max]
        else:
            self.bounds = self.grid_layer.meta.bounds
        return self.bounds

    @staticmethod
    def from_module_meta(module_meta):
        children = []
        for sub_module in module_meta.components:
            children.append(NetLayer.from_module_meta(sub_module))

        net_layer = NetLayer()
        net_layer.sub_layers = children
        net_layer.name = module_meta.name
        if module_meta.is_parameter:
            layer_grid = module_meta.get_data()
            if layer_grid.ndim > 2:
                # print("skipped unknown size", component.name, layer_grid.shape)
                layer_grid = np.ones([2, 2])
            net_layer.grid_layer = create_layer(layer_grid, net_layer.name)
        return net_layer

    @staticmethod
    def from_numpy_data(name, np_data):
        net_layer = NetLayer()
        net_layer.name = name
        net_layer.grid_layer = create_layer(np_data, net_layer.name)
        return net_layer

    @staticmethod
    def from_tensor(name, tensor):
        net_layer = NetLayer()
        net_layer.name = name
        np_data = tensor.detach().numpy()
        net_layer.grid_layer = create_layer(np_data, net_layer.name)
        return net_layer

    @staticmethod
    def from_size(name, size):
        net_layer = NetLayer()
        net_layer.name = name
        size_x = math.ceil(math.sqrt(size))
        size_y = size_x
        calculated_size = [size_x, size_y]
        rows_count, columns_count = calculated_size[0], calculated_size[1]
        layer_grid = np.random.uniform(0, 1, (rows_count, columns_count)).astype(np.float32)
        net_layer.grid_layer = layer_grid
        return net_layer


class NNet:
    def __init__(self, n_window, color_theme):
        self.n_window = n_window
        self.color_theme = color_theme
        self.net_layers = []
        self.layers_meta_dict = {}

        self.grid_columns_count = 0
        self.grid_rows_count = 0
        self.total_width = 0
        self.total_height = 0
        self.grid = create_grid()

        # Unique for each load
        self.loaded_data_id = None

    def clear(self):
        self.net_layers = []
        self.grid.layers = []
        self.layers_meta_dict = {}
        self.grid_columns_count = 0
        self.grid_rows_count = 0
        self.total_width = 0
        self.total_height = 0
        self.loaded_data_id = None

    def init_from_size(self, all_layers_sizes):
        print("Init net from sizes")
        self.net_layers = []
        for index, size in enumerate(all_layers_sizes):
            self.net_layers.append(NetLayer.from_size(f"basic_layer_{index}", size))
        grid_layers = []
        for n in self.net_layers:
            grid_layers += n.get_grid_layers()

        self.init_grid(grid_layers)
        self.finish_initialization(f"init_from_size_{time.time()}")

    def init_from_np_arrays(self, all_layers, names):
        print("Generating layers data")
        self.net_layers = []
        for index, layer_grid in enumerate(all_layers):
            self.net_layers.append(NetLayer.from_numpy_data(f"numpy_layer{index}", layer_grid))
        grid_layers = []
        for n in self.net_layers:
            grid_layers += n.get_grid_layers()
        self.init_grid(grid_layers)
        self.finish_initialization(f"init_from_np_arrays_{time.time()}")

    def init_from_model_parser(self, model_parser):
        print("Init net from activations parser")
        self.clear()
        net_layer = NetLayer.from_module_meta(model_parser.parsed_model)
        self.net_layers.append(net_layer)
        #
        # if len(net_layer.sub_layers) > 0:
        #     for s in net_layer.sub_layers:
        #         self.add_layers(s.get_grid_layers())
        # else:
        self.init_grid(net_layer.get_grid_layers())
        self.finish_initialization(net_layer.name)

    def finish_initialization(self, loaded_data_id):
        self.loaded_data_id = loaded_data_id

        for n in self.net_layers:
            n.calculate_bounds()
        meta_data = []
        for n in self.net_layers:
            meta_data += n.flatten_meta_data()
        for m in meta_data:
            self.layers_meta_dict[m.name] = m

    def init_grid(self, grid_layers):
        start_time = time.time()
        print(f"Init net, layers count:", len(grid_layers))
        if len(grid_layers) == 0:
            return
        max_row_count = max(l.rows_count for l in grid_layers)
        gap_between_layers = len(grid_layers)
        print("Loading offsets")
        for index, grid_layer in enumerate(grid_layers):
            column_offset = sum([l.columns_count for l in grid_layers[:index]])
            layer_offset = index * gap_between_layers
            current_row_count = grid_layer.rows_count
            row_offset = 0
            if current_row_count < max_row_count:
                row_offset = int((max_row_count - current_row_count) / 2)
            grid_layer.define_layer_offset(column_offset + layer_offset, row_offset)
            print(f"\rLoading offsets: {int(100 * index / len(grid_layers))}%", end="")
        print(f"\rLoading offsets: 100%", end="")
        print("")
        self.grid_columns_count = sum([l.columns_count for l in grid_layers]) + gap_between_layers * len(grid_layers)
        self.grid_rows_count = max([l.rows_count for l in grid_layers])
        self.total_width = self.grid_columns_count
        self.total_height = self.grid_rows_count
        print(f"Grid dimensions: {self.grid_rows_count}x{self.grid_columns_count}")
        self.grid.add_layers(grid_layers)
        print("Net initialized", time.time() - start_time, "s")

    # Add on top of previous layers
    def add_layers(self, grid_layers):
        current_row_offset = self.grid_rows_count
        current_gap = len(self.grid.layers)
        start_time = time.time()
        print(f"Init net, layers count:", len(grid_layers))
        if len(grid_layers) == 0:
            return
        max_row_count = max(l.rows_count for l in grid_layers)
        gap_between_layers = len(grid_layers) if current_gap == 0 else current_gap
        print("Loading offsets")
        for index, grid_layer in enumerate(grid_layers):
            column_offset = sum([l.columns_count for l in grid_layers[:index]])
            layer_offset = index * gap_between_layers
            current_row_count = grid_layer.rows_count
            row_offset = 0
            if current_row_count < max_row_count:
                row_offset = int((max_row_count - current_row_count) / 2)
            grid_layer.define_layer_offset(column_offset + layer_offset, row_offset + current_row_offset + current_gap)
            print(f"\rLoading offsets: {int(100 * index / len(grid_layers))}%", end="")
        print(f"\rLoading offsets: 100%", end="")
        print("")
        new_grid_columns_count = sum([l.columns_count for l in grid_layers]) + gap_between_layers * len(grid_layers)
        new_grid_rows_count = max([l.rows_count for l in grid_layers])

        self.grid_columns_count = max(self.grid_columns_count, new_grid_columns_count)
        self.grid_rows_count = self.grid_rows_count + new_grid_rows_count + current_gap
        self.total_width = self.grid_columns_count
        self.total_height = self.grid_rows_count

        print(f"Grid dimensions: {self.grid_rows_count}x{self.grid_columns_count}")
        self.grid.add_layers(grid_layers)
        print("Net initialized", time.time() - start_time, "s")

    def update_visible_layers(self, bounds):
        col_min = bounds.x1
        row_min = bounds.y1
        col_max = bounds.x2
        row_max = bounds.y2
        self.grid.get_visible_layers(col_min, row_min, col_max, row_max)

    def get_subgrid_chunks_grid_dimensions(self, col_min, row_min, col_max, row_max, factor):
        start_time = time.time()
        chunks, dimensions, = self.grid.get_visible_data_chunks(col_min, row_min, col_max, row_max,
                                                                factor,
                                                                factor,
                                                                True)
        print("Get grid chunks", (time.time() - start_time) * 1000, "ms", "factor:", factor, "count", len(chunks))
        return chunks, dimensions

    def update_tex_buffer_directly(self, col_min, row_min, col_max, row_max, factor, buffer, cancellation_signal):
        start_time = time.time()
        self.grid.update_texture_buffer_with_visible_data_directly(col_min, row_min, col_max,
                                                                   row_max,
                                                                   factor,
                                                                   factor,
                                                                   buffer,
                                                                   cancellation_signal)
        if not cancellation_signal.is_canceled():
            print("Updated tex buffer", (time.time() - start_time) * 1000, "ms", "factor:", factor, "layers count")

    def get_point_data(self, x, y):
        return self.grid.get_point_data(x, y)
