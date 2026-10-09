"""Draw functions that take a list of points name the first bad point."""

import array

import pytest
from pyglet.math import Vec2

import arcade
from arcade.draw.helpers import _flatten_points

GOOD = [(0, 0), (10, 10), (20, 0), (30, 10)]


def test_flatten_points():
    assert _flatten_points(GOOD) == array.array("f", [0, 0, 10, 10, 20, 0, 30, 10])
    assert _flatten_points([Vec2(1, 2), (3, 4)]) == array.array("f", [1, 2, 3, 4])
    assert _flatten_points([]) == array.array("f")


@pytest.mark.parametrize(
    "points, bad_index",
    [
        # The example from the issue: used to raise "'int' object is not iterable"
        ([(1, 1), 5, (2, 2)], 1),
        # Points with 1 or 3 numbers used to shift every number after them
        ([(1,), (2, 2), (3, 3)], 0),
        ([(1, 1), (2, 2, 2), (3, 3)], 1),
        ([(1, 1), ("a", 2)], 1),
    ],
)
def test_flatten_points_names_bad_point(points, bad_index):
    with pytest.raises(ValueError, match=rf"point_list\[{bad_index}\] is .*2 numbers"):
        _flatten_points(points)


@pytest.mark.parametrize(
    "draw",
    [
        lambda points: arcade.draw_lines(points, arcade.color.RED),
        lambda points: arcade.draw_points(points, arcade.color.RED),
        lambda points: arcade.draw_line_strip(points, arcade.color.RED),
        lambda points: arcade.draw_line_strip(points, arcade.color.RED, line_width=3),
        lambda points: arcade.draw_polygon_filled(points, arcade.color.RED),
        lambda points: arcade.draw_polygon_outline(points, arcade.color.RED, line_width=3),
    ],
    ids=["lines", "points", "line_strip", "thick_line_strip", "polygon_filled", "polygon_outline"],
)
def test_draw_functions_name_bad_point(window, draw):
    draw(GOOD)
    draw([Vec2(*point) for point in GOOD])
    with pytest.raises(ValueError, match=r"point_list\[2\] is 7"):
        draw([(0, 0), (10, 10), 7, (30, 10)])
