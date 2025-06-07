import array

from arcade import gl
from arcade.color import WHITE
from arcade.math import rotate_point
from arcade.sprite import BasicSprite
from arcade.texture import Texture
from arcade.texture_atlas.base import TextureAtlasBase
from arcade.types import LBWH, LRBT, XYWH, Color, Point2List, Rect, RGBOrA255
from arcade.window_commands import get_window

from .helpers import _generic_draw_line_strip


def draw_texture_rect(
    texture: Texture,
    rect: Rect,
    *,
    color: Color = WHITE,
    angle=0.0,
    blend=True,
    alpha=255,
    pixelated=False,
    atlas: TextureAtlasBase | None = None,
) -> None:
    """
    Draw a texture on a rectangle.

    Args:
        texture:
            The texture to draw.
        rect:
            Rectangle to draw the texture on.
        color:
             Color multiplier for the texture. Defaults to white.
        angle:
            Rotation of the texture in degrees. Defaults to zero.
        blend:
            If True, enable alpha blending. Defaults to True.
        alpha:
            Transparency of image. 0 is fully transparent, 255 (default) is fully opaque.
        atlas:
            The texture atlas the texture resides in.
            if not supplied the default texture atlas is used
    """
    ctx = get_window().ctx

    # Clamp alpha to 0-255
    alpha_normalized = max(0, min(255, alpha)) / 255.0

    if blend:
        ctx.enable(ctx.BLEND)
    else:
        ctx.disable(ctx.BLEND)

    atlas = atlas or ctx.default_atlas
    program = ctx.sprite_program_single_simple

    texture_id, _ = atlas.add(texture)
    if pixelated:
        atlas.texture.filter = gl.NEAREST, gl.NEAREST
        program.set_uniform_safe("uv_offset_bias", 0.0)
    else:
        atlas.texture.filter = gl.LINEAR, gl.LINEAR
        program.set_uniform_safe("uv_offset_bias", 1.0)

    atlas.texture.use(unit=0)
    atlas.use_uv_texture(unit=1)

    geometry = ctx.geometry_empty
    program["pos_rot"] = rect.x, rect.y, 0, angle
    program["color"] = color.normalized
    program["size"] = rect.width, rect.height
    program["texture_id"] = texture_id
    program["spritelist_color"] = 1.0, 1.0, 1.0, alpha_normalized

    geometry.render(program, mode=gl.TRIANGLE_STRIP, vertices=4)

    if blend:
        ctx.disable(ctx.BLEND)


def draw_sprite(
    sprite: BasicSprite,
    *,
    blend: bool = True,
    alpha=255,
    pixelated=False,
    atlas: TextureAtlasBase | None = None,
) -> None:
    """
    Draw a sprite.

    Args:
        sprite:
            The sprite to draw.
        blend:
            Draw the sprite with or without alpha blending
        alpha:
            Fade the sprite from completely transparent to opaque (range: 0 to 255)
        pixelated:
            If true the sprite will be render in pixelated style. Otherwise smooth/linear
        atlas:
            The texture atlas the texture resides in.
            if not supplied the default texture atlas is used
    """
    draw_texture_rect(
        sprite.texture,
        rect=XYWH(sprite.center_x, sprite.center_y, sprite.width, sprite.height),
        color=sprite.color,
        angle=sprite._angle,
        blend=blend,
        alpha=alpha,
        pixelated=pixelated,
        atlas=atlas,
    )


def draw_sprite_rect(
    sprite: BasicSprite,
    rect: Rect,
    *,
    blend: bool = True,
    alpha=255,
    pixelated=False,
    atlas: TextureAtlasBase | None = None,
) -> None:
    """Draw a sprite.

    Args:
        sprite:
            The sprite to draw.
        rect:
            The location and size of the sprite
        blend:
            Draw the sprite with or without alpha blending
        alpha:
            Fade the sprite from completely transparent to opaque (range: 0 to 255)
        pixelated:
            If true the sprite will be render in pixelated style.
            Otherwise smooth/linear
        atlas:
            The texture atlas the texture resides in.
            if not supplied the default texture atlas is used
    """
    draw_texture_rect(
        sprite.texture,
        rect=rect,
        color=sprite.color,
        angle=sprite._angle,
        blend=blend,
        alpha=alpha,
        pixelated=pixelated,
        atlas=atlas,
    )


def draw_lrbt_rectangle_outline(
    left: float,
    right: float,
    bottom: float,
    top: float,
    color: RGBOrA255,
    border_width: float = 1,
) -> None:
    """
    Draw a rectangle by specifying left, right, bottom and top edges.

    Args:
        left:
            The x coordinate of the left edge of the rectangle.
        right:
            The x coordinate of the right edge of the rectangle.
        bottom:
            The y coordinate of the rectangle bottom.
        top:
            The y coordinate of the top of the rectangle.
        color:
            The outline color as an RGBA :py:class:`tuple`, RGB
            :py:class:`tuple`, or a :py:class:`.Color` instance.
        border_width:
            The width of the border in pixels. Defaults to one.
    Raises:
        ValueError: Raised if left > right or top < bottom.
    """
    if left > right:
        raise ValueError("Left coordinate must be less than or equal to the right coordinate")

    if bottom > top:
        raise ValueError("Bottom coordinate must be less than or equal to the top coordinate")

    draw_rect_outline(LRBT(left, right, bottom, top), color, border_width)


def draw_lbwh_rectangle_outline(
    left: float,
    bottom: float,
    width: float,
    height: float,
    color: RGBOrA255,
    border_width: float = 1,
) -> None:
    """
    Draw a rectangle extending from bottom left to top right

    Args:
        left:
            The x coordinate of the left edge of the rectangle.
        bottom:
            The y coordinate of the bottom of the rectangle.
        width:
            The width of the rectangle.
        height:
            The height of the rectangle.
        color:
            The outline color as an RGBA :py:class:`tuple`, RGB
            :py:class:`tuple`, or a :py:class:`.Color` instance.
        border_width:
            The width of the border in pixels. Defaults to one.
    """
    draw_rect_outline(LBWH(left, bottom, width, height), color, border_width)


def draw_lrbt_rectangle_filled(
    left: float, right: float, bottom: float, top: float, color: RGBOrA255
) -> None:
    """
    Draw a rectangle by specifying left, right, bottom and top edges.

    Args:
        left:
            The x coordinate of the left edge of the rectangle.
        right:
            The x coordinate of the right edge of the rectangle.
        bottom:
            The y coordinate of the rectangle bottom.
        top:
            The y coordinate of the top of the rectangle.
        color:
            The fill color as an RGBA :py:class:`tuple`,
            RGB :py:class:`tuple`, or a :py:class:`.Color` instance.
    Raises:
        ValueError: Raised if left > right or top < bottom.
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
    left: float, bottom: float, width: float, height: float, color: RGBOrA255
) -> None:
    """
    Draw a filled rectangle extending from bottom left to top right

    Args:
        left:
            The x coordinate of the left edge of the rectangle.
        bottom:
            The y coordinate of the bottom of the rectangle.
        width:
            The width of the rectangle.
        height:
            The height of the rectangle.
        color:
            The fill color as an RGBA :py:class:`tuple`, RGB
            :py:class:`tuple`, :py:class:`.Color` instance
    """
    draw_rect_filled(LBWH(left, bottom, width, height), color)


def draw_rect_outline(
    rect: Rect, color: RGBOrA255, border_width: float = 1, tilt_angle: float = 0
) -> None:
    """
    Draw a rectangle outline.

    Args:
        rect:
            The rectangle to draw. a :py:class:`~arcade.Rect` instance.
        color:
            The outline color as an RGBA :py:class:`tuple`,
            RGB :py:class:`tuple`, or :py:class:`.Color` instance.
        border_width:
            width of the lines, in pixels.
        tilt_angle:
            rotation of the rectangle. Defaults to zero (clockwise).
    """

    HALF_BORDER = border_width / 2
    # Extremely unrolled code below

    # fmt: off
    left   = rect.left
    right  = rect.right
    bottom = rect.bottom
    top    = rect.top
    x      = rect.x
    y      = rect.y

    # o = outer, i = inner
    #
    # o_left, o_top                  o_right, o_top
    #  +----------------------------------------+
    #  | i_left, i_top          i_right, i_top  |
    #  |  +----------------------------------+  |
    #  |  |                                  |  |
    #  |  |                                  |  |
    #  |  |                                  |  |
    #  |  +----------------------------------+  |
    #  | i_left, i_bottom    i_right , i_bottom |
    #  +----------------------------------------+
    # o_left, o_bottom               o_right, o_bottom

    i_left   = left   + HALF_BORDER
    i_bottom = bottom + HALF_BORDER
    i_right  = right  - HALF_BORDER
    i_top    = top    - HALF_BORDER

    o_left   = left   - HALF_BORDER
    o_bottom = bottom - HALF_BORDER
    o_right  = right  + HALF_BORDER
    o_top    = top    + HALF_BORDER

    # Declared separately because the code below seems to break mypy
    point_list: Point2List

    # This is intentionally unrolled to minimize repacking tuples
    if tilt_angle == 0:
        point_list = (
            (o_left  , o_top   ),
            (i_left  , i_top   ),
            (o_right , o_top   ),
            (i_right , i_top   ),
            (o_right , o_bottom),
            (i_right , i_bottom),
            (o_left  , o_bottom),
            (i_left  , i_bottom),
            (o_left  , o_top   ),
            (i_left  , i_top   )
        )
    else:
        point_list = (
            rotate_point(o_left   , o_top   , x, y, tilt_angle),
            rotate_point(i_left   , i_top   , x, y, tilt_angle),
            rotate_point(o_right  , o_top   , x, y, tilt_angle),
            rotate_point(i_right  , i_top   , x, y, tilt_angle),
            rotate_point(o_right  , o_bottom, x, y, tilt_angle),
            rotate_point(i_right  , i_bottom, x, y, tilt_angle),
            rotate_point(o_left   , o_bottom, x, y, tilt_angle),
            rotate_point(i_left   , i_bottom, x, y, tilt_angle),
            rotate_point(o_left   , o_top   , x, y, tilt_angle),
            rotate_point(i_left   , i_top   , x, y, tilt_angle)
        )
    # fmt: on
    _generic_draw_line_strip(point_list, color, gl.TRIANGLE_STRIP)


def draw_rect_filled(rect: Rect, color: RGBOrA255, tilt_angle: float = 0) -> None:
    """
    Draw a filled-in rectangle.

    Args:
        rect:
            The rectangle to draw. a :py:class:`~arcade.Rect` instance.
        color:
            The fill color as an RGBA :py:class:`tuple`,
            RGB :py:class:`tuple`, or :py:class:`.Color` instance.
        tilt_angle:
            rotation of the rectangle (clockwise). Defaults to zero.
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

    geometry.render(program, instances=1)

    ctx.disable(ctx.BLEND)


# These might be "oddly specific" and also needs docstrings. Disabling or 3.0.0

# def draw_rect_outline_kwargs(
#     color: RGBAOrA255 = WHITE, border_width: int = 1, tilt_angle: float = 0, **kwargs: AsFloat
# ) -> None:
#     rect = Rect.from_kwargs(**kwargs)
#     draw_rect_outline(rect, color, border_width, tilt_angle)


# def draw_rect_filled_kwargs(
#     color: RGBAOrA255 = WHITE, tilt_angle: float = 0, **kwargs: AsFloat
# ) -> None:
#     rect = Rect.from_kwargs(**kwargs)
#     draw_rect_filled(rect, color, tilt_angle)
