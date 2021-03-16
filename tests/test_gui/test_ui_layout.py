from unittest.mock import Mock

import pytest

import arcade
from arcade import SpriteSolidColor
from arcade.gui import UIEvent
from arcade.gui.layouts import UILayout
from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.box import UIBoxLayout
from tests.test_gui import dummy_element, T


class TestLayout(UILayout):
    """
    Allow tests for the base UILayout functions.
    """

    def __init__(self, **kwargs):
        super().__init__(size_hint=(0, 0), **kwargs)

    def place_elements(self):
        pass


def test_move_layout():
    layout = TestLayout()
    layout.width = 100
    layout.height = 50

    assert layout.left == 0
    assert layout.top == 0

    layout.move(10, 20)
    assert layout.left == 10
    assert layout.top == 20


def test_layout_has_proper_position():
    layout = TestLayout()
    layout.width = 100
    layout.height = 50
    layout.left = 50
    layout.top = 500

    assert layout.bottom == 450
    assert layout.right == 150


def test_layout_moves_children():
    layout = TestLayout()
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
def test_passes_ui_events(layout):
    # GIVEN
    element = dummy_element()
    element.on_ui_event = Mock()
    layout.pack(element)

    sprite = SpriteSolidColor(100, 50, arcade.color.GREEN)
    layout.pack(sprite)

    child_layout = UIBoxLayout()
    child_layout.on_ui_event = Mock()
    layout.pack(child_layout)

    test_event = UIEvent('ANY EVENT')

    # WHEN
    layout.on_ui_event(test_event)

    # THEN
    element.on_ui_event.assert_called_once_with(test_event)


@pytest.mark.parametrize(
    ['layout'], [
        T('VBox', UIBoxLayout()),
        T('HBox', UIBoxLayout(vertical=False)),
        T('Anchor', UIAnchorLayout(800, 600)),
    ]
)
def test_pack_adds_elements_to_draw_layer(layout: UILayout):
    ui_element = dummy_element()
    sprite = SpriteSolidColor(100, 50, arcade.color.GREEN)

    layout.pack(ui_element)
    layout.pack(sprite)

    assert len(ui_element.sprite_lists) == 1
    assert len(sprite.sprite_lists) == 1


@pytest.mark.parametrize(
    ['layout'], [
        T('VBox', UIBoxLayout()),
        T('HBox', UIBoxLayout(vertical=False)),
        T('Anchor', UIAnchorLayout(800, 600)),
    ]
)
def test_remove_child(layout):
    sprite = SpriteSolidColor(100, 50, arcade.color.GREEN)
    layout.pack(sprite)

    layout.remove(sprite)
    layout.do_layout()

    assert len(layout) == 0
    assert len(sprite.sprite_lists) == 0


@pytest.mark.parametrize(
    ['layout'], [
        T('VBox', UIBoxLayout()),
        T('HBox', UIBoxLayout(vertical=False)),
        T('Anchor', UIAnchorLayout(800, 600)),
    ]
)
def test_child_expanded_to_parent_size(layout: UILayout):
    ui_element = dummy_element()
    ui_element.size_hint = (1, 1)
    layout.width = 300
    layout.height = 400
    layout.pack(ui_element)

    layout.do_layout()

    assert ui_element.width == 300
    assert ui_element.height == 400


def test_hbox_children_expanded_to_parent_size():
    layout = UIBoxLayout(vertical=False)

    ui_element_1 = dummy_element()
    ui_element_1.size_hint = (1, 1)
    ui_element_2 = dummy_element()
    ui_element_2.size_hint = (0.75, 0.75)
    layout.width = 300
    layout.height = 400

    layout.pack(ui_element_1)
    layout.pack(ui_element_2)

    layout.do_layout()

    assert ui_element_1.width == 157
    assert ui_element_1.height == 400
    assert ui_element_2.width == 142
    assert ui_element_2.height == 300


def test_vbox_children_expanded_to_parent_size():
    layout = UIBoxLayout()

    ui_element_1 = dummy_element()
    ui_element_1.size_hint = (1, 1)
    ui_element_2 = dummy_element()
    ui_element_2.size_hint = (0.75, 0.75)
    layout.width = 300
    layout.height = 400

    layout.pack(ui_element_1)
    layout.pack(ui_element_2)

    layout.do_layout()

    assert ui_element_1.width == 300
    assert ui_element_1.height == 221
    assert ui_element_2.width == 225
    assert ui_element_2.height == 178


def test_anchor_children_expanded_to_parent_size():
    """
    Anchor layout does not prevent overdrawing! This is accepted for now.
    """
    layout = UIAnchorLayout(300, 400)

    ui_element_1 = dummy_element()
    ui_element_1.size_hint = (1, 1)
    ui_element_2 = dummy_element()
    ui_element_2.size_hint = (0.75, 0.75)

    layout.pack(ui_element_1)
    layout.pack(ui_element_2)

    layout.do_layout()
    assert ui_element_1.width == 300
    assert ui_element_1.height == 400
    assert ui_element_2.width == 225
    assert ui_element_2.height == 300