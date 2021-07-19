"""
The better gui for arcade

- Improved events, now fully typed
- UIElements are now called Widgets (like everywhere else)
- Widgets render into a FrameBuffer, which supports in memory drawings with less memory usage
- Support for animated widgets
- Texts are now rendered with pyglet, open easier support for text areas with scolling
- TextArea with scroll support
"""
from typing import List

from arcade.experimental.gui_v2.events import MouseMovement, MousePress, MouseRelease, MouseScroll
from arcade.experimental.gui_v2.surface import Surface
from arcade.experimental.gui_v2.widgets import Widget





class UIManager:
    def __init__(self) -> None:
        self._surface = Surface()
        self._children: List[Widget] = []

    def add(self, widget: Widget) -> Widget:
        self._children.append(widget)
        return widget

    def render(self):
        with self._surface.activate():
            for child in self._children:
                self._surface.limit(*child.rect())
                child.render(self._surface)

    def on_update(self, time_delta):
        for child in self._children:
            child.on_update(time_delta)

    def draw(self):
        self._surface.draw()

    def on_event(self, event):
        for child in self._children:
            if child.on_event(event):
                # child can consume an event by returning True
                break

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.on_event(MouseMovement(x, y, dx, dy))

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.on_event(MousePress(x, y, button, modifiers))

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.on_event(MouseRelease(x, y, button, modifiers))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.on_event(MouseScroll(x, y, scroll_x, scroll_y))
