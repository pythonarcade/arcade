from dataclasses import dataclass

import arcade
from arcade.types import Color
from arcade.gui.style import UIStyleBase


@dataclass
class ExampleStyleDict(UIStyleBase):
    some_color: Color
    some_int: int


def test_read_dict():
    sd = ExampleStyleDict(some_color=arcade.color.BLACK, some_int=42)

    assert sd["some_color"] == arcade.color.BLACK
    assert sd["some_int"] == 42


def test_read_attrs():
    sd = ExampleStyleDict(some_color=arcade.color.BLACK, some_int=42)

    assert sd.some_color == arcade.color.BLACK
    assert sd.some_int == 42


def test_write_dict():
    sd = ExampleStyleDict(some_color=arcade.color.BLACK, some_int=42)

    sd["some_color"] = arcade.color.RED

    assert sd["some_color"] == arcade.color.RED


def test_write_attrs():
    sd = ExampleStyleDict(some_color=arcade.color.BLACK, some_int=42)

    sd.some_color = arcade.color.RED

    assert sd.some_color == arcade.color.RED


def test_defaults_behavior_using_inheritance():
    @dataclass
    class DefaultStyle(UIStyleBase):
        some_int: int = 42
        some_color: Color = arcade.color.WHITE

    @dataclass
    class DefaultStyleSubclass(DefaultStyle):
        some_color: Color = arcade.color.GREEN
        some_str: str = "Arcade"
        some_other_str: str = "is cool!"

    subject = DefaultStyleSubclass(some_other_str="is awesome!")

    assert subject.some_int == 42
    assert subject.some_color == arcade.color.GREEN
    assert subject.some_str == "Arcade"
    assert subject.some_other_str == "is awesome!"
