import pytest

import arcade
from arcade import SpriteSolidColor
from arcade.gui.layouts.box import UIBoxLayout
from . import t, dummy_element


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
    v_layout.do_layout()

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
    v_layout.do_layout()

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

    h_layout.size = h_layout.min_size
    h_layout.do_layout()

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

    h_layout.size = h_layout.min_size
    h_layout.do_layout()

    assert element_1.right == 200
    assert element_2.left == 210


def test_box_layout_updates_width_and_height(v_layout: UIBoxLayout):
    v_layout.pack(dummy_element(100, 50))

    v_layout.size = v_layout.min_size
    v_layout.do_layout()

    assert v_layout.width == 100
    assert v_layout.height == 50

    v_layout.pack(dummy_element(150, 50), space=10)

    v_layout.size = v_layout.min_size
    v_layout.do_layout()

    assert v_layout.width == 150
    assert v_layout.height == 110


def test_v_box_align_items_center():
    box = UIBoxLayout(vertical=False, align="center")
    element = dummy_element()
    box.pack(element)
    box.width = 400

    box.do_layout()

    assert element.center_x == 200


def test_v_box_align_items_left():
    box = UIBoxLayout(vertical=False, align="left")
    element = dummy_element()
    box.pack(element)
    box.width = 400

    box.do_layout()

    assert element.left == 0


@pytest.mark.parametrize(
    ["vertical", "align", "center_x", "center_y"],
    [
        t("vertical top", True, "top", 50, 475),
        t("vertical center", True, "center", 50, 250),
        t("vertical bottom", True, "bottom", 50, 25),
        t("horizontal left", False, "left", 50, 25),
        t("horizontal center", False, "center", 200, 25),
        t("horizontal right", False, "right", 350, 25),
        # use synonyms
        t("vertical start", True, "start", 50, 475),
        t("vertical end", True, "end", 50, 25),
        t("vertical left", True, "left", 50, 475),
        t("vertical right", True, "right", 50, 25),
        t("horizontal start", False, "start", 50, 25),
        t("horizontal end", False, "end", 350, 25),
        t("horizontal top", False, "top", 50, 25),
        t("horizontal bottom", False, "bottom", 350, 25),
    ],
)
def test_box_alignment(vertical, align, center_x, center_y):
    box = UIBoxLayout(vertical=vertical, align=align)
    element_1 = dummy_element(width=100, height=50)
    box.pack(element_1)
    box.height = 500
    box.width = 400
    box.left = 0
    box.bottom = 0

    box.do_layout()

    assert (element_1.center_x, element_1.center_y) == (center_x, center_y)


@pytest.mark.parametrize(
    ["vertical", "align", "center_x", "center_y"],
    [
        t("vertical top", True, "top", 50, 475),
        t("vertical center", True, "center", 50, 250),
        t("vertical bottom", True, "bottom", 50, 25),
        t("horizontal left", False, "left", 50, 25),
        t("horizontal center", False, "center", 200, 25),
        t("horizontal right", False, "right", 350, 25),
        # use synonyms
        t("vertical start", True, "start", 50, 475),
        t("vertical end", True, "end", 50, 25),
        t("vertical left", True, "left", 50, 475),
        t("vertical right", True, "right", 50, 25),
        t("horizontal start", False, "start", 50, 25),
        t("horizontal end", False, "end", 350, 25),
        t("horizontal top", False, "top", 50, 25),
        t("horizontal bottom", False, "bottom", 350, 25),
    ],
)
def test_box_alignment_for_sprites(vertical, align, center_x, center_y):
    box = UIBoxLayout(vertical=vertical, align=align)
    element_1 = SpriteSolidColor(width=100, height=50, color=arcade.color.RED)
    box.pack(element_1)
    box.height = 500
    box.width = 400
    box.left = 0
    box.bottom = 0

    box.do_layout()

    assert (element_1.center_x, element_1.center_y) == (center_x, center_y)


def test_min_size_vertical():
    box = UIBoxLayout(vertical=True)
    box.pack(dummy_element(width=100, height=50))
    box.pack(dummy_element(width=100, height=50), space=20)

    box.do_layout()

    assert box.min_size == (100, 120)


def test_min_size_horizontal():
    box = UIBoxLayout(vertical=False)
    box.pack(dummy_element(width=100, height=50))
    box.pack(dummy_element(width=100, height=50), space=20)

    box.do_layout()

    assert box.min_size == (220, 50)


def test_vertical_children_size_hint_mix():
    box = UIBoxLayout(vertical=True)
    box.top = 100

    dummy1 = dummy_element(width=100, height=50)
    dummy1.size_hint = None
    box.pack(dummy1)

    dummy2 = dummy_element(width=100, height=50)
    dummy2.size_hint = (0, 0)
    box.pack(dummy2)

    box.do_layout()

    assert dummy1.top == 100
    assert dummy2.top == 50


def test_horizontal_children_size_hint_mix():
    box = UIBoxLayout(vertical=False)
    box.left = 0

    dummy1 = dummy_element(width=100, height=50)
    dummy1.size_hint = None
    box.pack(dummy1)

    dummy2 = dummy_element(width=100, height=50)
    dummy2.size_hint = (0, 0)
    box.pack(dummy2)

    box.do_layout()

    assert dummy1.left == 0
    assert dummy2.left == 100


def test_horizontal_nested_layout():
    nested = UIBoxLayout(vertical=False)
    nested.pack(dummy_element(width=100, height=50))

    box = UIBoxLayout(vertical=False)
    box.pack(nested)

    print(nested.min_size)
    print(box.min_size)
    box.size = box.min_size
    box.do_layout()

    assert box.min_size == (100, 50)


def test_vertical_nested_layout():
    nested = UIBoxLayout(vertical=True)
    nested.pack(dummy_element(width=100, height=50))

    box = UIBoxLayout(vertical=False)
    box.pack(nested)

    print(nested.min_size)
    print(box.min_size)
    box.size = box.min_size
    box.do_layout()

    assert box.min_size == (100, 50)
