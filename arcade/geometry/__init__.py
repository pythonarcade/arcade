"""
The geometry module contains functions for checking collisions with geometry.

Other simpler math related functions are in the :py:mod:`arcade.math` module.
"""
from .geometry_python import (
    get_triangle_orientation,
    are_lines_intersecting,
    is_point_in_box,
)

# Shapely is disabled due to https://github.com/pythonarcade/arcade/pull/1535
# We are leaving the code in-place to make it easier for someone to revisit
# in the future and improve shapely's performance.
use_shapely = False
# try:
#     import shapely  # noqa: F401
#     use_shapely = True
# except ImportError:
#     use_shapely = False
if use_shapely:
    from .geometry_shapely import (
        are_polygons_intersecting,
        is_point_in_polygon,
    )
else:
    from .geometry_python import (
        are_polygons_intersecting,
        is_point_in_polygon,
    )

__all__ = [
    "are_polygons_intersecting",
    "is_point_in_polygon",
    "get_triangle_orientation",
    "are_lines_intersecting",
    "is_point_in_box",
    "shapely_installed",
]
