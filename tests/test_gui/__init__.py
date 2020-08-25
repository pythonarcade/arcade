import os
from typing import List, Optional
from uuid import uuid4

import PIL
import pytest

import arcade
import arcade.gui
from arcade.gui import UIClickable, UIManager
from arcade.gui.ui_style import UIStyle


class TestUIManager(UIManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_history: List[arcade.gui.UIEvent] = []

        self.push_handlers(on_ui_event=self._on_ui_event)

    def move_mouse(self, x: int, y: int):
        self.dispatch_ui_event(arcade.gui.UIEvent(
            arcade.gui.MOUSE_MOTION,
            x=x,
            y=y,
            button=1,
            modifier=0
        ))

    def click_and_hold(self, x: int, y: int):
        self.dispatch_ui_event(arcade.gui.UIEvent(
            arcade.gui.MOUSE_PRESS,
            x=x,
            y=y,
            button=1,
            modifier=0
        ))

    def release(self, x: int, y: int):
        self.dispatch_ui_event(arcade.gui.UIEvent(
            arcade.gui.MOUSE_RELEASE,
            x=x,
            y=y,
            button=1,
            modifier=0
        ))

    def click(self, x: int, y: int):
        self.click_and_hold(x, y)
        self.release(x, y)

    def _on_ui_event(self, event: arcade.gui.UIEvent):
        self.event_history.append(event)

    @property
    def last_event(self):
        return self.event_history[-1] if self.event_history else None


def T(name, *args):
    return pytest.param(*args, id=name)


class MockHolder(dict):
    """
    MockHolder, dict like object with property access
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Env:
    def __init__(self, **kwargs):
        self.variables = kwargs
        self.old_vars = {}

    def __enter__(self):
        for key, value in self.variables.items():
            if key in os.environ:
                self.old_vars[key] = os.environ[key]

            os.environ[key] = value

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.variables.keys():
            del os.environ[key]

        for key, value in self.old_vars.items():
            os.environ[key] = value


class MockButton(UIClickable):
    on_hover_called = False
    on_unhover_called = False
    on_press_called = False
    on_release_called = False
    on_click_called = False
    on_focus_called = False
    on_unfocus_called = False

    def __init__(self,
                 center_x=0,
                 center_y=0,
                 width=40,
                 height=40,
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        super().__init__(center_x=center_x, center_y=center_y, id=id, style=style, **kwargs)
        self.event_history: List[arcade.gui.UIEvent] = []
        self._width = width
        self._height = height

    def render(self):
        self.normal_texture = arcade.Texture(
            image=PIL.Image.new("RGBA", (self._width, self._height), color=(255, 0, 0)),
            name=str(uuid4()))
        self.hover_texture = arcade.Texture(
            image=PIL.Image.new("RGBA", (self._width, self._height), color=(255, 0, 0)),
            name=str(uuid4()))
        self.press_texture = arcade.Texture(
            image=PIL.Image.new("RGBA", (self._width, self._height), color=(255, 0, 0)),
            name=str(uuid4()))
        self.focus_texture = arcade.Texture(
            image=PIL.Image.new("RGBA", (self._width, self._height), color=(255, 0, 0)),
            name=str(uuid4()))

        self.set_proper_texture()

    def on_ui_event(self, event: arcade.gui.UIEvent):
        self.event_history.append(event)
        super().on_ui_event(event)

    @property
    def last_event(self):
        return self.event_history[-1] if self.event_history else None

    def on_hover(self):
        super().on_hover()
        self.on_hover_called = True

    def on_unhover(self):
        super().on_unhover()
        self.on_unhover_called = True

    def on_press(self):
        super().on_press()
        self.on_press_called = True

    def on_release(self):
        super().on_release()
        self.on_release_called = True

    def on_click(self):
        super().on_click()
        self.on_click_called = True

    def on_focus(self):
        super().on_focus()
        self.on_focus_called = True

    def on_unfocus(self):
        super().on_unfocus()
        self.on_unfocus_called = True
