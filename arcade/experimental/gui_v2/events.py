from dataclasses import dataclass
from typing import Any


class Event:
    pass


@dataclass
class MouseMovement(Event):
    x: float
    y: float
    dx: float
    dy: float


@dataclass
class MousePress(Event):
    x: float
    y: float
    button: int
    modifiers: int

@dataclass
class MouseDrag(Event):
    x: float
    y: float
    dx: float
    dy: float
    buttons: int
    modifiers: int


@dataclass
class MouseRelease(Event):
    x: float
    y: float
    button: int
    modifiers: int

@dataclass
class MouseScroll(Event):
    x: float
    y: float
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