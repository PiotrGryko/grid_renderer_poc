import math
import os
import time

import numpy as np
import psutil

from app.grid.n_grid import create_grid, create_layer


class NNet:
    def __init__(self, n_window, color_theme):
        self.n_window = n_window
        self.color_theme = color_theme
        self.layers = []
        self.grid_columns_count = 0
        self.grid_rows_count = 0
        self.total_width = 0
        self.total_height = 0
        self.total_size = 0
        self.grid = create_grid()
        self.visible_layers = []

        self.process = psutil.Process(os.getpid())
        self.memory_usage = 0
        self.virtual_memory_usage = 0

    def print_memory_usage(self):
        mem_info = self.process.memory_info()
        usage = f"{mem_info.rss / (1024 * 1024 * 1024):.2f}"
        if self.memory_usage != usage:
            self.memory_usage = usage
            print(f"Memory usage: {self.memory_usage} GB (Resident Set Size)")

    def init_from_size(self, all_layers_sizes):
        print("Init net from sizes")
        layers = []
        print("Generating layers data")
        for size in all_layers_sizes:
            size_x = math.ceil(math.sqrt(size))
            size_y = size_x
            calculated_size = [size_x, size_y]
            rows_count, columns_count = calculated_size[0], calculated_size[1]
            layer_grid = np.random.uniform(0, 1, (rows_count, columns_count)).astype(np.float32)
            layers.append(layer_grid)
        print("Creating layers")
        self.create_layers(layers)
        self.init_grid()

    def init_from_tensors(self, tensors):
        print("Init net from tensors")
        start_time = time.time()
        size = len(tensors)
        layers = []
        print("")
        for index, tensor in enumerate(tensors):
            print(f"\rDetaching tensors: {int(100 * index / size)}%", end="")
            layers.append(tensor.detach().numpy())
        print(f"\rDetaching tensors: 100%", time.time() - start_time, "s", end="")
        print("")
        self.create_layers(layers)
        self.init_grid()

    def create_layers(self, all_layers):
        start_time = time.time()
        print("Creating layers", len(all_layers))
        for index, layer_data in enumerate(all_layers):
            grid_layer = create_layer(layer_data)
            self.layers.append(grid_layer)
        print(f"Layers created", time.time() - start_time, "s")

    def init_grid(self):
        start_time = time.time()
        print(f"Init net, layers count:", len(self.layers))
        if len(self.layers) == 0:
            return
        max_row_count = max(l.rows_count for l in self.layers)
        gap_between_layers = 200
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
        self.print_memory_usage()
        return chunks, dimensions
