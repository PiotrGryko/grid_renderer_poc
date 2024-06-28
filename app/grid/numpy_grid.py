import math

import numpy as np


def unpack_shape(array):
    if type(array) is list:
        return len(array), 1
    shape = array.shape
    if len(shape) == 1:
        return shape[0], 1  # or (shape[0], 1) if you prefer to treat it as a single column with many rows
    return shape[0], shape[1]


class NumpyGrid:
    def __init__(self):
        self.layers = []
        self.visible_layers = []

    def add_layers(self, layers):
        self.layers = layers

    def rectangles_intersect(self, x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
        # Check if one rectangle is on left side of other
        if x1 > grid_x2 or grid_x1 > x2:
            return False
        # Check if one rectangle is above the other
        if y1 > grid_y2 or grid_y1 > y2:
            return False
        return True

    def get_visible_layers(self, x1, y1, x2, y2):
        visible_layers = []
        for sublayer in self.layers:
            grid_x1 = sublayer.column_offset
            grid_y1 = sublayer.row_offset
            grid_x2 = grid_x1 + sublayer.columns_count
            grid_y2 = grid_y1 + sublayer.rows_count
            if self.rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
                visible_layers.append(sublayer)
        self.visible_layers = visible_layers
        return visible_layers

    def get_visible_data_chunks(self, x1, y1, x2, y2, width_factor, height_factor, grid_space=False):
        result_chunks = []
        result_dimensions = []

        # Iterate over each subgrid to check for intersections
        for sublayer in self.visible_layers:

            grid_x1 = sublayer.column_offset
            grid_y1 = sublayer.row_offset
            grid_x2 = grid_x1 + sublayer.columns_count
            grid_y2 = grid_y1 + sublayer.rows_count

            if self.rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
                # Calculate the overlap area
                overlap_x1 = max(x1, grid_x1)
                overlap_y1 = max(y1, grid_y1)
                overlap_x2 = min(x2, grid_x2)
                overlap_y2 = min(y2, grid_y2)
                if sublayer.layer_grid.ndim == 1:
                    # Ensure consistent start for subsampling
                    start_index_y = (overlap_y1 - grid_y1) % height_factor
                    # Direct slicing and subsampling in one step
                    subgrid_slice = sublayer.layer_grid[
                                    (overlap_y1 - grid_y1 - start_index_y):overlap_y2 - grid_y1:height_factor]
                else:
                    # Ensure consistent start for subsampling in both dimensions
                    start_index_y = (overlap_y1 - grid_y1) % height_factor
                    start_index_x = (overlap_x1 - grid_x1) % width_factor
                    # For 2D arrays, perform slicing and subsampling for both dimensions in one step
                    subgrid_slice = sublayer.layer_grid[
                                    (overlap_y1 - grid_y1 - start_index_y):overlap_y2 - grid_y1:height_factor,
                                    (overlap_x1 - grid_x1 - start_index_x):overlap_x2 - grid_x1:width_factor]
                # print(unpack_shape(subgrid_slice), width_factor)
                result_chunks.append(subgrid_slice)
                if grid_space:
                    h, w = unpack_shape(subgrid_slice)
                    dx1 = math.ceil((overlap_x1 - x1) / width_factor)
                    dy1 = math.ceil((overlap_y1 - y1) / height_factor)
                    result_dimensions.append(
                        (
                            dx1,
                            dy1,
                            dx1 + w,
                            dy1 + h
                        )
                    )
                else:
                    result_dimensions.append(
                        (overlap_x1,
                         overlap_y1,
                         overlap_x2,
                         overlap_y2))
        return result_chunks, result_dimensions

    def get_visible_data_single_patch(self, x1, y1, x2, y2, width_factor, height_factor, grid_space=False):
        # Determine the dimensions of the output grid
        output_width = (x2 - x1) // width_factor
        output_height = (y2 - y1) // height_factor

        # Initialize the output grid with appropriate dimensions
        output_grid = np.zeros((output_height, output_width))
        # print("shape",output_grid.shape)
        for sublayer in self.visible_layers:
            grid_x1 = sublayer.column_offset
            grid_y1 = sublayer.row_offset
            grid_x2 = grid_x1 + sublayer.columns_count
            grid_y2 = grid_y1 + sublayer.rows_count

            if self.rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
                overlap_x1 = max(x1, grid_x1)
                overlap_y1 = max(y1, grid_y1)
                overlap_x2 = min(x2, grid_x2)
                overlap_y2 = min(y2, grid_y2)

                if sublayer.layer_grid.ndim == 1:
                    start_index_y = (overlap_y1 - grid_y1) % height_factor
                    subgrid_slice = sublayer.layer_grid[
                                    (overlap_y1 - grid_y1 - start_index_y):(overlap_y2 - grid_y1):height_factor]
                else:
                    start_index_y = (overlap_y1 - grid_y1) % height_factor
                    start_index_x = (overlap_x1 - grid_x1) % width_factor
                    subgrid_slice = sublayer.layer_grid[
                                    (overlap_y1 - grid_y1 - start_index_y):(overlap_y2 - grid_y1):height_factor,
                                    (overlap_x1 - grid_x1 - start_index_x):(overlap_x2 - grid_x1):width_factor]

                # # Determine the position in the output grid
                dx1 = (overlap_x1 - x1) // width_factor
                dy1 = (overlap_y1 - y1) // height_factor
                h, w = unpack_shape(subgrid_slice)
                # print("layer shape",sublayer.layer_grid.shape)
                # print("shapes",dx1,dy1,w,h)
                # print("slice shape",subgrid_slice.shape)
                if subgrid_slice.ndim == 1:
                    output_grid[dy1:dy1 + h, dx1:dx1 + w] = subgrid_slice[:, np.newaxis]
                else:
                    output_grid[dy1:dy1 + h, dx1:dx1 + w] = subgrid_slice
        h, w = output_grid.shape
        dimmensions = [
            (
                0,
                0,
                w,
                h
            )
        ]
        return [output_grid], dimmensions

    def update_texture_buffer_with_visible_data_directly(self, x1, y1, x2, y2, width_factor, height_factor, buffer):

        # Initialize the output grid with appropriate dimensions
        output_grid = buffer
        output_grid.fill(-1)
        # print("shape",output_grid.shape)
        for sublayer in self.visible_layers:
            grid_x1 = sublayer.column_offset
            grid_y1 = sublayer.row_offset
            grid_x2 = grid_x1 + sublayer.columns_count
            grid_y2 = grid_y1 + sublayer.rows_count

            if self.rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
                overlap_x1 = max(x1, grid_x1)
                overlap_y1 = max(y1, grid_y1)
                overlap_x2 = min(x2, grid_x2)
                overlap_y2 = min(y2, grid_y2)

                dx1 = (overlap_x1 - x1) // width_factor
                dy1 = (overlap_y1 - y1) // height_factor

                # Pre calculate the shape of the slice
                h = (overlap_y2 - overlap_y1 + height_factor - 1) // height_factor
                w = (overlap_x2 - overlap_x1 + width_factor - 1) // width_factor

                # Assign slice directly
                if sublayer.layer_grid.ndim == 1:
                    output_grid[dy1:dy1 + h, dx1:dx1 + 1] = sublayer.layer_grid[(overlap_y1 - grid_y1):(
                                overlap_y2 - grid_y1):height_factor][:, np.newaxis]
                else:
                    output_grid[dy1:dy1 + h, dx1:dx1 + w] = sublayer.layer_grid[
                                                            (overlap_y1 - grid_y1):(overlap_y2 - grid_y1):height_factor,
                                                            (overlap_x1 - grid_x1):(overlap_x2 - grid_x1):width_factor]

                # if sublayer.layer_grid.ndim == 1:
                #     start_index_y = (overlap_y1 - grid_y1) % height_factor
                #     subgrid_slice = sublayer.layer_grid[
                #                     (overlap_y1 - grid_y1 - start_index_y):(overlap_y2 - grid_y1):height_factor]
                # else:
                #     start_index_y = (overlap_y1 - grid_y1) % height_factor
                #     start_index_x = (overlap_x1 - grid_x1) % width_factor
                #     subgrid_slice = sublayer.layer_grid[
                #                     (overlap_y1 - grid_y1 - start_index_y):(overlap_y2 - grid_y1):height_factor,
                #                     (overlap_x1 - grid_x1 - start_index_x):(overlap_x2 - grid_x1):width_factor]
                #
                # # # Determine the position in the output grid
                # dx1 = (overlap_x1 - x1) // width_factor
                # dy1 = (overlap_y1 - y1) // height_factor
                # h, w = unpack_shape(subgrid_slice)
                #
                #
                # print(w,h,slice_w,slice_h)
                # if subgrid_slice.ndim == 1:
                #     output_grid[dy1:dy1 + h, dx1:dx1 + w] = subgrid_slice[:, np.newaxis]
                # else:
                #     output_grid[dy1:dy1 + h, dx1:dx1 + w] = subgrid_slice

    def update_open_gl_buffer_directly(self, x1, y1, x2, y2, width_factor, height_factor, buffer):

        # Initialize the output grid with appropriate dimensions
        output_grid = buffer
        output_grid.fill(-1)
        # print("shape",output_grid.shape)
        for sublayer in self.visible_layers:
            grid_x1 = sublayer.column_offset
            grid_y1 = sublayer.row_offset
            grid_x2 = grid_x1 + sublayer.columns_count
            grid_y2 = grid_y1 + sublayer.rows_count

            if self.rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
                overlap_x1 = max(x1, grid_x1)
                overlap_y1 = max(y1, grid_y1)
                overlap_x2 = min(x2, grid_x2)
                overlap_y2 = min(y2, grid_y2)

                dx1 = (overlap_x1 - x1) // width_factor
                dy1 = (overlap_y1 - y1) // height_factor

                # Pre calculate the shape of the slice
                h = (overlap_y2 - overlap_y1 + height_factor - 1) // height_factor
                w = (overlap_x2 - overlap_x1 + width_factor - 1) // width_factor

                # Assign slice directly
                if sublayer.layer_grid.ndim == 1:
                    output_grid[dy1:dy1 + h, dx1:dx1 + 1] = sublayer.layer_grid[(overlap_y1 - grid_y1):(
                            overlap_y2 - grid_y1):height_factor][:, np.newaxis]
                else:
                    output_grid[dy1:dy1 + h, dx1:dx1 + w] = sublayer.layer_grid[
                                                            (overlap_y1 - grid_y1):(overlap_y2 - grid_y1):height_factor,
                                                            (overlap_x1 - grid_x1):(overlap_x2 - grid_x1):width_factor]

                # if sublayer.layer_grid.ndim == 1:
                #     start_index_y = (overlap_y1 - grid_y1) % height_factor
                #     subgrid_slice = sublayer.layer_grid[
                #                     (overlap_y1 - grid_y1 - start_index_y):(overlap_y2 - grid_y1):height_factor]
                # else:
                #     start_index_y = (overlap_y1 - grid_y1) % height_factor
                #     start_index_x = (overlap_x1 - grid_x1) % width_factor
                #     subgrid_slice = sublayer.layer_grid[
                #                     (overlap_y1 - grid_y1 - start_index_y):(overlap_y2 - grid_y1):height_factor,
                #                     (overlap_x1 - grid_x1 - start_index_x):(overlap_x2 - grid_x1):width_factor]
                #
                # # # Determine the position in the output grid
                # dx1 = (overlap_x1 - x1) // width_factor
                # dy1 = (overlap_y1 - y1) // height_factor
                # h, w = unpack_shape(subgrid_slice)
                #
                #
                # print(w,h,slice_w,slice_h)
                # if subgrid_slice.ndim == 1:
                #     output_grid[dy1:dy1 + h, dx1:dx1 + w] = subgrid_slice[:, np.newaxis]
                # else:
                #     output_grid[dy1:dy1 + h, dx1:dx1 + w] = subgrid_slice

    def get_point_data(self, x1, y1):
        for sublayer in self.visible_layers:
            grid_x1 = sublayer.column_offset
            grid_y1 = sublayer.row_offset
            grid_x2 = grid_x1 + sublayer.columns_count
            grid_y2 = grid_y1 + sublayer.rows_count

            # Check if the point is within the bounds of the current sublayer
            if grid_x1 <= x1 < grid_x2 and grid_y1 <= y1 < grid_y2:
                # Calculate the index in the sublayer's grid
                grid_index_y = y1 - grid_y1
                grid_index_x = x1 - grid_x1

                # Retrieve the point value
                if sublayer.layer_grid.ndim == 1:
                    point_value = sublayer.layer_grid[grid_index_y]
                else:
                    point_value = sublayer.layer_grid[grid_index_y, grid_index_x]

                return point_value, sublayer.meta

        # Return None if the point is not found in any visible layer
        return None, None


# A bit retarded but I don't want to pass the grid data around
class LayerMetaData:
    def __init__(self, name, column_offset, row_offset, size, rows_count, columns_count, bounds):
        self.column_offset = column_offset
        self.name = name
        self.row_offset = row_offset
        self.size = size
        self.rows_count = rows_count,
        self.columns_count = columns_count
        self.bounds = bounds


class NumpyLayer:
    def __init__(self, layer_grid, name):
        self.column_offset = 0
        self.row_offset = 0
        self.layer_grid = layer_grid
        self.rows_count, self.columns_count = unpack_shape(self.layer_grid)
        self.size = self.layer_grid.size
        self.name = name
        self.id = None
        self.meta = None

    def define_layer_offset(self, column_offset, row_offset):
        self.column_offset = column_offset
        self.row_offset = row_offset
        self.id = f"{self.column_offset}-{self.row_offset}-{self.columns_count}-{self.rows_count}-{self.size}"
        bounds = (self.column_offset,
                  self.row_offset,
                  self.column_offset + self.columns_count,
                  self.row_offset + self.rows_count)

        self.meta = LayerMetaData(
            self.name,
            self.column_offset,
            self.row_offset,
            self.size,
            self.rows_count,
            self.columns_count,
            bounds
        )
