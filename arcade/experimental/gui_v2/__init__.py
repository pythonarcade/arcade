"""
The better gui for arcade

- Improved events, now fully typed
- UIElements are now called Widgets (like everywhere else)
- Widgets render into a FrameBuffer, which supports in memory drawings with less memory usage
- Support for animated widgets
- Texts are now rendered with pyglet, open easier support for text areas with scolling
- TextArea with scroll support
"""
import arcade
from typing import List

from arcade.experimental.gui_v2.events import MouseMovement, MousePress, MouseRelease, MouseScroll
from arcade.experimental.gui_v2.surface import Surface
from arcade.experimental.gui_v2.widgets import Widget


class UIManager:
    def __init__(self) -> None:
        self.window = arcade.get_window()
        self._surface = Surface(
            size=self.window.get_size(),
            pixel_ratio=self.window.get_pixel_ratio(),
        )
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

    def resize(self, width, height):
        scale = arcade.get_scaling_factor(self.window)
        self._surface.resize(size=(width, height), pixel_ratio=scale)
