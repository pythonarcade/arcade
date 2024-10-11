import array

from arcade import gl
from arcade.types import Color, RGBOrA255
from arcade.window_commands import get_window


def draw_circle_filled(
    center_x: float,
    center_y: float,
    radius: float,
    color: RGBOrA255,
    tilt_angle: float = 0,
    num_segments: int = -1,
) -> None:
    """
    Draw a filled-in circle.

    Args:
        center_x:
            x position that is the center of the circle.
        center_y:
            y position that is the center of the circle.
        radius:
            width of the circle.
        color:
            A 3 or 4 length tuple of 0-255 channel values
            or a :py:class:`.Color` instance.
        tilt_angle:
            Angle in degrees to tilt the circle. Useful for low segment count circles
        num_segments:
            Number of triangle segments that make up this circle.
            Higher is better quality, but slower render time.
            The default value of -1 means Arcade will try to calculate a reasonable
            amount of segments based on the size of the circle.
    """
    draw_ellipse_filled(
        center_x,
        center_y,
        radius * 2,
        radius * 2,
        color,
        tilt_angle=tilt_angle,
        num_segments=num_segments,
    )


def draw_circle_outline(
    center_x: float,
    center_y: float,
    radius: float,
    color: RGBOrA255,
    border_width: float = 1,
    tilt_angle: float = 0,
    num_segments: int = -1,
) -> None:
    """
    Draw the outline of a circle.

    Args:
        center_x:
            x position that is the center of the circle.
        center_y:
            y position that is the center of the circle.
        radius:
            width of the circle.
        color:
            A 3 or 4 length tuple of 0-255 channel values
            or a :py:class:`.Color` instance.
        border_width:
            Width of the circle outline in pixels.
        tilt_angle:
            Angle in degrees to tilt the circle (clockwise).
            Useful for low segment count circles
        num_segments:
            Number of triangle segments that make up this circle.
            Higher is better quality, but slower render time.
            The default value of -1 means Arcade will try to calculate a reasonable
            amount of segments based on the size of the circle.
    """
    draw_ellipse_outline(
        center_x=center_x,
        center_y=center_y,
        width=radius * 2,
        height=radius * 2,
        color=color,
        border_width=border_width,
        tilt_angle=tilt_angle,
        num_segments=num_segments,
    )


def draw_ellipse_filled(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBOrA255,
    tilt_angle: float = 0,
    num_segments: int = -1,
) -> None:
    """
    Draw a filled in ellipse.

    Args:
        center_x:
            x position that is the center of the circle.
        center_y:
            y position that is the center of the circle.
        width:
            width of the ellipse.
        height:
            height of the ellipse.
        color:
            A 3 or 4 length tuple of 0-255 channel values
            or a :py:class:`.Color` instance.
        color:
            Either a :py:class:`.Color` instance
            or an RGBA :py:class:`tuple` of 4 byte values (0 to 255).
        tilt_angle:
            Angle in degrees to tilt the ellipse (clockwise).
            Useful when drawing a circle with a low segment count, to make an octagon for example.
        num_segments:
            Number of triangle segments that make up this circle.
            Higher is better quality, but slower render time.
            The default value of -1 means Arcade will try to calculate a reasonable
            amount of segments based on the size of the circle.
    """
    # Fail immediately if we have no window or context
    window = get_window()
    ctx = window.ctx
    ctx.enable(ctx.BLEND)

    program = ctx.shape_ellipse_filled_unbuffered_program
    geometry = ctx.shape_ellipse_unbuffered_geometry
    buffer = ctx.shape_ellipse_unbuffered_buffer  # type: ignore

    # Normalize the color because this shader takes a float uniform
    color_normalized = Color.from_iterable(color).normalized

    # Pass data to the shader
    program["color"] = color_normalized
    program["shape"] = width / 2, height / 2, tilt_angle
    program["segments"] = num_segments
    buffer.orphan()
    buffer.write(data=array.array("f", (center_x, center_y)))

    geometry.render(program, mode=gl.POINTS, vertices=1)
    ctx.disable(ctx.BLEND)


def draw_ellipse_outline(
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    color: RGBOrA255,
    border_width: float = 1,
    tilt_angle: float = 0,
    num_segments: int = -1,
) -> None:
    """
    Draw the outline of an ellipse.

    Args:
        center_x:
            x position that is the center of the circle.
        center_y:
            y position that is the center of the circle.
        width:
            width of the ellipse.
        height:
            height of the ellipse.
        color:
            A 3 or 4 length tuple of 0-255 channel values
            or a :py:class:`.Color` instance.
        border_width:
            Width of the circle outline in pixels.
        tilt_angle:
            Angle in degrees to tilt the ellipse (clockwise).
            Useful when drawing a circle with a low segment count, to make an octagon for example.
        num_segments:
            Number of triangle segments that make up this circle.
            Higher is better quality, but slower render time.
            The default value of -1 means Arcade will try to calculate a reasonable
            amount of segments based on the size of the circle.
    """
    # Fail immediately if we have no window or context
    window = get_window()
    ctx = window.ctx
    program = ctx.shape_ellipse_outline_unbuffered_program
    geometry = ctx.shape_ellipse_outline_unbuffered_geometry
    buffer = ctx.shape_ellipse_outline_unbuffered_buffer  # type: ignore

    # Normalize the color because this shader takes a float uniform
    color_normalized = Color.from_iterable(color).normalized

    ctx.enable(ctx.BLEND)

    # Pass data to shader
    program["color"] = color_normalized
    program["shape"] = width / 2, height / 2, tilt_angle, border_width
    program["segments"] = num_segments
    buffer.orphan()
    buffer.write(data=array.array("f", (center_x, center_y)))

    geometry.render(program, mode=gl.POINTS, vertices=1)

    ctx.disable(ctx.BLEND)
