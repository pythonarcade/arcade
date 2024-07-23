from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pyglet.math import Vec2


@dataclass
class UIEvent:
    """An event created by the GUI system. Can be passed using widget.dispatch("on_event", event).
    An event always has a source, which is the UIManager for general input events,
    but will be the specific widget in case of events like on_click events.

    Args:
        source: The source of the event.
    """

    source: Any


@dataclass
class UIMouseEvent(UIEvent):
    """Covers all mouse event.

    Args:
        x: The x coordinate of the mouse.
        y: The y coordinate of the mouse.
    """

    x: int
    y: int

    @property
    def pos(self) -> Vec2:
        """Return the position as tuple (x, y)"""
        return Vec2(self.x, self.y)


@dataclass
class UIMouseMovementEvent(UIMouseEvent):
    """Triggered when the mouse is moved.

    Args:
        dx: The change in x coordinate.
        dy: The change in y coordinate.
    """

    dx: int
    dy: int


@dataclass
class UIMousePressEvent(UIMouseEvent):
    """Triggered when a mouse button(left, right, middle) is pressed.

    Args:
        button: The button pressed.
        modifiers: The modifiers pressed.
    """

    button: int
    modifiers: int


@dataclass
class UIMouseDragEvent(UIMouseEvent):
    """Triggered when the mouse moves while one of its buttons being pressed.

    Args:
        dx: The change in x coordinate.
        dy: The change in y coordinate.
        buttons: The buttons pressed.
        modifiers: The modifiers pressed.
    """

    dx: int
    dy: int
    buttons: int
    modifiers: int


@dataclass
class UIMouseReleaseEvent(UIMouseEvent):
    """Triggered when a mouse button is released.

    Args:
        button: The button released.
        modifiers: The modifiers pressed
    """

    button: int
    modifiers: int


@dataclass
class UIMouseScrollEvent(UIMouseEvent):
    """Triggered by rotating the scroll wheel on the mouse.

    Args:
        scroll_x: The horizontal scroll amount.
        scroll_y: The vertical scroll
    """

    scroll_x: int
    scroll_y: int


@dataclass
class UIKeyEvent(UIEvent):
    """Covers all keyboard event.

    Args:
        symbol: The key pressed.
        modifiers: The modifiers pressed.
    """

    symbol: int
    modifiers: int


@dataclass
class UIKeyPressEvent(UIKeyEvent):
    """Triggered when a key is pressed."""

    pass


@dataclass
class UIKeyReleaseEvent(UIKeyEvent):
    """Triggered when a key is released."""

    pass


@dataclass
class UITextEvent(UIEvent):
    """Covers all the text cursor event.

    Args:
        text: The text entered.
    """

    text: str


@dataclass
class UITextMotionEvent(UIEvent):
    """Triggered when text cursor moves.

    Args:
        motion: The motion of the cursor.
    """

    motion: Any


@dataclass
class UITextMotionSelectEvent(UIEvent):
    """Triggered when the text cursor moves selecting the text with it.

    Args:
        selection: The motion of the selection.
    """

    selection: Any


@dataclass
class UIOnClickEvent(UIMouseEvent):
    """Triggered when a widget is clicked.

    Args:
        button: The button clicked.
        modifiers: The modifiers pressed.
    """

    button: int
    modifiers: int


@dataclass
class UIOnUpdateEvent(UIEvent):
    """Arcade on_update callback passed as :class:`UIEvent`.

    Args:
        dt: Time since last update
    """

    dt: int


@dataclass
class UIOnChangeEvent(UIEvent):
    """Value of a widget changed.

    Args:
        old_value: The old value.
        new_value: The new value.
    """

    old_value: Any
    new_value: Any


@dataclass
class UIOnActionEvent(UIEvent):
    """Notification about an action.

    Args:
        action: Value describing the action, mostly a string
    """

    action: Any
