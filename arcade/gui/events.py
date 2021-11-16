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
    x: float
    y: float

    @property
    def pos(self):
        return self.x, self.y


@dataclass
class UIMouseMovementEvent(UIMouseEvent):
    dx: float
    dy: float


@dataclass
class UIMousePressEvent(UIMouseEvent):
    button: int
    modifiers: int


@dataclass
class UIMouseDragEvent(UIMouseEvent):
    dx: float
    dy: float
    buttons: int
    modifiers: int


@dataclass
class UIMouseReleaseEvent(UIMouseEvent):
    button: int
    modifiers: int


@dataclass
class UIMouseScrollEvent(UIMouseEvent):
    scroll_x: int
    scroll_y: int


@dataclass
class UIKeyEvent(UIEvent):
    symbol: int
    modifiers: int


@dataclass
class UIKeyPressEvent(UIKeyEvent):
    pass


@dataclass
class UIKeyReleaseEvent(UIKeyEvent):
    pass


@dataclass
class UITextEvent(UIEvent):
    text: str


@dataclass
class UITextMotionEvent(UIEvent):
    motion: Any


@dataclass
class UITextMotionSelectEvent(UIEvent):
    selection: Any


@dataclass
class UIOnClickEvent(UIMouseEvent):
    pass


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
