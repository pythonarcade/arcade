"""
The better gui for arcade

- Improved events, now fully typed
- UIElements are now called Widgets (like everywhere else)
- Widgets render into a FrameBuffer, which supports in memory drawings with less memory usage
- Support for animated widgets
- Texts are now rendered with pyglet, open easier support for text areas with scrolling
- TextArea with scroll support
"""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Type, TypeVar, Union, Tuple

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED, EventDispatcher
from typing_extensions import TypeGuard

import arcade
from arcade.gui.events import (UIKeyPressEvent, UIKeyReleaseEvent,
                               UIMouseDragEvent, UIMouseMovementEvent,
                               UIMousePressEvent, UIMouseReleaseEvent,
                               UIMouseScrollEvent, UIOnUpdateEvent,
                               UITextEvent, UITextMotionEvent,
                               UITextMotionSelectEvent)
from arcade.gui.surface import Surface
from arcade.gui.widgets import Rect, UIWidget
from arcade.types import Point

W = TypeVar("W", bound=UIWidget)


class UIManager(EventDispatcher):
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

        class MyView(arcade.View):
            def __init__():
                super().__init__()
                manager = UIManager()

                manager.add(Dummy())

            def on_show_view(self):
                # Set background color
                self.window.background_color = arcade.color.DARK_BLUE_GRAY

                # Enable UIManager when view is shown to catch window events
                self.ui.enable()

            def on_hide_view(self):
                # Disable UIManager when view gets inactive
                self.ui.disable()

            def on_draw():
                self.clear()

                ...

                manager.draw() # draws the UI on screen

    """

    _enabled = False

    OVERLAY_LAYER = 10

    def __init__(self, window: Optional[arcade.Window] = None):
        super().__init__()
        self.window = window or arcade.get_window()
        self._surfaces: Dict[int, Surface] = {}
        self.children: Dict[int, List[UIWidget]] = defaultdict(list)
        self._requires_render = True
        self.register_event_type("on_event")

    def add(self, widget: W, *, index=None, layer=0) -> W:
        """
        Add a widget to the :class:`UIManager`.
        Added widgets will receive ui events and be rendered.

        By default the latest added widget will receive ui events first and will be rendered on top of others.

        The UIManager supports layered setups, widgets added to a higher layer are drawn above lower layers
        and receive events first.
        The layer 10 is reserved for overlaying components like dropdowns or tooltips.

        :param widget: widget to add
        :param index: position a widget is added, None has the highest priority
        :param layer: layer which the widget should be added to, higher layer are above
        :return: the widget
        """
        if index is None:
            self.children[layer].append(widget)
        else:
            self.children[layer].insert(max(len(self.children), index), widget)
        widget.parent = self
        self.trigger_render()
        return widget

    def remove(self, child: UIWidget):
        """
        Removes the given widget from UIManager.

        :param child: widget to remove
        """
        for children in self.children.values():
            if child in children:
                children.remove(child)
                child.parent = None
                self.trigger_render()

    def walk_widgets(
        self, *, root: Optional[UIWidget] = None, layer=0
    ) -> Iterable[UIWidget]:
        """
        walks through widget tree, in reverse draw order (most top drawn widget first)

        :param root: root widget to start from, if None, the layer is used
        :param layer: layer to search, None will search through all layers
        """
        if layer is None:
            layers = sorted(self.children.keys(), reverse=True)
        else:
            layers = [layer]

        for layer in layers:
            children = root.children if root else self.children[layer]
            for child in reversed(children):
                yield from self.walk_widgets(root=child)
                yield child

    def clear(self):
        """
        Remove all widgets from UIManager
        """
        for layer in self.children.values():
            for widget in layer[:]:
                self.remove(widget)

    def get_widgets_at(
        self, pos: Point, cls: Type[W] = UIWidget, layer=0
    ) -> Iterable[W]:
        """
        Yields all widgets containing a position, returns first top laying widgets which is instance of cls.

        :param pos: Pos within the widget bounds
        :param cls: class which the widget should be an instance of
        :param layer: layer to search, None will search through all layers
        :return: iterator of widgets of given type at position
        """

        def check_type(widget) -> TypeGuard[W]:
            return isinstance(widget, cls)

        for widget in self.walk_widgets(layer=layer):
            if check_type(widget) and widget.rect.collide_with_point(*pos):
                yield widget

    def _get_surface(self, layer: int) -> Surface:
        if layer not in self._surfaces:
            if len(self._surfaces) > 2:
                raise Exception("Don't use too much layers!")

            self._surfaces[layer] = Surface(
                size=self.window.get_size(),
                pixel_ratio=self.window.get_pixel_ratio(),
            )

        return self._surfaces[layer]

    def trigger_render(self):
        """
        Request rendering of all widgets before next draw
        """
        self._requires_render = True

    def execute_layout(self):
        """
        Execute layout process for all widgets.

        This is automatically called during :py:meth:`UIManager.draw()`.
        """
        self._do_layout()

    def _do_layout(self):
        layers = sorted(self.children.keys())
        for layer in layers:
            surface = self._get_surface(layer)
            if not surface:
                raise ValueError("No surface exists for this layer.")
            surface_width, surface_height = surface.size

            for child in self.children[layer]:
                # prepare children, so size_hints are calculated
                child._prepare_layout()

                # actual layout
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

                # continue layout process down the tree
                child._do_layout()

    def _do_render(self, force=False):
        layers = sorted(self.children.keys())
        force = force or self._requires_render
        for layer in layers:
            surface = self._get_surface(layer)

            if surface is None:
                raise ValueError("Surface is None for layer, can't render.")

            with surface.activate():
                if force:
                    surface.clear()

                for child in self.children[layer]:
                    child._do_render(surface, force)

        self._requires_render = False

    def enable(self) -> None:
        """
        Registers handler functions (`on_...`) to :py:attr:`arcade.gui.UIElement`

        on_draw is not registered, to provide full control about draw order,
        so it has to be called by the devs themselves.

        Within a view, this method should be called from :py:meth:`arcade.View.on_show_view()`.
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
        current_cam = self.window.current_camera
        """
        Will draw all widgets to the window.

        UIManager caches all rendered widgets into a framebuffer (something like a window sized image)
        and only updates the framebuffer if a widget requests rendering via trigger_render().

        To ensure that the children are positioned properly,
        a layout process is executed before rendering, changes might also trigger a re-rendering of all widgets.

        Layouting is a two-step process:
        1. Prepare layout, which prepares children and updates own values
        2. Do layout, which actually sets the position and size of the children
        """
        # Request widgets to prepare for next frame
        self.execute_layout()

        ctx = self.window.ctx
        with ctx.enabled(ctx.BLEND):
            self._do_render()

        # Correct that the ui changes the currently active camera.
        current_cam.use()

        # Draw layers
        with ctx.enabled(ctx.BLEND):
            layers = sorted(self.children.keys())
            for layer in layers:
                self._get_surface(layer).draw()

    def adjust_mouse_coordinates(self, x: float, y: float) -> Tuple[float, float]:
        """
        This method is used, to translate mouse coordinates to coordinates
        respecting the viewport and projection of cameras.

        It uses the internal camera's map_coordinate methods, and should work with
        all transformations possible with the basic orthographic camera.
        """
        x_, y_, *c = self.window.current_camera.map_screen_to_world_coordinate((x, y))
        return x_, y_

    def on_event(self, event) -> Union[bool, None]:
        layers = sorted(self.children.keys(), reverse=True)
        for layer in layers:
            for child in reversed(self.children[layer]):
                if child.dispatch_event("on_event", event):
                    # child can consume an event by returning True
                    return EVENT_HANDLED
        return EVENT_UNHANDLED

    def dispatch_ui_event(self, event):
        return self.dispatch_event("on_event", event)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        x_, y_ = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMouseMovementEvent(self, int(x_), int(y), dx, dy))

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        x_, y_ = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMousePressEvent(self, int(x_), int(y_), button, modifiers))

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
    ):
        x_, y_ = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMouseDragEvent(self, int(x_), int(y_), dx, dy, buttons, modifiers))

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        x_, y_ = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(UIMouseReleaseEvent(self, int(x_), int(y_), button, modifiers))

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        x_, y_ = self.adjust_mouse_coordinates(x, y)
        return self.dispatch_ui_event(
            UIMouseScrollEvent(self, int(x_), int(y_), scroll_x, scroll_y)
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
        scale = self.window.get_pixel_ratio()
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
