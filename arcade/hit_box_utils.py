import numpy as np

from arcade.types import PointList

NumPyPointList = np.ndarray

def point_list_to_ndarray(point_list: PointList) -> NumPyPointList:
    print(point_list)
    return np.array(point_list, dtype=np.float64)

def ndarray_to_point_list(ndarray: NumPyPointList) -> PointList:
    return ndarray.tolist()