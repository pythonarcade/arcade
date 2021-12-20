import sys


if 'shapely' in sys.modules:
    from .geometry_shapely import are_polygons_intersecting
    from .geometry_shapely import is_point_in_polygon
else:
    from .geometry_python import are_polygons_intersecting
    from .geometry_python import is_point_in_polygon
