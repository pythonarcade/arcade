"""
Drawing commands that use the VBOs.

This module contains commands for basic graphics drawing commands,
but uses Vertex Buffer Objects. This keeps the vertices loaded on
the graphics card for much faster render times.
"""

import math
import ctypes
import pyglet.gl as gl

from typing import Iterable
from typing import TypeVar
from typing import Generic

from arcade.arcade_types import Color
from arcade.draw_commands import rotate_point
from arcade.arcade_types import PointList


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
    def __init__(self, vbo_vertex_id: gl.GLuint, size: float, draw_mode: int, vbo_color_id: gl.GLuint=None):
        self.vbo_vertex_id = vbo_vertex_id
        self.vbo_color_id = vbo_color_id
        self.size = size
        self.draw_mode = draw_mode
        self.color = None
        self.line_width = 0


def create_line(start_x: float, start_y: float, end_x: float, end_y: float,
                color: Color, border_width: float=1):
    """
    Create a line to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    :Example:

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> arcade.start_render()
    >>> line1 = arcade.create_line(0, 0, 100, 100, (255, 0, 0), 2)
    >>> arcade.render(line1)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)

    """
    data = [start_x, start_y,
            end_x, end_y]

    # print(data)
    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    data2 = (gl.GLfloat * len(data))(*data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)

    shape_mode = gl.GL_LINES
    shape = VertexBuffer(vbo_id, len(data) // 2, shape_mode)

    shape.color = color
    shape.line_width = border_width
    return shape


def create_line_generic(draw_type: int,
                        point_list: PointList,
                        color: Color, border_width: float=1):
    """
    This function is used by ``create_line_strip`` and ``create_line_loop``,
    just changing the OpenGL type for the line drawing.
    """
    data = []
    for point in point_list:
        data.append(point[0])
        data.append(point[1])

    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    data2 = (gl.GLfloat * len(data))(*data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)

    shape = VertexBuffer(vbo_id, len(data) // 2, draw_type)

    shape.color = color
    shape.line_width = border_width
    return shape


def create_line_strip(point_list: PointList,
                      color: Color, border_width: float=1):
    """
    Create a multi-point line to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    :Example:

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> arcade.start_render()
    >>> point_list = [[0, 0], [100, 100], [50, 0]]
    >>> line1 = arcade.create_line_strip(point_list, (255, 0, 0), 2)
    >>> arcade.render(line1)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)

    """
    return create_line_generic(gl.GL_LINE_STRIP, point_list, color, border_width)


def create_line_loop(point_list: PointList,
                     color: Color, border_width: float=1):
    """
    Create a multi-point line loop to be rendered later. This works faster than draw_line because
    the vertexes are only loaded to the graphics card once, rather than each frame.

    :Example:

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> arcade.start_render()
    >>> point_list = [[0, 0], [100, 100], [50, 0]]
    >>> line1 = arcade.create_line_loop(point_list, (255, 0, 0), 2)
    >>> arcade.render(line1)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    return create_line_generic(gl.GL_LINE_LOOP, point_list, color, border_width)


def create_polygon(point_list: PointList,
                   color: Color, border_width: float=1):
    """
    Draw a convex polygon. This will NOT draw a concave polygon.
    Because of this, you might not want to use this function.


    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> arcade.start_render()
    >>> point_list = [[0, 0], [100, 100], [50, 0]]
    >>> line1 = arcade.create_polygon(point_list, (255, 0, 0), 2)
    >>> arcade.render(line1)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    return create_line_generic(gl.GL_POLYGON, point_list, color, border_width)


def create_rectangle_filled(center_x: float, center_y: float, width: float,
                            height: float, color: Color,
                            tilt_angle: float=0) -> VertexBuffer:
    """
    Create a filled rectangle.
    """

    border_width = 0
    return create_rectangle(center_x, center_y, width, height, color, border_width, tilt_angle)


def create_rectangle_outline(center_x: float, center_y: float, width: float,
                             height: float, color: Color,
                             border_width: float=1, tilt_angle: float=0) -> VertexBuffer:
    """
    Create a rectangle outline.
    """
    return create_rectangle(center_x, center_y, width, height, color, border_width, tilt_angle, filled=False)


def get_rectangle_points(center_x: float, center_y: float, width: float,
                         height: float, tilt_angle: float=0):
    """
    Utility function that will return all four coordinate points of a
    rectangle given the x, y center, width, height, and rotation.
    """
    x1 = -width / 2 + center_x
    y1 = -height / 2 + center_y

    x2 = width / 2 + center_x
    y2 = -height / 2 + center_y

    x3 = width / 2 + center_x
    y3 = height / 2 + center_y

    x4 = -width / 2 + center_x
    y4 = height / 2 + center_y

    if tilt_angle:
        x1, y1 = rotate_point(x1, y1, center_x, center_y, tilt_angle)
        x2, y2 = rotate_point(x2, y2, center_x, center_y, tilt_angle)
        x3, y3 = rotate_point(x3, y3, center_x, center_y, tilt_angle)
        x4, y4 = rotate_point(x4, y4, center_x, center_y, tilt_angle)

    data = [x1, y1,
            x2, y2,
            x3, y3,
            x4, y4]

    return data


def create_rectangle(center_x: float, center_y: float, width: float,
                     height: float, color: Color,
                     border_width: float=0, tilt_angle: float=0,
                     filled=True) -> VertexBuffer:
    """
    This function creates a rectangle using a vertex buffer object.
    Creating the rectangle, and then later drawing it with ``render_rectangle``
    is faster than calling ``draw_rectangle``.

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> my_rect = arcade.create_rectangle(200, 200, 50, 50, (0, 255, 0), 3, 45)
    >>> arcade.render(my_rect)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    data = get_rectangle_points(center_x, center_y, width, height, tilt_angle)

    # print(data)
    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    data2 = (gl.GLfloat * len(data))(*data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)

    if filled:
        shape_mode = gl.GL_QUADS
    else:
        shape_mode = gl.GL_LINE_LOOP
    shape = VertexBuffer(vbo_id, len(data) // 2, shape_mode)

    shape.color = color
    shape.line_width = border_width
    return shape


def create_filled_rectangles(point_list, color: Color) -> VertexBuffer:
    """
    This function creates multiple rectangle/quads using a vertex buffer object.
    Creating the rectangles, and then later drawing it with ``render``
    is faster than calling ``draw_rectangle``.

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> point_list = [0, 0, 100, 0, 100, 100, 0, 100]
    >>> my_rect = arcade.create_filled_rectangles(point_list, (0, 255, 0))
    >>> arcade.render(my_rect)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    data = point_list

    # print(data)
    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    data2 = (gl.GLfloat * len(data))(*data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)

    shape_mode = gl.GL_QUADS
    shape = VertexBuffer(vbo_id, len(data) // 2, shape_mode)

    shape.color = color
    return shape


def create_filled_rectangles_with_colors(point_list, color_list) -> VertexBuffer:
    """
    This function creates multiple rectangle/quads using a vertex buffer object.
    Creating the rectangles, and then later drawing it with ``render``
    is faster than calling ``draw_rectangle``.

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> point_list = [0, 0, 100, 0, 100, 100, 0, 100]
    >>> color_list = [0, 255, 0]
    >>> my_shape = arcade.create_filled_rectangles_with_colors(point_list, color_list)
    >>> my_shape_list = ShapeElementList()
    >>> my_shape_list.append(my_shape)
    >>> my_shape_list.draw()
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)

    """

    vbo_vertex_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_vertex_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    gl_point_list = (gl.GLfloat * len(point_list))(*point_list)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_vertex_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(gl_point_list), gl_point_list, gl.GL_STATIC_DRAW)

    # Colors
    vbo_color_id = gl.GLuint()
    gl.glGenBuffers(1, ctypes.pointer(vbo_color_id))

    gl_color_list = (gl.GLfloat * len(color_list))(*color_list)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_color_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(gl_color_list), gl_color_list, gl.GL_STATIC_DRAW)

    shape_mode = gl.GL_QUADS
    shape = VertexBuffer(vbo_vertex_id, len(point_list) // 2, shape_mode, vbo_color_id=vbo_color_id)

    return shape


def create_ellipse_filled(center_x: float, center_y: float,
                          width: float, height: float, color: Color,
                          tilt_angle: float=0, num_segments=128) -> VertexBuffer:
    """
    Create a filled ellipse. Or circle if you use the same width and height.

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> my_shape = arcade.create_ellipse_filled(300, 300, 50, 100, (0, 255, 255, 64), 45, 64)
    >>> arcade.render(my_shape)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    border_width = 0
    return create_ellipse(center_x, center_y, width, height, color, border_width, tilt_angle, num_segments, True)


def create_ellipse_outline(center_x: float, center_y: float,
                           width: float, height: float, color: Color,
                           border_width: float=1,
                           tilt_angle: float=0, num_segments=128) -> VertexBuffer:
    """
    Create an outline of an ellipse.

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> my_shape = arcade.create_ellipse_outline(300, 300, 50, 100, (0, 255, 255), 45, 64)
    >>> arcade.render(my_shape)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    return create_ellipse(center_x, center_y, width, height, color, border_width, tilt_angle, num_segments, False)


def create_ellipse(center_x: float, center_y: float,
                   width: float, height: float, color: Color,
                   border_width: float=0,
                   tilt_angle: float=0, num_segments=32,
                   filled=True) -> VertexBuffer:

    """
    This creates an ellipse vertex buffer object (VBO). It can later be
    drawn with ``render_ellipse_filled``. This method of drawing an ellipse
    is much faster than calling ``draw_ellipse_filled`` each frame.

    Note: This can't be unit tested on Appveyor because its support for OpenGL is
    poor.

    >>> import arcade
    >>> arcade.open_window(800, 600, "Drawing Example")
    >>> arcade.start_render()
    >>> rect = arcade.create_ellipse(50, 50, 20, 20, arcade.color.RED, 2, 45)
    >>> arcade.render(rect)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)

    """
    # Create an array with the vertex data
    data = []

    for segment in range(num_segments + 1):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta) + center_x
        y = height * math.sin(theta) + center_y

        if tilt_angle:
            x, y = rotate_point(x, y, center_x, center_y, tilt_angle)

        data.extend([x, y])

    # Create an id for our vertex buffer
    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    data2 = (gl.GLfloat * len(data))(*data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)

    if filled:
        shape_mode = gl.GL_TRIANGLE_FAN
    else:
        shape_mode = gl.GL_LINE_LOOP

    shape = VertexBuffer(vbo_id, len(data) // 2, shape_mode)
    shape.color = color
    shape.line_width = border_width
    return shape


def render(shape: VertexBuffer):
    """
    Render an shape previously created with a ``create`` function.
    """
    # Set color
    if shape.color is None:
        raise ValueError("Error: Color parameter not set.")

    gl.glLoadIdentity()
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, shape.vbo_vertex_id)
    gl.glVertexPointer(2, gl.GL_FLOAT, 0, 0)

    if shape.line_width:
        gl.glLineWidth(shape.line_width)

    if len(shape.color) == 4:
        gl.glColor4ub(shape.color[0], shape.color[1], shape.color[2],
                      shape.color[3])
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    elif len(shape.color) == 3:
        gl.glDisable(gl.GL_BLEND)
        gl.glColor4ub(shape.color[0], shape.color[1], shape.color[2], 255)

    gl.glDrawArrays(shape.draw_mode, 0, shape.size)


def stripped_render(shape: VertexBuffer):
    """
    Render an shape previously created with a ``create`` function.
    Used by ``ShapeElementList.draw()`` for drawing several shapes in a batch.
    """

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, shape.vbo_vertex_id)
    gl.glVertexPointer(2, gl.GL_FLOAT, 0, 0)
    gl.glDrawArrays(shape.draw_mode, 0, shape.size)


def stripped_render_with_colors(shape: VertexBuffer):
    """
    Render an shape previously created with a ``create`` function.
    Used by ``ShapeElementList.draw()`` for drawing several shapes in a batch.
    This version also assumes there is a color list as part of the VBO.
    """

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, shape.vbo_vertex_id)
    gl.glVertexPointer(2, gl.GL_FLOAT, 0, None)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, shape.vbo_color_id)
    gl.glColorPointer(4, gl.GL_FLOAT, 0, None)
    gl.glDrawArrays(shape.draw_mode, 0, shape.size)


T = TypeVar('T', bound=VertexBuffer)


class ShapeElementList(Generic[T]):
    """
    A program can put multiple drawimg primitives in a ShapeElementList, and then
    move and draw them as one. Do this when you want to create a more complex object
    out of simpler primitives. This also speeds rendering as all objects are drawn
    in one operation.

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> my_list = ShapeElementList()
    >>> my_shape = arcade.create_ellipse_outline(50, 50, 20, 20, arcade.color.RED, 45)
    >>> my_list.append(my_shape)
    >>> my_shape = arcade.create_ellipse_filled(50, 50, 20, 20, arcade.color.RED, 2, 45)
    >>> my_list.append(my_shape)
    >>> my_shape = arcade.create_rectangle_filled(250, 50, 20, 20, arcade.color.RED, 45)
    >>> my_list.append(my_shape)
    >>> my_shape = arcade.create_rectangle_outline(450, 50, 20, 20, (127, 0, 27, 127), 2, 45)
    >>> my_list.append(my_shape)
    >>> my_list.move(5, 5)
    >>> arcade.start_render()
    >>> my_list.draw()
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)

    """
    def __init__(self):
        """
        Initialize the sprite list
        """
        # List of sprites in the sprite list
        self.shape_list = []
        self.change_x = 0
        self.change_y = 0
        self.center_x = 0
        self.center_y = 0
        self.angle = 0

    def append(self, item: T):
        """
        Add a new shape to the list.
        """
        self.shape_list.append(item)

    def remove(self, item: T):
        """
        Remove a specific shape from the list.
        """
        self.shape_list.remove(item)

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
        # gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glLoadIdentity()

        gl.glTranslatef(self.center_x, self.center_y, 0)
        if self.angle:
            gl.glRotatef(self.angle, 0, 0, 1)

        last_color = None
        last_line_width = None

        for shape in self.shape_list:
            if shape.vbo_color_id is not None:
                gl.glEnableClientState(gl.GL_COLOR_ARRAY)
            else:
                gl.glDisableClientState(gl.GL_COLOR_ARRAY)
                if last_color is None or last_color != shape.color:
                    last_color = shape.color

                    if len(shape.color) == 4:
                        gl.glColor4ub(shape.color[0], shape.color[1], shape.color[2],
                                      shape.color[3])
                        gl.glEnable(gl.GL_BLEND)
                        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
                    elif len(shape.color) == 3:
                        gl.glDisable(gl.GL_BLEND)
                        gl.glColor4ub(shape.color[0], shape.color[1], shape.color[2], 255)

            if shape.line_width and last_line_width != shape.line_width:
                last_line_width = shape.line_width
                gl.glLineWidth(shape.line_width)

            if shape.vbo_color_id is None:
                stripped_render(shape)
            else:
                stripped_render_with_colors(shape)
