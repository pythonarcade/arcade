from typing import Set

import arcade
from arcade.gui import UIFlatButton, UIGhostFlatButton
from arcade.gui.style import UIStyle


def test_ui_element_uses_default_style():
    button = UIFlatButton(
        "Love snakes.", center_x=100, center_y=100, min_size=(100, 30)
    )

    assert button._style == UIStyle.default_style()


def test_ui_style_has_on_change_event_type():
    style = UIStyle({})
    assert "on_style_change" in style.event_types


def test_ui_style_dispatches_event_on_change():
    style = UIStyle({})
    updated_style_classes = None

    @style.event()
    def on_style_change(style_classes: Set[str]):
        nonlocal updated_style_classes
        updated_style_classes = style_classes

    style.set_class_attrs("some-class", color=arcade.color.BLUE)

    assert {"some-class"} == updated_style_classes


def test_style_returns_property_for_ui_elements():
    style = UIStyle(
        {
            "flatbutton": {"normal_color": arcade.color.RED},
            "ghostflatbutton": {"normal_color": arcade.color.BLUE},
        }
    )
    flat = UIFlatButton(
        "Love snakes.", center_x=100, center_y=100, min_size=(100, 30), style=style
    )
    ghost = UIGhostFlatButton(
        "Love snakes.", center_x=100, center_y=100, min_size=(100, 30), style=style
    )

    assert flat.style_attr("normal_color") == arcade.color.RED
    assert ghost.style_attr("normal_color") == arcade.color.BLUE


def test_style_returns_property_for_custom_ui_element():
    class MyButton(UIFlatButton):
        """Custom button, which should use style attributes of FlatButton"""

        pass

    style = UIStyle(
        {
            "flatbutton": {"normal_color": arcade.color.RED},
        }
    )

    flat = MyButton(
        "Love snakes.", center_x=100, center_y=100, min_size=(100, 30), style=style
    )

    assert flat.style_attr("normal_color") == arcade.color.RED


def test_style_returns_none_for_unknown_ui_element_class():
    style = UIStyle(
        {
            "flatbutton": {"normal_color": arcade.color.RED},
        }
    )
    button = UIGhostFlatButton(
        "Love snakes.", center_x=100, center_y=100, min_size=(100, 30), style=style
    )

    assert button.style_attr("normal_color") is None


def test_new_class_for_custom_overwrites():
    style = UIStyle(
        {
            "flatbutton": {"normal_color": arcade.color.RED},
        }
    )
    button = UIGhostFlatButton(
        "Love snakes.", center_x=100, center_y=100, min_size=(100, 30), style=style
    )
    button.set_style_attrs(normal_color=arcade.color.BLUE)

    assert button.style_attr("normal_color") == arcade.color.BLUE
    assert len(style.data) == 2
