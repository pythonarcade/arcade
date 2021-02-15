import arcade
from arcade.gui.layouts.box import UIBoxLayout
from . import dummy_element


def test_vertical_with_spacing_and_padding():
    v_layout = UIBoxLayout(padding=(10, 20, 30, 40))
    v_layout.top = 200
    v_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    v_layout.pack(element_1)
    v_layout.pack(element_2, space=10)

    v_layout.size = v_layout.min_size
    v_layout.do_layout()

    assert v_layout.width == 40 + 100 + 20
    assert v_layout.height == 10 + 50 + 10 + 50 + 30

    assert element_1.top == 190
    assert element_1.left == 140

    assert element_2.top == 130
    assert element_2.left == 140


def test_vertical_with_spacing_padding_and_border():
    v_layout = UIBoxLayout(padding=(10, 20, 30, 40),
                           border_color=arcade.color.RED,
                           border_width=5)
    v_layout.top = 200
    v_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    v_layout.pack(element_1)
    v_layout.pack(element_2, space=10)

    v_layout.size = v_layout.min_size
    v_layout.do_layout()

    assert v_layout.width == 5 + 40 + 100 + 20 + 5
    assert v_layout.height == 5 + 10 + 50 + 10 + 50 + 30 + 5

    assert element_1.top == 185
    assert element_1.left == 145

    assert element_2.top == 125
    assert element_2.left == 145


def test_horizontal_with_spacing_and_padding():
    v_layout = UIBoxLayout(vertical=False, padding=(10, 20, 30, 40))
    v_layout.top = 200
    v_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    v_layout.pack(element_1)
    v_layout.pack(element_2, space=10)

    v_layout.size = v_layout.min_size
    v_layout.do_layout()

    assert v_layout.width == 40 + 100 + 10 + 100 + 20
    assert v_layout.height == 10 + 50 + 30

    assert element_1.top == 190
    assert element_1.left == 140

    assert element_2.top == 190
    assert element_2.left == 250


def test_horizontal_with_spacing_padding_and_border():
    v_layout = UIBoxLayout(vertical=False,
                           padding=(10, 20, 30, 40),
                           border_color=arcade.color.RED,
                           border_width=5)
    v_layout.top = 200
    v_layout.left = 100

    element_1 = dummy_element()
    element_2 = dummy_element()

    v_layout.pack(element_1)
    v_layout.pack(element_2, space=10)

    v_layout.size = v_layout.min_size
    v_layout.do_layout()

    # border, pad left, element, space, element, pad right, border
    assert v_layout.width == 5 + 40 + 100 + 10 + 100 + 20 + 5
    assert v_layout.height == 5 + 10 + 50 + 30 + 5

    assert element_1.top == 185
    assert element_1.left == 145

    assert element_2.top == 185
    assert element_2.left == 255
