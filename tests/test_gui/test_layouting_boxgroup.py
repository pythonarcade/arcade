from arcade.gui.widgets import UIDummy
from arcade.gui import UIBoxLayout


# Vertical
def test_do_layout_vertical_with_initial_children():
    # add two 100x100 Dummy widgets
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(x=100, y=400, vertical=True, children=[element_1, element_2])

    group.do_layout()

    assert element_1.top == 400
    assert element_1.bottom == 300
    assert element_1.left == 100

    assert element_2.top == 300
    assert element_2.bottom == 200
    assert element_2.left == 100


def test_do_layout_vertical_add_children():
    group = UIBoxLayout(x=100, y=400, vertical=True)

    element_1 = UIDummy()
    element_2 = UIDummy()

    group.add(element_1)
    group.add(element_2)
    group.do_layout()

    assert element_1.top == 400
    assert element_1.bottom == 300
    assert element_1.left == 100

    assert element_2.top == 300
    assert element_2.bottom == 200
    assert element_2.left == 100


def test_do_layout_vertical_add_child_with_initial_children():
    element_1 = UIDummy()
    element_2 = UIDummy()
    element_3 = UIDummy()

    group = UIBoxLayout(x=100, y=400, vertical=True, children=[element_1, element_2])

    group.add(element_3)
    group.do_layout()

    assert element_1.top == 400
    assert element_1.bottom == 300
    assert element_1.left == 100

    assert element_2.top == 300
    assert element_2.bottom == 200
    assert element_2.left == 100

    assert element_3.top == 200
    assert element_3.bottom == 100
    assert element_3.left == 100


def test_vertical_group_keep_top_alignment_while_adding_children():
    element_1 = UIDummy()
    element_2 = UIDummy()
    element_3 = UIDummy()

    group = UIBoxLayout(x=100, y=400, vertical=True, children=[element_1, element_2])
    assert group.top == 400

    group.add(element_3)
    group.do_layout()

    assert group.top == 400  # group starts with 0 height, so top == bottom, adding children should keep top alignment
    assert group.left == 100
    assert group.height == 300
    assert group.width == 100


def test_do_layout_vertical_align_left():
    element_1 = UIDummy(width=50)
    element_2 = UIDummy(width=100)

    group = UIBoxLayout(x=100, y=400, align="left", vertical=True, children=[element_1, element_2])
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 200
    assert group.width == 100

    assert element_1.left == 100
    assert element_2.left == 100


def test_do_layout_vertical_align_right():
    element_1 = UIDummy(width=50)
    element_2 = UIDummy(width=100)

    group = UIBoxLayout(x=100, y=400, align="right", vertical=True, children=[element_1, element_2])
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 200
    assert group.width == 100

    assert element_1.left == 150
    assert element_2.left == 100


def test_do_layout_vertical_space_between():
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(x=100, y=400, space_between=10, vertical=True, children=[element_1, element_2])
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 210
    assert group.width == 100

    assert element_1.top == 400
    assert element_2.top == 290


# Horizontal
def test_do_layout_horizontal_with_initial_children():
    # add two 100x100 Dummy widgets
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(x=100, y=400, vertical=False, children=[element_1, element_2])

    group.do_layout()

    assert element_1.left == 100
    assert element_1.right == 200
    assert element_1.top == 400

    assert element_2.left == 200
    assert element_2.right == 300
    assert element_2.top == 400


def test_do_layout_horizontal_add_children():
    group = UIBoxLayout(x=100, y=400, vertical=False)

    element_1 = UIDummy()
    element_2 = UIDummy()

    group.add(element_1)
    group.add(element_2)
    group.do_layout()

    assert element_1.left == 100
    assert element_1.right == 200
    assert element_1.top == 400

    assert element_2.left == 200
    assert element_2.right == 300
    assert element_2.top == 400


def test_do_layout_horizontal_add_child_with_initial_children():
    element_1 = UIDummy()
    element_2 = UIDummy()
    element_3 = UIDummy()

    group = UIBoxLayout(x=100, y=400, vertical=False, children=[element_1, element_2])

    group.add(element_3)
    group.do_layout()

    assert element_1.left == 100
    assert element_1.right == 200
    assert element_1.top == 400

    assert element_2.left == 200
    assert element_2.right == 300
    assert element_2.top == 400

    assert element_3.left == 300
    assert element_3.right == 400
    assert element_3.top == 400


def test_horizontal_group_keep_left_alignment_while_adding_children():
    element_1 = UIDummy()
    element_2 = UIDummy()
    element_3 = UIDummy()

    group = UIBoxLayout(x=100, y=400, vertical=False, children=[element_1, element_2])

    group.add(element_3)
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 100
    assert group.width == 300


def test_do_layout_horizontal_align_top():
    element_1 = UIDummy(height=50)
    element_2 = UIDummy(height=100)

    group = UIBoxLayout(x=100, y=400, align="top", vertical=False, children=[element_1, element_2])
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 100
    assert group.width == 200


def test_do_layout_horizontal_align_bottom():
    element_1 = UIDummy(height=50)
    element_2 = UIDummy(height=100)

    group = UIBoxLayout(x=100, y=400, align="bottom", vertical=False, children=[element_1, element_2])
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 100
    assert group.width == 200

    assert element_1.top == 350
    assert element_2.top == 400


def test_do_layout_horizontal_space_between():
    element_1 = UIDummy()
    element_2 = UIDummy()

    group = UIBoxLayout(x=100, y=400, space_between=10, vertical=False, children=[element_1, element_2])
    group.do_layout()

    assert group.left == 100
    assert group.top == 400
    assert group.height == 100
    assert group.width == 210

    assert element_1.left == 100
    assert element_2.left == 210
