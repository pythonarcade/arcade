from typing import List
from unittest.mock import Mock

import arcade
from arcade.gui.events import UIEvent, UIOnClickEvent, UIMousePressEvent, UIMouseReleaseEvent
from arcade.gui.widgets import UIDummy
from . import record_ui_events


def test_hover_on_widget(ui):
    # GIVEN
    widget = UIDummy()
    ui.add(widget)

    # WHEN
    ui.move_mouse(widget.center_x, widget.center_y)

    # THEN
    assert widget.hovered is True


def test_overlapping_hover_on_widget(ui):
    # GIVEN
    widget1 = UIDummy()
    widget2 = UIDummy()
    ui.add(widget1)
    ui.add(widget2)

    # WHEN
    ui.move_mouse(widget1.center_x, widget1.center_y)

    # THEN
    assert widget1.hovered is True
    assert widget2.hovered is True


def test_left_click_on_widget(ui):
    # GIVEN
    widget1 = UIDummy()
    widget1.on_click = Mock()
    ui.add(widget1)

    # WHEN
    with record_ui_events(widget1, "on_event", "on_click") as records:
        ui.click(widget1.center_x, widget1.center_y, button=arcade.MOUSE_BUTTON_LEFT)

    # THEN
    records: List[UIEvent]
    assert len(records) == 3
    assert isinstance(records[0], UIMousePressEvent)
    assert isinstance(records[1], UIMouseReleaseEvent)

    click_event = records[2]
    assert isinstance(click_event, UIOnClickEvent)
    assert click_event.source == widget1
    assert click_event.x == widget1.center_x
    assert click_event.y == widget1.center_y
    assert click_event.button == arcade.MOUSE_BUTTON_LEFT
    assert click_event.modifiers == 0

    assert widget1.on_click.called


def test_ignores_right_click_on_widget(ui):
    # GIVEN
    widget1 = UIDummy()
    widget1.on_click = Mock()
    ui.add(widget1)

    # WHEN
    with record_ui_events(widget1, "on_event", "on_click") as records:
        ui.click(widget1.center_x, widget1.center_y, button=arcade.MOUSE_BUTTON_RIGHT)

    # THEN
    records: List[UIEvent]
    assert len(records) == 2
    assert isinstance(records[0], UIMousePressEvent)
    assert isinstance(records[1], UIMouseReleaseEvent)
    assert not widget1.on_click.called


def test_click_on_widget_if_disabled(ui):
    # GIVEN
    widget1 = UIDummy()
    widget1.disabled = True
    widget1.on_click = Mock()
    ui.add(widget1)

    # WHEN
    with record_ui_events(widget1, "on_event", "on_click") as records:
        ui.click(widget1.center_x, widget1.center_y)

    # THEN
    records: List[UIEvent]
    assert len(records) == 2
    assert isinstance(records[0], UIMousePressEvent)
    assert isinstance(records[1], UIMouseReleaseEvent)

    assert not widget1.on_click.called


def test_click_on_overlay_widget_consumes_events(ui):
    # GIVEN
    widget1 = UIDummy()
    widget2 = UIDummy()
    ui.add(widget1)
    ui.add(widget2)

    # WHEN
    with record_ui_events(widget1, "on_click") as w1_records:
        with record_ui_events(widget2, "on_click") as w2_records:
            ui.click(widget1.center_x, widget1.center_y)

    # THEN
    # events are consumed before they get to underlying widget
    w1_records: List[UIEvent]
    assert len(w1_records) == 0

    # events are dispatched on widget2
    w2_records: List[UIEvent]
    assert len(w2_records) == 1
    click_event = w2_records[0]
    assert isinstance(click_event, UIOnClickEvent)
    assert click_event.source == widget2
    assert click_event.x == widget2.center_x
    assert click_event.y == widget2.center_y


def test_click_consumed_by_nested_widget(ui):
    # GIVEN
    widget1 = UIDummy()
    widget2 = UIDummy()
    widget1.add(widget2)
    ui.add(widget1)

    # WHEN
    with record_ui_events(widget1, "on_click") as w1_records:
        with record_ui_events(widget2, "on_click") as w2_records:
            ui.click(widget1.center_x, widget1.center_y)

    # THEN
    # events are consumed before they get to underlying widget
    w1_records: List[UIEvent]
    assert len(w1_records) == 0

    # events are dispatched on widget2
    w2_records: List[UIEvent]
    assert len(w2_records) == 1
    click_event = w2_records[0]
    assert isinstance(click_event, UIOnClickEvent)
    assert click_event.source == widget2
    assert click_event.x == widget2.center_x
    assert click_event.y == widget2.center_y
