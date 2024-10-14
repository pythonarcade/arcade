from arcade.types import RGBOrA255

from .arc import draw_arc_filled, draw_arc_outline


def draw_parabola_filled(
    start_x: float,
    start_y: float,
    end_x: float,
    height: float,
    color: RGBOrA255,
    tilt_angle: float = 0,
) -> None:
    """
    Draws a filled in parabola.

    Args:
        start_x:
            The starting x position of the parabola
        start_y:
            The starting y position of the parabola
        end_x:
            The ending x position of the parabola
        height:
            The height of the parabola
        color:
            A 3 or 4 length tuple of 0-255 channel values
            or a :py:class:`.Color` instance.
        tilt_angle:
            The angle of the tilt of the parabola (clockwise)
    """
    center_x = (start_x + end_x) / 2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = start_x - end_x
    draw_arc_filled(center_x, center_y, width, height, color, start_angle, end_angle, tilt_angle)


def draw_parabola_outline(
    start_x: float,
    start_y: float,
    end_x: float,
    height: float,
    color: RGBOrA255,
    border_width: float = 1,
    tilt_angle: float = 0,
) -> None:
    """
    Draws the outline of a parabola.

    Args:
        start_x:
            The starting x position of the parabola
        start_y:
            The starting y position of the parabola
        end_x:
            The ending x position of the parabola
        height:
            The height of the parabola
        color:
            A 3 or 4 length tuple of 0-255 channel values
            or a :py:class:`.Color` instance.
        border_width:
            The width of the parabola
        tilt_angle:
            The angle of the tilt of the parabola (clockwise)
    """
    center_x = (start_x + end_x) / 2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = start_x - end_x
    draw_arc_outline(
        center_x,
        center_y,
        width,
        height,
        color,
        start_angle,
        end_angle,
        border_width,
        tilt_angle,
    )
