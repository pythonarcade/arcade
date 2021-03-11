from arcade.gui.layouts.anchor import UIAnchorLayout
from arcade.gui.layouts.box import UIBoxLayout
from arcade.gui.layouts.manager import UIStack


def test_ui_stack_provides_default_layout():
    # WHEN
    stack = UIStack(UIAnchorLayout(100, 100))

    # THEN
    assert type(stack.peek()) is UIAnchorLayout


def test_ui_stack_push_pop_peek():
    # GIVEN
    stack = UIStack(UIAnchorLayout(100, 100))

    box_1 = UIBoxLayout()
    box_2 = UIBoxLayout()

    # WHEN
    stack.push(box_1)
    stack.push(box_2)

    # THEN
    assert stack.peek() == box_2
    assert stack.pop() == box_2

    assert stack.peek() == box_1
    assert stack.pop() == box_1

    assert stack.peek() == stack.default_layout
    assert stack.pop() == stack.default_layout


def test_ui_stack_allows_pop_on_empty_stack():
    stack = UIStack(UIAnchorLayout(100, 100))

    assert stack.pop() == stack.default_layout
    assert stack.pop() == stack.default_layout


def test_ui_stack_remove_element():
    # GIVEN
    stack = UIStack(UIAnchorLayout(100, 100))

    box_1 = UIBoxLayout()
    box_2 = UIBoxLayout()

    # WHEN
    stack.push(box_1)
    stack.push(box_2)

    # THEN
    assert stack.pop(box_1) == box_1

    assert stack.pop() == box_2
    assert stack.pop() == stack.default_layout


def test_ui_stack_is_iterable():
    # GIVEN
    stack = UIStack(UIAnchorLayout(100, 100))

    box_1 = UIBoxLayout()
    box_2 = UIBoxLayout()

    # WHEN
    stack.push(box_1)
    stack.push(box_2)

    # THEN
    assert list(stack) == [stack.default_layout, box_1, box_2]
