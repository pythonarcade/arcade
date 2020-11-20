import pytest

from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.box import UIBoxLayout
from tests.test_gui import dummy_element


@pytest.fixture()
def anchor_layout():
    layout = UIAnchorLayout(800, 600)
    layout.left = 55
    layout.top = 88
    return layout


def test_anchor_bottom_left(anchor_layout):
    element_1 = dummy_element()

    anchor_layout.pack(element_1, bottom=100, left=10)
    anchor_layout.refresh()

    assert element_1.bottom == anchor_layout.bottom + 100
    assert element_1.left == anchor_layout.left + 10


def test_anchor_bottom_right(anchor_layout):
    element_1 = dummy_element()

    anchor_layout.pack(element_1, bottom=100, right=10)
    anchor_layout.refresh()

    assert element_1.bottom == anchor_layout.bottom + 100
    assert element_1.right == anchor_layout.right - 10


def test_anchor_top_right(anchor_layout):
    element_1 = dummy_element()

    anchor_layout.pack(element_1, top=100, right=10)
    anchor_layout.refresh()

    assert element_1.top == anchor_layout.top - 100
    assert element_1.right == anchor_layout.right - 10


def test_anchor_top_left(anchor_layout):
    element_1 = dummy_element()

    anchor_layout.pack(element_1, top=100, left=10)
    anchor_layout.refresh()

    assert element_1.top == anchor_layout.top - 100
    assert element_1.left == anchor_layout.left + 10


def test_anchor_layout_support_fill_x():
    anchor = UIAnchorLayout(800, 600)
    box = UIBoxLayout(vertical=False)

    anchor.pack(box, bottom=0, left=0, fill_x=True)
    box.pack(dummy_element())
    anchor.refresh()

    assert box.width == 800
    assert box.height == 50


def test_anchor_layout_support_fill_y():
    anchor = UIAnchorLayout(800, 600)
    box = UIBoxLayout(vertical=True)

    anchor.pack(box, bottom=0, left=0, fill_y=True)
    box.pack(dummy_element())
    anchor.refresh()

    assert box.width == 100
    assert box.height == 600


def test_anchor_center(anchor_layout):
    element_1 = dummy_element()

    anchor_layout.pack(element_1, center_x=0, center_y=0)
    anchor_layout.refresh()

    assert element_1.center_x == anchor_layout.center_x
    assert element_1.center_y == anchor_layout.center_y


def test_anchor_center_with_offset(anchor_layout):
    element_1 = dummy_element()

    anchor_layout.pack(element_1, center_x=10, center_y=-20)
    anchor_layout.refresh()

    assert element_1.center_x == anchor_layout.center_x + 10
    assert element_1.center_y == anchor_layout.center_y - 20
