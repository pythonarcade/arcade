from _pytest.python_api import approx

from arcade.gui import UIBoxLayout
from arcade.gui.widgets import UIDummy, Rect


# Vertical
def test_do_layout_vertical_with_initial_children(window):
    # add two 100x100 Dummy widgets
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(vertical=True, children=[element_1, element_2])
    group.rect = Rect(100, 200, *group.size_hint_min)

    group._do_layout()

    assert element_1.top == 400
    assert element_1.bottom == 300
    assert element_1.left == 100

    assert element_2.top == 300
    assert element_2.bottom == 200
    assert element_2.left == 100


def test_do_layout_vertical_add_children(window):
    group = UIBoxLayout(vertical=True)

    element_1 = UIDummy()
    element_2 = UIDummy()

    group.add(element_1)
    group.add(element_2)

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert element_1.top == 400
    assert element_1.bottom == 300
    assert element_1.left == 100

    assert element_2.top == 300
    assert element_2.bottom == 200
    assert element_2.left == 100


def test_do_layout_vertical_add_child_with_initial_children(window):
    element_1 = UIDummy()
    element_2 = UIDummy()
    element_3 = UIDummy()

    group = UIBoxLayout(vertical=True, children=[element_1, element_2])

    group.add(element_3)

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert element_1.top == 500
    assert element_1.bottom == 400
    assert element_1.left == 100

    assert element_2.top == 400
    assert element_2.bottom == 300
    assert element_2.left == 100

    assert element_3.top == 300
    assert element_3.bottom == 200
    assert element_3.left == 100


def test_do_layout_vertical_align_left(window):
    element_1 = UIDummy(width=50)
    element_2 = UIDummy(width=100)

    group = UIBoxLayout(align="left", vertical=True, children=[element_1, element_2])

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 200
    assert group.width == 100

    assert element_1.left == 100
    assert element_2.left == 100


def test_do_layout_vertical_align_right(window):
    element_1 = UIDummy(width=50)
    element_2 = UIDummy(width=100)

    group = UIBoxLayout(align="right", vertical=True, children=[element_1, element_2])

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 200
    assert group.width == 100

    assert element_1.left == 150
    assert element_2.left == 100


def test_do_layout_vertical_space_between(window):
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(space_between=10, vertical=True, children=[element_1, element_2])

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 410
    assert group.height == 210
    assert group.width == 100

    assert element_1.top == 410
    assert element_2.top == 300


# Horizontal
def test_do_layout_horizontal_with_initial_children(window):
    # add two 100x100 Dummy widgets
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(vertical=False, children=[element_1, element_2])

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert element_1.left == 100
    assert element_1.right == 200
    assert element_1.top == 300

    assert element_2.left == 200
    assert element_2.right == 300
    assert element_2.top == 300


def test_do_layout_horizontal_add_children(window):
    group = UIBoxLayout(vertical=False)

    element_1 = UIDummy()
    element_2 = UIDummy()

    group.add(element_1)
    group.add(element_2)

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert element_1.left == 100
    assert element_1.right == 200
    assert element_1.top == 300

    assert element_2.left == 200
    assert element_2.right == 300
    assert element_2.top == 300


def test_do_layout_horizontal_add_child_with_initial_children(window):
    element_1 = UIDummy()
    element_2 = UIDummy()
    element_3 = UIDummy()

    group = UIBoxLayout(vertical=False, children=[element_1, element_2])
    group.add(element_3)

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert element_1.left == 100
    assert element_1.right == 200
    assert element_1.top == 300

    assert element_2.left == 200
    assert element_2.right == 300
    assert element_2.top == 300

    assert element_3.left == 300
    assert element_3.right == 400
    assert element_3.top == 300


def test_horizontal_group_keep_left_alignment_while_adding_children(window):
    element_1 = UIDummy()
    element_2 = UIDummy()
    element_3 = UIDummy()

    group = UIBoxLayout(vertical=False, children=[element_1, element_2])
    group.add(element_3)

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 300
    assert group.height == 100
    assert group.width == 300


def test_do_layout_horizontal_align_top(window):
    element_1 = UIDummy(height=50)
    element_2 = UIDummy(height=100)
    group = UIBoxLayout(align="top", vertical=False, children=[element_1, element_2])

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 300
    assert group.height == 100
    assert group.width == 200

    assert element_1.top == 300
    assert element_2.top == 300


def test_do_layout_horizontal_align_bottom(window):
    element_1 = UIDummy(height=50)
    element_2 = UIDummy(height=100)
    group = UIBoxLayout(align="bottom", vertical=False, children=[element_1, element_2])

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 300
    assert group.height == 100
    assert group.width == 200

    assert element_1.top == 250
    assert element_2.top == 300


def test_do_layout_horizontal_space_between(window):
    element_1 = UIDummy()
    element_2 = UIDummy()
    group = UIBoxLayout(space_between=10, vertical=False, children=[element_1, element_2])

    group.rect = Rect(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 300
    assert group.height == 100
    assert group.width == 210

    assert element_1.left == 100
    assert element_2.left == 210


def test_size_hint_min_contains_children_vertically(window):
    box = UIBoxLayout()

    box.add(UIDummy(width=100, height=100))
    box.add(UIDummy(width=100, height=100))

    assert box.size_hint_min == (100, 200)


def test_size_hint_min_contains_children_horizontal(window):
    box = UIBoxLayout(vertical=False)

    box.add(UIDummy(width=100, height=100))
    box.add(UIDummy(width=100, height=100))

    assert box.size_hint_min == (200, 100)


def test_size_hint_contains_border_and_padding(window):
    box = UIBoxLayout()
    box.with_border(width=3)
    box.with_padding(10, 20, 30, 40)
    box.add(UIDummy(width=100, height=100))
    box.add(UIDummy(width=100, height=100))

    assert box.size_hint_min == (100 + 2 * 3 + 20 + 40, 200 + 2 * 3 + 10 + 30)


def test_vertical_resize_child_according_size_hint_full(window):
    box = UIBoxLayout(width=200, height=200, vertical=True)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, 1)))

    box._do_layout()

    assert box.size == (200, 200)
    assert dummy_1.size == (200, 200)

def test_vertical_resize_child_according_size_hint_half(window):
    box = UIBoxLayout(width=200, height=200, vertical=True)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == (200, 200)
    assert dummy_1.size == (100, 100)


def test_vertical_resize_children_according_size_hint(window):
    box = UIBoxLayout(width=300, height=400, vertical=True)
    dummy_1 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(1, 1)))
    dummy_2 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == (300, 400)
    assert dummy_1.size == (300, approx(100 + 200 / 3 * 2))
    assert dummy_2.size == (150, approx(100 + 200 / 3 * 1))

def test_vertical_ignores_size_hint_none(window):
    box = UIBoxLayout(width=300, height=400, vertical=True)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, None)))
    dummy_2 = box.add(UIDummy(width=100, height=100, size_hint=(None, 1)))

    box._do_layout()

    assert box.size == (300, 400)
    assert dummy_1.size == (300, 100)
    assert dummy_2.size == (100, 300)


def test_horizontal_resize_child_according_size_hint_full(window):
    box = UIBoxLayout(width=200, height=200, vertical=False)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, 1)))

    box._do_layout()

    assert box.size == (200, 200)
    assert dummy_1.size == (200, 200)

def test_horizontal_resize_child_according_size_hint_half(window):
    box = UIBoxLayout(width=200, height=200, vertical=False)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == (200, 200)
    assert dummy_1.size == (100, 100)

def test_horizontal_resize_children_according_size_hint(window):
    box = UIBoxLayout(width=300, height=400, vertical=False)
    dummy_1 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(1, 1)))
    dummy_2 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == (300, 400)
    assert dummy_1.size == (approx(100 + 100 / 3 * 2), 400)
    assert dummy_2.size == (approx(100 + 100 / 3 * 1), 200)


def test_horizontal_ignores_size_hint_none(window):
    box = UIBoxLayout(width=300, height=400, vertical=False)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, None)))
    dummy_2 = box.add(UIDummy(width=100, height=100, size_hint=(None, 1)))

    box._do_layout()

    assert box.size == (300, 400)
    assert dummy_1.size == (200, 100)
    assert dummy_2.size == (100, 400)

# TODO test size hint < 1 (do not take full width)