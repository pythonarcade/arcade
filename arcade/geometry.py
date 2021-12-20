import sys

shapely_exists = False

try:
    import shapely
    shapely_exists = True
except ImportError:
    pass


if shapely_exists:
    from .geometry_shapely import are_polygons_intersecting
    from .geometry_shapely import is_point_in_polygon
else:
    if (sys.platform == "linux" or sys.platform == "linux2") or sys.version_info[1] < 10:
        print("Note: Installing the optional Shapely library will improve performance.")
        print("      However, Shapely does not run on Python 3.10 for macOS and Windows machines.")

    from .geometry_python import are_polygons_intersecting
    from .geometry_python import is_point_in_polygon
