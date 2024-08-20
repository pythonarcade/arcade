from _pytest.python_api import approx
from pyglet.math import Vec2

from arcade.gui import UIBoxLayout, UIManager
from arcade.gui.widgets import UIDummy
from arcade.types import LBWH


# Vertical
def test_do_layout_vertical_with_initial_children(window):
    # add two 100x100 Dummy widgets
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(vertical=True, children=[element_1, element_2])
    group.rect = LBWH(100, 200, *group.size_hint_min)

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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
    group.do_layout()

    assert group.left == 100
    assert group.top == 300
    assert group.height == 100
    assert group.width == 300


def test_do_layout_horizontal_align_top(window):
    element_1 = UIDummy(height=50)
    element_2 = UIDummy(height=100)
    group = UIBoxLayout(align="top", vertical=False, children=[element_1, element_2])

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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

    group.rect = LBWH(100, 200, *group.size_hint_min)
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
    box.with_padding(top=10, right=20, bottom=30, left=40)
    box.add(UIDummy(width=100, height=100))
    box.add(UIDummy(width=100, height=100))

    assert box.size_hint_min == (100 + 2 * 3 + 20 + 40, 200 + 2 * 3 + 10 + 30)


def test_vertical_resize_child_according_size_hint_full(window):
    box = UIBoxLayout(width=200, height=200, vertical=True)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, 1)))

    box._do_layout()

    assert box.size == Vec2(200, 200)
    assert dummy_1.size == Vec2(200, 200)


def test_vertical_resize_child_according_size_hint_half(window):
    box = UIBoxLayout(width=200, height=200, vertical=True)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == Vec2(200, 200)
    assert dummy_1.size == Vec2(100, 100)


def test_vertical_resize_children_according_size_hint(window):
    box = UIBoxLayout(width=300, height=400, vertical=True)
    dummy_1 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(1, 1)))
    dummy_2 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == Vec2(300, 400)
    assert dummy_1.size == Vec2(300, approx(400 / 3 * 2))
    assert dummy_2.size == Vec2(150, approx(400 / 3 * 1))


def test_vertical_ignores_size_hint_none(window):
    box = UIBoxLayout(width=300, height=400, vertical=True)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, None)))
    dummy_2 = box.add(UIDummy(width=100, height=100, size_hint=(None, 1)))

    box._do_layout()

    assert box.size == Vec2(300, 400)
    assert dummy_1.size == Vec2(300, 100)
    assert dummy_2.size == Vec2(100, 300)


def test_vertical_fit_content(window):
    box = UIBoxLayout(width=100, height=100, vertical=True)
    _ = box.add(UIDummy(width=100, height=50))
    _ = box.add(UIDummy(width=20, height=100))

    box.fit_content()

    assert box.size == Vec2(100, 150)


def test_horizontal_resize_child_according_size_hint_full(window):
    box = UIBoxLayout(width=200, height=200, vertical=False)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, 1)))

    box._do_layout()

    assert box.size == Vec2(200, 200)
    assert dummy_1.size == Vec2(200, 200)


def test_horizontal_resize_child_according_size_hint_half(window):
    box = UIBoxLayout(width=200, height=200, vertical=False)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == Vec2(200, 200)
    assert dummy_1.size == Vec2(100, 100)


def test_horizontal_resize_children_according_size_hint(window):
    box = UIBoxLayout(width=300, height=400, vertical=False)
    dummy_1 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(1, 1)))
    dummy_2 = box.add(UIDummy(size_hint_min=(100, 100), size_hint=(0.5, 0.5)))

    box._do_layout()

    assert box.size == Vec2(300, 400)
    assert dummy_1.size == Vec2(box.width * 2 / 3, 400)
    assert dummy_2.size == Vec2(box.width * 1 / 3, 200)


def test_horizontal_ignores_size_hint_none(window):
    box = UIBoxLayout(width=300, height=400, vertical=False)
    dummy_1 = box.add(UIDummy(width=100, height=100, size_hint=(1, None)))
    dummy_2 = box.add(UIDummy(width=100, height=100, size_hint=(None, 1)))

    box._do_layout()

    assert box.size == Vec2(300, 400)
    assert dummy_1.size == Vec2(200, 100)
    assert dummy_2.size == Vec2(100, 400)


def test_horizontal_fit_content(window):
    box = UIBoxLayout(width=100, height=100, vertical=False)
    _ = box.add(UIDummy(width=100, height=50))
    _ = box.add(UIDummy(width=20, height=100))

    box.fit_content()

    assert box.size == Vec2(120, 100)


def test_nested_layouts(window):
    ui = UIManager()
    box1 = UIBoxLayout()
    box2 = UIBoxLayout()
    box3 = UIBoxLayout()
    dummy = UIDummy(width=100, height=100)

    ui.add(box1)
    box1.add(box2)
    box2.add(box3)
    box3.add(dummy)

    ui.execute_layout()

    assert box1.size == Vec2(100, 100)
    assert box2.size == Vec2(100, 100)
    assert box3.size == Vec2(100, 100)
    assert dummy.size == Vec2(100, 100)


def test_children_change_size_hint_min(window):
    ui = UIManager()
    box1 = UIBoxLayout()
    dummy = UIDummy(width=100, height=100, size_hint=(1, 1))

    ui.add(box1)
    box1.add(dummy)

    dummy.size_hint_min = (150, 150)

    ui.execute_layout()

    assert box1.size == Vec2(150, 150)
    assert dummy.size == Vec2(150, 150)


# TODO test size hint < 1 (do not take full width)


def test_children_size_hint_sum_below_1(window):
    ui = UIManager()
    box1 = UIBoxLayout(width=100, height=100, vertical=False, size_hint=None)
    dummy_1 = UIDummy(width=10, height=10, size_hint=(0.2, 1))
    dummy_2 = UIDummy(width=10, height=10, size_hint=(0.5, 1))

    ui.add(box1)
    box1.add(dummy_1)
    box1.add(dummy_2)

    ui.execute_layout()

    assert box1.size == Vec2(100, 100)
    assert dummy_1.size == Vec2(20, 100)
    assert dummy_2.size == Vec2(50, 100)


def test_children_size_hint_sum_below_1_with_shm(window):
    ui = UIManager()
    box1 = UIBoxLayout(width=100, height=100, vertical=False, size_hint=None)
    dummy_1 = UIDummy(width=10, height=10, size_hint=(0.2, 1))
    dummy_2 = UIDummy(width=10, height=10, size_hint=(0.5, 1), size_hint_min=(40, 100))

    ui.add(box1)
    box1.add(dummy_1)
    box1.add(dummy_2)

    ui.execute_layout()

    assert box1.size == Vec2(100, 100)
    assert dummy_1.size == Vec2(20, 100)
    assert dummy_2.size == Vec2(50, 100)


def test_children_size_hint_sum_below_1_with_shm_to_big(window):
    """size_hint_min of second child requests more space, then would be available."""
    ui = UIManager()
    box1 = UIBoxLayout(width=100, height=100, vertical=False, size_hint=None)
    dummy_1 = UIDummy(width=10, height=10, size_hint=(0.2, 1))
    dummy_2 = UIDummy(width=10, height=10, size_hint=(0.5, 1), size_hint_min=(90, 100))

    ui.add(box1)
    box1.add(dummy_1)
    box1.add(dummy_2)

    ui.execute_layout()

    assert box1.size == Vec2(100, 100)
    assert dummy_1.size == Vec2(10, 100)
    assert dummy_2.size == Vec2(90, 100)


def test_children_size_hint_sum_above_1(window):
    """Children get less space than requested. but relative to their size hints."""
    ui = UIManager()
    box1 = UIBoxLayout(width=100, height=100, vertical=False, size_hint=None)
    dummy_1 = UIDummy(width=10, height=10, size_hint=(0.5, 1))
    dummy_2 = UIDummy(width=10, height=10, size_hint=(0.6, 1))

    ui.add(box1)
    box1.add(dummy_1)
    box1.add(dummy_2)

    ui.execute_layout()

    assert box1.size == Vec2(100, 100)
    assert dummy_1.width == approx(45.45, rel=0.01)
    assert dummy_2.width == approx(54.55, rel=0.01)
