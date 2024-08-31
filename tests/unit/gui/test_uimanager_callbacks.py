import arcade
from arcade.gui import UIMousePressEvent, UIMouseReleaseEvent, UIKeyReleaseEvent
from arcade.gui.events import (
    UIMouseScrollEvent,
    UIMouseMovementEvent,
    UIKeyPressEvent,
    UITextInputEvent,
    UITextMotionEvent,
    UITextMotionSelectEvent,
)
from arcade.gui.widgets import UIDummy
from arcade.key import MOTION_UP
from . import record_ui_events


def test_on_mouse_press_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_mouse_press(1, 2, 3, 4)

    event = records[-1]
    assert isinstance(event, UIMousePressEvent)
    assert event.x == 1
    assert event.y == 2
    assert event.button == 3
    assert event.modifiers == 4


def test_on_mouse_release_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_mouse_release(1, 2, 3, 4)

    event = records[-1]
    assert isinstance(event, UIMouseReleaseEvent)
    assert event.x == 1
    assert event.y == 2
    assert event.button == 3
    assert event.modifiers == 4


def test_on_mouse_scroll_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_mouse_scroll(1, 2, 3, 4)

    event = records[-1]
    assert isinstance(event, UIMouseScrollEvent)
    assert event.x == 1
    assert event.y == 2
    assert event.scroll_x == 3
    assert event.scroll_y == 4


def test_on_mouse_motion_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_mouse_motion(1, 2, 3, 4)

    event = records[-1]
    assert isinstance(event, UIMouseMovementEvent)
    assert event.x == 1
    assert event.y == 2
    assert event.dx == 3
    assert event.dy == 4


def test_on_key_press_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_key_press(arcade.key.ENTER, 0)

    event = records[-1]
    assert isinstance(event, UIKeyPressEvent)
    assert event.symbol == arcade.key.ENTER
    assert event.modifiers == 0


def test_on_key_release_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_key_release(arcade.key.ENTER, 0)

    event = records[-1]
    assert isinstance(event, UIKeyReleaseEvent)
    assert event.symbol == arcade.key.ENTER
    assert event.modifiers == 0


def test_on_text_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_text("a")

    event = records[-1]
    assert isinstance(event, UITextInputEvent)
    assert event.text == "a"


def test_on_text_motion_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_text_motion(MOTION_UP)

    event = records[-1]
    assert isinstance(event, UITextMotionEvent)
    assert event.motion == MOTION_UP


def test_on_text_motion_selection_passes_an_event(ui):
    ui.add(UIDummy())

    with record_ui_events(ui, "on_event") as records:
        ui.on_text_motion_select(MOTION_UP)

    event = records[-1]
    assert isinstance(event, UITextMotionSelectEvent)
    assert event.selection == MOTION_UP
