from app.grid.numba_grid import NumbaGrid, NumbaLayer
from app.grid.numpy_average_grid import NumpyAverageGrid
from app.grid.numpy_grid import NumpyGrid, NumpyLayer

NUMPY = 0
NUMPY_AVERAGE = 4
NUMBA = 1
EIGEN = 2
XTENSOR = 3

CURRENT_GRID = 0


# self.grid = mylittlenet.EigenGrid()
# self.grid = mylittlenet.XTensorGrid()

# grid_layer = mylittlenet.EigenLayer(layer_data)
# grid_layer = mylittlenet.XTensorLayer(layer_data)

def create_grid():
    if CURRENT_GRID == NUMPY:
        return NumpyGrid()
    if CURRENT_GRID == NUMPY_AVERAGE:
        return NumpyAverageGrid()
    if CURRENT_GRID == NUMBA:
        return NumbaGrid()
    if CURRENT_GRID == EIGEN:
        import mylittlenet
        return mylittlenet.EigenGrid()


def create_layer(np_array, name):
    if CURRENT_GRID == NUMPY:
        return NumpyLayer(np_array, name)
    if CURRENT_GRID == NUMPY_AVERAGE:
        return NumpyLayer(np_array, name)
    if CURRENT_GRID == NUMBA:
        return NumbaLayer(np_array)
    if CURRENT_GRID == EIGEN:
        import mylittlenet
        return mylittlenet.EigenLayer(np_array)

