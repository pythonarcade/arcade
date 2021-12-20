from arcade import SpriteList

from shapely import speedups  # type: ignore
from shapely.geometry import Polygon, Point  # type: ignore
from shapely.geometry import LineString, Polygon  # type: ignore
speedups.enable()


def has_line_of_sight(point_1: Point,
                      point_2: Point,
                      walls: SpriteList,
                      max_distance: int = -1) -> bool:
    """
    Determine if we have line of sight between two points. Having a line of
    sight means, that you can connect both points with straight line without
    intersecting any obstacle.
    Thanks to the shapely efficiency and speedups boost, this function is very
    fast. It can easily test 10 000 lines_of_sight.

    :param point_1: tuple -- coordinates of first position (x, y)
    :param point_2: tuple -- coordinates of second position (x, y)
    :param walls: list -- Obstacle objects to check against
    :param max_distance: int --
    :return: tuple -- (bool, list)
    """
    line_of_sight = LineString([point_1, point_2])
    if 0 < max_distance < line_of_sight.length:
        return False
    if not walls:
        return True
    return not any((Polygon(o.get_adjusted_hit_box()).crosses(line_of_sight) for o in walls))
