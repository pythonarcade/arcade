import pytest

import arcade
import arcade.gui
from arcade.gui import UIClickable


class TestClickable(UIClickable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.render()

    def render(self):
        self.normal_texture = arcade.load_texture(
            ":resources:gui_basic_assets/red_button_normal.png",
            can_cache=False,
            hit_box_algorithm="None",
        )
        self.hover_texture = arcade.load_texture(
            ":resources:gui_basic_assets/red_button_normal.png",
            can_cache=False,
            hit_box_algorithm="None",
        )
        self.focus_texture = arcade.load_texture(
            ":resources:gui_basic_assets/red_button_normal.png",
            can_cache=False,
            hit_box_algorithm="None",
        )
        self.press_texture = arcade.load_texture(
            ":resources:gui_basic_assets/red_button_normal.png",
            can_cache=False,
            hit_box_algorithm="None",
        )


@pytest.fixture()
def clickable(mock_mng) -> UIClickable:
    b = TestClickable(
        center_x=30,
        center_y=40,
    )

    mock_mng.add_ui_element(b)
    return b


def test_shows_normal_texture(clickable):
    assert clickable.texture == clickable.normal_texture


def test_shows_hover_texture(clickable):
    clickable.on_hover()
    assert clickable.texture == clickable.hover_texture


def test_shows_press_texture(clickable):
    clickable.on_press()
    assert clickable.texture == clickable.press_texture


def test_shows_focus_texture(clickable):
    clickable.on_focus()
    assert clickable.texture == clickable.focus_texture


def test_updates_texture_after_style_change(clickable):
    old_texture = clickable.normal_texture
    clickable.set_style_attrs(some_att="new_value")

    assert old_texture != clickable.normal_texture
    assert clickable.texture == clickable.normal_texture
