"""
Functions used to support drawing. No Pyglet/OpenGL here.
"""

import math

from typing import Tuple, Union, cast

from arcade import Color
from arcade import RGBA, RGB


def get_points_for_thick_line(start_x: float, start_y: float,
                              end_x: float, end_y: float,
                              line_width: float):
    """
    Function used internally for Arcade. OpenGL draws triangles only, so a think
    line must be two triangles that make up a rectangle. This calculates those
    points.
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
    points = (r1_x, r1_y), (r2_x, r2_y), (r4_x, r4_y), (r3_x, r3_y)
    return points


def get_four_byte_color(color: Color) -> RGBA:
    """
    Given a RGB list, it will return RGBA.
    Given a RGBA list, it will return the same RGBA.

    :param Color color: Three or four byte tuple

    :returns:  return: Four byte RGBA tuple
    """

    if len(color) == 4:
        return cast(RGBA, color)
    elif len(color) == 3:
        return color[0], color[1], color[2], 255
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def get_four_float_color(color: Color) -> Tuple[float, float, float, float]:
    """
    Given a 3 or 4 RGB/RGBA color where each color goes 0-255, this
    returns a RGBA tuple where each item is a scaled float from 0 to 1.

    :param Color color: Three or four byte tuple
    :return: Four floats as a RGBA tuple
    """
    if len(color) == 4:
        return color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255  # type: ignore
    elif len(color) == 3:
        return color[0] / 255, color[1] / 255, color[2] / 255, 1.0
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def get_three_float_color(color: Color) -> Tuple[float, float, float]:
    """
    Given a 3 or 4 RGB/RGBA color where each color goes 0-255, this
    returns a RGBA tuple where each item is a scaled float from 0 to 1.

    :param Color color: Three or four byte tuple
    :return: Three floats as a RGB tuple
    """
    if len(color) == 4 or len(color) == 3:
        return color[0] / 255, color[1] / 255, color[2] / 255  # type: ignore
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def make_transparent_color(color: Color, transparency: float):
    """
    Given a RGB color, along with an alpha, returns a RGBA color tuple.

    :param Color color: Three or four byte RGBA color
    :param float transparency: Transparency
    """
    return color[0], color[1], color[2], transparency


def uint24_to_three_byte_color(color: int) -> RGB:
    """
    Given an int between 0 and 16777215, return a RGB color tuple.

    :param int color: 3 byte int
    """
    return (color & (255 << 16)) >> 16, (color & (255 << 8)) >> 8, color & 255


def uint32_to_four_byte_color(color: int) -> RGBA:
    """
    Given an int between 0 and 4294967295, return a RGBA color tuple.

    :param int color: 4 byte int
    """
    return (color & (255 << 24)) >> 24, (color & (255 << 16)) >> 16, (color & (255 << 8)) >> 8, color & 255


def color_from_hex_string(code: str) -> RGBA:
    """
    Make a color from a hex code (3, 4, 6 or 8 characters of hex, normally with a hashtag)
    """
    code = code.lstrip("#")
    if len(code) <= 4:
        code = "".join(i + "0" for i in code)
    if len(code) == 6:
        # full opacity if no alpha specified
        return int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), 255
    elif len(code) == 8:
        return int(code[2:4], 16), int(code[4:6], 16), int(code[6:8], 16), int(code[0:2], 16)

    raise ValueError("Improperly formatted color passed to color_from_hex")


def float_to_byte_color(
    color: Union[Tuple[float, float, float, float], Tuple[float, float, float]],
) -> Color:
    """
    Converts a float colors to a byte color.
    This works for 3 of 4-component colors.
    """
    if len(color) == 3:
        return int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
    elif len(color) == 4:
        color = cast(Tuple[float, float, float, float], color)
        return int(color[0] * 255), int(color[1] * 255), int(color[2] * 255), int(color[3] * 255)
    else:
        raise ValueError(f"color needs to have 3 or 4 components, not {color}")
