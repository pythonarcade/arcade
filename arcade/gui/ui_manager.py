"""
The better gui for arcade

- Improved events, now fully typed
- UIElements are now called Widgets (like everywhere else)
- Widgets render into a FrameBuffer, which supports in memory drawings with less memory usage
- Support for animated widgets
- Texts are now rendered with pyglet, open easier support for text areas with scrolling
- TextArea with scroll support
"""
from collections import defaultdict
from typing import List, Dict, TypeVar, Iterable, Optional

from pyglet.event import EventDispatcher, EVENT_HANDLED, EVENT_UNHANDLED

import arcade
from arcade.gui.events import (
    UIMouseMovementEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIMouseScrollEvent,
    UITextEvent,
    UIMouseDragEvent,
    UITextMotionEvent,
    UITextMotionSelectEvent,
    UIKeyPressEvent,
    UIKeyReleaseEvent,
    UIOnUpdateEvent,
)
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIWidget, UIWidgetParent, Rect

W = TypeVar("W", bound=UIWidget)


class UIManager(EventDispatcher, UIWidgetParent):
    """
    UIManager is the central component within Arcade's GUI system.
    Handles window events, layout process and rendering.

    To process window events, :py:meth:`UIManager.enable()` has to be called,
    which will inject event callbacks for all window events and redirects them through the widget tree.

    If used within a view :py:meth:`UIManager.enable()` should be called from :py:meth:`View.on_show_view()` and
    :py:meth:`UIManager.disable()` should be called from :py:meth:`View.on_hide_view()`

    Supports `size_hint` to grow/shrink direct children dependent on window size.
    Supports `size_hint_min` to ensure size of direct children (e.g. UIBoxLayout).
    Supports `size_hint_max` to ensure size of direct children (e.g. UIBoxLayout).

    .. code:: py

        manager = UIManager()
        manager.enable() # hook up window events

        manager.add(Dummy())

        def on_draw():
            self.clear()

            ...

            manager.draw() # draws the UI on screen

    """

    _enabled = False

    def __init__(self, window: Optional[arcade.Window] = None):
        super().__init__()
        self.window = window or arcade.get_window()
        self._surfaces: Dict[int, Surface] = {}
        self.children: Dict[int, List[UIWidget]] = defaultdict(list)
        self._rendered = False

        self.register_event_type("on_event")

    def add(self, widget: W, *, index=None) -> W:
        """
        Add a widget to the :class:`UIManager`.
        Added widgets will receive ui events and be rendered.

        By default the latest added widget will receive ui events first and will be rendered on top of others.

        :param widget: widget to add
        :param index: position a widget is added, None has the highest priority
        :return: the widget
        """
        if index is None:
            self.children[0].append(widget)
        else:
            self.children[0].insert(max(len(self.children), index), widget)
        widget.parent = self
        self.trigger_render()
        return widget

    def remove(self, child: UIWidget):
        """
        Removes the given widget from UIManager.

        :param UIWidget child: widget to remove
        """
        for children in self.children.values():
            if child in children:
                children.remove(child)
                child.parent = None
                self.trigger_render()

    def walk_widgets(self, *, root: Optional[UIWidget] = None) -> Iterable[UIWidget]:
        """walks through widget tree, in reverse draw order (most top drawn widget first)"""
        layer = 0
        children = root.children if root else self.children[layer]
        for child in reversed(children):
            yield from self.walk_widgets(root=child)
            yield child

    def clear(self):
        """
        Remove all widgets from UIManager
        """
        for layer in self.children.values():
            for widget in layer:
                self.remove(widget)

    def get_widgets_at(self, pos, cls=UIWidget) -> Iterable[W]:
        """
        Yields all widgets containing a position, returns first top laying widgets which is instance of cls.

        :param pos: Pos within the widget bounds
        :param cls: class which the widget should be instance of
        :return: iterator of widgets of given type at position
        """
        for widget in self.walk_widgets():
            if isinstance(widget, cls) and widget.rect.collide_with_point(*pos):
                yield widget

    def _get_surface(self, layer: int):
        if layer not in self._surfaces:
            if len(self._surfaces) > 2:
                raise Exception("Don't use too much layers!")

            self._surfaces[layer] = Surface(
                size=self.window.get_size(),
                pixel_ratio=self.window.get_pixel_ratio(),
            )

        return self._surfaces.get(layer)

    def trigger_render(self):
        """
        Request rendering of all widgets
        """
        self._rendered = False

    def _do_layout(self):
        layers = sorted(self.children.keys())
        for layer in layers:
            surface = self._get_surface(layer)
            surface_width, surface_height = surface.size

            for child in self.children[layer]:

                if child.size_hint:
                    sh_x, sh_y = child.size_hint
                    nw = surface_width * sh_x if sh_x else None
                    nh = surface_height * sh_y if sh_y else None
                    child.rect = child.rect.resize(nw, nh)

                if child.size_hint_min:
                    shm_w, shm_h = child.size_hint_min
                    child.rect = child.rect.min_size(shm_w or 0, shm_h or 0)

                if child.size_hint_max:
                    shm_w, shm_h = child.size_hint_max
                    child.rect = child.rect.max_size(
                        shm_w or child.width, shm_h or child.height
                    )

                child._do_layout()

    def _do_render(self, force=False):
        layers = sorted(self.children.keys())
        force = force or not self._rendered
        for layer in layers:
            surface = self._get_surface(layer)
            with surface.activate():
                if force:
                    surface.clear()

                for child in self.children[layer]:
                    child._do_render(surface, force)

        self._rendered = True

    def enable(self) -> None:
        """
        Registers handler functions (`on_...`) to :py:attr:`arcade.gui.UIElement`

        on_draw is not registered, to provide full control about draw order,
        so it has to be called by the devs themselves.
        """
        if not self._enabled:
            self._enabled = True
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

    def disable(self) -> None:
        """
        Remove handler functions (`on_...`) from :py:attr:`arcade.Window`

        If every :py:class:`arcade.View` uses its own :py:class:`arcade.gui.UIManager`,
        this method should be called in :py:meth:`arcade.View.on_hide_view()`.
        """
        if self._enabled:
            self._enabled = False
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
        return self.dispatch_ui_event(UIOnUpdateEvent(self, time_delta))

    def draw(self) -> None:
        # Request Widgets to prepare for next frame
        self._do_layout()

        ctx = self.window.ctx

        # When drawing into the framebuffer we need to set a separate
        # blend function for the alpha component.
        ctx.blend_func = (
            ctx.SRC_ALPHA,
            ctx.ONE_MINUS_SRC_ALPHA,  # RGB blend func (default)
            ctx.ONE,
            ctx.ONE_MINUS_SRC_ALPHA,  # Alpha blend func
        )
        self._do_render()

        # Reset back to default blend function
        ctx.blend_func = ctx.BLEND_DEFAULT

        # Draw layers
        layers = sorted(self.children.keys())
        for layer in layers:
            self._get_surface(layer).draw()

        # Reset back to default blend function
        ctx.blend_func = ctx.BLEND_DEFAULT

    def adjust_mouse_coordinates(self, x, y):
        """
        This method is used, to translate mouse coordinates to coordinates
        respecting the viewport and projection of cameras.
        The implementation should work in most common cases.

        If you use scrolling in the :py:class:`arcade.Camera` you have to reset scrolling
        or overwrite this method using the camera conversion::

            ui_manager.adjust_mouse_coordinates = camera.mouse_coordinates_to_world
        """
        # TODO This code does not work anymore, for now no camera support by default
        # vx, vy, vw, vh = self.window.ctx.viewport
        # pl, pr, pb, pt = self.window.ctx.projection_2d
        # proj_width, proj_height = pr - pl, pt - pb
        # dx, dy = proj_width / vw, proj_height / vh
        # return (x - vx) * dx, (y - vy) * dy
        return x, y

    def on_event(self, event) -> bool:
        layers = sorted(self.children.keys(), reverse=True)
        for layer in layers:
            for child in reversed(self.children[layer]):
                if child.dispatch_event("on_event", event):
                    # child can consume an event by returning True
                    return EVENT_HANDLED
        return EVENT_UNHANDLED

    def dispatch_ui_event(self, event):
        return self.dispatch_event("on_event", event)

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        x, y = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMouseMovementEvent(self, x, y, dx, dy))  # type: ignore

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        x, y = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMousePressEvent(self, x, y, button, modifiers))  # type: ignore

    def on_mouse_drag(
        self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int
    ):
        x, y = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMouseDragEvent(self, x, y, dx, dy, buttons, modifiers))  # type: ignore

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        x, y = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMouseReleaseEvent(self, x, y, button, modifiers))  # type: ignore

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x, y = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(
            UIMouseScrollEvent(self, x, y, scroll_x, scroll_y)
        )

    def on_key_press(self, symbol: int, modifiers: int):
        return self.dispatch_ui_event(UIKeyPressEvent(self, symbol, modifiers))  # type: ignore

    def on_key_release(self, symbol: int, modifiers: int):
        return self.dispatch_ui_event(UIKeyReleaseEvent(self, symbol, modifiers))  # type: ignore

    def on_text(self, text):
        return self.dispatch_ui_event(UITextEvent(self, text))

    def on_text_motion(self, motion):
        return self.dispatch_ui_event(UITextMotionEvent(self, motion))

    def on_text_motion_select(self, motion):
        return self.dispatch_ui_event(UITextMotionSelectEvent(self, motion))

    def on_resize(self, width, height):
        scale = arcade.get_scaling_factor(self.window)

        for surface in self._surfaces.values():
            surface.resize(size=(width, height), pixel_ratio=scale)

        self.trigger_render()

    @property
    def rect(self) -> Rect:  # type: ignore
        return Rect(0, 0, *self.window.get_size())

    def debug(self):
        """Walks through all widgets of a UIManager and prints out the rect"""
        for index, layer in self.children.items():
            print(f"Layer {index}")
            for child in reversed(layer):
                self._debug(child, prefix="  ")
        return

    @staticmethod
    def _debug(element, prefix=""):
        print(f"{prefix}{element.__class__}:{element.rect}")
        if isinstance(element, UIWidget):
            for child in element.children:
                UIManager._debug(child, prefix=prefix + "  ")
