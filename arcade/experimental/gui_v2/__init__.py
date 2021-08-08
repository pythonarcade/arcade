"""
The better gui for arcade

- Improved events, now fully typed
- UIElements are now called Widgets (like everywhere else)
- Widgets render into a FrameBuffer, which supports in memory drawings with less memory usage
- Support for animated widgets
- Texts are now rendered with pyglet, open easier support for text areas with scolling
- TextArea with scroll support
"""
from collections import defaultdict
from typing import List, Dict

import pyglet.event

import arcade
from arcade.experimental.gui_v2.events import UIMouseMovementEvent, UIMousePressEvent, UIMouseReleaseEvent, \
    UIMouseScrollEvent, UITextEvent, \
    UIMouseDragEvent, \
    UITextMotionEvent, UITextMotionSelectEvent, UIEvent, UIKeyPressEvent, UIKeyReleaseEvent
from arcade.experimental.gui_v2.surface import Surface
from arcade.experimental.gui_v2.widgets import Widget, WidgetParent, Rect


class UIManager(pyglet.event.EventDispatcher, WidgetParent):
    """
    V2 UIManager

    manager = UIManager()
    manager.enable() # hook up window events

    manager.add(Dummy())

    def on_update(dt):
        # This will update all children and prepares the UI
        manager.on_update(dt)

    def on_draw():
        arcade.start_render()

        ...

        manager.draw() # draws the UI on screen

    """

    def __init__(self, window: arcade.Window = None, auto_enable=False):
        self.window = window or arcade.get_window()
        self._surfaces = {0: Surface(
            size=self.window.get_size(),
            pixel_ratio=self.window.get_pixel_ratio(),
        )}
        self._children: Dict[int, List[Widget]] = defaultdict(list)
        self.rendered = False

        self.register_event_type("on_event")

        if auto_enable:
            self.enable()

    def add(self, widget: Widget, layer=0) -> Widget:
        self._children[layer].append(widget)
        widget.parent = self
        return widget

    def remove(self, child: Widget):
        for children in self._children.values():
            if child in children:
                children.remove(child)
                self.rendered = False

    def _get_surface(self, layer: int):
        if layer not in self._surfaces:
            if len(self._surfaces) > 2:
                raise Exception("Don't use too much layers!")

            self._surfaces[layer] = Surface(
                size=self.window.get_size(),
                pixel_ratio=self.window.get_pixel_ratio(),
            )

        return self._surfaces.get(layer)

    def _render(self, force=False):
        force = force or not self.rendered

        layers = sorted(self._children.keys())
        for layer in layers:
            for child in self._children[layer]:
                force = child.do_layout() or force

            surface = self._get_surface(layer)
            with surface.activate():
                if force:
                    surface.clear()

                for child in self._children[layer]:
                    surface.limit(*child.rect)
                    child.render(surface, force)

        self.rendered = True

    def enable(self):
        """
        Registers handler functions (`on_...`) to :py:attr:`arcade.gui.UIElement`

        on_draw is not registered, to provide full control about draw order,
        so it has to be called by the devs themselves.
        """
        self.window.push_handlers(
            self.on_resize,
            self.on_update,
            self.on_mouse_drag,
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_key_press,
            self.on_key_release,
            self.on_text,
            self.on_text_motion,
            self.on_text_motion_select,
        )

    def disable(self):
        """
        Remove handler functions (`on_...`) from :py:attr:`arcade.Window`

        If every :py:class:`arcade.View` uses its own :py:class:`arcade.gui.UIManager`,
        this method should be called in :py:meth:`arcade.View.on_hide_view()`.
        """
        self.window.remove_handlers(
            self.on_resize,
            self.on_update,
            self.on_mouse_drag,
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_key_press,
            self.on_key_release,
            self.on_text,
            self.on_text_motion,
            self.on_text_motion_select,
        )

    def on_update(self, time_delta):
        layers = sorted(self._children.keys())
        for layer in layers:
            for child in self._children[layer]:
                child.on_update(time_delta)

        self._render()

    def draw(self):
        layers = sorted(self._children.keys())
        for layer in layers:
            self._get_surface(layer).draw()

    def on_event(self, event):
        layers = sorted(self._children.keys(), reverse=True)
        for layer in layers:
            for child in reversed(self._children[layer]):
                if child.dispatch_event("on_event", event):
                    # child can consume an event by returning True
                    return

    def dispatch_ui_event(self, event):
        self.dispatch_event("on_event", event)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.dispatch_ui_event(UIMouseMovementEvent(self, x, y, dx, dy))

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.dispatch_ui_event(UIMousePressEvent(self, x, y, button, modifiers))

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        self.dispatch_ui_event(UIMouseDragEvent(self, x, y, dx, dy, buttons, modifiers))

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.dispatch_ui_event(UIMouseReleaseEvent(self, x, y, button, modifiers))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.dispatch_ui_event(UIMouseScrollEvent(self, x, y, scroll_x, scroll_y))

    def on_key_press(self, symbol: int, modifiers: int):
        self.dispatch_ui_event(UIKeyPressEvent(self, symbol, modifiers))

    def on_key_release(self, symbol: int, modifiers: int):
        self.dispatch_ui_event(UIKeyReleaseEvent(self, symbol, modifiers))

    def on_text(self, text):
        self.dispatch_ui_event(UITextEvent(self, text))

    def on_text_motion(self, motion):
        self.dispatch_ui_event(UITextMotionEvent(self, motion))

    def on_text_motion_select(self, motion):
        self.dispatch_ui_event(UITextMotionSelectEvent(self, motion))

    def on_resize(self, width, height):
        scale = arcade.get_scaling_factor(self.window)

        for surface in self._surfaces.values():
            surface.resize(size=(width, height), pixel_ratio=scale)

        self.rendered = False

    @property
    def rect(self) -> Rect:
        return Rect(0, 0, *self._surfaces[0].size)
