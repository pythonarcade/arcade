import math

from arcade import gl
from arcade.math import rotate_point
from arcade.types import RGBOrA255

from .helpers import _generic_draw_line_strip


def draw_arc_filled(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBOrA255,
    start_angle: float,
    end_angle: float,
    tilt_angle: float = 0,
    num_segments: int = 128,
) -> None:
    """
    Draw a filled in arc. Useful for drawing pie-wedges, or Pac-Man.

    Args:
        center_x:
            x position that is the center of the arc.
        center_y:
            y position that is the center of the arc.
        width:
            width of the arc.
        height:
            height of the arc.
        color:
            A 3 or 4 length tuple of 0-255 channel values or a
            :py:class:`.Color` instance.
        start_angle:
            start angle of the arc in degrees.
        end_angle:
            end angle of the arc in degrees.
        tilt_angle:
            angle the arc is tilted (clockwise).
        num_segments:
            Number of line segments used to draw arc.
    """
    unrotated_point_list = [(0.0, 0.0)]

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)

    for segment in range(start_segment, end_segment + 1):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta) / 2
        y = height * math.sin(theta) / 2

        unrotated_point_list.append((x, y))

    if tilt_angle == 0:
        uncentered_point_list = unrotated_point_list
    else:
        uncentered_point_list = [
            rotate_point(point[0], point[1], 0, 0, tilt_angle) for point in unrotated_point_list
        ]

    point_list = [(point[0] + center_x, point[1] + center_y) for point in uncentered_point_list]

    _generic_draw_line_strip(point_list, color, gl.TRIANGLE_FAN)


def draw_arc_outline(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBOrA255,
    start_angle: float,
    end_angle: float,
    border_width: float = 1,
    tilt_angle: float = 0,
    num_segments: int = 128,
) -> None:
    """
    Draw the outside edge of an arc. Useful for drawing curved lines.

    Args:
        center_x:
            x position that is the center of the arc.
        center_y:
            y position that is the center of the arc.
        width:
            width of the arc.
        height:
            height of the arc.
        color:
            A 3 or 4 length tuple of 0-255 channel values or a
            :py:class:`.Color` instance.
        start_angle:
            Start angle of the arc in degrees.
        end_angle:
            End angle of the arc in degrees.
        border_width:
            width of line in pixels.
        tilt_angle:
            Angle the arc is tilted (clockwise).
        num_segments:
            Number of triangle segments that make up this circle.
            Higher is better quality, but slower render time.
    """
    unrotated_point_list = []

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)

    inside_width = (width - border_width / 2) / 2
    outside_width = (width + border_width / 2) / 2
    inside_height = (height - border_width / 2) / 2
    outside_height = (height + border_width / 2) / 2

    for segment in range(start_segment, end_segment + 1):
        theta = 2.0 * math.pi * segment / num_segments

        x1 = inside_width * math.cos(theta)
        y1 = inside_height * math.sin(theta)

        x2 = outside_width * math.cos(theta)
        y2 = outside_height * math.sin(theta)

        unrotated_point_list.append((x1, y1))
        unrotated_point_list.append((x2, y2))

    if tilt_angle == 0:
        uncentered_point_list = unrotated_point_list
    else:
        uncentered_point_list = [
            rotate_point(point[0], point[1], 0, 0, tilt_angle) for point in unrotated_point_list
        ]

    point_list = [(point[0] + center_x, point[1] + center_y) for point in uncentered_point_list]

    _generic_draw_line_strip(point_list, color, gl.TRIANGLE_STRIP)
