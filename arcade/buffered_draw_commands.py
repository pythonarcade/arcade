"""
Drawing commands that use vertex buffer objects (VBOs).

This module contains commands for basic graphics drawing commands,
but uses Vertex Buffer Objects. This keeps the vertices loaded on
the graphics card for much faster render times.
"""

import math
import itertools
from collections import defaultdict
import pyglet.gl as gl
import numpy as np

from typing import Iterable
from typing import TypeVar
from typing import Generic

from arcade.arcade_types import Color
from arcade.draw_commands import rotate_point
from arcade.arcade_types import PointList
from arcade.draw_commands import get_four_byte_color
from arcade.draw_commands import get_projection
from arcade.draw_commands import _get_points_for_thick_line
from arcade import shader


class VertexBuffer:
    """
    This class represents a `vertex buffer object`_ for internal library use. Clients
    of the library probably don't need to use this.

    Attributes:
        :vbo_id: ID of the vertex buffer as assigned by OpenGL
        :size:
        :width:
        :height:
        :color:


    .. _vertex buffer object:
       https://en.wikipedia.org/wiki/Vertex_Buffer_Object

    """
    def __init__(self, vbo_vertex_id: gl.GLuint, size: float, draw_mode: int, vbo_color_id: gl.GLuint = None):
        self.vbo_vertex_id = vbo_vertex_id
        self.vbo_color_id = vbo_color_id
        self.size = size
        self.draw_mode = draw_mode
        self.color = None
        self.line_width = 0


class Shape:
    def __init__(self):
        self.vao = None
        self.vbo = None
        self.program = None
        self.mode = None
        self.line_width = 1

    def draw(self):
        # program['Projection'].write(get_projection().tobytes())

        with self.vao:
            assert(self.line_width == 1)
            gl.glLineWidth(self.line_width)

            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            gl.glEnable(gl.GL_LINE_SMOOTH)
            gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
            gl.glHint(gl.GL_POLYGON_SMOOTH_HINT, gl.GL_NICEST)
            gl.glEnable(gl.GL_PRIMITIVE_RESTART)
            gl.glPrimitiveRestartIndex(2 ** 32 - 1)

            self.vao.render(mode=self.mode)


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

    points = _get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
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
    program = shader.program(
        vertex_shader='''
            #version 330
            uniform mat4 Projection;
            in vec2 in_vert;
            in vec4 in_color;
            out vec4 v_color;
            void main() {
               gl_Position = Projection * vec4(in_vert, 0.0, 1.0);
               v_color = in_color;
            }
        ''',
        fragment_shader='''
            #version 330
            in vec4 v_color;
            out vec4 f_color;
            void main() {
                f_color = v_color;
            }
        ''',
    )

    buffer_type = np.dtype([('vertex', '2f4'), ('color', '4B')])
    data = np.zeros(len(point_list), dtype=buffer_type)
    data['vertex'] = point_list
    data['color'] = [get_four_byte_color(color) for color in color_list]

    vbo = shader.buffer(data.tobytes())
    vao_content = [
        shader.BufferDescription(
            vbo,
            '2f 4B',
            ('in_vert', 'in_color'),
            normalized=['in_color']
        )
    ]

    vao = shader.vertex_array(program, vao_content)
    with vao:
        program['Projection'] = get_projection().flatten()

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

    :param PointList point_list:
    :param Color color:
    :param PointList line_width:

    :Returns Shape:

    """
    if line_width == 1:
        return create_line_generic(point_list, color, gl.GL_LINE_STRIP, line_width)
    else:
        triangle_point_list = []
        new_color_list = []
        for i in range(1, len(point_list)):
            start_x = point_list[i - 1][0]
            start_y = point_list[i - 1][1]
            end_x = point_list[i][0]
            end_y = point_list[i][1]
            color1 = color
            color2 = color
            points = _get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
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
    return create_line_generic(point_list, color, gl.GL_LINE_STRIP, line_width)


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
                             color_list: Iterable[Color],
                             line_width: float = 1):

    if line_width == 1:
        return create_line_generic_with_colors(point_list, color_list, gl.GL_LINES, line_width)
    else:

        triangle_point_list = []
        new_color_list = []
        for i in range(1, len(point_list), 2):
            start_x = point_list[i-1][0]
            start_y = point_list[i-1][1]
            end_x = point_list[i][0]
            end_y = point_list[i][1]
            color1 = color_list[i-1]
            color2 = color_list[i]
            points = _get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
            new_color_list += color1, color1, color2, color2
            triangle_point_list += points[1], points[0], points[2], points[3]

            shape = create_triangles_filled_with_colors(triangle_point_list, new_color_list)

        return shape



def create_polygon(point_list: PointList,
                   color: Color):
    """
    Draw a convex polygon. This will NOT draw a concave polygon.
    Because of this, you might not want to use this function.

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

    Args:
        center_x:
        center_y:
        width:
        height:
        color:
        border_width:
        tilt_angle:

    Returns:

    """
    return create_rectangle(center_x, center_y, width, height,
                            color, border_width, tilt_angle, filled=False)


def get_rectangle_points(center_x: float, center_y: float, width: float,
                         height: float, tilt_angle: float = 0) -> PointList:
    """
    Utility function that will return all four coordinate points of a
    rectangle given the x, y center, width, height, and rotation.

    Args:
        center_x:
        center_y:
        width:
        height:
        tilt_angle:

    Returns:

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
    Creating the rectangle, and then later drawing it with ``render_rectangle``
    is faster than calling ``draw_rectangle``.

    Args:
        center_x:
        center_y:
        width:
        height:
        color:
        border_width:
        tilt_angle:
        filled:

    Returns:

    """
    data = get_rectangle_points(center_x, center_y, width, height, tilt_angle)

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

        data = o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt

        if tilt_angle != 0:
            point_list_2 = []
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
    Creating the rectangles, and then later drawing it with ``render``
    is faster than calling ``draw_rectangle``.
    """

    shape_mode = gl.GL_TRIANGLE_STRIP
    new_point_list = [point_list[0], point_list[1], point_list[3], point_list[2]]
    new_color_list = [color_list[0], color_list[1], color_list[3], color_list[2]]
    return create_line_generic_with_colors(new_point_list, new_color_list, shape_mode)

def create_rectangles_filled_with_colors(point_list, color_list) -> Shape:
    """
    This function creates multiple rectangle/quads using a vertex buffer object.
    Creating the rectangles, and then later drawing it with ``render``
    is faster than calling ``draw_rectangle``.
    """

    shape_mode = gl.GL_TRIANGLES
    new_point_list = []
    new_color_list = []
    for i in range(0, len(point_list), 4):
        new_point_list += [point_list[0 + i], point_list[1 + i], point_list[3 + i]]
        new_point_list += [point_list[1 + i], point_list[3 + i], point_list[2 + i]]

        new_color_list += [color_list[0 + i], color_list[1 + i], color_list[3 + i]]
        new_color_list += [color_list[1 + i], color_list[3 + i], color_list[2 + i]]

    return create_line_generic_with_colors(new_point_list, new_color_list, shape_mode)

def create_triangles_filled_with_colors(point_list, color_list) -> Shape:
    """
    This function creates multiple rectangle/quads using a vertex buffer object.
    Creating the rectangles, and then later drawing it with ``render``
    is faster than calling ``draw_rectangle``.
    """

    shape_mode = gl.GL_TRIANGLE_STRIP
    return create_line_generic_with_colors(point_list, color_list, shape_mode)


def create_ellipse_filled(center_x: float, center_y: float,
                          width: float, height: float, color: Color,
                          tilt_angle: float = 0, num_segments: int = 128) -> Shape:
    """
    Create a filled ellipse. Or circle if you use the same width and height.
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
    """

    return create_ellipse(center_x, center_y, width, height, color,
                          border_width, tilt_angle, num_segments, filled=False)


def create_ellipse(center_x: float, center_y: float,
                   width: float, height: float, color: Color,
                   border_width: float = 1,
                   tilt_angle: float = 0, num_segments: int = 32,
                   filled=True) -> Shape:

    """
    This creates an ellipse vertex buffer object (VBO). It can later be
    drawn with ``render_ellipse_filled``. This method of drawing an ellipse
    is much faster than calling ``draw_ellipse_filled`` each frame.

    Note: This can't be unit tested on Appveyor because its support for OpenGL is
    poor.
    """
    # Create an array with the vertex point_list
    point_list = []

    for segment in range(num_segments):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta) + center_x
        y = height * math.sin(theta) + center_y

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


T = TypeVar('T', bound=Shape)


class ShapeElementList(Generic[T]):
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
        # List of sprites in the sprite list
        self.shape_list = []
        self.change_x = 0
        self.change_y = 0
        self._center_x = 0
        self._center_y = 0
        self._angle = 0
        self.program = shader.program(
            vertex_shader='''
                #version 330
                uniform mat4 Projection;
                uniform vec2 Position;
                uniform float Angle;

                in vec2 in_vert;
                in vec4 in_color;

                out vec4 v_color;
                void main() {
                    float angle = radians(Angle);
                    mat2 rotate = mat2(
                        cos(angle), sin(angle),
                        -sin(angle), cos(angle)
                    );
                   gl_Position = Projection * vec4(Position + (rotate * in_vert), 0.0, 1.0);
                   v_color = in_color;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec4 v_color;
                out vec4 f_color;
                void main() {
                    f_color = v_color;
                }
            ''',
        )
        # Could do much better using just one vbo and glDrawElementsBaseVertex
        self.batches = defaultdict(_Batch)
        self.dirties = set()

    def append(self, item: T):
        """
        Add a new shape to the list.
        """
        self.shape_list.append(item)
        group = (item.mode, item.line_width)
        self.batches[group].items.append(item)
        self.dirties.add(group)

    def remove(self, item: T):
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
        vbo = shader.Buffer.create_with_size(total_vbo_bytes)
        offset = 0
        gl.glBindBuffer(gl.GL_COPY_WRITE_BUFFER, vbo.buffer_id)
        # Copy all the shapes buffer in our own vbo
        for shape in batch.items:
            gl.glBindBuffer(gl.GL_COPY_READ_BUFFER, shape.vbo.buffer_id)
            gl.glCopyBufferSubData(
                gl.GL_COPY_READ_BUFFER,
                gl.GL_COPY_WRITE_BUFFER,
                gl.GLintptr(0),
                gl.GLintptr(offset),
                shape.vbo.size)
            offset += shape.vbo.size

        # Create an index buffer objet. It should count starting from 0. We need to
        # use a reset_idx to indicate that a new shape will start.
        reset_idx = 2 ** 32 - 1
        indices = []
        counter = itertools.count()
        for shape in batch.items:
            indices.extend(itertools.islice(counter, shape.vao.num_vertices))
            indices.append(reset_idx)
        del indices[-1]
        indices = np.array(indices)
        ibo = shader.Buffer(indices.astype('i4').tobytes())

        vao_content = [
            shader.BufferDescription(
                vbo,
                '2f 4B',
                ('in_vert', 'in_color'),
                normalized=['in_color']
            )
        ]
        vao = shader.vertex_array(self.program, vao_content, ibo)
        with self.program:
            self.program['Projection'] = get_projection().flatten()
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

    def __iter__(self) -> Iterable[T]:
        """ Return an iterable object of sprites. """
        return iter(self.shape_list)

    def __getitem__(self, i):
        return self.shape_list[i]

    def draw(self):
        """
        Draw everything in the list.
        """
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
        with self.program:
            self.program['Position'] = [self._center_x, self._center_y]

    center_x = property(_get_center_x, _set_center_x)

    def _get_center_y(self) -> float:
        """Get the center y coordinate of the ShapeElementList."""
        return self._center_y

    def _set_center_y(self, value: float):
        """Set the center y coordinate of the ShapeElementList."""
        self._center_y = value
        with self.program:
            self.program['Position'] = [self._center_x, self._center_y]

    center_y = property(_get_center_y, _set_center_y)

    def _get_angle(self) -> float:
        """Get the angle of the ShapeElementList in degrees."""
        return self._angle

    def _set_angle(self, value: float):
        """Set the angle of the ShapeElementList in degrees."""
        self._angle = value
        with self.program:
            self.program['Angle'] = self._angle

    angle = property(_get_angle, _set_angle)


class _Batch(Generic[T]):
    def __init__(self):
        self.shape = Shape()
        self.items = []
