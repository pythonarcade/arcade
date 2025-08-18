from __future__ import annotations

import weakref
from abc import ABC
from collections.abc import Iterable
from enum import IntEnum
from types import EllipsisType
from typing import Any, Generic, TYPE_CHECKING, NamedTuple, TypeVar, overload
from weakref import WeakKeyDictionary

from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED, EventDispatcher
from pyglet.math import Vec2
from typing_extensions import Self

import arcade
from arcade import LBWH, Rect, Sprite, Texture
from arcade.color import TRANSPARENT_BLACK
from arcade.gui.events import (
    UIEvent,
    UIMouseMovementEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIOnClickEvent,
    UIOnUpdateEvent,
    UIControllerButtonPressEvent,
    UIControllerButtonReleaseEvent,
    UIKeyPressEvent,
    UIKeyReleaseEvent,
)
from arcade.gui.nine_patch import NinePatchTexture
from arcade.gui.property import ListProperty, Property, bind
from arcade.gui.surface import Surface
from arcade.types import AnchorPoint, AsFloat, Color
from arcade.utils import copy_dunders_unimplemented

if TYPE_CHECKING:
    from arcade.gui.ui_manager import UIManager

W = TypeVar("W", bound="UIWidget")
P = TypeVar("P")


class FocusMode(IntEnum):
    """Defines the focus mode of a widget.

    0: Not focusable
    1: Focusable

    We might support different focus modes in the future, but for now on/off is enough.
    """

    NONE = 0
    ALL = 2


class _ChildEntry(NamedTuple):
    child: UIWidget
    data: dict


class WeakRef(Generic[P]):
    """A weak reference to a UIWidget parent, which is used to prevent memory leaks."""

    __slots__ = ("name", "obs")
    name: str
    """Attribute name of the property"""
    obs: WeakKeyDictionary[Any, weakref.ref[P]]
    """Weak dictionary to hold the values"""

    def __init__(self):
        self.obs = WeakKeyDictionary()

    def get(self, instance: Any) -> P | None:
        """Get value for owner instance"""
        # If the value is not set, return None
        value = self.obs.get(instance)
        return value() if value else None

    def set(self, instance, value: P | None):
        """Set value for owner instance"""
        # Store a weak reference to the value
        if value is None:
            self.obs.pop(instance, None)
        else:
            self.obs[instance] = weakref.ref(value)

    def __set_name__(self, owner, name):
        self.name = name

    @overload
    def __get__(self, instance: None, instance_type) -> Self: ...

    @overload
    def __get__(self, instance: Any, instance_type) -> P | None: ...

    def __get__(self, instance: Any | None, instance_type) -> Self | P | None:
        """Get the value for the owner instance, or None if not set."""
        if instance is None:
            return self
        return self.get(instance)

    def __set__(self, instance, value: P | None):
        self.set(instance, value)


@copy_dunders_unimplemented
class UIWidget(EventDispatcher, ABC):
    """The :class:`UIWidget` class is the base class required for creating widgets.

    We also have some default values and behaviors that you should be aware of:

    * A :class:`UIWidget` is not a :class:`~arcade.gui.UILayout`: it will not
      change the position or the size of its children. If you want control over
      positioning or sizing, use a :class:`~arcade.gui.UILayout`.

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget
        height: height of widget
        size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
        size_hint_min: min width and height in pixel
        size_hint_max: max width and height in pixel
    """

    parent: WeakRef[UIManager | UIWidget | None] = WeakRef()
    """A weak reference to the parent UIManager or UIWidget,
    which does not prevent garbage collection of the parent."""
    rect = Property(LBWH(0, 0, 1, 1))
    visible = Property[bool | None](True)
    """If True, the widget is visible and will be rendered. If None,
    the widget should also be skipped by layouts."""
    focused = Property(False)
    focus_mode: FocusMode = FocusMode.NONE

    size_hint = Property[tuple[float | None, float | None] | None](None)
    size_hint_min = Property[tuple[float | None, float | None] | None](None)
    size_hint_max = Property[tuple[float | None, float | None] | None](None)

    _children = ListProperty[_ChildEntry]()
    _border_width = Property(0)
    _border_color = Property[Color | None](arcade.color.BLACK)
    _bg_color = Property[Color | None]()
    _bg_tex = Property[Texture | NinePatchTexture | None]()
    _padding_top = Property(0)
    _padding_right = Property(0)
    _padding_bottom = Property(0)
    _padding_left = Property(0)
    _strong_background = Property(False)
    """If True, the background will clear the surface, even if it is not fully opaque.
    This is not part of the public API and subject to change.
    UILabel have a strong background if set.
    """
    _active = Property[bool](False)
    """If True, the widget is active"""

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        children: Iterable[UIWidget] = tuple(),
        # Properties which might be used by layouts
        size_hint: tuple[float | None, float | None] | None = None,  # in percentage
        size_hint_min: tuple[float | None, float | None] | None = None,  # in pixel
        size_hint_max: tuple[float | None, float | None] | None = None,  # in pixel
        **kwargs,
    ):
        self._requires_render = True
        self.rect = LBWH(x, y, width, height)

        # Size hints are properties that can be used by layouts
        self.size_hint = size_hint
        self.size_hint_min = size_hint_min
        self.size_hint_max = size_hint_max

        self.register_event_type("on_event")
        self.register_event_type("on_update")

        for child in children:
            self.add(child)

        bind(self, "rect", UIWidget.trigger_full_render)
        bind(self, "focused", UIWidget.trigger_full_render)
        bind(
            self, "visible", UIWidget.trigger_full_render
        )  # TODO maybe trigger_parent_render would be enough
        bind(self, "_children", UIWidget.trigger_render)
        bind(self, "_border_width", UIWidget.trigger_render)
        bind(self, "_border_color", UIWidget.trigger_render)
        bind(self, "_bg_color", UIWidget.trigger_render)
        bind(self, "_bg_tex", UIWidget.trigger_render)
        bind(self, "_padding_top", UIWidget.trigger_render)
        bind(self, "_padding_right", UIWidget.trigger_render)
        bind(self, "_padding_bottom", UIWidget.trigger_render)
        bind(self, "_padding_left", UIWidget.trigger_render)
        bind(self, "_strong_background", UIWidget.trigger_render)

    def add(self, child: W, **kwargs) -> W:
        """Add a widget as a child.

        Added widgets will receive UI events and be rendered.

        By default, the latest added widget will receive ui events first and will
        be rendered on top of others.

        Args:
            child: widget to add
            index: position a widget is added, None has the highest
                priority

        Returns:
            given child
        """
        child.parent = self
        index = kwargs.pop("index") if "index" in kwargs else None
        if index is None:
            self._children.append(_ChildEntry(child, kwargs))
        else:
            if not 0 <= index <= len(self.children):
                raise ValueError("Index must be between 0 and the number of children")
            self._children.insert(index, _ChildEntry(child, kwargs))

        return child

    # TODO "focus" would be more intuative but clashes with the UIFocusGroups :/
    # maybe the two systems should be merged?
    def _grap_active(self):
        """Sets itself as the single active widget in the UIManager."""
        ui_manager: UIManager | None = self.get_ui_manager()
        if ui_manager:
            ui_manager._set_active_widget(self)

    def _release_active(self):
        """Make this widget inactive in the UIManager."""
        if not self._active:
            return

        ui_manager: UIManager | None = self.get_ui_manager()
        if ui_manager and ui_manager._active_widget is self:
            ui_manager._set_active_widget(None)

    def remove(self, child: UIWidget) -> dict | None:
        """Removes a child from the UIManager which was directly added to it.
        This will not remove widgets which are added to a child of UIManager.

        Return:
            kwargs which were used when child was added
        """
        child.parent = None
        for c in self._children:
            if c.child == child:
                self._children.remove(c)
                return c.data
        return None

    def clear(self):
        """Removes all children"""
        for child in self.children:
            child.parent = None

        self._children.clear()

    def __contains__(self, item):
        return item in self.children

    def on_update(self, dt):
        """Custom logic which will be triggered."""
        pass

    def on_event(self, event: UIEvent) -> bool | None:
        """Passes :class:`UIEvent` s through the widget tree."""
        # UpdateEvents are past to the first invisible widget
        if isinstance(event, UIOnUpdateEvent):
            self.dispatch_event("on_update", event.dt)

        if self.visible:
            # pass event to children
            for child in reversed(self.children):
                if child.dispatch_event("on_event", event):
                    return EVENT_HANDLED

        return EVENT_UNHANDLED

    def _walk_parents(self) -> Iterable[UIWidget | UIManager]:
        parent = self.parent
        while isinstance(parent, UIWidget):
            yield parent
            parent = parent.parent

        if parent:
            yield parent

    def trigger_render(self):
        """This will delay a render right before the next frame is rendered, so that
        :meth:`UIWidget.do_render` is not called multiple times.
        """
        self._requires_render = True

    def trigger_full_render(self) -> None:
        """In case a widget uses transparent areas or was moved,
        it might be important to request a full rendering of parents
        """
        self.trigger_render()
        for parent in self._walk_parents():
            parent.trigger_render()

    def _prepare_layout(self):
        """Helper function to trigger :meth:`UILayout.prepare_layout` through the widget tree,
        should only be used internally!
        """
        for child in self.children:
            child._prepare_layout()

    def _do_layout(self):
        """Helper function to trigger :meth:`UIWidget.do_layout` through the widget tree,
        should only be used by UIManager!
        """
        for child in self.children:
            # rect changes in children will trigger_full_render
            child._do_layout()

    def _do_render(self, surface: Surface, force=False) -> bool:
        """Helper function to trigger :meth:`UIWidget.do_render` through the widget tree,
        should only be used by UIManager!

        Returns:
            if this widget or a child was rendered
        """
        rendered = False

        should_render = force or self._requires_render
        if should_render and self.visible:
            rendered = True
            self.do_render_base(surface)
            self.do_render(surface)
            if self.focused:
                self.do_render_focus(surface)
            self._requires_render = False

        # only render children if self is visible
        if self.visible:
            for child in self.children:
                rendered |= child._do_render(surface, should_render)

        return rendered

    def do_render_base(self, surface: Surface):
        """Renders background, border and "padding"""
        surface.limit(self.rect)

        # draw background
        if self._bg_color:
            if self._bg_color.a == 255 or self._strong_background:
                surface.clear(self._bg_color)
            else:
                arcade.draw_rect_filled(LBWH(0, 0, self.width, self.height), color=self._bg_color)
        # draw background texture
        if self._bg_tex:
            surface.draw_texture(x=0, y=0, width=self.width, height=self.height, tex=self._bg_tex)

        # draw border
        if self._border_width and self._border_color:
            arcade.draw_lbwh_rectangle_outline(
                0,
                0,
                self.width,
                self.height,
                color=self._border_color,
                border_width=self._border_width * 2,
            )

    def prepare_render(self, surface):
        """Helper for rendering, the drawing area will be adjusted to the own position and size.
        Draw calls have to be relative to 0,0.
        This will also prevent any overdraw outside of the widgets area

        Args:
            surface: Surface used for rendering
        """
        surface.limit(self.content_rect)

    def do_render(self, surface: Surface):
        """Render the widgets graphical representation, use :meth:`UIWidget.prepare_render`
        to limit the drawing area to the widgets rect and draw relative to 0,0.
        """
        pass

    def do_render_focus(self, surface: Surface):
        """Render the widgets focus representation overlay`"""
        self.prepare_render(surface)
        arcade.draw_rect_outline(
            rect=LBWH(0, 0, self.content_width, self.content_height),
            color=arcade.color.WHITE,
            border_width=4,
        )

    def dispatch_ui_event(self, event: UIEvent):
        """Dispatch a :class:`UIEvent` using pyglet event dispatch mechanism"""
        return self.dispatch_event("on_event", event)

    def move(self, dx=0, dy=0):
        """Move the widget by dx and dy.

        Args:
            dx: x axis difference
            dy: y axis difference
        """
        self.rect = self.rect.move(dx, dy)

    def scale(self, factor: AsFloat, anchor: Vec2 = AnchorPoint.CENTER):
        """Scales the size of the widget (x,y,width, height) by factor.

        Args:
            factor: scale factor
            anchor: anchor point
        """
        self.rect = self.rect.scale(new_scale=factor, anchor=anchor)

    def get_ui_manager(self) -> UIManager | None:
        """The UIManager this widget is attached to. During creation, this will be None."""
        from arcade.gui.ui_manager import UIManager

        w: UIWidget | None = self
        while w and w.parent:
            parent = w.parent
            if isinstance(parent, UIManager):
                return parent

            w = parent
        return None

    @property
    def left(self) -> float:
        """Left coordinate of the widget"""
        return self.rect.left

    @left.setter
    def left(self, value: float):
        self.rect = LBWH(value, self.bottom, self.width, self.height)

    @property
    def right(self) -> float:
        """Right coordinate of the widget"""
        return self.rect.right

    @right.setter
    def right(self, value: float):
        self.rect = LBWH(value - self.width, self.bottom, self.width, self.height)

    @property
    def bottom(self) -> float:
        """Bottom coordinate of the widget"""
        return self.rect.bottom

    @bottom.setter
    def bottom(self, value: float):
        self.rect = LBWH(self.left, value, self.width, self.height)

    @property
    def top(self) -> float:
        """Top coordinate of the widget"""
        return self.rect.top

    @top.setter
    def top(self, value: float):
        self.rect = LBWH(self.left, value - self.height, self.width, self.height)

    @property
    def position(self) -> Vec2:
        """Returns bottom left coordinates"""
        return self.rect.bottom_left

    @property
    def center(self) -> Vec2:
        """Returns center coordinates"""
        return self.rect.center

    @center.setter
    def center(self, value: tuple[int, int]):
        self.rect = self.rect.align_center(value)

    @property
    def center_x(self) -> float:
        """Center x coordinate"""
        return self.rect.x

    @center_x.setter
    def center_x(self, value: float):
        self.rect = self.rect.align_center_x(value)

    @property
    def center_y(self) -> float:
        """Center y coordinate"""
        return self.rect.y

    @center_y.setter
    def center_y(self, value: float):
        self.rect = self.rect.align_center_y(value)

    @property
    def padding(self):
        """Returns padding as tuple (top, right, bottom, left)"""
        return (
            self._padding_top,
            self._padding_right,
            self._padding_bottom,
            self._padding_left,
        )

    @padding.setter
    def padding(self, args: int | tuple[int, int] | tuple[int, int, int, int]):
        if isinstance(args, int):  # self.padding = 10 -> 10, 10, 10, 10
            args = (args, args, args, args)

        elif len(args) == 2:  # self.padding = 10, 20 -> 10, 20, 10, 20
            args = args + args

        pt, pr, pb, pl = args  # self.padding = 10, 20, 30, 40
        self._padding_top = pt
        self._padding_right = pr
        self._padding_bottom = pb
        self._padding_left = pl

    @property
    def children(self) -> list[UIWidget]:
        """Provides all child widgets."""
        return [child for child, data in self._children]

    def __iter__(self):
        return iter(self.children)

    def resize(self, *, width=None, height=None, anchor: Vec2 = AnchorPoint.CENTER):
        """Resizes the widget.

        Args:
            width: new width
            height: new height
            anchor: anchor point for resizing, default is center
        """
        self.rect = self.rect.resize(width=width, height=height, anchor=anchor)

    def with_border(self, *, width=2, color: Color | None = arcade.color.GRAY) -> Self:
        """Sets border properties

        Args:
            width: border width
            color: border color

        Returns:
            self
        """
        self._border_width = width
        self._border_color = color
        return self

    def with_padding(
        self,
        *,
        top: int | None = None,
        right: int | None = None,
        bottom: int | None = None,
        left: int | None = None,
        all: int | None = None,
    ) -> Self:
        """Changes the padding to the given values if set. Returns itself

        Returns:
            self
        """
        if all is not None:
            self.padding = all
        if top is not None:
            self._padding_top = top
        if right is not None:
            self._padding_right = right
        if bottom is not None:
            self._padding_bottom = bottom
        if left is not None:
            self._padding_left = left
        return self

    def with_background(
        self,
        *,
        color: Color | EllipsisType | None = ...,
        texture: Texture | NinePatchTexture | EllipsisType | None = ...,
    ) -> Self:
        """Set widgets background.

        A color or texture can be used for background,
        if a texture is given, start and end point can be added to use the texture as ninepatch.

        Args:
            color: A color used as background
            texture: A texture or ninepatch texture used as background

        Returns:
            self
        """
        if color is not ...:
            if color is not None:
                color = Color.from_iterable(color)

            self._bg_color = color

        if texture is not ...:
            self._bg_tex = texture

        return self

    @property
    def content_size(self) -> tuple[float, float]:
        """Returns the size of the content area,
        which is the size of the widget minus padding and border."""
        return self.content_width, self.content_height

    @property
    def content_width(self) -> float:
        """Returns the width of the content area,
        which is the width of the widget minus padding and border."""
        return self.rect.width - 2 * self._border_width - self._padding_left - self._padding_right

    @property
    def content_height(self) -> float:
        """Returns the height of the content area,
        which is the height of the widget minus padding and border."""
        return self.rect.height - 2 * self._border_width - self._padding_top - self._padding_bottom

    @property
    def content_rect(self) -> Rect:
        """Returns the content area as a rect.
        The content area is the area of the widget minus padding and border."""
        return LBWH(
            self.left + self._border_width + self._padding_left,
            self.bottom + self._border_width + self._padding_bottom,
            self.content_width,
            self.content_height,
        )

    @property
    def width(self) -> float:
        """Width of the widget."""
        return self.rect.width

    @width.setter
    def width(self, value: float):
        if value <= 0:
            raise ValueError("Width must be positive")
        self.rect = LBWH(self.left, self.bottom, value, self.height)

    @property
    def height(self) -> float:
        """Height of the widget."""
        return self.rect.height

    @height.setter
    def height(self, value: float):
        if value <= 0:
            raise ValueError("Height must be positive")
        self.rect = LBWH(self.left, self.bottom, self.width, value)

    @property
    def size(self) -> Vec2:
        """Size of the widget."""
        return Vec2(self.width, self.height)

    @size.setter
    def size(self, value: tuple[float, float] | Vec2):
        width, height = value
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self.rect = LBWH(self.left, self.bottom, width, height)

    def center_on_screen(self: W) -> W:
        """Places this widget in the center of the current window.

        This is a convenience method for simple centering of widgets without using
        a layout.

        In general, it is recommended to use layouts for more complex UIs.
        """
        center = arcade.get_window().center
        self.rect = self.rect.align_center(center)
        return self

    def __str__(self):
        return f"{self.__class__.__name__}()"

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.rect.lbwh}>"


class UIInteractiveWidget(UIWidget):
    """Base class for widgets which use mouse interaction (hover, pressed, clicked)

    It provides properties for hovered, pressed and disabled states.

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget
        height: height of widget
        size_hint: Tuple of floats (0.0-1.0), how much space of the
            parent should be requested
        size_hint_min: min width and height in pixel
        size_hint_max: max width and height in pixel
        interaction_buttons: defines, which mouse buttons should trigger
            the interaction (default: left mouse button)
    """

    focus_mode = FocusMode.ALL

    # States
    hovered = Property(False)
    """True if the mouse is over the widget"""
    pressed = Property(False)
    """True if the widget is pressed"""
    disabled = Property(False)
    """True if the widget is disabled"""

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        interaction_buttons=(arcade.MOUSE_BUTTON_LEFT,),
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )
        self.register_event_type("on_click")

        self.interaction_buttons = interaction_buttons

        bind(self, "pressed", UIInteractiveWidget.trigger_render)
        bind(self, "hovered", UIInteractiveWidget.trigger_render)
        bind(self, "disabled", UIInteractiveWidget.trigger_render)
        bind(self, "focused", UIInteractiveWidget._on_focus_change)

    def _on_focus_change(self):
        """If focus lost, release active state"""
        if self.pressed and not self.focused:
            self.pressed = False
            self._release_active()

    def on_event(self, event: UIEvent) -> bool | None:
        """Handles mouse events and triggers on_click event if the widget is clicked.

        This also sets the hovered and pressed state of the widget.
        """
        if super().on_event(event):
            return EVENT_HANDLED

        # mouse event handling
        if isinstance(event, UIMouseMovementEvent):
            self.hovered = self.rect.point_in_rect(event.pos)

        if (
            isinstance(event, UIMousePressEvent)
            and self.rect.point_in_rect(event.pos)
            and event.button in self.interaction_buttons
        ):
            self.pressed = True
            self._grap_active()  # make this the active widget
            return EVENT_HANDLED

        if (
            self.pressed
            and isinstance(event, UIMouseReleaseEvent)
            and event.button in self.interaction_buttons
        ):
            self.pressed = False
            if self.rect.point_in_rect(event.pos):
                if not self.disabled:
                    # Dispatch new on_click event, source is this widget itself
                    self._grap_active()  # make this the active widget
                    self.dispatch_event(
                        "on_click",
                        UIOnClickEvent(
                            source=self,
                            x=event.x,
                            y=event.y,
                            button=event.button,
                            modifiers=event.modifiers,
                        ),
                    )
                    return EVENT_HANDLED  # TODO should we return the result from on_click?

        # focus related events
        if self.focused:
            if isinstance(event, UIKeyPressEvent) and event.symbol == arcade.key.SPACE:
                self.pressed = True
                self._grap_active()  # make this the active widget
                return EVENT_HANDLED

            if isinstance(event, UIControllerButtonPressEvent) and event.button in ("a",):
                self.pressed = True
                self._grap_active()  # make this the active widget
                return EVENT_HANDLED

            if self.pressed:
                keyboard_interaction = (
                    isinstance(event, UIKeyReleaseEvent) and event.symbol == arcade.key.SPACE
                )
                controller_interaction = isinstance(
                    event, UIControllerButtonReleaseEvent
                ) and event.button in ("a",)

                if keyboard_interaction or controller_interaction:
                    self.pressed = False
                    if not self.disabled:
                        # Dispatch new on_click event, source is this widget itself
                        self._grap_active()
                        self.dispatch_event(
                            "on_click",
                            UIOnClickEvent(  # simulate mouse click
                                source=self,
                                x=int(self.center_x),
                                y=int(self.center_y),
                                button=self.interaction_buttons[0],
                                modifiers=0,
                            ),
                        )
                        return EVENT_HANDLED  # TODO should we return the result from on_click?

        return EVENT_UNHANDLED

    def on_click(self, event: UIOnClickEvent):
        """Triggered when the widget is clicked."""
        pass


class UIDummy(UIInteractiveWidget):
    """Solid color widget used for testing & examples.

    Starts with a random color.
    It should not be subclassed for real-world usage.

    When clicked, it does the following:

    * Outputs its `rect` attribute to the console
    * Changes its color to a random fully opaque color

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget
        height: height of widget
        size_hint: Tuple of floats (0.0-1.0), how much space of the
            parent should be requested
        size_hint_min: min width and height in pixel
        size_hint_max: max width and height in pixel
        **kwargs: passed to UIWidget
    """

    def __init__(
        self,
        *,
        x=0,
        y=0,
        width=100,
        height=100,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )
        self.with_background(color=Color.random(a=255))
        self.with_border(color=arcade.color.BATTLESHIP_GREY, width=0)

    def on_click(self, event: UIOnClickEvent):
        """Prints the rect and changes the color"""
        print("UIDummy.rect:", self.rect)
        self.with_background(color=Color.random(a=255))

    def on_update(self, dt):
        """Update the border of the widget if hovered"""
        self.with_border(
            width=2 if self.hovered else 0,
            color=arcade.color.WHITE if self.pressed else arcade.color.BATTLESHIP_GREY,
        )


class UISpriteWidget(UIWidget):
    """Create a UI element with a sprite that controls what is displayed.

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget
        height: height of widget
        sprite: Sprite to embed in gui
        size_hint: Tuple of floats (0.0-1.0), how much space of the
            parent should be requested
        size_hint_min: min width and height in pixel
        size_hint_max: max width and height in pixel
    """

    def __init__(
        self,
        *,
        x=0,
        y=0,
        width=100,
        height=100,
        sprite: Sprite | None = None,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )
        self._sprite = sprite

    def on_update(self, dt):
        """Pass update event to sprite"""
        if self._sprite:
            self._sprite.update()
            self._sprite.update_animation(dt)
            self.trigger_render()

    def do_render(self, surface: Surface):
        """Render the sprite"""
        self.prepare_render(surface)
        surface.clear(color=TRANSPARENT_BLACK)
        if self._sprite is not None:
            surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class UILayout(UIWidget):
    """Base class for widgets, which position themselves or their children.

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget
        height: height of widget
        children: Child widgets of this group
        size_hint: Tuple of floats (0.0-1.0), how much space of the
            parent should be requested
        size_hint_min: min width and height in pixel
        size_hint_max: max width and height in pixel
    """

    @staticmethod
    def min_size_of(child: UIWidget) -> tuple[float, float]:
        """Resolves the minimum size of a child. If it has a size_hint set for the axis,
        it will use size_hint_min if set, otherwise the actual size will be used.
        """
        sh_w, sh_h = child.size_hint or (None, None)
        shmn_w, shmn_h = child.size_hint_min or (None, None)

        min_w, min_h = child.size

        if sh_w is not None:
            min_w = shmn_w or 0

        if sh_h is not None:
            min_h = shmn_h or 0

        return min_w, min_h

    def _prepare_layout(self):
        """Triggered to prepare layout of this widget and its children.
        Common example is to update size_hints(min/max).
        """
        super()._prepare_layout()
        self.prepare_layout()

    def prepare_layout(self):
        """Triggered by the UIManager before layouting,
        :class:`UILayout` s should prepare themselves based on children.

        Prepare layout is triggered on children first.
        """
        pass

    def _do_layout(self):
        # rect change will trigger full render automatically
        self.do_layout()

        # Continue do_layout within subtree
        super()._do_layout()

    def do_layout(self):
        """do_layout is triggered by the UIManager before rendering.
         :class:`UILayout` should position their children.
         Afterward, do_layout of child widgets will be triggered.

        Use :meth:`UIWidget.trigger_render` to trigger a rendering before the next
        frame, this will happen automatically if the position or size of this widget changed.
        """


class UISpace(UIWidget):
    """Widget reserving space, can also have a background color.

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget
        height: height of widget
        color: Color for widget area, if None, it will be transparent
            (this will set the background color)
        size_hint: Tuple of floats (0.0-1.0), how much space of the
            parent should be requested
        size_hint_min: min width and height in pixel
        size_hint_max: max width and height in pixel
        **kwargs: passed to UIWidget
    """

    def __init__(
        self,
        *,
        x=0,
        y=0,
        width=1,
        height=1,
        color=None,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )
        self.with_background(color=color)

    @property
    def color(self):
        """Color of the widget, alias for background color"""
        return self._bg_color

    @color.setter
    def color(self, value):
        self.with_background(color=value)


__all__ = ["Surface", "UIDummy", "FocusMode", "UIInteractiveWidget", "UIWidget"]
