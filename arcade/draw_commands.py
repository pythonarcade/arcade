"""
This module contains commands for basic graphics drawing commands.
(Drawing primitives.)

Many of these commands are slow, because they load everything to the
graphics card each time a shape is drawn. For faster drawing, see the
Buffered Draw Commands.
"""
# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods

import math
import array

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

import pyglet.gl as gl

from typing import List
from typing import Tuple
from typing import TYPE_CHECKING

from arcade import Color
from arcade import PointList
from arcade import earclip
from .geometry_generic import rotate_point
from arcade import get_four_byte_color
from arcade import get_points_for_thick_line
from arcade import Texture
from arcade import get_window


if TYPE_CHECKING:  # import for mypy only
    from arcade.arcade_types import Point


# --- BEGIN ARC FUNCTIONS # # #


def draw_arc_filled(center_x: float, center_y: float,
                    width: float, height: float,
                    color: Color,
                    start_angle: float, end_angle: float,
                    tilt_angle: float = 0,
                    num_segments: int = 128):
    """
    Draw a filled in arc. Useful for drawing pie-wedges, or Pac-Man.

    :param float center_x: x position that is the center of the arc.
    :param float center_y: y position that is the center of the arc.
    :param float width: width of the arc.
    :param float height: height of the arc.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float start_angle: start angle of the arc in degrees.
    :param float end_angle: end angle of the arc in degrees.
    :param float tilt_angle: angle the arc is tilted.
    :param float num_segments: Number of line segments used to draw arc.
    """
    unrotated_point_list = [[0.0, 0.0]]

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)

    for segment in range(start_segment, end_segment + 1):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta) / 2
        y = height * math.sin(theta) / 2

        unrotated_point_list.append([x, y])

    if tilt_angle == 0:
        uncentered_point_list = unrotated_point_list
    else:
        uncentered_point_list = []
        for point in unrotated_point_list:
            uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

    point_list = []
    for point in uncentered_point_list:
        point_list.append((point[0] + center_x, point[1] + center_y))

    _generic_draw_line_strip(point_list, color, gl.GL_TRIANGLE_FAN)


def draw_arc_outline(center_x: float, center_y: float, width: float,
                     height: float, color: Color,
                     start_angle: float, end_angle: float,
                     border_width: float = 1, tilt_angle: float = 0,
                     num_segments: int = 128):
    """
    Draw the outside edge of an arc. Useful for drawing curved lines.

    :param float center_x: x position that is the center of the arc.
    :param float center_y: y position that is the center of the arc.
    :param float width: width of the arc.
    :param float height: height of the arc.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float start_angle: start angle of the arc in degrees.
    :param float end_angle: end angle of the arc in degrees.
    :param float border_width: width of line in pixels.
    :param float tilt_angle: angle the arc is tilted.
    :param int num_segments: float of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
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

        unrotated_point_list.append([x1, y1])
        unrotated_point_list.append([x2, y2])

    if tilt_angle == 0:
        uncentered_point_list = unrotated_point_list
    else:
        uncentered_point_list = []
        for point in unrotated_point_list:
            uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

    point_list = []
    for point in uncentered_point_list:
        point_list.append((point[0] + center_x, point[1] + center_y))

    _generic_draw_line_strip(point_list, color, gl.GL_TRIANGLE_STRIP)


# --- END ARC FUNCTIONS # # #


# --- BEGIN PARABOLA FUNCTIONS # # #

def draw_parabola_filled(start_x: float, start_y: float, end_x: float,
                         height: float, color: Color,
                         tilt_angle: float = 0):
    """
    Draws a filled in parabola.

    :param float start_x: The starting x position of the parabola
    :param float start_y: The starting y position of the parabola
    :param float end_x: The ending x position of the parabola
    :param float height: The height of the parabola
    :param Color color: The color of the parabola
    :param float tilt_angle: The angle of the tilt of the parabola

    """
    center_x = (start_x + end_x) / 2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    draw_arc_filled(center_x, center_y, width, height, color,
                    start_angle, end_angle, tilt_angle)


def draw_parabola_outline(start_x: float, start_y: float, end_x: float,
                          height: float, color: Color,
                          border_width: float = 1, tilt_angle: float = 0):
    """
    Draws the outline of a parabola.

    :param float start_x: The starting x position of the parabola
    :param float start_y: The starting y position of the parabola
    :param float end_x: The ending x position of the parabola
    :param float height: The height of the parabola
    :param Color color: The color of the parabola
    :param float border_width: The width of the parabola
    :param float tilt_angle: The angle of the tilt of the parabola
    """
    center_x = (start_x + end_x) / 2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    draw_arc_outline(center_x, center_y, width, height, color,
                     start_angle, end_angle, border_width, tilt_angle)


# --- END PARABOLA FUNCTIONS # # #


# --- BEGIN CIRCLE FUNCTIONS # # #

def draw_circle_filled(center_x: float, center_y: float, radius: float,
                       color: Color,
                       tilt_angle: float = 0,
                       num_segments: int = -1):
    """
    Draw a filled-in circle.

    :param float center_x: x position that is the center of the circle.
    :param float center_y: y position that is the center of the circle.
    :param float radius: width of the circle.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float tilt_angle: Angle in degrees to tilt the circle. Useful for low segment count circles
    :param int num_segments: Number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
         The default value of -1 means arcade will try to calculate a reasonable
         amount of segments based on the size of the circle.
    """
    draw_ellipse_filled(center_x, center_y, radius * 2, radius * 2, color,
                        tilt_angle=tilt_angle,
                        num_segments=num_segments)


def draw_circle_outline(center_x: float, center_y: float, radius: float,
                        color: Color, border_width: float = 1,
                        tilt_angle: float = 0,
                        num_segments: int = -1):
    """
    Draw the outline of a circle.

    :param float center_x: x position that is the center of the circle.
    :param float center_y: y position that is the center of the circle.
    :param float radius: width of the circle.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float border_width: Width of the circle outline in pixels.
    :param float tilt_angle: Angle in degrees to tilt the circle. Useful for low segment count circles
    :param int num_segments: Number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
         The default value of -1 means arcade will try to calculate a reasonable
         amount of segments based on the size of the circle.
    """
    draw_ellipse_outline(center_x=center_x, center_y=center_y,
                         width=radius * 2, height=radius * 2,
                         color=color,
                         border_width=border_width,
                         tilt_angle=tilt_angle,
                         num_segments=num_segments)

# --- END CIRCLE FUNCTIONS # # #


# --- BEGIN ELLIPSE FUNCTIONS # # #

def draw_ellipse_filled(center_x: float, center_y: float,
                        width: float, height: float, color: Color,
                        tilt_angle: float = 0, num_segments: int = -1):
    """
    Draw a filled in ellipse.

    :param float center_x: x position that is the center of the circle.
    :param float center_y: y position that is the center of the circle.
    :param float width: width of the ellipse.
    :param float height: height of the ellipse.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float tilt_angle: Angle in degrees to tilt the ellipse.
    :param int num_segments: Number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
         The default value of -1 means arcade will try to calculate a reasonable
         amount of segments based on the size of the circle.
    """
    window = get_window()
    ctx = window.ctx

    program = ctx.shape_ellipse_filled_unbuffered_program
    geometry = ctx.shape_ellipse_unbuffered_geometry
    buffer = ctx.shape_ellipse_unbuffered_buffer
    # We need to normalize the color because we are setting it as a float uniform
    if len(color) == 3:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
    elif len(color) == 4:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)  # type: ignore
    else:
        raise ValueError("Invalid color format. Use a 3 or 4 component tuple")

    program['color'] = color_normalized
    program['shape'] = width / 2, height / 2, tilt_angle
    program['segments'] = num_segments
    buffer.write(data=array.array('f', (center_x, center_y)))

    geometry.render(program, mode=gl.GL_POINTS, vertices=1)


def draw_ellipse_outline(center_x: float, center_y: float,
                         width: float,
                         height: float, color: Color,
                         border_width: float = 1,
                         tilt_angle: float = 0,
                         num_segments: int = -1):
    """
    Draw the outline of an ellipse.

    :param float center_x: x position that is the center of the circle.
    :param float center_y: y position that is the center of the circle.
    :param float width: width of the ellipse.
    :param float height: height of the ellipse.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float border_width: Width of the circle outline in pixels.
    :param float tilt_angle: Angle in degrees to tilt the ellipse.
    :param int num_segments: Number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
         The default value of -1 means arcade will try to calculate a reasonable
         amount of segments based on the size of the circle.
    :param float tilt_angle: Tile of the circle. Useful when drawing a circle with a low segment count
    """
    window = get_window()
    ctx = window.ctx

    program = ctx.shape_ellipse_outline_unbuffered_program
    geometry = ctx.shape_ellipse_outline_unbuffered_geometry
    buffer = ctx.shape_ellipse_outline_unbuffered_buffer
    # We need to normalize the color because we are setting it as a float uniform
    if len(color) == 3:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
    elif len(color) == 4:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)  # type: ignore
    else:
        raise ValueError("Invalid color format. Use a 3 or 4 component tuple")

    program['color'] = color_normalized
    program['shape'] = width / 2, height / 2, tilt_angle, border_width
    program['segments'] = num_segments
    buffer.write(data=array.array('f', (center_x, center_y)))

    geometry.render(program, mode=gl.GL_POINTS, vertices=1)


# --- END ELLIPSE FUNCTIONS # # #


# --- BEGIN LINE FUNCTIONS # # #


def _generic_draw_line_strip(point_list: PointList,
                             color: Color,
                             mode: int = gl.GL_LINE_STRIP):
    """
    Draw a line strip. A line strip is a set of continuously connected
    line segments.

    :param point_list: List of points making up the line. Each point is
         in a list. So it is a list of lists.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    """
    window = get_window()
    ctx = window.ctx

    c4 = get_four_byte_color(color)
    c4e = c4 * len(point_list)
    a = array.array('B', c4e)

    def gen_flatten(my_list):
        return [item for sublist in my_list for item in sublist]

    vertices = array.array('f', gen_flatten(point_list))

    geometry = ctx.generic_draw_line_strip_geometry
    program = ctx.line_vertex_shader
    geometry.num_vertices = len(point_list)

    # Double buffer sizes if out of space
    while len(vertices) * 4 > ctx.generic_draw_line_strip_vbo.size:
        ctx.generic_draw_line_strip_vbo.orphan(ctx.generic_draw_line_strip_vbo.size * 2)
        ctx.generic_draw_line_strip_color.orphan(ctx.generic_draw_line_strip_color.size * 2)

    ctx.generic_draw_line_strip_vbo.write(vertices)
    ctx.generic_draw_line_strip_color.write(a)

    geometry.render(program, mode=mode)


def draw_line_strip(point_list: PointList,
                    color: Color, line_width: float = 1):
    """
    Draw a multi-point line.

    :param PointList point_list: List of x, y points that make up this strip
    :param Color color: Color of line strip
    :param float line_width: Width of the line
    """
    if line_width == 1:
        _generic_draw_line_strip(point_list, color, gl.GL_LINE_STRIP)
    else:
        triangle_point_list: PointList = []
        # This needs a lot of improvement
        last_point = None
        for point in point_list:
            if last_point is not None:
                points = get_points_for_thick_line(last_point[0], last_point[1], point[0], point[1], line_width)
                reordered_points = points[1], points[0], points[2], points[3]
                # noinspection PyUnresolvedReferences
                triangle_point_list.extend(reordered_points)
            last_point = point
        _generic_draw_line_strip(triangle_point_list, color, gl.GL_TRIANGLE_STRIP)


def draw_line(start_x: float, start_y: float, end_x: float, end_y: float,
              color: Color, line_width: float = 1):
    """
    Draw a line.

    :param float start_x: x position of line starting point.
    :param float start_y: y position of line starting point.
    :param float end_x: x position of line ending point.
    :param float end_y: y position of line ending point.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float line_width: Width of the line in pixels.
    """
    window = get_window()
    ctx = window.ctx

    program = ctx.shape_line_program
    geometry = ctx.shape_line_geometry
    # We need to normalize the color because we are setting it as a float uniform
    if len(color) == 3:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
    elif len(color) == 4:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)  # type: ignore
    else:
        raise ValueError("Invalid color format. Use a 3 or 4 component tuple")

    program['line_width'] = line_width
    program['color'] = color_normalized
    ctx.shape_line_buffer_pos.write(
        data=array.array('f', [start_x, start_y, end_x, end_y]))
    geometry.render(program, mode=gl.GL_LINES, vertices=2)


def draw_lines(point_list: PointList,
               color: Color,
               line_width: float = 1):
    """
    Draw a set of lines.

    Draw a line between each pair of points specified.

    :param PointList point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float line_width: Width of the line in pixels.
    """
    window = get_window()
    ctx = window.ctx

    program = ctx.shape_line_program
    geometry = ctx.shape_line_geometry
    # We need to normalize the color because we are setting it as a float uniform
    if len(color) == 3:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
    elif len(color) == 4:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)  # type: ignore
    else:
        raise ValueError("Invalid color format. Use a 3 or 4 component tuple")

    while len(point_list) * 3 * 4 > ctx.shape_line_buffer_pos.size:
        ctx.shape_line_buffer_pos.orphan(ctx.shape_line_buffer_pos.size * 2)

    program['line_width'] = line_width
    program['color'] = color_normalized
    ctx.shape_line_buffer_pos.write(
        data=array.array('f', [v for point in point_list for v in point]))
    geometry.render(program, mode=gl.GL_LINES, vertices=len(point_list))


# --- BEGIN POINT FUNCTIONS # # #


def draw_point(x: float, y: float, color: Color, size: float):
    """
    Draw a point.

    :param float x: x position of point.
    :param float y: y position of point.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float size: Size of the point in pixels.
    """
    draw_rectangle_filled(x, y, size, size, color)


def draw_points(point_list: PointList, color: Color, size: float = 1):
    """
    Draw a set of points.

    :param PointList point_list: List of points Each point is
         in a list. So it is a list of lists.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float size: Size of the point in pixels.
    """
    window = get_window()
    ctx = window.ctx

    program = ctx.shape_rectangle_filled_unbuffered_program
    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
    buffer = ctx.shape_rectangle_filled_unbuffered_buffer
    # We need to normalize the color because we are setting it as a float uniform
    if len(color) == 3:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
    elif len(color) == 4:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)  # type: ignore
    else:
        raise ValueError("Invalid color format. Use a 3 or 4 component tuple")

    # Resize buffer
    data_size = len(point_list) * 8
    # if data_size > buffer.size:
    buffer.orphan(size=data_size)

    program['color'] = color_normalized
    program['shape'] = size, size, 0
    buffer.write(data=array.array('f', [v for point in point_list for v in point]))
    geometry.render(program, mode=ctx.POINTS, vertices=data_size // 8)


# --- END POINT FUNCTIONS # # #

# --- BEGIN POLYGON FUNCTIONS # # #


def draw_polygon_filled(point_list: PointList,
                        color: Color):
    """
    Draw a polygon that is filled in.

    :param PointList point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
    :param Color color: The color, specified in RGB or RGBA format.
    """

    triangle_points = earclip(point_list)
    flattened_list = [i for g in triangle_points for i in g]
    _generic_draw_line_strip(flattened_list, color, gl.GL_TRIANGLES)


def draw_polygon_outline(point_list: PointList,
                         color: Color, line_width: float = 1):
    """
    Draw a polygon outline. Also known as a "line loop."

    :param PointList point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param int line_width: Width of the line in pixels.
    """
    new_point_list = [point for point in point_list]
    new_point_list.append(point_list[0])

    triangle_point_list = []
    # This needs a lot of improvement
    last_point = None
    for point in new_point_list:
        if last_point is not None:
            points = get_points_for_thick_line(last_point[0], last_point[1], point[0], point[1], line_width)
            reordered_points = points[1], points[0], points[2], points[3]
            triangle_point_list.extend(reordered_points)
        last_point = point

    points = get_points_for_thick_line(new_point_list[0][0], new_point_list[0][1], new_point_list[1][0],
                                       new_point_list[1][1], line_width)
    triangle_point_list.append(points[1])
    _generic_draw_line_strip(triangle_point_list, color, gl.GL_TRIANGLE_STRIP)


def draw_triangle_filled(x1: float, y1: float,
                         x2: float, y2: float,
                         x3: float, y3: float, color: Color):
    """
    Draw a filled in triangle.

    :param float x1: x value of first coordinate.
    :param float y1: y value of first coordinate.
    :param float x2: x value of second coordinate.
    :param float y2: y value of second coordinate.
    :param float x3: x value of third coordinate.
    :param float y3: y value of third coordinate.
    :param Color color: Color of triangle.
    """

    first_point = (x1, y1)
    second_point = (x2, y2)
    third_point = (x3, y3)
    point_list = (first_point, second_point, third_point)
    _generic_draw_line_strip(point_list, color, gl.GL_TRIANGLES)


def draw_triangle_outline(x1: float, y1: float,
                          x2: float, y2: float,
                          x3: float, y3: float,
                          color: Color,
                          border_width: float = 1):
    """
    Draw a the outline of a triangle.

    :param float x1: x value of first coordinate.
    :param float y1: y value of first coordinate.
    :param float x2: x value of second coordinate.
    :param float y2: y value of second coordinate.
    :param float x3: x value of third coordinate.
    :param float y3: y value of third coordinate.
    :param Color color: Color of triangle.
    :param float border_width: Width of the border in pixels. Defaults to 1.
    """
    first_point = [x1, y1]
    second_point = [x2, y2]
    third_point = [x3, y3]
    point_list = (first_point, second_point, third_point)
    draw_polygon_outline(point_list, color, border_width)


# --- END POLYGON FUNCTIONS # # #


# --- BEGIN RECTANGLE FUNCTIONS # # #


def draw_lrtb_rectangle_outline(left: float, right: float, top: float,
                                bottom: float, color: Color,
                                border_width: float = 1):
    """
    Draw a rectangle by specifying left, right, top, and bottom edges.

    :param float left: The x coordinate of the left edge of the rectangle.
    :param float right: The x coordinate of the right edge of the rectangle.
    :param float top: The y coordinate of the top of the rectangle.
    :param float bottom: The y coordinate of the rectangle bottom.
    :param Color color: The color of the rectangle.
    :param float border_width: The width of the border in pixels. Defaults to one.
    :Raises AttributeError: Raised if left > right or top < bottom.

    """

    if left > right:
        raise AttributeError("Left coordinate must be less than or equal to "
                             "the right coordinate")

    if bottom > top:
        raise AttributeError("Bottom coordinate must be less than or equal to "
                             "the top coordinate")

    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    width = right - left
    height = top - bottom
    draw_rectangle_outline(center_x, center_y, width, height, color,
                           border_width)


def draw_xywh_rectangle_outline(bottom_left_x: float, bottom_left_y: float,
                                width: float, height: float,
                                color: Color,
                                border_width: float = 1):
    """
    Draw a rectangle extending from bottom left to top right

    :param float bottom_left_x: The x coordinate of the left edge of the rectangle.
    :param float bottom_left_y: The y coordinate of the bottom of the rectangle.
    :param float width: The width of the rectangle.
    :param float height: The height of the rectangle.
    :param Color color: The color of the rectangle.
    :param float border_width: The width of the border in pixels. Defaults to one.
    """
    center_x = bottom_left_x + (width / 2)
    center_y = bottom_left_y + (height / 2)
    draw_rectangle_outline(center_x, center_y, width, height, color,
                           border_width)


def draw_rectangle_outline(center_x: float, center_y: float, width: float,
                           height: float, color: Color,
                           border_width: float = 1, tilt_angle: float = 0):
    """
    Draw a rectangle outline.

    :param float center_x: x coordinate of top left rectangle point.
    :param float center_y: y coordinate of top left rectangle point.
    :param float width: width of the rectangle.
    :param float height: height of the rectangle.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float border_width: width of the lines, in pixels.
    :param float tilt_angle: rotation of the rectangle. Defaults to zero.
    """

    i_lb = center_x - width / 2 + border_width / 2, center_y - height / 2 + border_width / 2
    i_rb = center_x + width / 2 - border_width / 2, center_y - height / 2 + border_width / 2
    i_rt = center_x + width / 2 - border_width / 2, center_y + height / 2 - border_width / 2
    i_lt = center_x - width / 2 + border_width / 2, center_y + height / 2 - border_width / 2

    o_lb = center_x - width / 2 - border_width / 2, center_y - height / 2 - border_width / 2
    o_rb = center_x + width / 2 + border_width / 2, center_y - height / 2 - border_width / 2
    o_rt = center_x + width / 2 + border_width / 2, center_y + height / 2 + border_width / 2
    o_lt = center_x - width / 2 - border_width / 2, center_y + height / 2 + border_width / 2

    point_list: List[Point] = [o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt]

    if tilt_angle != 0:
        point_list_2: List[Point] = []
        for point in point_list:
            new_point = rotate_point(point[0], point[1], center_x, center_y, tilt_angle)
            point_list_2.append(new_point)
        point_list = point_list_2

    _generic_draw_line_strip(point_list, color, gl.GL_TRIANGLE_STRIP)


def draw_lrtb_rectangle_filled(left: float, right: float, top: float,
                               bottom: float, color: Color):
    """
    Draw a rectangle by specifying left, right, top, and bottom edges.

    :param float left: The x coordinate of the left edge of the rectangle.
    :param float right: The x coordinate of the right edge of the rectangle.
    :param float top: The y coordinate of the top of the rectangle.
    :param float bottom: The y coordinate of the rectangle bottom.
    :param Color color: The color of the rectangle.
    :Raises AttributeError: Raised if left > right or top < bottom.

    """
    if left > right:
        raise AttributeError("Left coordinate {} must be less than or equal "
                             "to the right coordinate {}".format(left, right))

    if bottom > top:
        raise AttributeError("Bottom coordinate {} must be less than or equal "
                             "to the top coordinate {}".format(bottom, top))

    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    width = right - left + 1
    height = top - bottom + 1
    draw_rectangle_filled(center_x, center_y, width, height, color)


def draw_xywh_rectangle_filled(bottom_left_x: float, bottom_left_y: float,
                               width: float, height: float,
                               color: Color):
    """
    Draw a filled rectangle extending from bottom left to top right

    :param float bottom_left_x: The x coordinate of the left edge of the rectangle.
    :param float bottom_left_y: The y coordinate of the bottom of the rectangle.
    :param float width: The width of the rectangle.
    :param float height: The height of the rectangle.
    :param Color color: The color of the rectangle.
    """

    center_x = bottom_left_x + (width / 2)
    center_y = bottom_left_y + (height / 2)
    draw_rectangle_filled(center_x, center_y, width, height, color)


def draw_rectangle_filled(center_x: float, center_y: float, width: float,
                          height: float, color: Color,
                          tilt_angle: float = 0):
    """
    Draw a filled-in rectangle.

    :param float center_x: x coordinate of rectangle center.
    :param float center_y: y coordinate of rectangle center.
    :param float width: width of the rectangle.
    :param float height: height of the rectangle.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float tilt_angle: rotation of the rectangle. Defaults to zero.
    """
    window = get_window()
    ctx = window.ctx

    program = ctx.shape_rectangle_filled_unbuffered_program
    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
    buffer = ctx.shape_rectangle_filled_unbuffered_buffer
    # We need to normalize the color because we are setting it as a float uniform
    if len(color) == 3:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, 1.0)
    elif len(color) == 4:
        color_normalized = (color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)  # type: ignore
    else:
        raise ValueError("Invalid color format. Use a 3 or 4 component tuple")

    program['color'] = color_normalized
    program['shape'] = width, height, tilt_angle
    buffer.write(data=array.array('f', (center_x, center_y)))
    geometry.render(program, mode=ctx.POINTS, vertices=1)


def draw_scaled_texture_rectangle(center_x: float, center_y: float,
                                  texture: Texture,
                                  scale: float = 1.0,
                                  angle: float = 0,
                                  alpha: int = 255):
    """
    Draw a textured rectangle on-screen.

    :param float center_x: x coordinate of rectangle center.
    :param float center_y: y coordinate of rectangle center.
    :param int texture: identifier of texture returned from load_texture() call
    :param float scale: scale of texture
    :param float angle: rotation of the rectangle. Defaults to zero.
    :param float alpha: Transparency of image. 0 is fully transparent, 255 (default) is visible
    """

    texture.draw_scaled(center_x, center_y, scale, angle, alpha)


def draw_texture_rectangle(center_x: float, center_y: float,
                           width: float,
                           height: float,
                           texture: Texture,
                           angle: float = 0,
                           alpha: int = 255):
    """
    Draw a textured rectangle on-screen.

    :param float center_x: x coordinate of rectangle center.
    :param float center_y: y coordinate of rectangle center.
    :param float width: width of texture
    :param float height: height of texture
    :param int texture: identifier of texture returned from load_texture() call
    :param float angle: rotation of the rectangle. Defaults to zero.
    :param float alpha: Transparency of image. 0 is fully transparent, 255 (default) is visible
    """

    texture.draw_sized(center_x, center_y, width, height, angle, alpha)


def draw_lrwh_rectangle_textured(bottom_left_x: float, bottom_left_y: float,
                                 width: float,
                                 height: float,
                                 texture: Texture, angle: float = 0,
                                 alpha: int = 255):
    """
    Draw a texture extending from bottom left to top right.

    :param float bottom_left_x: The x coordinate of the left edge of the rectangle.
    :param float bottom_left_y: The y coordinate of the bottom of the rectangle.
    :param float width: The width of the rectangle.
    :param float height: The height of the rectangle.
    :param int texture: identifier of texture returned from load_texture() call
    :param float angle: rotation of the rectangle. Defaults to zero.
    :param int alpha: Transparency of image. 0 is fully transparent, 255 (default) is visible
    """

    center_x = bottom_left_x + (width / 2)
    center_y = bottom_left_y + (height / 2)
    texture.draw_sized(center_x, center_y, width, height, angle=angle, alpha=alpha)


def get_pixel(x: int, y: int, components: int = 3) -> Tuple[int, ...]:
    """
    Given an x, y, will return a color value of that point.

    :param int x: x location
    :param int y: y location
    :param int components: Number of components to fetch. By default we fetch 3
        3 components (RGB). 4 componets would be RGBA.
    :rtype: Color
    """
    # noinspection PyCallingNonCallable,PyTypeChecker

    # The window may be 'scaled' on hi-res displays. Particularly Macs. OpenGL
    # won't account for this, so we need to.
    window = get_window()

    pixel_ratio = window.get_pixel_ratio()
    x = int(pixel_ratio * x)
    y = int(pixel_ratio * y)

    a = (gl.GLubyte * 4)(0)
    gl.glReadPixels(x, y, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, a)
    return tuple(int(i) for i in a[:components])


def get_image(x: int = 0, y: int = 0, width: int = None, height: int = None) -> PIL.Image.Image:
    """
    Get an image from the screen.

    Example::

        image = get_image()
        image.save('screenshot.png', 'PNG')

    :param int x: Start (left) x location
    :param int y: Start (top) y location
    :param int width: Width of image. Leave blank for grabbing the 'rest' of the image
    :param int height: Height of image. Leave blank for grabbing the 'rest' of the image
    :returns: A Pillow Image
    :rtype: PIL.Image.Image
    """
    window = get_window()

    pixel_ratio = window.get_pixel_ratio()
    x = int(pixel_ratio * x)
    y = int(pixel_ratio * y)

    if width is None:
        width = window.width - x
    if height is None:
        height = window.height - y

    width = int(pixel_ratio * width)
    height = int(pixel_ratio * height)

    # Create an image buffer
    # noinspection PyTypeChecker
    image_buffer = (gl.GLubyte * (4 * width * height))(0)

    gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_buffer)
    image = PIL.Image.frombytes("RGBA", (width, height), image_buffer)
    image = PIL.ImageOps.flip(image)

    return image
