import pytest

import arcade
from arcade import SpriteSolidColor
from arcade.gui.layouts import UIAbstractLayout
from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.box import UIBoxLayout
from tests.test_gui import dummy_element
from . import T


class TestAbstractLayout(UIAbstractLayout):
    """
    Allow tests for the base UILayout functions.
    """

    def place_elements(self):
        pass


def test_move_layout():
    layout = TestAbstractLayout()
    layout.width = 100
    layout.height = 50

    assert layout.left == 0
    assert layout.top == 0

    layout.move(10, 20)
    assert layout.left == 10
    assert layout.top == 20


def test_layout_has_proper_position():
    layout = TestAbstractLayout()
    layout.width = 100
    layout.height = 50
    layout.left = 50
    layout.top = 500

    assert layout.bottom == 450
    assert layout.right == 150


def test_layout_moves_children():
    layout = TestAbstractLayout()
    child = dummy_element()
    layout.pack(child)

    layout.move(10, 20)
    assert child.center_x == 10
    assert child.center_y == 20

@pytest.mark.parametrize(
    ['layout'], [
        T('VBox', UIBoxLayout()),
        T('HBox', UIBoxLayout(vertical=False)),
        T('Anchor', UIAnchorLayout(800, 600)),
    ]
)
def test_pack_adds_elements_to_draw_layer(layout: UIAbstractLayout):
    ui_element = dummy_element()
    sprite = SpriteSolidColor(100, 50, arcade.color.GREEN)

    layout.pack(ui_element)
    layout.pack(sprite)

    assert len(ui_element.sprite_lists) == 1
    assert len(sprite.sprite_lists) == 1