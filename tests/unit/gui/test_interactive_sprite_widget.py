from unittest.mock import Mock

import arcade
from arcade.gui import UIInteractiveSpriteWidget, UIBoxLayout
from arcade.gui.events import UIOnClickEvent, UIMousePressEvent, UIMouseReleaseEvent
from arcade.gui.widgets.layout import UIAnchorLayout

from . import record_ui_events


def _make_widget(**kwargs) -> UIInteractiveSpriteWidget:
    sprite = arcade.SpriteSolidColor(100, 100, color=arcade.color.RED)
    return UIInteractiveSpriteWidget(sprite=sprite, **kwargs)


def test_click_fires_on_click(ui):
    """Clicking the widget should dispatch an on_click event."""
    widget = _make_widget()
    ui.add(widget)

    with record_ui_events(widget, "on_click") as events:
        ui.click(widget.center_x, widget.center_y)

    assert len(events) == 1
    assert isinstance(events[0], UIOnClickEvent)
    assert events[0].source is widget


def test_click_outside_does_not_fire(ui):
    """Clicking outside the widget should not dispatch on_click."""
    widget = _make_widget()
    ui.add(widget)

    with record_ui_events(widget, "on_click") as events:
        ui.click(widget.right + 50, widget.top + 50)

    assert len(events) == 0


def test_hovered_updates_on_mouse_move(ui):
    """Moving the mouse over the widget should set hovered=True."""
    widget = _make_widget()
    ui.add(widget)

    assert widget.hovered is False
    ui.move_mouse(widget.center_x, widget.center_y)
    assert widget.hovered is True
    ui.move_mouse(widget.right + 50, widget.top + 50)
    assert widget.hovered is False


def test_pressed_between_press_and_release(ui):
    """pressed should be True between mouse press and release."""
    widget = _make_widget()
    ui.add(widget)

    assert widget.pressed is False
    ui.click_and_hold(widget.center_x, widget.center_y)
    assert widget.pressed is True
    ui.release(widget.center_x, widget.center_y)
    assert widget.pressed is False


def test_disabled_blocks_click(ui):
    """Clicking a disabled widget should not fire on_click."""
    widget = _make_widget()
    widget.disabled = True
    ui.add(widget)

    with record_ui_events(widget, "on_click") as events:
        ui.click(widget.center_x, widget.center_y)

    assert len(events) == 0


def test_widget_rect_matches_sprite_size(window):
    """Widget dimensions should default to sprite texture size."""
    sprite = arcade.SpriteSolidColor(150, 75, color=arcade.color.BLUE)
    widget = UIInteractiveSpriteWidget(sprite=sprite)
    assert widget.width == 150
    assert widget.height == 75


def test_explicit_size_overrides_sprite(window):
    """Explicit width/height should override sprite texture size."""
    sprite = arcade.SpriteSolidColor(100, 100, color=arcade.color.RED)
    widget = UIInteractiveSpriteWidget(sprite=sprite, width=200, height=50)
    assert widget.width == 200
    assert widget.height == 50


def test_works_in_box_layout(ui):
    """Widget should be usable inside a UIBoxLayout."""
    layout = UIBoxLayout(vertical=False, space_between=10, size_hint=None)
    widget_a = _make_widget()
    widget_b = _make_widget()
    layout.add(widget_a)
    layout.add(widget_b)
    ui.add(layout)

    layout.do_layout()

    with record_ui_events(widget_a, "on_click") as events:
        ui.click(widget_a.center_x, widget_a.center_y)

    assert len(events) == 1
    assert events[0].source is widget_a


def test_works_in_anchor_layout(ui):
    """Widget should be usable inside a UIAnchorLayout."""
    layout = UIAnchorLayout(width=500, height=500, size_hint=None)
    widget = _make_widget()
    layout.add(widget, anchor_x="center", anchor_y="center")
    ui.add(layout)

    layout.do_layout()

    with record_ui_events(widget, "on_click") as events:
        ui.click(widget.center_x, widget.center_y)

    assert len(events) == 1


def test_callback_via_event_decorator(ui):
    """Callback registration via @widget.event('on_click') should work."""
    widget = _make_widget()
    callback = Mock()
    widget.push_handlers(on_click=callback)
    ui.add(widget)

    ui.click(widget.center_x, widget.center_y)

    assert callback.called
    assert isinstance(callback.call_args[0][0], UIOnClickEvent)


def test_callback_via_assignment(ui):
    """Callback registration via widget.on_click = callback should work."""
    widget = _make_widget()
    widget.on_click = Mock()
    ui.add(widget)

    ui.click(widget.center_x, widget.center_y)

    assert widget.on_click.called
