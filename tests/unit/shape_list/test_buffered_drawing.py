import copy
import pytest

import arcade
from arcade.shape_list import (
    ShapeElementList,
    create_line,
    create_ellipse_outline,
    create_ellipse_filled,
    create_ellipse_filled_with_colors,
    create_rectangle_filled,
    create_rectangle_outline,
    create_ellipse_outline,
    create_rectangle_filled_with_colors,
    create_line_generic,
    create_line_strip,
)
import pyglet.gl as gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture
def shape_list_instance() -> ShapeElementList:

    shape_list = ShapeElementList()

    center_x = 0
    center_y = 0
    width = 20
    height = 20
    shape = create_ellipse_filled(center_x, center_y, width, height, arcade.color.WHITE)
    shape_list.append(shape)

    center_x += 40
    shape = create_ellipse_outline(center_x, center_y, width, height, arcade.color.RED, border_width=1)
    shape_list.append(shape)

    center_x += 40
    shape = create_ellipse_outline(center_x, center_y, width, height, arcade.color.DARK_RED, border_width=1)
    shape_list.append(shape)

    shape = create_line(0, 0, 80, 0, arcade.color.BLUE, line_width=1)
    shape_list.append(shape)

    shape = create_line(0, 0, 80, 0, arcade.color.LIGHT_BLUE, line_width=1)
    shape_list.append(shape)

    center_x = 0
    center_y = 50
    width = 20
    height = 20
    outside_color = arcade.color.AERO_BLUE
    inside_color = arcade.color.AFRICAN_VIOLET
    tilt_angle = 45
    shape = create_ellipse_filled_with_colors(center_x, center_y,
                                                     width, height,
                                                     outside_color, inside_color,
                                                     tilt_angle)
    shape_list.append(shape)

    center_x = 0
    center_y = -50
    width = 20
    height = 20
    shape = create_rectangle_filled(center_x, center_y, width, height,
                                           arcade.color.WHITE)
    shape_list.append(shape)
    shape = create_rectangle_outline(center_x, center_y, width, height,
                                            arcade.color.BLACK, border_width=1)
    shape_list.append(shape)
    shape = create_rectangle_outline(center_x, center_y, width, height,
                                            arcade.color.AMERICAN_ROSE, border_width=1)
    shape_list.append(shape)

    color1 = (215, 214, 165)
    color2 = (219, 166, 123)
    points = (70, 70), (150, 70), (150, 150), (70, 150)
    colors = (color1, color1, color2, color2)
    shape = create_rectangle_filled_with_colors(points, colors)
    shape_list.append(shape)

    points = (0, 0), (150, 150), (0, 150), (0, 250)
    shape = create_line_strip(points, arcade.color.AFRICAN_VIOLET)
    shape_list.append(shape)

    points = (0, 0), (75, 90), (60, 150), (90, 250)
    shape = create_line_generic(points, arcade.color.ALIZARIN_CRIMSON, gl.GL_TRIANGLE_FAN)
    shape_list.append(shape)

    return shape_list


def test_shape_copy_dunders_raise_notimplemented_error(window, shape_list_instance):

    for shape in shape_list_instance:
        with pytest.raises(NotImplementedError):
            _ = copy.copy(shape)
        with pytest.raises(NotImplementedError):
            _ = copy.deepcopy(shape)


# Temp fix for https://github.com/pythonarcade/arcade/issues/2074
def test_shapeelementlist_copy_dunders_raise_notimplemented_error(window, shape_list_instance):

    with pytest.raises(NotImplementedError):
        _ = copy.copy(shape_list_instance)

    with pytest.raises(NotImplementedError):
        _ = copy.deepcopy(shape_list_instance)


def test_buffered_drawing(window, shape_list_instance):

    shape_list_instance.center_x = 200
    shape_list_instance.center_y = 200

    for _ in range(10):
        shape_list_instance.draw()
        window.flip()
        window.clear()
        shape_list_instance.move(1, 1)
