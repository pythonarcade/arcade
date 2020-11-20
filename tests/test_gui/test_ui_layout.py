from arcade.gui.layouts import UIAbstractLayout
from tests.test_gui import dummy_element


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

# TODO remove if parent not needed
# def test_layout_forwards_new_parent():
#     layout = TestAbstractLayout()
#     layout_1 = TestAbstractLayout()
#     layout_2 = TestAbstractLayout()
#     layout.pack(layout_1)
#     layout.pack(layout_2)
#
#     layout.parent = 1
#
#     assert layout.parent == 1
#     assert layout_1.parent == 1
#     assert layout_2.parent == 1
