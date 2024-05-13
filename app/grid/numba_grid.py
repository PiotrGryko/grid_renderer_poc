from numba import jit


@jit(nopython=True, cache=True)
def unpack_h(shape):
    return shape[0]


@jit(nopython=True, cache=True)
def unpack_w(shape):
    if len(shape) == 1:
        return 1
    else:
        return shape[1]


@jit(nopython=True, cache=True)
def rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
    # Check if one rectangle is on left side of other
    if x1 > grid_x2 or grid_x1 > x2:
        return False
    # Check if one rectangle is above the other
    if y1 > grid_y2 or grid_y1 > y2:
        return False
    return True


@jit(nopython=True, cache=True)
def get_visible_chunk_accelerated(x1, y1, x2, y2,
                                  layer_grid,
                                  column_offset, row_offset, columns_count, rows_count,
                                  width_factor, height_factor,
                                  grid_space):
    grid_x1 = column_offset
    grid_y1 = row_offset
    grid_x2 = grid_x1 + columns_count
    grid_y2 = grid_y1 + rows_count

    if rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
        # Calculate the overlap area
        overlap_x1 = max(x1, grid_x1)
        overlap_y1 = max(y1, grid_y1)
        overlap_x2 = min(x2, grid_x2)
        overlap_y2 = min(y2, grid_y2)
        if layer_grid.ndim == 1:
            # Direct slicing and subsampling in one step
            subgrid_slice = layer_grid[overlap_y1 - grid_y1:overlap_y2 - grid_y1:height_factor]
        else:
            # For 2D arrays, perform slicing and subsampling for both dimensions in one step
            subgrid_slice = layer_grid[
                            overlap_y1 - grid_y1:overlap_y2 - grid_y1:height_factor,
                            overlap_x1 - grid_x1:overlap_x2 - grid_x1:width_factor]
        if grid_space:
            shape = subgrid_slice.shape
            h = unpack_h(shape)
            w = unpack_w(shape)
            dx1 = int((overlap_x1 - x1) / width_factor)
            dy1 = int((overlap_y1 - y1) / height_factor)
            dims = (
                dx1,
                dy1,
                dx1 + w,
                dy1 + h
            )
        else:
            dims = (overlap_x1,
                    overlap_y1,
                    overlap_x2,
                    overlap_y2)
        return subgrid_slice, dims
    return None, None


@jit(nopython=True, cache=True)
def get_visible_layers_accelerated(layers_properties, x1, y1, x2, y2):
    visible_layers_indexes = []
    for index, props in enumerate(layers_properties):
        column_offset, row_offset, columns_count, rows_count = props
        grid_x1 = column_offset
        grid_y1 = row_offset
        grid_x2 = grid_x1 + columns_count
        grid_y2 = grid_y1 + rows_count
        if rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
            visible_layers_indexes.append(index)
    return visible_layers_indexes


class NumbaGrid:
    def __init__(self):
        self.layers_data = []
        self.layers_properties = []
        self.default_value = -2
        self.visible_layers_indexes = []
        print("Numba grid created")

    def add_layers(self, layers):
        for index, l in enumerate(layers):
            self.layers_data.append(l.layer_grid)
            self.layers_properties.append((
                l.column_offset, l.row_offset, l.columns_count, l.rows_count
            ))

    def get_visible_layers(self, x1, y1, x2, y2):
        self.visible_layers_indexes = get_visible_layers_accelerated(self.layers_properties, x1, y1, x2, y2)

    def get_visible_data_chunks(self, x1, y1, x2, y2, width_factor, height_factor, grid_space=False):
        result_chunks = []
        result_dimensions = []
        # Iterate over each subgrid to check for intersections
        for index in self.visible_layers_indexes:
            sublayer_data = self.layers_data[index]
            column_offset, row_offset, columns_count, rows_count = self.layers_properties[index]
            chunk, dims = get_visible_chunk_accelerated(
                x1, y1, x2, y2,
                sublayer_data,
                column_offset,
                row_offset,
                columns_count,
                rows_count,
                width_factor,
                height_factor,
                grid_space
            )
            if chunk is not None:
                result_chunks.append(chunk)
            if dims is not None:
                result_dimensions.append(dims)
        return result_chunks, result_dimensions


class NumbaLayer:
    def __init__(self, layer_grid):
        self.column_offset = 0
        self.row_offset = 0
        self.layer_grid = layer_grid
        shape = self.layer_grid.shape
        self.rows_count = unpack_h(shape)
        self.columns_count = unpack_w(shape)
        self.size = self.layer_grid.size
        self.id = None

    def define_layer_offset(self, column_offset, row_offset):
        self.column_offset = column_offset
        self.row_offset = row_offset
        self.id = f"{self.column_offset}-{self.row_offset}-{self.columns_count}-{self.rows_count}-{self.size}"








############### Maybe for later



# @jit(nopython=True, cache=True)
# def get_visible_data_chunks_accelerated_2d(
#         layers_data_2d,
#         layers_indexes_2d,
#         layers_properties_2d,
#         visible_layers_indexes_2d,
#         x1, y1, x2, y2, width_factor, height_factor, grid_space=False):
#     result_chunks = []
#     result_dimensions = []
#     # Iterate over each subgrid to check for intersections
#     for index in visible_layers_indexes_2d:
#         index_2d = layers_indexes_2d.index(index)
#         layer_grid = layers_data_2d[index_2d]
#
#         # layer_grid = layers_data[index]
#         column_offset, row_offset, columns_count, rows_count = layers_properties_2d[index]
#         grid_x1 = column_offset
#         grid_y1 = row_offset
#         grid_x2 = grid_x1 + columns_count
#         grid_y2 = grid_y1 + rows_count
#
#         if rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
#             # Calculate the overlap area
#             overlap_x1 = max(x1, grid_x1)
#             overlap_y1 = max(y1, grid_y1)
#             overlap_x2 = min(x2, grid_x2)
#             overlap_y2 = min(y2, grid_y2)
#             subgrid_slice = layer_grid[
#                             overlap_y1 - grid_y1:overlap_y2 - grid_y1:height_factor,
#                             overlap_x1 - grid_x1:overlap_x2 - grid_x1:width_factor]
#             result_chunks.append(subgrid_slice)
#             if grid_space:
#                 shape = subgrid_slice.shape
#                 h = unpack_h(shape)
#                 w = unpack_w(shape)
#                 dx1 = int((overlap_x1 - x1) / width_factor)
#                 dy1 = int((overlap_y1 - y1) / height_factor)
#                 result_dimensions.append(
#                     (
#                         dx1,
#                         dy1,
#                         dx1 + w,
#                         dy1 + h
#                     )
#                 )
#             else:
#                 result_dimensions.append(
#                     (overlap_x1,
#                      overlap_y1,
#                      overlap_x2,
#                      overlap_y2))
#     return result_chunks, result_dimensions
#
#
# @jit(nopython=True, cache=True)
# def get_visible_data_chunks_accelerated(
#         layers_data_2d,
#         layers_data_1d,
#         layers_indexes_2d,
#         layers_indexes_1d,
#         layers_properties,
#         visible_layers_indexes,
#         x1, y1, x2, y2, width_factor, height_factor, grid_space=False):
#     result_chunks = []
#     result_dimensions = []
#     # Iterate over each subgrid to check for intersections
#     for index in visible_layers_indexes:
#         if index in layers_indexes_2d:
#             index_2d = layers_indexes_2d.index(index)
#             layer_grid = layers_data_2d[index_2d]
#         else:
#             index_1d = layers_indexes_1d.index(index)
#             layer_grid = layers_data_1d[index_1d]
#
#         # layer_grid = layers_data[index]
#         column_offset, row_offset, columns_count, rows_count = layers_properties[index]
#         grid_x1 = column_offset
#         grid_y1 = row_offset
#         grid_x2 = grid_x1 + columns_count
#         grid_y2 = grid_y1 + rows_count
#
#         if rectangles_intersect(x1, y1, x2, y2, grid_x1, grid_y1, grid_x2, grid_y2):
#             # Calculate the overlap area
#             overlap_x1 = max(x1, grid_x1)
#             overlap_y1 = max(y1, grid_y1)
#             overlap_x2 = min(x2, grid_x2)
#             overlap_y2 = min(y2, grid_y2)
#             if layer_grid.ndim == 1:
#                 # Direct slicing and subsampling in one step
#                 subgrid_slice = layer_grid[overlap_y1 - grid_y1:overlap_y2 - grid_y1:height_factor]
#             else:
#                 # For 2D arrays, perform slicing and subsampling for both dimensions in one step
#                 subgrid_slice = layer_grid[
#                                 overlap_y1 - grid_y1:overlap_y2 - grid_y1:height_factor,
#                                 overlap_x1 - grid_x1:overlap_x2 - grid_x1:width_factor]
#             result_chunks.append(subgrid_slice)
#             if grid_space:
#                 shape = subgrid_slice.shape
#                 h = unpack_h(shape)
#                 w = unpack_w(shape)
#                 dx1 = int((overlap_x1 - x1) / width_factor)
#                 dy1 = int((overlap_y1 - y1) / height_factor)
#                 result_dimensions.append(
#                     (
#                         dx1,
#                         dy1,
#                         dx1 + w,
#                         dy1 + h
#                     )
#                 )
#             else:
#                 result_dimensions.append(
#                     (overlap_x1,
#                      overlap_y1,
#                      overlap_x2,
#                      overlap_y2))
#     return result_chunks, result_dimensions

