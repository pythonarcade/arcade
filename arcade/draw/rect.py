import array

from arcade import gl
from arcade.math import rotate_point
from arcade.types import RGBA255, PointList, AsFloat, Rect, LRBT, LBWH, Color
from arcade.texture import Texture
from arcade.window_commands import get_window
from .helpers import _generic_draw_line_strip
from arcade.color import WHITE


def draw_lrbt_rectangle_outline(
    left: float,
    right: float,
    bottom: float,
    top: float,
    color: RGBA255,
    border_width: float = 1,
) -> None:
    """
    Draw a rectangle by specifying left, right, bottom and top edges.

    :param left: The x coordinate of the left edge of the rectangle.
    :param right: The x coordinate of the right edge of the rectangle.
    :param bottom: The y coordinate of the rectangle bottom.
    :param top: The y coordinate of the top of the rectangle.
    :param color: The color of the rectangle.
    :param border_width: The width of the border in pixels. Defaults to one.
    :Raises ValueError: Raised if left > right or top < bottom.

    """
    if left > right:
        raise ValueError("Left coordinate must be less than or equal to " "the right coordinate")

    if bottom > top:
        raise ValueError("Bottom coordinate must be less than or equal to " "the top coordinate")

    draw_rect_outline(LRBT(left, right, bottom, top), color, border_width)


def draw_lbwh_rectangle_outline(
    left: float,
    bottom: float,
    width: float,
    height: float,
    color: RGBA255,
    border_width: float = 1,
) -> None:
    """
    Draw a rectangle extending from bottom left to top right

    :param bottom_left_x: The x coordinate of the left edge of the rectangle.
    :param bottom_left_y: The y coordinate of the bottom of the rectangle.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    :param color: The color of the rectangle as an RGBA
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    :param border_width: The width of the border in pixels. Defaults to one.
    """
    draw_rect_outline(LBWH(left, bottom, width, height), color, border_width)


def draw_lrbt_rectangle_filled(
    left: float, right: float, bottom: float, top: float, color: RGBA255
) -> None:
    """
    Draw a rectangle by specifying left, right, bottom and top edges.

    :param left: The x coordinate of the left edge of the rectangle.
    :param right: The x coordinate of the right edge of the rectangle.
    :param bottom: The y coordinate of the rectangle bottom.
    :param top: The y coordinate of the top of the rectangle.
    :param color: The color of the rectangle.
    :Raises ValueError: Raised if left > right or top < bottom.
    """
    if left > right:
        raise ValueError(
            f"Left coordinate {left} must be less than or equal to the right coordinate {right}"
        )

    if bottom > top:
        raise ValueError(
            f"Bottom coordinate {bottom} must be less than or equal to the top coordinate {top}"
        )

    draw_rect_filled(LRBT(left, right, bottom, top), color)


def draw_lbwh_rectangle_filled(
    left: float, bottom: float, width: float, height: float, color: RGBA255
) -> None:
    """
    Draw a filled rectangle extending from bottom left to top right

    :param left: The x coordinate of the left edge of the rectangle.
    :param bottom: The y coordinate of the bottom of the rectangle.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    :param color: The color of the rectangles an RGBA
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    """
    draw_rect_filled(LBWH(left, bottom, width, height), color)


def draw_scaled_texture_rectangle(
    center_x: float,
    center_y: float,
    texture: Texture,
    scale: float = 1.0,
    angle: float = 0,
    alpha: int = 255,
) -> None:
    """
    Draw a textured rectangle on-screen.

    .. warning:: This method can be slow!

                 Most users should consider using
                 :py:class:`arcade.Sprite` with
                 :py:class:`arcade.SpriteList` instead of this
                 function.

    OpenGL accelerates drawing by using batches to draw multiple things
    at once. This method doesn't do that.

    If you need finer control or less overhead than arcade allows,
    consider `pyglet's batching features
    <https://pyglet.readthedocs.io/en/master/modules/graphics/index.html#batches-and-groups>`_.

    :param center_x: x coordinate of rectangle center.
    :param center_y: y coordinate of rectangle center.
    :param texture: identifier of texture returned from
                        load_texture() call
    :param scale: scale of texture
    :param angle: rotation of the rectangle (clockwise). Defaults to zero.
    :param alpha: Transparency of image. 0 is fully transparent,
                        255 (default) is fully visible
    """
    texture.draw_scaled(center_x, center_y, scale, angle, alpha)


def draw_texture_rectangle(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    texture: Texture,
    angle: float = 0,
    alpha: int = 255,
) -> None:
    """
    Draw a textured rectangle on-screen.

    :param center_x: x coordinate of rectangle center.
    :param center_y: y coordinate of rectangle center.
    :param width: width of texture
    :param height: height of texture
    :param texture: identifier of texture returned from load_texture() call
    :param angle: rotation of the rectangle. Defaults to zero (clockwise).
    :param alpha: Transparency of image. 0 is fully transparent, 255 (default) is visible
    """
    texture.draw_sized(center_x, center_y, width, height, angle, alpha)


# def draw_texture_rect(texture: Texture, rect: Rect, blend=True) -> None:
#     """
#     Draw a texture on a rectangle.

#     :param texture: identifier of texture returned from load_texture() call
#     :param rect: Rectangle to draw the texture on.
#     """
#     ctx = get_window().ctx
#     if blend:
#         ctx.enable(ctx.BLEND)

#     texture_id, region = ctx.default_atlas.add(texture)

#     ctx.default_atlas.use_uv_texture(unit=0)
#     program = None  # texture program
#     # program["texture"] = 0
#     # program["alpha"] = 1.0
#     geometry = None  # texture geometry
#     # geometry.render(program, mode=gl.GL_TRIANGLE_STRIP, vertices=4)

#     if blend:
#         ctx.disable(ctx.BLEND)


def draw_lbwh_rectangle_textured(
    left: float,
    bottom: float,
    width: float,
    height: float,
    texture: Texture,
    angle: float = 0,
    alpha: int = 255,
) -> None:
    """
    Draw a texture extending from bottom left to top right.

    :param left: The x coordinate of the left edge of the rectangle.
    :param bottom: The y coordinate of the bottom of the rectangle.
    :param width: The width of the rectangle.
    :param height: The height of the rectangle.
    :param texture: identifier of texture returned from load_texture() call
    :param angle: rotation of the rectangle. Defaults to zero (clockwise).
    :param alpha: Transparency of image. 0 is fully transparent, 255 (default) is visible
    """

    center_x = left + (width / 2)
    center_y = bottom + (height / 2)
    texture.draw_sized(center_x, center_y, width, height, angle=angle, alpha=alpha)


# Reference implementations: drawing of new Rect


def draw_rect_outline(
    rect: Rect, color: RGBA255, border_width: float = 1, tilt_angle: float = 0
) -> None:
    """
    Draw a rectangle outline.

    :param rect: The rectangle to draw.
        a :py:class`~arcade.types.Rect` instance.
    :param color: The color of the rectangle.
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    :param border_width: width of the lines, in pixels.
    :param tilt_angle: rotation of the rectangle. Defaults to zero (clockwise).
    """

    HALF_BORDER = border_width / 2

    # fmt: off
    i_lb = rect.bottom_left.x  + HALF_BORDER, rect.bottom_left.y  + HALF_BORDER
    i_rb = rect.bottom_right.x - HALF_BORDER, rect.bottom_right.y + HALF_BORDER
    i_rt = rect.top_right.x    - HALF_BORDER, rect.top_right.y    - HALF_BORDER
    i_lt = rect.top_left.x     + HALF_BORDER, rect.top_left.y     - HALF_BORDER
    o_lb = rect.bottom_left.x  - HALF_BORDER, rect.bottom_left.y  - HALF_BORDER
    o_rb = rect.bottom_right.x + HALF_BORDER, rect.bottom_right.y - HALF_BORDER
    o_rt = rect.top_right.x    + HALF_BORDER, rect.top_right.y    + HALF_BORDER
    o_lt = rect.top_left.x     - HALF_BORDER, rect.top_right.y    + HALF_BORDER
    # fmt: on

    point_list: PointList = (o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt)

    if tilt_angle != 0:
        point_list_2 = []
        for point in point_list:
            new_point = rotate_point(point[0], point[1], rect.x, rect.y, tilt_angle)
            point_list_2.append(new_point)
        point_list = point_list_2

    _generic_draw_line_strip(point_list, color, gl.TRIANGLE_STRIP)


def draw_rect_filled(rect: Rect, color: RGBA255, tilt_angle: float = 0) -> None:
    """
    Draw a filled-in rectangle.

    :param rect: The rectangle to draw.
        a :py:class`~arcade.types.Rect` instance.
    :param color: The color of the rectangle as an RGBA
        :py:class:`tuple` or :py:class`~arcade.types.Color` instance.
    :param tilt_angle: rotation of the rectangle (clockwise). Defaults to zero.
    """
    # Fail if we don't have a window, context, or right GL abstractions
    window = get_window()
    ctx = window.ctx
    program = ctx.shape_rectangle_filled_unbuffered_program  # type: ignore
    geometry = ctx.shape_rectangle_filled_unbuffered_geometry
    buffer = ctx.shape_rectangle_filled_unbuffered_buffer  # type: ignore

    # Validate & normalize to a pass the shader an RGBA float uniform
    color_normalized = Color.from_iterable(color).normalized

    ctx.enable(ctx.BLEND)

    # Pass data to the shader
    program["color"] = color_normalized
    program["shape"] = rect.width, rect.height, tilt_angle
    buffer.orphan()
    buffer.write(data=array.array("f", (rect.x, rect.y)))

    geometry.render(program, mode=ctx.POINTS, vertices=1)

    ctx.disable(ctx.BLEND)


def draw_rect_outline_kwargs(
    color: RGBA255 = WHITE, border_width: int = 1, tilt_angle: float = 0, **kwargs: AsFloat
) -> None:
    rect = Rect.from_kwargs(**kwargs)
    draw_rect_outline(rect, color, border_width, tilt_angle)


def draw_rect_filled_kwargs(
    color: RGBA255 = WHITE, tilt_angle: float = 0, **kwargs: AsFloat
) -> None:
    rect = Rect.from_kwargs(**kwargs)
    draw_rect_filled(rect, color, tilt_angle)
