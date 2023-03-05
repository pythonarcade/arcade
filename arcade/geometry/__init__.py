"""
The geometry module contains functions for checking collisions with geometry.

Other simpler math related functions are in the :py:mod:`arcade.math` module.
"""
from .geometry_python import (
    get_triangle_orientation,
    are_lines_intersecting,
    is_point_in_box,
)
try:
    from .geometry_shapely import (
        are_polygons_intersecting,
        is_point_in_polygon,
    )
    shapely_installed = True
except ImportError:
    from .geometry_python import (
        are_polygons_intersecting,
        is_point_in_polygon,
    )
    shapely_installed = False


__all__ = [
    "are_polygons_intersecting",
    "is_point_in_polygon",
    "get_triangle_orientation",
    "are_lines_intersecting",
    "is_point_in_box",
    "shapely_installed",
]
