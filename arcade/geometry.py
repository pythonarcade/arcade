shapely_exists = False

try:
    import shapely  # noqa: F401
    shapely_exists = True
except ImportError:
    pass


if shapely_exists:
    from .geometry_shapely import are_polygons_intersecting  # noqa: F401
    from .geometry_shapely import is_point_in_polygon  # noqa: F401
else:
    from .geometry_python import are_polygons_intersecting  # noqa: F401
    from .geometry_python import is_point_in_polygon  # noqa: F401
