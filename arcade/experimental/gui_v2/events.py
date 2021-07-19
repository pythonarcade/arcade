from dataclasses import dataclass


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
