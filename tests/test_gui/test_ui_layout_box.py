import pytest

import arcade
from arcade import SpriteSolidColor
from arcade.gui.layouts.box import UIBoxLayout
from . import T, dummy_element


@pytest.fixture()
def v_layout():
    return UIBoxLayout()


def test_vertical(v_layout):
    v_layout.top = 200
    v_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    v_layout.pack(element_1)
    v_layout.pack(element_2)
    v_layout.refresh()

    assert element_1.top == 200
    assert element_1.bottom == 150
    assert element_1.left == 100

    assert element_2.top == element_1.bottom
    assert element_2.left == 100


def test_vertical_with_spacing(v_layout):
    v_layout.top = 200
    v_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    v_layout.pack(element_1)
    v_layout.pack(element_2, space=10)
    v_layout.refresh()

    assert element_1.bottom == 150
    assert element_2.top == 140


@pytest.fixture()
def h_layout():
    return UIBoxLayout(vertical=False)


def test_horizontal(h_layout):
    h_layout.top = 200
    h_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    h_layout.pack(element_1)
    h_layout.pack(element_2)
    h_layout.refresh()

    assert element_1.top == 200
    assert element_1.left == 100

    assert element_2.top == 200
    assert element_2.left == 200


def test_horizontal_with_spacing(h_layout):
    h_layout.top = 200
    h_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    h_layout.pack(element_1)
    h_layout.pack(element_2, space=10)
    h_layout.refresh()

    assert element_1.right == 200
    assert element_2.left == 210


def test_box_layout_updates_width_and_height(v_layout: UIBoxLayout):
    v_layout.pack(dummy_element(100, 50))

    assert v_layout.width == 100
    assert v_layout.height == 50

    v_layout.pack(dummy_element(150, 50), space=10)
    assert v_layout.width == 150
    assert v_layout.height == 110


def test_v_box_align_items_center():
    box = UIBoxLayout(vertical=False, align='center')
    element = dummy_element()
    box.pack(element)
    box.width = 400

    box.refresh()

    assert element.center_x == 200


def test_v_box_align_items_left():
    box = UIBoxLayout(vertical=False, align='left')
    element = dummy_element()
    box.pack(element)
    box.width = 400

    box.refresh()

    assert element.left == 0


@pytest.mark.parametrize(
    ['vertical', 'align', 'center_x', 'center_y'], [
        T('vertical top', True, 'top', 50, 475),
        T('vertical center', True, 'center', 50, 250),
        T('vertical bottom', True, 'bottom', 50, 25),

        T('horizontal left', False, 'left', 50, 25),
        T('horizontal center', False, 'center', 200, 25),
        T('horizontal right', False, 'right', 350, 25),

        # use synonyms
        T('vertical start', True, 'start', 50, 475),
        T('vertical end', True, 'end', 50, 25),
        T('vertical left', True, 'left', 50, 475),
        T('vertical right', True, 'right', 50, 25),

        T('horizontal start', False, 'start', 50, 25),
        T('horizontal end', False, 'end', 350, 25),
        T('horizontal top', False, 'top', 50, 25),
        T('horizontal bottom', False, 'bottom', 350, 25),
    ]
)
def test_box_alignment(vertical, align, center_x, center_y):
    box = UIBoxLayout(vertical=vertical, align=align)
    element_1 = dummy_element(width=100, height=50)
    box.pack(element_1)
    box.height = 500
    box.width = 400
    box.left = 0
    box.bottom = 0

    box.refresh()

    assert (element_1.center_x, element_1.center_y) == (center_x, center_y)


@pytest.mark.parametrize(
    ['vertical', 'align', 'center_x', 'center_y'], [
        T('vertical top', True, 'top', 50, 475),
        T('vertical center', True, 'center', 50, 250),
        T('vertical bottom', True, 'bottom', 50, 25),

        T('horizontal left', False, 'left', 50, 25),
        T('horizontal center', False, 'center', 200, 25),
        T('horizontal right', False, 'right', 350, 25),

        # use synonyms
        T('vertical start', True, 'start', 50, 475),
        T('vertical end', True, 'end', 50, 25),
        T('vertical left', True, 'left', 50, 475),
        T('vertical right', True, 'right', 50, 25),

        T('horizontal start', False, 'start', 50, 25),
        T('horizontal end', False, 'end', 350, 25),
        T('horizontal top', False, 'top', 50, 25),
        T('horizontal bottom', False, 'bottom', 350, 25),
    ]
)
def test_box_alignment_for_sprites(vertical, align, center_x, center_y):
    box = UIBoxLayout(vertical=vertical, align=align)
    element_1 = SpriteSolidColor(width=100, height=50, color=arcade.color.RED)
    box.pack(element_1)
    box.height = 500
    box.width = 400
    box.left = 0
    box.bottom = 0

    box.refresh()

    assert (element_1.center_x, element_1.center_y) == (center_x, center_y)


def test_min_size_vertical():
    box = UIBoxLayout(vertical=True)
    box.pack(dummy_element(width=100, height=50))
    box.pack(dummy_element(width=100, height=50), space=20)

    box.refresh()

    assert box.min_size() == (100, 120)


def test_min_size_horizontal():
    box = UIBoxLayout(vertical=False)
    box.pack(dummy_element(width=100, height=50))
    box.pack(dummy_element(width=100, height=50), space=20)

    box.refresh()

    assert box.min_size() == (220, 50)
