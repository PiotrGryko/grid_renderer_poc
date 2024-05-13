def unpack_shape(array):
    shape = array.shape
    if len(shape) == 1:
        return shape[0], 1  # or (shape[0], 1) if you prefer to treat it as a single column with many rows
    return shape[0], shape[1]


class NumpyGrid:
    def __init__(self):
        self.layers = []
        self.default_value = -2
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
                    # Direct slicing and subsampling in one step
                    subgrid_slice = sublayer.layer_grid[overlap_y1 - grid_y1:overlap_y2 - grid_y1:height_factor]
                else:
                    # For 2D arrays, perform slicing and subsampling for both dimensions in one step
                    subgrid_slice = sublayer.layer_grid[
                                    overlap_y1 - grid_y1:overlap_y2 - grid_y1:height_factor,
                                    overlap_x1 - grid_x1:overlap_x2 - grid_x1:width_factor]
                result_chunks.append(subgrid_slice)
                if grid_space:
                    h, w = unpack_shape(subgrid_slice)
                    dx1 = int((overlap_x1 - x1) / width_factor)
                    dy1 = int((overlap_y1 - y1) / height_factor)
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


class NumpyLayer:
    def __init__(self, layer_grid):
        self.column_offset = 0
        self.row_offset = 0
        self.layer_grid = layer_grid
        self.rows_count, self.columns_count = unpack_shape(self.layer_grid)
        self.size = self.layer_grid.size
        self.id = None

    def define_layer_offset(self, column_offset, row_offset):
        self.column_offset = column_offset
        self.row_offset = row_offset
        self.id = f"{self.column_offset}-{self.row_offset}-{self.columns_count}-{self.rows_count}-{self.size}"
