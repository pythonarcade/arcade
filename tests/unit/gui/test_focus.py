from pyglet.math import Vec2

from arcade.gui import UIFlatButton
from arcade.gui.experimental.focus import UIFocusGroup


def test_focus_group_no_focus_set_by_default(ui):
    group = UIFocusGroup()
    _ = group.add(UIFlatButton())

    group.detect_focusable_widgets()

    assert group.focused_widget is None


def test_focus_group_focus_set(ui):
    group = UIFocusGroup()

    assert group.focused_widget is None
    btn_1 = group.add(UIFlatButton())
    btn_2 = group.add(UIFlatButton())

    group.detect_focusable_widgets()

    group.set_focus(btn_1)

    assert group.focused_widget == btn_1
    assert btn_1.focused is True
    assert btn_2.focused is False


def test_nested_groups_button_press(ui):
    """
    Test when nested UIFocusGroups are used.

    The inner group should consume the focus event and not pass it to the outer group.
    """

    group_1 = ui.add(UIFocusGroup())
    btn_1 = group_1.add(UIFlatButton())

    group_2 = group_1.add(UIFocusGroup())
    btn_2 = group_2.add(UIFlatButton())

    group_1.detect_focusable_widgets()
    group_2.detect_focusable_widgets()

    group_1.set_focus(btn_1)
    group_2.set_focus(btn_2)

    ui.on_button_press(None, "a")

    assert btn_1.pressed is False
    assert btn_2.pressed is True


def test_nested_groups_dpad(ui):
    """
    Test when nested UIFocusGroups are used.

    The inner group should consume the focus event and not pass it to the outer group.
    """

    group_1 = ui.add(UIFocusGroup())
    btn_1_1 = group_1.add(UIFlatButton())
    btn_1_2 = group_1.add(UIFlatButton())

    group_2 = group_1.add(UIFocusGroup())
    btn_2_1 = group_2.add(UIFlatButton())
    btn_2_2 = group_2.add(UIFlatButton())

    group_1.detect_focusable_widgets()
    group_2.detect_focusable_widgets()

    group_1.set_focus(btn_1_1)
    group_2.set_focus(btn_2_1)

    ui.on_dpad_motion(None, Vec2(0, 1))

    assert btn_1_1.focused is True
    assert btn_1_2.focused is False
    assert btn_2_1.focused is False
    assert btn_2_2.focused is True
