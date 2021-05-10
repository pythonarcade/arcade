"""
Drawing text with pyglet label
"""
from typing import Tuple, Union

import arcade
import pyglet
from arcade.arcade_types import Color
from arcade.draw_commands import get_four_byte_color


class Text:

    def __init__(
        self,
        text: str,
        start_x: float,
        start_y: float,
        color: Color = arcade.color.WHITE,
        font_size: float = 12,
        width: int = 0,
        align: str = "left",
        font_name: Union[str, Tuple[str, ...]] = ("calibri", "arial"),
        bold: bool = False,
        italic: bool = False,
        anchor_x: str = "left",
        anchor_y: str = "baseline",
        rotation: float = 0,
    ):
        self._label = pyglet.text.Label(
            text=text,
            x=start_x,
            y=start_y,
            font_name=font_name,
            font_size=font_size,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=color,
            width=width,
            align=align,
            bold=bold,
            italic=italic,
        )

    @property
    def value(self) -> str:
        self._label.text

    @value.setter
    def value(self, value: str):
        self._label.text = value

    def draw(self):
        self._label.draw()


def draw_text(
    text: str,
    start_x: float,
    start_y: float,
    color: Color = arcade.color.WHITE,
    font_size: float = 12,
    width: int = 0,
    align: str = "left",
    font_name: Union[str, Tuple[str, ...]] = ("calibri", "arial"),
    bold: bool = False,
    italic: bool = False,
    anchor_x: str = "left",
    anchor_y: str = "baseline",
    rotation: float = 0,
):
    """
    Draws text to the screen using pyglet's label instead. Doesn't work.

    :param str text: Text to draw
    :param float start_x:
    :param float start_y:
    :param Color color: Color of the text
    :param float font_size: Size of the text
    :param float width:
    :param str align:
    :param Union[str, Tuple[str, ...]] font_name:
    :param bool bold:
    :param bool italic:
    :param str anchor_x:
    :param str anchor_y:
    :param float rotation:
    """
    # See : https://github.com/pyglet/pyglet/blob/ff30eadc2942553c9de96d6ce564ad1bc3128fb4/pyglet/text/__init__.py#L401

    color = get_four_byte_color(color)
    # Cache the states that are expensive to change
    key = f"{font_size}{font_name}{bold}{italic}{anchor_x}{anchor_y}{align}{width}"
    cache = arcade.get_window().ctx.pyglet_label_cache
    label = cache.get(key)
    if not label:
        label = pyglet.text.Label(
            text=text,
            x=start_x,
            y=start_y,
            font_name=font_name,
            font_size=font_size,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=color,
            width=width,
            align=align,
            bold=bold,
            italic=italic,
            multiline=True if width else None,
        )
        cache[key] = label

    # These updates are relatively cheap
    label.text = text
    label.x = start_x
    label.y = start_y
    label.color = color

    window = arcade.get_window()
    with arcade.get_window().ctx.pyglet_rendering():
        window.view = pyglet.math.Mat4().rotate(0.1, z=1)
        label.draw()


def create_text(*args, **kwargs):
    return Text("Hello")
