import arcade
import pytest

import arcade.gui
from arcade.gui import UIClickable


@pytest.fixture()
def button(mock_mng) -> UIClickable:
    normal_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_normal.png', can_cache=False)
    hover_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_normal.png', can_cache=False)
    focus_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_normal.png', can_cache=False)
    press_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_normal.png', can_cache=False)

    b = UIClickable(
        center_x=30,
        center_y=40,
    )
    b.normal_texture = normal_texture
    b.hover_texture = hover_texture
    b.press_texture = press_texture
    b.focus_texture = focus_texture

    mock_mng.add_ui_element(b)
    return b


def test_shows_normal_texture(button):
    assert button.texture == button.normal_texture


def test_shows_hover_texture(button):
    button.on_hover()
    assert button.texture == button.hover_texture


def test_shows_press_texture(button):
    button.on_press()
    assert button.texture == button.press_texture


def test_shows_focus_texture(button):
    button.on_focus()
    assert button.texture == button.focus_texture
