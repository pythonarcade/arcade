"""
Functions used to support drawing. No Pyglet/OpenGL here.
"""

import math

from arcade.types import Color, ColorLike


def get_points_for_thick_line(start_x: float, start_y: float,
                              end_x: float, end_y: float,
                              line_width: float):
    """
    Function used internally for Arcade. OpenGL draws triangles only, so a thick
    line must be two triangles that make up a rectangle. This calculates and returns
    those points.
    """
    vector_x = start_x - end_x
    vector_y = start_y - end_y
    perpendicular_x = vector_y
    perpendicular_y = -vector_x
    length = math.sqrt(vector_x * vector_x + vector_y * vector_y)
    if length == 0:
        normal_x = 1.0
        normal_y = 1.0
    else:
        normal_x = perpendicular_x / length
        normal_y = perpendicular_y / length
    r1_x = start_x + normal_x * line_width / 2
    r1_y = start_y + normal_y * line_width / 2
    r2_x = start_x - normal_x * line_width / 2
    r2_y = start_y - normal_y * line_width / 2
    r3_x = end_x + normal_x * line_width / 2
    r3_y = end_y + normal_y * line_width / 2
    r4_x = end_x - normal_x * line_width / 2
    r4_y = end_y - normal_y * line_width / 2
    return (r1_x, r1_y), (r2_x, r2_y), (r4_x, r4_y), (r3_x, r3_y)


def get_four_byte_color(color: ColorLike) -> Color:
    """
    Converts a color to RGBA. If the color is already
    RGBA the original color value will be returned.
    If the alpha channel is not present a 255 value will be added.

    This function is useful when a mix of RGB and RGBA
    values are used and you need to enforce RGBA.

    Examples::

        >>> arcade.get_four_byte_color((255, 255, 255))
        (255, 255, 255, 255)

    :param Color color: Three or four byte tuple

    :returns:  return: Four byte RGBA tuple
    """

    if len(color) in (3, 4):
        return Color(*color)

    raise ValueError(f"This isn't a 3 or 4 byte color: {color}")
