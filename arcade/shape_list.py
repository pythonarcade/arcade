"""
Drawing commands that use vertex buffer objects (VBOs).

This module contains commands for basic graphics drawing commands,
but uses Vertex Buffer Objects. This keeps the vertices loaded on
the graphics card for much faster render times.
"""

import itertools
import math
from array import array
from collections import OrderedDict
from collections.abc import Iterable, Sequence
from typing import (
    Generic,
    TypeVar,
    cast,
)

import pyglet.gl as gl

from arcade import ArcadeContext, get_points_for_thick_line, get_window
from arcade.gl import Buffer, BufferDescription, Geometry, Program
from arcade.math import rotate_point
from arcade.types import RGBA255, Color, Point, PointList
from arcade.utils import copy_dunders_unimplemented

__all__ = [
    "Shape",
    "create_line",
    "create_line_generic_with_colors",
    "create_line_generic",
    "create_line_strip",
    "create_line_loop",
    "create_lines",
    "create_lines_with_colors",
    "create_polygon",
    "create_rectangle_filled",
    "create_rectangle_outline",
    "get_rectangle_points",
    "create_rectangle",
    "create_rectangle_filled_with_colors",
    "create_rectangles_filled_with_colors",
    "create_triangles_filled_with_colors",
    "create_triangles_strip_filled_with_colors",
    "create_ellipse_filled",
    "create_ellipse_outline",
    "create_ellipse",
    "create_ellipse_filled_with_colors",
    "ShapeElementList",
]


@copy_dunders_unimplemented  # Temp fix for https://github.com/pythonarcade/arcade/issues/2074
class Shape:
    """
    A container for arbitrary geometry representing a shape.

    This shape can be drawn using the draw() method, or added to a
    ShapeElementList for drawing in batch.

    Args:
        points: A list of points that make up the shape.
        colors: A list of colors that correspond to the points.
        mode: The OpenGL drawing mode. Defaults to GL_TRIANGLES.
        program: The program to use when drawing this shape (Shape.draw() only)
    """

    def __init__(
        self,
        points: PointList,
        colors: Sequence[RGBA255],
        # vao: Geometry,
        # vbo: Buffer,
        mode: int = gl.GL_TRIANGLES,
        program: Program | None = None,
    ) -> None:
        self.ctx = get_window().ctx
        self.program = program or self.ctx.line_generic_with_colors_program
        self.mode = mode

        if len(points) != len(colors):
            raise ValueError("Number of points and colors must match.")

        self.points = points
        # Ensure colors have 4 components
        self.colors = [Color.from_iterable(color) for color in colors]
        # Pack the data into a single array
        self.data = array("f", [c for a in zip(self.points, self.colors) for b in a for c in b])
        self.vertices = len(points)

        self.geometry: Geometry | None = None
        self.buffer: Buffer | None = None

    def _init_geometry(self) -> None:
        # NOTE: When drawing a single shape we're not using an index buffer
        self.buffer = self.program.ctx.buffer(data=self.data)
        self.geometry = self.ctx.geometry(
            [
                BufferDescription(
                    self.buffer,
                    "2f 4f",
                    ("in_vert", "in_color"),
                ),
            ]
        )

    def draw(self) -> None:
        """
        Draw this shape. Drawing this way isn't as fast as drawing multiple
        shapes batched together in a ShapeElementList.
        """
        if self.geometry is None:
            self._init_geometry()

        if self.geometry is not None:
            self.geometry.render(self.program, mode=self.mode)


def create_line(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    color: RGBA255,
    line_width: float = 1,
) -> Shape:
    """
    Create a Shape object for a line.

    Args:
        start_x: Starting x position
        start_y: Starting y position
        end_x: Ending x position
        end_y: Ending y position
        color: Color of the line
        line_width: Width of the line
    """
    points = get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
    color_list = [color, color, color, color]
    triangle_point_list = points[1], points[0], points[2], points[3]
    return create_triangles_strip_filled_with_colors(triangle_point_list, color_list)


def create_line_generic_with_colors(
    point_list: PointList,
    color_sequence: Sequence[RGBA255],
    shape_mode: int,
) -> Shape:
    """
    This function is used by ``create_line_strip`` and ``create_line_loop``,
    just changing the OpenGL type for the line drawing.

    Args:
        point_list: A list of points that make up the shape.
        color_sequence: A sequence of colors such
            as a :py:class:`list`; each color must be either a
            :py:class:`~arcade.types.Color` instance or a 4-length RGBA
            :py:class:`tuple`.
        shape_mode: The OpenGL drawing mode. Defaults to ``GL_TRIANGLES``.
    """
    return Shape(
        points=point_list,
        colors=color_sequence,
        mode=shape_mode,
    )


def create_line_generic(
    point_list: PointList,
    color: RGBA255,
    shape_mode: int,
) -> Shape:
    """
    This function is used by ``create_line_strip`` and ``create_line_loop``,
    just changing the OpenGL type for the line drawing.

    Args:
        point_list: A list of points that make up the shape.
        color: A color such as a :py:class:`~arcade.types.Color`
        shape_mode: The OpenGL drawing mode. Defaults to ``GL_TRIANGLES``.
    """
    colors = [Color.from_iterable(color)] * len(point_list)
    return create_line_generic_with_colors(point_list, colors, shape_mode)


def create_line_strip(point_list: PointList, color: RGBA255, line_width: float = 1) -> Shape:
    """
    Create a multi-point line to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    Internally, thick lines are created by two triangles.

    Args:
        point_list: A list of points that make up the shape.
        color: A color such as a :py:class:`~arcade.types.Color`
        line_width: Width of the line
    """
    if line_width == 1:
        return create_line_generic(point_list, color, gl.GL_LINE_STRIP)

    triangle_point_list: list[Point] = []
    new_color_list: list[RGBA255] = []
    for i in range(1, len(point_list)):
        start_x = point_list[i - 1][0]
        start_y = point_list[i - 1][1]
        end_x = point_list[i][0]
        end_y = point_list[i][1]
        color1 = color
        color2 = color
        points = get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
        new_color_list += color1, color2, color1, color2
        triangle_point_list += points[1], points[0], points[2], points[3]

    return create_triangles_strip_filled_with_colors(triangle_point_list, new_color_list)


def create_line_loop(
    point_list: PointList,
    color: RGBA255,
    line_width: float = 1,
) -> Shape:
    """
    Create a multi-point line loop to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    Args:
        point_list: A list of points that make up the shape.
        color: A color such as a :py:class:`~arcade.types.Color`
        line_width: Width of the line
    """
    point_list = list(point_list) + [point_list[0]]
    return create_line_strip(point_list, color, line_width)


def create_lines(
    point_list: PointList,
    color: RGBA255,
) -> Shape:
    """
    Create a multi-point line loop to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    Args:
        point_list: A list of points that make up the shape.
        color: A color such as a :py:class:`~arcade.types.Color`
    """
    return create_line_generic(point_list, color, gl.GL_LINES)


def create_lines_with_colors(
    point_list: PointList,
    color_list: Sequence[RGBA255],
    line_width: float = 1,
) -> Shape:
    """
    Create a line segments to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    Args:
        point_list: Line segments start and end point tuples list
        color_list: Three or four byte tuples list for every point
        line_width: Width of the line
    """
    if line_width == 1:
        return create_line_generic_with_colors(point_list, color_list, gl.GL_LINES)

    triangle_point_list: list[Point] = []
    new_color_list: list[RGBA255] = []
    for i in range(1, len(point_list), 2):
        start_x = point_list[i - 1][0]
        start_y = point_list[i - 1][1]
        end_x = point_list[i][0]
        end_y = point_list[i][1]
        color1 = color_list[i - 1]
        color2 = color_list[i]
        points = get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
        new_color_list += color1, color1, color2, color1, color2, color2
        triangle_point_list += points[0], points[1], points[2], points[0], points[2], points[3]

    return create_triangles_filled_with_colors(triangle_point_list, new_color_list)


def create_polygon(point_list: PointList, color: RGBA255) -> Shape:
    """
    Draw a convex polygon. This will NOT draw a concave polygon.
    Because of this, you might not want to use this function.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        point_list: A list of points that make up the shape.
        color: A color such as a :py:class:`~arcade.types.Color`
    """
    # We assume points were given in order, either clockwise or counter clockwise.
    # Polygon is assumed to be monotone.
    # To fill the polygon, we start by one vertex, and we chain triangle strips
    # alternating with vertices to the left and vertices to the right of the
    # initial vertex.
    half = len(point_list) // 2
    interleaved = itertools.chain.from_iterable(
        itertools.zip_longest(point_list[:half], reversed(point_list[half:]))
    )
    point_list = [p for p in interleaved if p is not None]
    return create_line_generic(point_list, color, gl.GL_TRIANGLE_STRIP)


def create_rectangle_filled(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBA255,
    tilt_angle: float = 0,
) -> Shape:
    """
    Create a filled rectangle.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        center_x: X position of the center of the rectangle
        center_y: Y position of the center of the rectangle
        width: Width of the rectangle
        height: Height of the rectangle
        color: A color such as a :py:class:`~arcade.types.Color`
        tilt_angle: Angle to tilt the rectangle in degrees
    """
    return create_rectangle(
        center_x,
        center_y,
        width,
        height,
        color,
        tilt_angle=tilt_angle,
    )


def create_rectangle_outline(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBA255,
    border_width: float = 1,
    tilt_angle: float = 0,
) -> Shape:
    """
    Create a rectangle outline.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        center_x: X position of the center of the rectangle
        center_y: Y position of the center of the rectangle
        width: Width of the rectangle
        height: Height of the rectangle
        color: A color such as a :py:class:`~arcade.types.Color`
        border_width: Width of the border
        tilt_angle: Angle to tilt the rectangle in degrees
    """
    return create_rectangle(
        center_x,
        center_y,
        width,
        height,
        color,
        border_width,
        tilt_angle,
        filled=False,
    )


def get_rectangle_points(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    tilt_angle: float = 0,
) -> PointList:
    """
    Utility function that will return all four coordinate points of a
    rectangle given the x, y center, width, height, and rotation.

    Args:
        center_x: X position of the center of the rectangle
        center_y: Y position of the center of the rectangle
        width: Width of the rectangle
        height: Height of the rectangle
        tilt_angle: Angle to tilt the rectangle in degrees
    """
    x1 = -width / 2 + center_x
    y1 = -height / 2 + center_y

    x2 = -width / 2 + center_x
    y2 = height / 2 + center_y

    x3 = width / 2 + center_x
    y3 = height / 2 + center_y

    x4 = width / 2 + center_x
    y4 = -height / 2 + center_y

    if tilt_angle:
        x1, y1 = rotate_point(x1, y1, center_x, center_y, tilt_angle)
        x2, y2 = rotate_point(x2, y2, center_x, center_y, tilt_angle)
        x3, y3 = rotate_point(x3, y3, center_x, center_y, tilt_angle)
        x4, y4 = rotate_point(x4, y4, center_x, center_y, tilt_angle)

    return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]


def create_rectangle(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBA255,
    border_width: float = 1,
    tilt_angle: float = 0,
    filled=True,
) -> Shape:
    """
    This function creates a rectangle using a vertex buffer object.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        center_x: X position of the center of the rectangle
        center_y: Y position of the center of the rectangle
        width: Width of the rectangle
        height: Height of the rectangle
        color: A color such as a :py:class:`~arcade.types.Color`
        border_width: Width of the border
        tilt_angle: Angle to tilt the rectangle in degrees
        filled: If True, the rectangle is filled. If False, it is an outline.
    """
    data: list[Point] = cast(
        list[Point], get_rectangle_points(center_x, center_y, width, height, tilt_angle)
    )

    if filled:
        data[-2:] = reversed(data[-2:])
    else:
        i_lb = (
            center_x - width / 2 + border_width / 2,
            center_y - height / 2 + border_width / 2,
        )
        i_rb = (
            center_x + width / 2 - border_width / 2,
            center_y - height / 2 + border_width / 2,
        )
        i_rt = (
            center_x + width / 2 - border_width / 2,
            center_y + height / 2 - border_width / 2,
        )
        i_lt = (
            center_x - width / 2 + border_width / 2,
            center_y + height / 2 - border_width / 2,
        )

        o_lb = (
            center_x - width / 2 - border_width / 2,
            center_y - height / 2 - border_width / 2,
        )
        o_rb = (
            center_x + width / 2 + border_width / 2,
            center_y - height / 2 - border_width / 2,
        )
        o_rt = (
            center_x + width / 2 + border_width / 2,
            center_y + height / 2 + border_width / 2,
        )
        o_lt = (
            center_x - width / 2 - border_width / 2,
            center_y + height / 2 + border_width / 2,
        )

        data = [o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt]

        if tilt_angle != 0:
            point_list_2: list[Point] = []
            for point in data:
                new_point = rotate_point(point[0], point[1], center_x, center_y, tilt_angle)
                point_list_2.append(new_point)
            data = point_list_2

        border_width = 1

    shape_mode = gl.GL_TRIANGLE_STRIP
    return create_line_generic(data, color, shape_mode)


def create_rectangle_filled_with_colors(point_list, color_list) -> Shape:
    """
    This function creates one rectangle/quad using a vertex buffer object.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        point_list: List of points to create the rectangle from
        color_list: List of colors to create the rectangle from
    """
    shape_mode = gl.GL_TRIANGLE_STRIP
    new_point_list = [point_list[0], point_list[1], point_list[3], point_list[2]]
    new_color_list = [color_list[0], color_list[1], color_list[3], color_list[2]]
    return create_line_generic_with_colors(new_point_list, new_color_list, shape_mode)


def create_rectangles_filled_with_colors(point_list, color_list: Sequence[RGBA255]) -> Shape:
    """
    This function creates multiple rectangle/quads using a vertex buffer object.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        point_list: List of points to create the rectangles from
        color_list: List of colors to create the rectangles from
    """
    shape_mode = gl.GL_TRIANGLES
    new_point_list: list[Point] = []
    new_color_list: list[RGBA255] = []
    for i in range(0, len(point_list), 4):
        new_point_list += [point_list[0 + i], point_list[1 + i], point_list[3 + i]]
        new_point_list += [point_list[1 + i], point_list[3 + i], point_list[2 + i]]

        new_color_list += [color_list[0 + i], color_list[1 + i], color_list[3 + i]]
        new_color_list += [color_list[1 + i], color_list[3 + i], color_list[2 + i]]

    return create_line_generic_with_colors(new_point_list, new_color_list, shape_mode)


def create_triangles_filled_with_colors(
    point_list: PointList,
    color_sequence: Sequence[RGBA255],
) -> Shape:
    """
    This function creates multiple triangles using a vertex buffer object.
    Triangles are build for every 3 sequential vertices with step of 3 vertex
    Total amount of triangles to be rendered: len(point_list) / 3

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        point_list: Triangles vertices tuples.
        color_sequence: A sequence of colors such
            as a :py:class:`list`; each color must be either a
            :py:class:`~arcade.types.Color` instance or a 4-length RGBA
            :py:class:`tuple`.
    """
    shape_mode = gl.GL_TRIANGLES
    return create_line_generic_with_colors(point_list, color_sequence, shape_mode)


def create_triangles_strip_filled_with_colors(
    point_list,
    color_sequence: Sequence[RGBA255],
) -> Shape:
    """
    This function creates multiple triangles using a vertex buffer object.
    Triangles are built for every 3 sequential vertices with step of 1 vertex
    Total amount of triangles to be rendered: len(point_list) - 2

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        point_list: Triangles vertices tuples.
        color_sequence: A sequence of colors such
            as a :py:class:`list`; each color must be either a
            :py:class:`~arcade.types.Color` instance or a 4-length RGBA
            :py:class:`tuple`.
    """
    shape_mode = gl.GL_TRIANGLE_STRIP
    return create_line_generic_with_colors(point_list, color_sequence, shape_mode)


def create_ellipse_filled(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBA255,
    tilt_angle: float = 0,
    num_segments: int = 128,
) -> Shape:
    """
    Create a filled ellipse. Or circle if you use the same width and height.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        center_x: X position of the center of the ellipse
        center_y: Y position of the center of the ellipse
        width: Width of the ellipse
        height: Height of the ellipse
        color: A color such as a :py:class:`~arcade.types.Color`
        tilt_angle: Angle to tilt the ellipse
        num_segments: Number of segments to use to draw the ellipse
    """
    border_width = 1
    return create_ellipse(
        center_x,
        center_y,
        width,
        height,
        color,
        border_width,
        tilt_angle,
        num_segments,
        filled=True,
    )


def create_ellipse_outline(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBA255,
    border_width: float = 1,
    tilt_angle: float = 0,
    num_segments: int = 128,
) -> Shape:
    """
    Create an outline of an ellipse.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        center_x: X position of the center of the ellipse
        center_y: Y position of the center of the ellipse
        width: Width of the ellipse
        height: Height of the ellipse
        color: A color such as a :py:class:`~arcade.types.Color`
        border_width: Width of the border
        tilt_angle: Angle to tilt the ellipse
        num_segments: Number of segments to use to draw the ellipse
    """
    return create_ellipse(
        center_x,
        center_y,
        width,
        height,
        color,
        border_width,
        tilt_angle,
        num_segments,
        filled=False,
    )


def create_ellipse(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBA255,
    border_width: float = 1,
    tilt_angle: float = 0,
    num_segments: int = 32,
    filled: bool = True,
) -> Shape:
    """
    This creates an ellipse vertex buffer object (VBO).

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        center_x: X position of the center of the ellipse.
        center_y: Y position of the center of the ellipse.
        width: Width of the ellipse.
        height: Height of the ellipse.
        color: Color of the ellipse.
        border_width: Width of the border.
        tilt_angle: Angle to tilt the ellipse.
        num_segments: Number of segments to use to draw the ellipse.
        filled: If True, create a filled ellipse. If False, create an outline.
    """
    # Create an array with the vertex point_list
    point_list = []

    for segment in range(num_segments):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width / 2 * math.cos(theta) + center_x
        y = height / 2 * math.sin(theta) + center_y

        if tilt_angle:
            x, y = rotate_point(x, y, center_x, center_y, tilt_angle)

        point_list.append((x, y))

    if filled:
        half = len(point_list) // 2
        interleaved = itertools.chain.from_iterable(
            itertools.zip_longest(point_list[:half], reversed(point_list[half:]))
        )
        point_list = [p for p in interleaved if p is not None]
        shape_mode = gl.GL_TRIANGLE_STRIP
    else:
        point_list.append(point_list[0])
        shape_mode = gl.GL_LINE_STRIP

    return create_line_generic(point_list, color, shape_mode)


def create_ellipse_filled_with_colors(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    outside_color: RGBA255,
    inside_color: RGBA255,
    tilt_angle: float = 0,
    num_segments: int = 32,
) -> Shape:
    """
    Draw an ellipse, and specify inside/outside color. Used for doing gradients.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    Args:
        center_x: X position of the center of the ellipse.
        center_y:  Y position of the center of the ellipse.
        width: Width of the ellipse.
        height: Height of the ellipse.
        outside_color: Color of the outside of the ellipse.
        inside_color: Color of the inside of the ellipse.
        tilt_angle: Angle to tilt the ellipse.
        num_segments: Number of segments to use to draw the ellipse.
    """
    # Create an array with the vertex data
    # Create an array with the vertex point_list
    point_list = [(center_x, center_y)]

    for segment in range(num_segments):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta) + center_x
        y = height * math.sin(theta) + center_y

        if tilt_angle:
            x, y = rotate_point(x, y, center_x, center_y, tilt_angle)

        point_list.append((x, y))
    point_list.append(point_list[1])

    color_list = [inside_color] + [outside_color] * (num_segments + 1)
    return create_line_generic_with_colors(point_list, color_list, gl.GL_TRIANGLE_FAN)


TShape = TypeVar("TShape", bound=Shape)
"""
Type variable for Shape or subclasses.
"""


@copy_dunders_unimplemented
class ShapeElementList(Generic[TShape]):
    """
    A ShapeElementList is a list of shapes that can be drawn together
    in a back for better performance. ShapeElementLists are suited for
    drawing a large number of shapes that are static. If you need to
    move a lot of shapes it's better to use pyglet's shape system.

    Adding new shapes is fast, but removing them is slow.

    Args:
        blend: If True, shapes will be drawn with blending enabled.
    """

    def __init__(self, blend: bool = True) -> None:
        # The context this shape list belongs to
        self.ctx = get_window().ctx
        # List of sprites in the sprite list
        self.shape_list: list[TShape] = []
        self.change_x = 0.0
        self.change_y = 0.0
        self._center_x = 0.0
        self._center_y = 0.0
        self._angle = 0.0
        self.program = self.ctx.shape_element_list_program
        self.batches: dict[int, _Batch] = OrderedDict()
        self.dirties: set[_Batch] = set()

        self._blend = blend

    def append(self, item: TShape) -> None:
        """
        Add a new shape to the list.

        Args:
            item: Shape to add to the list.
        """
        self.shape_list.append(item)
        batch = self.batches.get(item.mode, None)
        if batch is None:
            batch = _Batch(
                self.ctx,
                self.program,
                item.mode,
            )
            self.batches[item.mode] = batch

        batch.append(item)

        # Mark the group as dirty
        self.dirties.add(batch)

    def remove(self, item: TShape) -> None:
        """
        Remove a specific shape from the list.

        Args:
            item: Shape to remove from the list.
        """
        self.shape_list.remove(item)
        batch = self.batches[item.mode]
        batch.remove(item)
        self.dirties.add(batch)

    def update(self) -> None:
        """
        Update the internals of the shape list.
        This is automatically called when you call draw().

        In some instances you may need to call this manually to
        update the shape list before drawing.
        """
        for group in self.dirties:
            group.update()

    def draw(self) -> None:
        """
        Draw all the shapes.
        """
        self.program["Position"] = self._center_x, self._center_y
        self.program["Angle"] = -self._angle

        self.update()
        self.dirties.clear()

        if self._blend:
            self.ctx.enable_only(self.ctx.BLEND)

        # Draw the batches
        for batch in self.batches.values():
            batch.draw()

        if self._blend:
            self.ctx.disable(self.ctx.BLEND)

    def clear(self, position: bool = True, angle: bool = True) -> None:
        """
        Clear all the contents from the shape list.

        Args:
            position: Reset the position to ``0, 0``
            angle: Reset the angle to ``0.0``
        """
        self.shape_list.clear()
        self.batches.clear()
        self.dirties.clear()
        if position:
            self.center_x = 0
            self.center_y = 0
        if angle:
            self.angle = 0

    def move(self, change_x: float, change_y: float) -> None:
        """
        Change the center_x/y of the shape list relative to the current position.

        Args:
            change_x: Amount to move on the x axis
            change_y: Amount to move on the y axis
        """
        self.center_x += change_x
        self.center_y += change_y

    @property
    def position(self) -> tuple[float, float]:
        """
        Get or set the position of the ShapeElementList.

        This is the equivalent of setting center_x and center_y
        """
        return self._center_x, self._center_y

    @position.setter
    def position(self, value: tuple[float, float]) -> None:
        self._center_x, self._center_y = value

    @property
    def center_x(self) -> float:
        """Get or set the center x coordinate of the shape list."""
        return self._center_x

    @center_x.setter
    def center_x(self, value: float) -> None:
        self._center_x = value

    @property
    def center_y(self) -> float:
        """Get or set the center y coordinate of the shape list."""
        return self._center_y

    @center_y.setter
    def center_y(self, value: float) -> None:
        self._center_y = value

    @property
    def angle(self) -> float:
        """Get or set the rotation in degrees (clockwise)"""
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = value

    def __len__(self) -> int:
        """Return the length of the shape list."""
        return len(self.shape_list)

    def __iter__(self) -> Iterable[TShape]:
        """Return an iterable object of sprites."""
        return iter(self.shape_list)

    def __getitem__(self, i):
        return self.shape_list[i]


class _Batch(Generic[TShape]):
    """
    A collection of shapes with the same configuration.

    The group uniqueness is based on the primitive mode
    """

    # Flags for keeping track of changes
    ADD = 1
    REMOVE = 3
    # The byte size of a vertex
    VERTEX_SIZE = 4 * 6  # 24 bytes (2 floats for position, 4 floats for color)
    RESET_IDX = 2**32 - 1

    def __init__(
        self,
        ctx: ArcadeContext,
        program: Program,
        mode: int,
    ) -> None:
        self.ctx = ctx
        self.program = program
        self.mode = mode

        self.vbo = self.ctx.buffer(reserve=1024 * self.VERTEX_SIZE, usage="dynamic")
        self.ibo = self.ctx.buffer(reserve=1024 * 4, usage="dynamic")

        self.geometry = self.ctx.geometry(
            content=[
                BufferDescription(
                    self.vbo,
                    "2f 4f",
                    ("in_vert", "in_color"),
                )
            ],
            index_buffer=self.ibo,
        )

        self.items: list[TShape] = []
        self.new_items: list[TShape] = []
        self.vertices = 0  # Total vertices in the batch
        self.elements = 0  # Total elements in the batch
        self.FLAGS = 0  # Flags to indicate changes

    def draw(self) -> None:
        """Draw the batch."""
        if self.elements == 0:
            return

        self.geometry.render(self.program, vertices=self.elements, mode=self.mode)

    def append(self, item: TShape) -> None:
        self.new_items.append(item)
        self.FLAGS |= self.ADD

    def remove(self, item: TShape) -> None:
        self.items.remove(item)
        self.FLAGS |= self.REMOVE

    def update(self) -> None:
        """Update the internals of the batch."""
        if self.FLAGS == 0:
            return

        # If only add flag is set we simply copy in the new data
        if self.FLAGS == self.ADD:
            new_data = array("f")
            new_ibo = array("I")
            counter = itertools.count(self.vertices)
            new_vertices = 0

            # Prepare data for new newly added items
            for item in self.new_items:
                # Update the batch vertex count
                new_vertices += item.vertices
                # Build up an array of new vertex data
                new_data.extend(item.data)

                # Build new index buffer data
                new_ibo.extend(itertools.islice(counter, item.vertices))
                new_ibo.append(self.RESET_IDX)  # Restart the primitive

            # Calculate the size of new and old data
            vbo_old_size = self.vertices * self.VERTEX_SIZE
            vbo_new_data_size = len(new_data) * self.VERTEX_SIZE
            vbo_new_size = vbo_old_size + vbo_new_data_size

            if vbo_new_size > self.vbo.size:
                # Copy out the buffer, resize and copy back
                buff = self.ctx.buffer(reserve=self.vbo.size)
                buff.copy_from_buffer(self.vbo)
                self.vbo.orphan(size=vbo_new_size * 2)
                self.vbo.copy_from_buffer(buff)

            # Calculate the index buffer size
            ibo_old_size = self.elements * 4
            ibo_new_data_size = len(new_ibo) * 4
            ibo_new_size = ibo_old_size + ibo_new_data_size

            if ibo_new_size > self.ibo.size:
                # Copy out the buffer, resize and copy back
                buff = self.ctx.buffer(reserve=self.ibo.size)
                buff.copy_from_buffer(self.ibo)
                self.ibo.orphan(size=ibo_new_size * 2)
                self.ibo.copy_from_buffer(buff)

            # Copy in the new data with offsets
            self.vbo.write(new_data, offset=vbo_old_size)
            self.ibo.write(new_ibo, offset=ibo_old_size)

            self.items.extend(self.new_items)
            self.new_items.clear()
            # Element count is the vertex count + the number of restart indices
            self.vertices += new_vertices
            self.elements = self.vertices + len(self.items)
        else:
            # Do the expensive rebuild
            # NOTE: We don't need to worry about buffer size here
            #       because we know the buffer hasn't grown.
            #       Simply collect the data and write it to the buffer.
            #       and update the vertex count.
            # NOTE: This can be optimized in the future, but pyglet shapes are better.
            self.items.extend(self.new_items)
            self.new_items.clear()

            data = array("f")
            ibo = array("I")
            counter = itertools.count()
            self.vertices = 0
            self.elements = 0

            for item in self.items:
                # Build up an array of new vertex data
                data.extend(item.data)
                # Build new index buffer data
                ibo.extend(itertools.islice(counter, item.vertices))
                ibo.append(self.RESET_IDX)  # Restart the primitive

                self.vertices += item.vertices
                self.elements += item.vertices + 1

            # Resize the buffers if needed
            data_size = self.vertices * self.VERTEX_SIZE
            if data_size > self.vbo.size:
                self.vbo.orphan(size=data_size * 2)

            index_size = self.elements * 4
            if index_size > self.ibo.size:
                self.ibo.orphan(size=index_size * 2)

            self.vbo.write(data)
            self.ibo.write(ibo)

        self.FLAGS = 0
