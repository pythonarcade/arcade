from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class UIEvent:
    """
    An event created by the GUI system. Can be passed using widget.dispatch("on_event", event).
    An event always has a source, which is the UIManager for general input events,
    but will be the specific widget in case of events like on_click events.
    """

    source: Any


@dataclass
class UIMouseEvent(UIEvent):
    """
    Covers all mouse event
    """

    x: int
    y: int

    @property
    def pos(self):
        return self.x, self.y


@dataclass
class UIMouseMovementEvent(UIMouseEvent):
    """Triggered when the mouse is moved."""

    dx: int
    dy: int


@dataclass
class UIMousePressEvent(UIMouseEvent):
    """Triggered when a mouse button(left, right, middle) is pressed."""

    button: int
    modifiers: int


@dataclass
class UIMouseDragEvent(UIMouseEvent):
    """Triggered when the mouse moves while one of its buttons being pressed."""

    dx: int
    dy: int
    buttons: int
    modifiers: int


@dataclass
class UIMouseReleaseEvent(UIMouseEvent):
    """Triggered when a mouse button is released."""

    button: int
    modifiers: int


@dataclass
class UIMouseScrollEvent(UIMouseEvent):
    """Triggered by rotating the scroll wheel on the mouse."""

    scroll_x: int
    scroll_y: int


@dataclass
class UIKeyEvent(UIEvent):
    """Covers all keyboard event."""

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
    """Covers all the text cursor event."""

    text: str


@dataclass
class UITextMotionEvent(UIEvent):
    """Triggered when text cursor moves."""

    motion: Any


@dataclass
class UITextMotionSelectEvent(UIEvent):
    """Triggered when the text cursor moves selecting the text with it."""

    selection: Any


@dataclass
class UIOnClickEvent(UIMouseEvent):
    """Triggered when a widget is clicked."""

    button: int
    modifiers: int


@dataclass
class UIOnUpdateEvent(UIEvent):
    """
    Arcade on_update callback passed as :class:`UIEvent`
    """

    dt: int


@dataclass
class UIOnChangeEvent(UIEvent):
    """
    Value of a widget changed
    """

    old_value: Any
    new_value: Any


@dataclass
class UIOnActionEvent(UIEvent):
    """
    Notification about an action

    :param action: Value describing the action, mostly a string
    """

    action: Any
