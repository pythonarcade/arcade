import math
import ctypes
import pyglet.gl as gl

from typing import Iterable
# from pyglet.gl import glu as glu
from arcade.arcade_types import Color
from arcade.draw_commands import rotate_point


class VertexBuffer:
    """
    This class represents a
    `vertex buffer object`_.

    Attributes:
        :vbo_id: ID of the vertex buffer as assigned by OpenGL
        :size:
        :width:
        :height:
        :color:


    .. _vertex buffer object:
       https://en.wikipedia.org/wiki/Vertex_Buffer_Object

    >>> import arcade
    >>> x = arcade.VertexBuffer(0, 10, 10, 10)
    """
    def __init__(self, vbo_id: gl.GLuint, size: float, draw_mode: int):
        self.vbo_id = vbo_id
        self.size = size
        self.draw_mode = draw_mode
        self.color = None
        self.line_width = 0


def create_rectangle_filled(center_x: float, center_y: float, width: float,
                            height: float, color: Color,
                            tilt_angle: float=0) -> VertexBuffer:
    border_width = 0
    return create_rectangle(center_x, center_y, width, height, color, border_width, tilt_angle)


def create_rectangle_outline(center_x: float, center_y: float, width: float,
                             height: float, color: Color,
                             border_width: float=1, tilt_angle: float=0) -> VertexBuffer:

    return create_rectangle(center_x, center_y, width, height, color, border_width, tilt_angle, filled=False)


def create_rectangle(center_x: float, center_y: float, width: float,
                     height: float, color: Color,
                     border_width: float=0, tilt_angle: float=0,
                     filled=True) -> VertexBuffer:
    """
    This function creates a rectangle using a vertex buffer object.
    Creating the rectangle, and then later drawing it with ``render_rectangle``
    is faster than calling ``draw_rectangle``.
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

    print(data)
    vbo_id = gl.GLuint()

    gl.glGenBuffers(1, ctypes.pointer(vbo_id))

    # Create a buffer with the data
    # This line of code is a bit strange.
    # (gl.GLfloat * len(data)) creates an array of GLfloats, one for each number
    # (*data) initalizes the list with the floats. *data turns the list into a
    # tuple.
    data2 = (gl.GLfloat * len(data)) (*data)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    gl.GL_STATIC_DRAW)

    if filled:
        shape_mode = gl.GL_QUADS
    else:
        shape_mode = gl.GL_LINE_LOOP
    shape = VertexBuffer(vbo_id, len(data) // 2, shape_mode)

    shape.color = color
    return shape


def create_ellipse_filled(center_x: float, center_y: float,
                          width: float, height: float, color: Color,
                          tilt_angle: float=0, num_segments=128) -> VertexBuffer:

    border_width = 0
    return create_ellipse(center_x, center_y, width, height, color, border_width, tilt_angle, num_segments, True)


def create_ellipse_outline(center_x: float, center_y: float,
                           width: float, height: float, color: Color,
                           border_width: float=1,
                           tilt_angle: float=0, num_segments=128) -> VertexBuffer:

    return create_ellipse(center_x, center_y, width, height, color, border_width, tilt_angle, num_segments, False)


def create_ellipse(center_x: float, center_y: float,
                   width: float, height: float, color: Color,
                   border_width=0,
                   tilt_angle: float=0, num_segments=128,
                   filled=True) -> VertexBuffer:

    """
    This creates an ellipse vertex buffer object (VBO). It can later be
    drawn with ``render_ellipse_filled``. This method of drawing an ellipse
    is much faster than calling ``draw_ellipse_filled`` each frame.

    Note: THis can't be unit tested on Appveyor because its support for OpenGL is
    poor.

    >>> import arcade
    >>> arcade.open_window(800,600,"Drawing Example")
    >>> arcade.start_render()
    >>> rect = arcade.create_ellipse(50, 50)
    >>> arcade.render_ellipse_filled(rect, 0, 0, arcade.color.RED, 45)
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
    data2 = (gl.GLfloat * len(data)) (*data)

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

def render(shape: VertexBuffer, reload_identity=True):
    """
    Render an ellipse previously created with the ``create_ellipse`` function.
    """
    # Set color
    if shape.color == None:
        raise ValueError("Error: Color parameter not set.")


    gl.glLoadIdentity()
    gl.glVertexPointer(2, gl.GL_FLOAT, 0, 0)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, shape.vbo_id)

    gl.glDrawArrays(shape.draw_mode, 0, shape.size)

class ShapeList:
    def __init__(self):
        """
        Initialize the sprite list
        """
        # List of sprites in the sprite list
        self.shape_list = []
        self.change_x = 0
        self.change_y = 0
        self.tilt_angle = 0
        self.angle = 0

    def append(self, item: VertexBuffer):
        """
        Add a new shape to the list.
        """
        self.shape_list.append(item)

    def remove(self, item: VertexBuffer):
        """
        Remove a specific shape from the list.
        """
        self.shape_list.remove(item)

    def move(self, change_x: float, change_y: float):
        self.change_x += change_x
        self.change_y += change_y

    def __len__(self) -> int:
        """ Return the length of the sprite list. """
        return len(self.shape_list)

    def __iter__(self) -> Iterable[VertexBuffer]:
        """ Return an iterable object of sprites. """
        return iter(self.shape_list)

    def __getitem__(self, i):
        return self.shape_list[i]

    def draw(self, fast: bool=True):

        gl.glVertexPointer(2, gl.GL_FLOAT, 0, 0)
        gl.glLoadIdentity()

        gl.glTranslatef(self.change_x, self.change_y, 0)
        if self.angle:
            gl.glRotatef(self.angle, 0, 0, 1)

        last_color = None
        last_line_width = None

        for shape in self.shape_list:
            #if last_color is None or last_color != shape.color:
                last_color = shape.color
                if len(shape.color) == 4:
                    gl.glColor4ub(shape.color[0], shape.color[1], shape.color[2],
                                  shape.color[3])
                    gl.glEnable(gl.GL_BLEND)
                    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
                elif len(shape.color) == 3:
                    gl.glDisable(gl.GL_BLEND)
                    gl.glColor4ub(shape.color[0], shape.color[1], shape.color[2], 255)

            #if last_line_width is None or last_line_width == shape.line_width:
                last_line_width = shape.line_width
                if shape.line_width:
                    gl.glLineWidth(shape.line_width)

            render(shape, False)
