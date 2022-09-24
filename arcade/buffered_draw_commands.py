"""
Drawing commands that use vertex buffer objects (VBOs).

This module contains commands for basic graphics drawing commands,
but uses Vertex Buffer Objects. This keeps the vertices loaded on
the graphics card for much faster render times.
"""

from array import array
import struct
import math
import itertools
from collections import defaultdict
import pyglet.gl as gl

from typing import List, Iterable, Sequence
from typing import TypeVar
from typing import Generic
from typing import cast

from arcade import Color
from arcade import Point, PointList
from arcade import get_four_byte_color
from arcade import get_window
from arcade import get_points_for_thick_line
from arcade.gl import BufferDescription

from .geometry_generic import rotate_point


class Shape:
    """
    Primitive drawing shape. This can be part of a ShapeElementList so
    shapes can be drawn faster in batch.
    """
    def __init__(self):
        self.vao = None
        self.vbo = None
        self.program = None
        self.mode = None
        self.line_width = 1

    def draw(self):
        """
        Draw this shape. Drawing this way isn't as fast as drawing multiple
        shapes batched together in a ShapeElementList.
        """
        assert self.line_width == 1
        gl.glLineWidth(self.line_width)

        gl.glEnable(gl.GL_PRIMITIVE_RESTART)
        gl.glPrimitiveRestartIndex(2 ** 32 - 1)

        self.vao.render(self.program, mode=self.mode)


def create_line(start_x: float, start_y: float, end_x: float, end_y: float,
                color: Color, line_width: float = 1) -> Shape:
    """
    Create a line to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    :param float start_x:
    :param float start_y:
    :param float end_x:
    :param float end_y:
    :param Color color:
    :param float line_width:

    :Returns Shape:

    """

    points = get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
    color_list = [color, color, color, color]
    triangle_point_list = points[1], points[0], points[2], points[3]
    shape = create_triangles_filled_with_colors(triangle_point_list, color_list)
    return shape


def create_line_generic_with_colors(point_list: PointList,
                                    color_list: Iterable[Color],
                                    shape_mode: int,
                                    line_width: float = 1) -> Shape:
    """
    This function is used by ``create_line_strip`` and ``create_line_loop``,
    just changing the OpenGL type for the line drawing.

    :param PointList point_list:
    :param Iterable[Color] color_list:
    :param float shape_mode:
    :param float line_width:

    :Returns Shape:
    """
    window = get_window()
    ctx = window.ctx
    program = ctx.line_generic_with_colors_program

    # Ensure colors have 4 components
    color_list = [get_four_byte_color(color) for color in color_list]

    vertex_size = 12  # 2f 4f1 = 12 bytes
    data = bytearray(vertex_size * len(point_list))
    for i, entry in enumerate(zip(point_list, color_list)):
        offset = i * vertex_size
        struct.pack_into("ffBBBB", data, offset, *entry[0], *entry[1])

    vbo = ctx.buffer(data=data)
    vao_content = [
        BufferDescription(
            vbo,
            '2f 4f1',
            ('in_vert', 'in_color'),
            normalized=['in_color']
        )
    ]

    vao = ctx.geometry(vao_content)

    shape = Shape()
    shape.vao = vao
    shape.vbo = vbo
    shape.program = program
    shape.mode = shape_mode
    shape.line_width = line_width

    return shape


def create_line_generic(point_list: PointList,
                        color: Color,
                        shape_mode: int, line_width: float = 1) -> Shape:
    """
    This function is used by ``create_line_strip`` and ``create_line_loop``,
    just changing the OpenGL type for the line drawing.
    """
    colors = [get_four_byte_color(color)] * len(point_list)
    shape = create_line_generic_with_colors(
        point_list,
        colors,
        shape_mode,
        line_width)

    return shape


def create_line_strip(point_list: PointList,
                      color: Color, line_width: float = 1):
    """
    Create a multi-point line to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    Internally, thick lines are created by two triangles.

    :param PointList point_list:
    :param Color color:
    :param PointList line_width:

    :Returns Shape:

    """
    if line_width == 1:
        return create_line_generic(point_list, color, gl.GL_LINE_STRIP, line_width)
    else:
        triangle_point_list: List[Point] = []
        new_color_list: List[Color] = []
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

        shape = create_triangles_filled_with_colors(triangle_point_list, new_color_list)
        return shape


def create_line_loop(point_list: PointList,
                     color: Color, line_width: float = 1):
    """
    Create a multi-point line loop to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    :param PointList point_list:
    :param Color color:
    :param float line_width:

    :Returns Shape:

    """
    point_list = list(point_list) + [point_list[0]]
    return create_line_strip(point_list, color, line_width)


def create_lines(point_list: PointList,
                 color: Color, line_width: float = 1):
    """
    Create a multi-point line loop to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    :param PointList point_list:
    :param Color color:
    :param float line_width:

    :Returns Shape:

    """
    return create_line_generic(point_list, color, gl.GL_LINES, line_width)


def create_lines_with_colors(point_list: PointList,
                             color_list: Sequence[Color],
                             line_width: float = 1):

    if line_width == 1:
        return create_line_generic_with_colors(point_list, color_list, gl.GL_LINES, line_width)
    else:

        triangle_point_list: List[Point] = []
        new_color_list: List[Color] = []
        for i in range(1, len(point_list), 2):
            start_x = point_list[i - 1][0]
            start_y = point_list[i - 1][1]
            end_x = point_list[i][0]
            end_y = point_list[i][1]
            color1 = color_list[i - 1]
            color2 = color_list[i]
            points = get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
            new_color_list += color1, color1, color2, color2
            triangle_point_list += points[1], points[0], points[2], points[3]

        return create_triangles_filled_with_colors(triangle_point_list, new_color_list)


def create_polygon(point_list: PointList,
                   color: Color):
    """
    Draw a convex polygon. This will NOT draw a concave polygon.
    Because of this, you might not want to use this function.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    :param PointList point_list:
    :param color:

    :Returns Shape:

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
    return create_line_generic(point_list, color, gl.GL_TRIANGLE_STRIP, 1)


def create_rectangle_filled(center_x: float, center_y: float, width: float,
                            height: float, color: Color,
                            tilt_angle: float = 0) -> Shape:
    """
    Create a filled rectangle.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    :param float center_x:
    :param float center_y:
    :param float width:
    :param float height:
    :param Color color:
    :param float tilt_angle:

    :Returns Shape:

    """
    return create_rectangle(center_x, center_y, width, height,
                            color, tilt_angle=tilt_angle)


def create_rectangle_outline(center_x: float, center_y: float, width: float,
                             height: float, color: Color,
                             border_width: float = 1, tilt_angle: float = 0) -> Shape:
    """
    Create a rectangle outline.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    :param float center_x:
    :param float center_y:
    :param float width:
    :param float height:
    :param Color color:
    :param Color border_width:
    :param float tilt_angle:

    Returns: Shape

    """
    return create_rectangle(center_x, center_y, width, height,
                            color, border_width, tilt_angle, filled=False)


def get_rectangle_points(center_x: float, center_y: float, width: float,
                         height: float, tilt_angle: float = 0) -> PointList:
    """
    Utility function that will return all four coordinate points of a
    rectangle given the x, y center, width, height, and rotation.

    :param float center_x:
    :param float center_y:
    :param float width:
    :param float height:
    :param float tilt_angle:

    Returns: PointList

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

    data = [(x1, y1),
            (x2, y2),
            (x3, y3),
            (x4, y4)]

    return data


def create_rectangle(center_x: float, center_y: float, width: float,
                     height: float, color: Color,
                     border_width: float = 1, tilt_angle: float = 0,
                     filled=True) -> Shape:
    """
    This function creates a rectangle using a vertex buffer object.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    :param float center_x:
    :param float center_y:
    :param float width:
    :param float height:
    :param Color color:
    :param float border_width:
    :param float tilt_angle:
    :param bool filled:

    """
    data: List[Point] = cast(List[Point], get_rectangle_points(center_x, center_y, width, height, tilt_angle))

    if filled:
        shape_mode = gl.GL_TRIANGLE_STRIP
        data[-2:] = reversed(data[-2:])
    else:

        i_lb = center_x - width / 2 + border_width / 2, center_y - height / 2 + border_width / 2
        i_rb = center_x + width / 2 - border_width / 2, center_y - height / 2 + border_width / 2
        i_rt = center_x + width / 2 - border_width / 2, center_y + height / 2 - border_width / 2
        i_lt = center_x - width / 2 + border_width / 2, center_y + height / 2 - border_width / 2

        o_lb = center_x - width / 2 - border_width / 2, center_y - height / 2 - border_width / 2
        o_rb = center_x + width / 2 + border_width / 2, center_y - height / 2 - border_width / 2
        o_rt = center_x + width / 2 + border_width / 2, center_y + height / 2 + border_width / 2
        o_lt = center_x - width / 2 - border_width / 2, center_y + height / 2 + border_width / 2

        data = [o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt]

        if tilt_angle != 0:
            point_list_2: List[Point] = []
            for point in data:
                new_point = rotate_point(point[0], point[1], center_x, center_y, tilt_angle)
                point_list_2.append(new_point)
            data = point_list_2

        border_width = 1
        shape_mode = gl.GL_TRIANGLE_STRIP

        # _generic_draw_line_strip(point_list, color, gl.GL_TRIANGLE_STRIP)

        # shape_mode = gl.GL_LINE_STRIP
        # data.append(data[0])

    shape = create_line_generic(data, color, shape_mode, border_width)
    return shape


def create_rectangle_filled_with_colors(point_list, color_list) -> Shape:
    """
    This function creates one rectangle/quad using a vertex buffer object.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    """

    shape_mode = gl.GL_TRIANGLE_STRIP
    new_point_list = [point_list[0], point_list[1], point_list[3], point_list[2]]
    new_color_list = [color_list[0], color_list[1], color_list[3], color_list[2]]
    return create_line_generic_with_colors(new_point_list, new_color_list, shape_mode)


def create_rectangles_filled_with_colors(point_list, color_list) -> Shape:
    """
    This function creates multiple rectangle/quads using a vertex buffer object.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    """

    shape_mode = gl.GL_TRIANGLES
    new_point_list: List[Point] = []
    new_color_list: List[Color] = []
    for i in range(0, len(point_list), 4):
        new_point_list += [point_list[0 + i], point_list[1 + i], point_list[3 + i]]
        new_point_list += [point_list[1 + i], point_list[3 + i], point_list[2 + i]]

        new_color_list += [color_list[0 + i], color_list[1 + i], color_list[3 + i]]
        new_color_list += [color_list[1 + i], color_list[3 + i], color_list[2 + i]]

    return create_line_generic_with_colors(new_point_list, new_color_list, shape_mode)


def create_triangles_filled_with_colors(point_list, color_list) -> Shape:
    """
    This function creates multiple rectangle/quads using a vertex buffer object.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    """

    shape_mode = gl.GL_TRIANGLE_STRIP
    return create_line_generic_with_colors(point_list, color_list, shape_mode)


def create_ellipse_filled(center_x: float, center_y: float,
                          width: float, height: float, color: Color,
                          tilt_angle: float = 0, num_segments: int = 128) -> Shape:
    """
    Create a filled ellipse. Or circle if you use the same width and height.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    """

    border_width = 1
    return create_ellipse(center_x, center_y, width, height, color,
                          border_width, tilt_angle, num_segments, filled=True)


def create_ellipse_outline(center_x: float, center_y: float,
                           width: float, height: float, color: Color,
                           border_width: float = 1,
                           tilt_angle: float = 0, num_segments: int = 128) -> Shape:
    """
    Create an outline of an ellipse.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

    """

    return create_ellipse(center_x, center_y, width, height, color,
                          border_width, tilt_angle, num_segments, filled=False)


def create_ellipse(center_x: float, center_y: float,
                   width: float, height: float, color: Color,
                   border_width: float = 1,
                   tilt_angle: float = 0, num_segments: int = 32,
                   filled=True) -> Shape:

    """
    This creates an ellipse vertex buffer object (VBO).

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.

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

    return create_line_generic(point_list, color, shape_mode, border_width)


def create_ellipse_filled_with_colors(center_x: float, center_y: float,
                                      width: float, height: float,
                                      outside_color: Color, inside_color: Color,
                                      tilt_angle: float = 0, num_segments: int = 32) -> Shape:
    """
    Draw an ellipse, and specify inside/outside color. Used for doing gradients.

    The function returns a Shape object that can be drawn with ``my_shape.draw()``.
    Don't create the shape in the draw method, create it in the setup method and then
    draw it in ``on_draw``.

    For even faster performance, add multiple shapes into a ShapeElementList and
    draw that list. This allows nearly unlimited shapes to be drawn just as fast
    as one.


    :param float center_x:
    :param float center_y:
    :param float width:
    :param float height:
    :param Color outside_color:
    :param float inside_color:
    :param float tilt_angle:
    :param int num_segments:

    :Returns Shape:

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


TShape = TypeVar('TShape', bound=Shape)


class ShapeElementList(Generic[TShape]):
    """
    A program can put multiple drawing primitives in a ShapeElementList, and then
    move and draw them as one. Do this when you want to create a more complex object
    out of simpler primitives. This also speeds rendering as all objects are drawn
    in one operation.
    """
    def __init__(self):
        """
        Initialize the sprite list
        """
        # The context this shape list belongs to
        self.ctx = get_window().ctx
        # List of sprites in the sprite list
        self.shape_list = []
        self.change_x = 0
        self.change_y = 0
        self._center_x = 0
        self._center_y = 0
        self._angle = 0
        self.program = self.ctx.shape_element_list_program
        # Could do much better using just one vbo and glDrawElementsBaseVertex
        self.batches = defaultdict(_Batch)
        self.dirties = set()

    def append(self, item: TShape):
        """
        Add a new shape to the list.
        """
        self.shape_list.append(item)
        group = (item.mode, item.line_width)
        self.batches[group].items.append(item)
        self.dirties.add(group)

    def remove(self, item: TShape):
        """
        Remove a specific shape from the list.
        """
        self.shape_list.remove(item)
        group = (item.mode, item.line_width)
        self.batches[group].items.remove(item)
        self.dirties.add(group)

    def _refresh_shape(self, group):
        # Create a buffer large enough to hold all the shapes buffers
        batch = self.batches[group]

        total_vbo_bytes = sum(s.vbo.size for s in batch.items)
        vbo = self.ctx.buffer(reserve=total_vbo_bytes)
        offset = 0
        # Copy all the shapes buffer in our own vbo
        for shape in batch.items:
            vbo.copy_from_buffer(shape.vbo, offset=offset)
            offset += shape.vbo.size

        # Create an index buffer object. It should count starting from 0. We need to
        # use a reset_idx to indicate that a new shape will start.
        reset_idx = 2 ** 32 - 1
        indices = []
        counter = itertools.count()
        for shape in batch.items:
            indices.extend(itertools.islice(counter, shape.vao.num_vertices))
            indices.append(reset_idx)
        del indices[-1]

        ibo = self.ctx.buffer(data=array('I', indices))

        vao_content = [
            BufferDescription(
                vbo,
                '2f 4f1',
                ('in_vert', 'in_color'),
                normalized=['in_color']
            )
        ]
        vao = self.ctx.geometry(vao_content, ibo)
        self.program['Position'] = [self.center_x, self.center_y]
        self.program['Angle'] = self.angle

        batch.shape.vao = vao
        batch.shape.vbo = vbo
        batch.shape.ibo = ibo
        batch.shape.program = self.program
        mode, line_width = group
        batch.shape.mode = mode
        batch.shape.line_width = line_width

    def move(self, change_x: float, change_y: float):
        """
        Move all the shapes ion the list
        :param change_x: Amount to move on the x axis
        :param change_y: Amount to move on the y axis
        """
        self.center_x += change_x
        self.center_y += change_y

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.shape_list)

    def __iter__(self) -> Iterable[TShape]:
        """ Return an iterable object of sprites. """
        return iter(self.shape_list)

    def __getitem__(self, i):
        return self.shape_list[i]

    def draw(self):
        """
        Draw everything in the list.
        """
        self.program['Position'] = [self._center_x, self._center_y]
        self.program['Angle'] = self._angle

        for group in self.dirties:
            self._refresh_shape(group)
        self.dirties.clear()
        for batch in self.batches.values():
            batch.shape.draw()

    def _get_center_x(self) -> float:
        """Get the center x coordinate of the ShapeElementList."""
        return self._center_x

    def _set_center_x(self, value: float):
        """Set the center x coordinate of the ShapeElementList."""
        self._center_x = value

    center_x = property(_get_center_x, _set_center_x)

    def _get_center_y(self) -> float:
        """Get the center y coordinate of the ShapeElementList."""
        return self._center_y

    def _set_center_y(self, value: float):
        """Set the center y coordinate of the ShapeElementList."""
        self._center_y = value
        self.program['Position'] = [self._center_x, self._center_y]

    center_y = property(_get_center_y, _set_center_y)

    def _get_angle(self) -> float:
        """Get the angle of the ShapeElementList in degrees."""
        return self._angle

    def _set_angle(self, value: float):
        """Set the angle of the ShapeElementList in degrees."""
        self._angle = value
        self.program['Angle'] = self._angle

    angle = property(_get_angle, _set_angle)


class _Batch(Generic[TShape]):
    def __init__(self):
        self.shape = Shape()
        self.items = []
