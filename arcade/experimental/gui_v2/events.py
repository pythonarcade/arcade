from dataclasses import dataclass
from typing import Any


class Event:
    pass


@dataclass
class MouseEvent(Event):
    """
    Covers all mouse event
    """
    x: float
    y: float


@dataclass
class MouseMovement(MouseEvent):
    dx: float
    dy: float


@dataclass
class MousePress(MouseEvent):
    button: int
    modifiers: int


@dataclass
class MouseDrag(MouseEvent):
    dx: float
    dy: float
    buttons: int
    modifiers: int


@dataclass
class MouseRelease(MouseEvent):
    button: int
    modifiers: int


@dataclass
class MouseScroll(MouseEvent):
    scroll_x: int
    scroll_y: int


@dataclass
class Text(Event):
    text: str


@dataclass
class TextMotion(Event):
    motion: Any


@dataclass
class TextMotionSelect(Event):
    motion: Any
