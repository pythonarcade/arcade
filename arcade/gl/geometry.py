"""
A module providing commonly used geometry
"""
import array
from typing import Tuple

from arcade.gl import Context, BufferDescription
from arcade.gl.vertex_array import Geometry


def _get_active_context() -> Context:
    ctx = Context.active
    if not ctx:
        raise RuntimeError("No context is currently activated")
    return ctx


def quad_2d_fs() -> Geometry:
    """Creates a screen aligned quad using normalized device coordinates"""
    return quad_2d(size=(2.0, 2.0))


def quad_2d(size: Tuple[float, float] = (1.0, 1.0), pos: Tuple[float, float] = (0.0, 0.0)) -> Geometry:
    """
    Creates 2D quad Geometry using 2 triangle strip with texture coordinates.

    :param tuple size: width and height
    :param float pos: Center position x and y
    :rtype: A :py:class:`~arcade.gl.geometry.Geometry` instance.       
    """
    ctx = _get_active_context()
    width, height = size
    x_pos, y_pos = pos

    data = array.array('f', [
        x_pos - width / 2.0, y_pos + height / 2.0, 0.0, 1.0,
        x_pos - width / 2.0, y_pos - height / 2.0, 0.0, 0.0,
        x_pos + width / 2.0, y_pos + height / 2.0, 1.0, 1.0,
        x_pos + width / 2.0, y_pos - height / 2.0, 1.0, 0.0,
    ])

    return ctx.geometry([BufferDescription(
        ctx.buffer(data=data),
        '2f 2f',
        ['in_vert', 'in_uv'],
    )], mode=ctx.TRIANGLE_STRIP)


def screen_rectangle(left: float, right: float, top: float, bottom: float) -> Geometry:
    """Create a screen rectangle by specifying left, right, top, and bottom edges"""
    width, height = right - left, top - bottom
    x_pos, y_pos = left + width / 2, right + height / 2
    print(f"size=({width}, {height}), pos=({x_pos}, {y_pos})")

    return quad_2d(pos=(x_pos, y_pos), size=(width, height))


# def screen_rectangle(rectangle_size=None,
#                      center_pos=None,
#                      screen_size=None):
#     """ Calculate a rectangle """

#     if rectangle_size is None and center_pos is None and screen_size is None:
#         rectangle_size = (2.0, 2.0)
#         center_pos = (0.0, 0.0)
#         screen_size = (2.0, 2.0)
#     elif screen_size is None:
#         screen_size = (get_window().width, get_window().height)
#         if center_pos is None:
#             center_pos = (get_window().width / 2.0, get_window().height / 2.0)
#     print(f"Size: {screen_size}")
#     screen_width, screen_height = screen_size
#     quad_width, quad_height = rectangle_size
#     normalized_width = quad_width / screen_width * 2
#     normalized_height = quad_height / screen_height * 2
#     xpos, ypos = center_pos
#     normalized_xpos = xpos / (screen_width / 2) - 1
#     normalized_ypos = ypos / (screen_height / 2) - 1
#     my_array = \
#         [
#             normalized_xpos - normalized_width / 2, normalized_ypos + normalized_height / 2, 0.0, 1.0,
#             normalized_xpos - normalized_width / 2, normalized_ypos - normalized_height / 2, 0.0, 0.0,
#             normalized_xpos + normalized_width / 2, normalized_ypos - normalized_height / 2, 1.0, 0.0,
#             normalized_xpos - normalized_width / 2, normalized_ypos + normalized_height / 2, 0.0, 1.0,
#             normalized_xpos + normalized_width / 2, normalized_ypos - normalized_height / 2, 1.0, 0.0,
#             normalized_xpos + normalized_width / 2, normalized_ypos + normalized_height / 2, 1.0, 1.0
#         ]
#     data = array.array('f', my_array)

#     ctx = get_window().ctx
#     vbo = ctx.buffer(data=data)
#     vao_content = [
#         BufferDescription(
#             vbo,
#             '2f 2f',
#             ('in_vert', 'in_uv'),
#         )
#     ]
#     return ctx.geometry(vao_content)
