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
import sys

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

import pyglet.gl as gl

from typing import List
from typing import TYPE_CHECKING

from arcade import get_projection
from arcade import get_window
from arcade import Color
from arcade import PointList
from arcade import shader
from arcade import earclip
from arcade import rotate_point
from arcade import get_four_byte_color
from arcade import get_points_for_thick_line
from arcade import Texture
from arcade import get_window


if TYPE_CHECKING:  # import for mypy only
    from arcade.arcade_types import Point

_line_vertex_shader = '''
    #version 330
    uniform mat4 Projection;
    in vec2 in_vert;
    in vec4 in_color;
    out vec4 v_color;
    void main() {
       gl_Position = Projection * vec4(in_vert, 0.0, 1.0);
       v_color = in_color;
    }
'''

_line_fragment_shader = '''
    #version 330
    in vec4 v_color;
    out vec4 f_color;
    void main() {
        f_color = v_color;
    }
'''


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
    unrotated_point_list = [(0.0, 0.0)]

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)

    for segment in range(start_segment, end_segment + 1):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        unrotated_point_list.append((x, y))

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

    inside_width = width - border_width / 2
    outside_width = width + border_width / 2
    inside_height = height - border_width / 2
    outside_height = height + border_width / 2

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
                       num_segments: int = 128):
    """
    Draw a filled-in circle.

    :param float center_x: x position that is the center of the circle.
    :param float center_y: y position that is the center of the circle.
    :param float radius: width of the circle.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param int num_segments: float of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    """
    width = radius * 2
    height = radius * 2
    draw_ellipse_filled(center_x, center_y, width, height, color, num_segments=num_segments)


def draw_circle_outline(center_x: float, center_y: float, radius: float,
                        color: Color, border_width: float = 1,
                        num_segments: int = 128):
    """
    Draw the outline of a circle.

    :param float center_x: x position that is the center of the circle.
    :param float center_y: y position that is the center of the circle.
    :param float radius: width of the circle.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float border_width: Width of the circle outline in pixels.
    :param int num_segments: Int of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    """
    width = radius * 2
    height = radius * 2
    draw_ellipse_outline(center_x, center_y, width, height,
                         color, border_width, num_segments=num_segments)


# --- END CIRCLE FUNCTIONS # # #


# --- BEGIN ELLIPSE FUNCTIONS # # #

def draw_ellipse_filled(center_x: float, center_y: float,
                        width: float, height: float, color: Color,
                        tilt_angle: float = 0, num_segments: int = 128):
    """
    Draw a filled in ellipse.

    :param float center_x: x position that is the center of the circle.
    :param float center_y: y position that is the center of the circle.
    :param float width: width of the ellipse.
    :param float height: height of the ellipse.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float tilt_angle: Angle in degrees to tilt the ellipse.
    :param int num_segments: float of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    """

    unrotated_point_list = []

    for segment in range(num_segments):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = (width / 2) * math.cos(theta)
        y = (height / 2) * math.sin(theta)

        unrotated_point_list.append((x, y))

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


def draw_ellipse_outline(center_x: float, center_y: float, width: float,
                         height: float, color: Color,
                         border_width: float = 1, tilt_angle: float = 0,
                         num_segments: int = 128):
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
    :param int num_segments: Number of line segments used to make the ellipse
    """

    if border_width == 1:
        unrotated_point_list = []

        for segment in range(num_segments):
            theta = 2.0 * 3.1415926 * segment / num_segments

            x = (width / 2) * math.cos(theta)
            y = (height / 2) * math.sin(theta)

            unrotated_point_list.append((x, y))

        if tilt_angle == 0:
            uncentered_point_list = unrotated_point_list
        else:
            uncentered_point_list = []
            for point in unrotated_point_list:
                uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

        point_list = []
        for point in uncentered_point_list:
            point_list.append((point[0] + center_x, point[1] + center_y))

        _generic_draw_line_strip(point_list, color, gl.GL_LINE_LOOP)
    else:

        unrotated_point_list = []

        start_segment = 0
        end_segment = num_segments

        inside_width = (width / 2) - border_width / 2
        outside_width = (width / 2) + border_width / 2
        inside_height = (height / 2) - border_width / 2
        outside_height = (height / 2) + border_width / 2

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
            uncentered_point_list = []
            for point in unrotated_point_list:
                uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

        point_list = []
        for point in uncentered_point_list:
            point_list.append((point[0] + center_x, point[1] + center_y))

        _generic_draw_line_strip(point_list, color, gl.GL_TRIANGLE_STRIP)


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
    # Cache the program. But not on linux because it fails unit tests for some reason.
    # if not _generic_draw_line_strip.program or sys.platform == "linux":

    _generic_draw_line_strip.program = shader.program(
        vertex_shader=_line_vertex_shader,
        fragment_shader=_line_fragment_shader,
    )

    c4 = get_four_byte_color(color)
    c4e = c4 * len(point_list)
    a = array.array('B', c4e)
    color_buf = shader.buffer(a.tobytes())
    color_buf_desc = shader.BufferDescription(
        color_buf,
        '4B',
        ['in_color'],
        normalized=['in_color'],
    )

    def gen_flatten(my_list):
        return [item for sublist in my_list for item in sublist]

    vertices = array.array('f', gen_flatten(point_list))

    vbo_buf = shader.buffer(vertices.tobytes())
    vbo_buf_desc = shader.BufferDescription(
        vbo_buf,
        '2f',
        ['in_vert']
    )

    vao_content = [vbo_buf_desc, color_buf_desc]

    vao = shader.vertex_array(_generic_draw_line_strip.program, vao_content)
    with vao:
        _generic_draw_line_strip.program['Projection'] = get_projection().flatten()
        vao.render(mode=mode)


_generic_draw_line_strip.program = None

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

    # points = (start_x, start_y), (end_x, end_y)
    points = get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
    triangle_point_list = points[1], points[0], points[2], points[3]
    _generic_draw_line_strip(triangle_point_list, color, gl.GL_TRIANGLE_STRIP)


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

    triangle_point_list: PointList = []
    last_point = None
    for point in point_list:
        if last_point is not None:
            points = get_points_for_thick_line(last_point[0], last_point[1], point[0], point[1], line_width)
            reordered_points = points[1], points[0], points[2], points[0], points[2], points[3]
            # noinspection PyUnresolvedReferences
            triangle_point_list.extend(reordered_points)
            _generic_draw_line_strip(triangle_point_list, color, gl.GL_TRIANGLES)
            last_point = None
        else:
            last_point = point


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
    draw_rectangle_filled(x, y, size / 2, size / 2, color)


def _get_points_for_points(point_list, size):
    new_point_list = []
    hs = size / 2
    for point in point_list:
        x = point[0]
        y = point[1]
        new_point_list.append((x - hs, y - hs))
        new_point_list.append((x + hs, y - hs))
        new_point_list.append((x + hs, y + hs))

        new_point_list.append((x + hs, y + hs))
        new_point_list.append((x - hs, y - hs))
        new_point_list.append((x - hs, y + hs))

    return new_point_list


def draw_points(point_list: PointList,
                color: Color, size: float = 1):
    """
    Draw a set of points.

    :param PointList point_list: List of points Each point is
         in a list. So it is a list of lists.
    :param Color color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    :param float size: Size of the point in pixels.
    """
    new_point_list = _get_points_for_points(point_list, size)
    _generic_draw_line_strip(new_point_list, color, gl.GL_TRIANGLES)


# --- END POINT FUNCTIONS # # #

# --- BEGIN POLYGON FUNCTIONS # # #


def draw_polygon_filled(point_list: PointList,
                        color: Color):
    """
    Draw a polygon that is filled in.

    Args:
        :point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    Returns:
        None
    Raises:
        None
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
    p1 = -width // 2 + center_x, -height // 2 + center_y
    p2 = width // 2 + center_x, -height // 2 + center_y
    p3 = width // 2 + center_x, height // 2 + center_y
    p4 = -width // 2 + center_x, height // 2 + center_y

    if tilt_angle != 0:
        p1 = rotate_point(p1[0], p1[1], center_x, center_y, tilt_angle)
        p2 = rotate_point(p2[0], p2[1], center_x, center_y, tilt_angle)
        p3 = rotate_point(p3[0], p3[1], center_x, center_y, tilt_angle)
        p4 = rotate_point(p4[0], p4[1], center_x, center_y, tilt_angle)

    _generic_draw_line_strip((p1, p2, p4, p3), color, gl.GL_TRIANGLE_STRIP)


def draw_texture_rectangle(center_x: float, center_y: float, width: float,
                           height: float, texture: Texture, angle: float = 0,
                           alpha: int = 255,
                           repeat_count_x: int = 1, repeat_count_y: int = 1):
    """
    Draw a textured rectangle on-screen.

    :param float center_x: x coordinate of rectangle center.
    :param float center_y: y coordinate of rectangle center.
    :param float width: width of the rectangle.
    :param float height: height of the rectangle.
    :param int texture: identifier of texture returned from load_texture() call
    :param float angle: rotation of the rectangle. Defaults to zero.
    :param float alpha: Transparency of image. 0 is fully transparent, 255 (default) is visible
    :param int repeat_count_x: Unused for now
    :param int repeat_count_y: Unused for now
    """

    texture.draw(center_x, center_y, width,
                 height, angle, alpha, False,
                 repeat_count_x, repeat_count_y)


# noinspection PyUnusedLocal
def draw_xywh_rectangle_textured(bottom_left_x: float, bottom_left_y: float,
                                 width: float, height: float,
                                 texture: Texture, angle: float = 0,
                                 alpha: int = 255,
                                 repeat_count_x: int = 1, repeat_count_y: int = 1):
    """
    Draw a texture extending from bottom left to top right.

    :param float bottom_left_x: The x coordinate of the left edge of the rectangle.
    :param float bottom_left_y: The y coordinate of the bottom of the rectangle.
    :param float width: The width of the rectangle.
    :param float height: The height of the rectangle.
    :param int texture: identifier of texture returned from load_texture() call
    :param float angle: rotation of the rectangle. Defaults to zero.
    :param int alpha: Transparency of image. 0 is fully transparent, 255 (default) is visible
    :param int repeat_count_x: Unused for now
    :param int repeat_count_y: Unused for now
    """

    center_x = bottom_left_x + (width / 2)
    center_y = bottom_left_y + (height / 2)
    draw_texture_rectangle(center_x, center_y,
                           width, height,
                           texture,
                           angle=angle, alpha=alpha)


def get_pixel(x: int, y: int):
    """
    Given an x, y, will return RGB color value of that point.

    :param int x: x location
    :param int y: y location
    :returns: Color
    """
    # noinspection PyCallingNonCallable,PyTypeChecker

    # The window may be 'scaled' on hi-res displays. Particularly Macs. OpenGL
    # won't account for this, so we need to.
    pixel_ratio = get_window().get_pixel_ratio()
    x = int(pixel_ratio * x)
    y = int(pixel_ratio * y)

    a = (gl.GLubyte * 3)(0)
    gl.glReadPixels(x, y, 1, 1, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, a)
    red = a[0]
    green = a[1]
    blue = a[2]
    return red, green, blue


def get_image(x: int = 0, y: int = 0, width: int = None, height: int = None):
    """
    Get an image from the screen.

    :param int x: Start (left) x location
    :param int y: Start (top) y location
    :param int width: Width of image. Leave blank for grabbing the 'rest' of the image
    :param int height: Height of image. Leave blank for grabbing the 'rest' of the image

    You can save the image like:

    .. highlight:: python
    .. code-block:: python

        image = get_image()
        image.save('screenshot.png', 'PNG')
    """

    # Get the dimensions
    window = get_window()
    if window is None:
        raise RuntimeError("Handle to the current window is None")
    if width is None:
        width = window.width - x
    if height is None:
        height = window.height - y

    # Create an image buffer
    # noinspection PyTypeChecker
    image_buffer = (gl.GLubyte * (4 * width * height))(0)

    gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_buffer)
    image = PIL.Image.frombytes("RGBA", (width, height), image_buffer)
    image = PIL.ImageOps.flip(image)

    # image.save('glutout.png', 'PNG')
    return image
