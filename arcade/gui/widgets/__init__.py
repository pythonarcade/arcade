from __future__ import annotations

from abc import ABC
from random import randint
from typing import (
    NamedTuple,
    Iterable,
    Optional,
    Union,
    TYPE_CHECKING,
    TypeVar,
    Tuple,
    List,
    Dict,
)
from typing_extensions import Self

from pyglet.event import EventDispatcher, EVENT_HANDLED, EVENT_UNHANDLED

import arcade
from arcade import Sprite, get_window, Texture
from arcade.color import TRANSPARENT_BLACK
from arcade.gui.events import (
    UIEvent,
    UIMouseMovementEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIOnClickEvent,
    UIOnUpdateEvent,
)
from arcade.gui.nine_patch import NinePatchTexture
from arcade.gui.property import Property, bind, ListProperty
from arcade.gui.surface import Surface
from arcade.types import RGBA255, Color

if TYPE_CHECKING:
    from arcade.gui.ui_manager import UIManager

__all__ = ["Surface", "UIDummy"]


class Rect(NamedTuple):
    """
    Representing a rectangle for GUI module.
    Rect is idempotent.

    Bottom left corner is used as fix point (x, y)
    """

    x: float
    y: float
    width: float
    height: float

    def move(self, dx: float = 0, dy: float = 0):
        """Returns new Rect which is moved by dx and dy"""
        return Rect(self.x + dx, self.y + dy, self.width, self.height)

    def collide_with_point(self, x, y):
        left, bottom, width, height = self
        return left < x < left + width and bottom < y < bottom + height

    def scale(self, scale: float) -> "Rect":
        """Returns a new rect with scale applied"""
        return Rect(
            int(self.x * scale),
            int(self.y * scale),
            int(self.width * scale),
            int(self.height * scale),
        )

    def resize(self, width=None, height=None):
        """
        Returns a rect with changed width and height.
        Fix x and y coordinate.
        """
        width = width if width is not None else self.width
        height = height if height is not None else self.height
        return Rect(self.x, self.y, width, height)

    @property
    def size(self):
        return self.width, self.height

    @property
    def left(self):
        return self.x

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y

    @property
    def top(self):
        return self.y + self.height

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

    @property
    def center(self):
        return self.center_x, self.center_y

    @property
    def position(self):
        """Bottom left coordinates"""
        return self.left, self.bottom

    def align_top(self, value: float) -> "Rect":
        """Returns new Rect, which is aligned to the top"""
        diff_y = value - self.top
        return self.move(dy=diff_y)

    def align_bottom(self, value: float) -> "Rect":
        """Returns new Rect, which is aligned to the bottom"""
        diff_y = value - self.bottom
        return self.move(dy=diff_y)

    def align_left(self, value: float) -> "Rect":
        """Returns new Rect, which is aligned to the left"""
        diff_x = value - self.left
        return self.move(dx=diff_x)

    def align_right(self, value: float) -> "Rect":
        """Returns new Rect, which is aligned to the right"""
        diff_x = value - self.right
        return self.move(dx=diff_x)

    def align_center(self, center_x, center_y):
        """Returns new Rect, which is aligned to the center x and y"""
        diff_x = center_x - self.center_x
        diff_y = center_y - self.center_y
        return self.move(dx=diff_x, dy=diff_y)

    def align_center_x(self, value: float) -> "Rect":
        """Returns new Rect, which is aligned to the center_x"""
        diff_x = value - self.center_x
        return self.move(dx=diff_x)

    def align_center_y(self, value: float) -> "Rect":
        """Returns new Rect, which is aligned to the center_y"""
        diff_y = value - self.center_y
        return self.move(dy=diff_y)

    def min_size(self, width=None, height=None):
        """
        Sets the size to at least the given min values.
        """
        return Rect(
            self.x,
            self.y,
            max(width or 0.0, self.width),
            max(height or 0.0, self.height),
        )

    def max_size(self, width: Optional[float] = None, height: Optional[float] = None):
        """
        Limits the size to the given max values.
        """
        w, h = self.size
        if width:
            w = min(width, self.width)
        if height:
            h = min(height, self.height)

        return Rect(self.x, self.y, w, h)

    def union(self, rect: "Rect"):
        """
        Returns a new Rect that is the union of this rect and another.
        The union is the smallest rectangle that contains theses two rectangles.
        """
        x = min(self.x, rect.x)
        y = min(self.y, rect.y)
        right = max(self.right, rect.right)
        top = max(self.top, rect.top)
        return Rect(
            x=x,
            y=y,
            width=right - x,
            height=top - y
        )


W = TypeVar("W", bound="UIWidget")


class _ChildEntry(NamedTuple):
    child: "UIWidget"
    data: Dict


class UIWidget(EventDispatcher, ABC):
    """
    The :class:`UIWidget` class is the base class required for creating widgets.

    We also have some default values and behaviors that you should be aware of:

    * A :class:`UIWidget` is not a :class:`~arcade.gui.UILayout`: it will not
      change the position or the size of its children. If you want control over
      positioning or sizing, use a :class:`~arcade.gui.UILayout`.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    rect: Rect = Property(Rect(0, 0, 1, 1))  # type: ignore
    visible: bool = Property(True)  # type: ignore

    _children: List[_ChildEntry] = ListProperty()  # type: ignore
    _border_width: int = Property(0)  # type: ignore
    _border_color: Optional[RGBA255] = Property(arcade.color.BLACK)  # type: ignore
    _bg_color: Optional[RGBA255] = Property(None)  # type: ignore
    _bg_tex: Union[None, Texture, NinePatchTexture] = Property(None)  # type: ignore
    _padding_top: int = Property(0)  # type: ignore
    _padding_right: int = Property(0)  # type: ignore
    _padding_bottom: int = Property(0)  # type: ignore
    _padding_left: int = Property(0)  # type: ignore

    # TODO add padding, bg, border to constructor
    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        children: Iterable["UIWidget"] = tuple(),
        # Properties which might be used by layouts
        size_hint=None,  # in percentage
        size_hint_min=None,  # in pixel
        size_hint_max=None,  # in pixel
        **kwargs,
    ):
        self._rendered = False
        self.rect = Rect(x, y, width, height)
        self.parent: Optional[Union[UIManager, UIWidget]] = None

        # Size hints are properties that can be used by layouts
        self.size_hint = size_hint
        self.size_hint_min = size_hint_min
        self.size_hint_max = size_hint_max

        self.register_event_type("on_event")
        self.register_event_type("on_update")

        for child in children:
            self.add(child)

        bind(self, "rect", self.trigger_full_render)
        bind(
            self, "visible", self.trigger_full_render
        )  # TODO maybe trigger_parent_render would be enough
        bind(self, "_children", self.trigger_render)
        bind(self, "_border_width", self.trigger_render)
        bind(self, "_border_color", self.trigger_render)
        bind(self, "_bg_color", self.trigger_render)
        bind(self, "_bg_tex", self.trigger_render)
        bind(self, "_padding_top", self.trigger_render)
        bind(self, "_padding_right", self.trigger_render)
        bind(self, "_padding_bottom", self.trigger_render)
        bind(self, "_padding_left", self.trigger_render)

    def trigger_render(self):
        """
        This will delay a render right before the next frame is rendered, so that :meth:`UIWidget.do_render`
        is not called multiple times.
        """
        self._rendered = False

    def add(self, child: W, **kwargs) -> W:
        """
        Add a widget to this :class:`UIWidget` as a child.
        Added widgets will receive ui events and be rendered.

        By default, the latest added widget will receive ui events first and will be rendered on top of others.

        :param child: widget to add
        :param index: position a widget is added, None has the highest priority
        :return: given child
        """
        child.parent = self
        index = kwargs.pop("index") if "index" in kwargs else None
        if index is None:
            self._children.append(_ChildEntry(child, kwargs))
        else:
            self._children.insert(
                max(len(self.children), index), _ChildEntry(child, kwargs)
            )

        return child

    def remove(self, child: "UIWidget"):
        """
        Removes a child from the UIManager which was directly added to it.
        This will not remove widgets which are added to a child of UIManager.
        """
        child.parent = None
        for c in self._children:
            if c.child == child:
                self._children.remove(c)

    def clear(self):
        for child in self.children:
            child.parent = None

        self._children.clear()

    def __contains__(self, item):
        return item in self.children

    def on_update(self, dt):
        """Custom logic which will be triggered."""
        pass

    def on_event(self, event: UIEvent) -> Optional[bool]:
        """Passes :class:`UIEvent` s through the widget tree."""
        # UpdateEvents are past to the first invisible widget
        if isinstance(event, UIOnUpdateEvent):
            self.dispatch_event("on_update", event.dt)

        if self.visible:
            # pass event to children
            for child in self.children:
                if child.dispatch_event("on_event", event):
                    return EVENT_HANDLED

        return EVENT_UNHANDLED

    def _walk_parents(self) -> Iterable[Union["UIWidget", "UIManager"]]:
        parent = self.parent
        while isinstance(parent, UIWidget):
            yield parent
            parent = parent.parent

        if parent:
            yield parent  # type: ignore

    def trigger_full_render(self) -> None:
        """In case a widget uses transparent areas or was moved,
        it might be important to request a full rendering of parents"""
        self.trigger_render()
        for parent in self._walk_parents():
            parent.trigger_render()

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

        :return: if this widget or a child was rendered
        """
        rendered = False

        should_render = force or not self._rendered
        if should_render and self.visible:
            rendered = True
            self.do_render_base(surface)
            self.do_render(surface)
            self._rendered = True

        # only render children if self is visible
        if self.visible:
            for child in self.children:
                rendered |= child._do_render(surface, should_render)

        return rendered

    def do_render_base(self, surface: Surface):
        """
        Renders background, border and "padding"
        """
        surface.limit(*self.rect)

        # draw background
        if self._bg_color:
            surface.clear(self._bg_color)
        # draw background texture
        if self._bg_tex:
            surface.draw_texture(
                x=0,
                y=0,
                width=self.width,
                height=self.height,
                tex=self._bg_tex
            )

        # draw border
        if self._border_width and self._border_color:
            arcade.draw_xywh_rectangle_outline(
                0,
                0,
                self.width,
                self.height,
                color=self._border_color,
                border_width=self._border_width * 2,
            )

    def prepare_render(self, surface):
        """
        Helper for rendering, the drawing area will be adjusted to the own position and size.
        Draw calls have to be relative to 0,0.
        This will also prevent any overdraw outside of the widgets area

        :param surface: Surface used for rendering
        """
        surface.limit(*self.content_rect)

    def do_render(self, surface: Surface):
        """Render the widgets graphical representation, use :meth:`UIWidget.prepare_render` to limit the drawing area
        to the widgets rect and draw relative to 0,0."""
        pass

    def dispatch_ui_event(self, event: UIEvent):
        """Dispatch a :class:`UIEvent` using pyglet event dispatch mechanism"""
        return self.dispatch_event("on_event", event)

    def move(self, dx=0, dy=0):
        """
        Move the widget by dx and dy.

        :param dx: x axis difference
        :param dy: y axis difference
        """
        self.rect = self.rect.move(dx, dy)

    def scale(self, factor):
        """
        Scales the size of the widget (x,y,width, height) by factor.
        :param factor: scale factor
        """
        self.rect = self.rect.scale(factor)

    @property
    def x(self):
        return self.rect.x

    @property
    def left(self):
        return self.rect.x

    @property
    def right(self):
        rect = self.rect
        return rect.x + rect.width

    @property
    def y(self):
        return self.rect.y

    @property
    def bottom(self):
        return self.rect.y

    @property
    def top(self):
        rect = self.rect
        return rect.y + rect.height

    @property
    def position(self):
        """Returns bottom left coordinates"""
        return self.left, self.bottom

    @property
    def center(self):
        return self.rect.center

    @center.setter
    def center(self, value: Tuple[int, int]):
        cx, cy = value
        self.rect = self.rect.align_center(cx, cy)

    @property
    def center_x(self):
        return self.rect.center_x

    @property
    def center_y(self):
        return self.rect.center_y

    @property
    def padding(self):
        return (
            self._padding_top,
            self._padding_right,
            self._padding_bottom,
            self._padding_left,
        )

    @padding.setter
    def padding(self, args: Union[int, Tuple[int, int], Tuple[int, int, int, int]]):
        if isinstance(args, int):  # self.padding = 10 -> 10, 10, 10, 10
            args = (args, args, args, args)

        elif len(args) == 2:  # self.padding = 10, 20 -> 10, 20, 10, 20
            args = args + args  # type: ignore

        pt, pr, pb, pl = args  # type: ignore # self.padding = 10, 20, 30, 40
        self._padding_top = pt
        self._padding_right = pr
        self._padding_bottom = pb
        self._padding_left = pl

    @property
    def children(self) -> List["UIWidget"]:
        return [child for child, data in self._children]

    def __iter__(self):
        return iter(self.children)

    def resize(self, *, width=None, height=None):
        self.rect = self.rect.resize(width=width, height=height)

    def with_border(self, width=2, color=(0, 0, 0)) -> Self:
        """
        Sets border properties
        :param width: border width
        :param color: border color
        :return: self
        """
        self._border_width = width
        self._border_color = color
        return self

    def with_padding(
        self, top=..., right=..., bottom=..., left=..., all=...
    ) -> "UIWidget":
        """
        Changes the padding to the given values if set. Returns itself
        :return: self
        """
        if all is not ...:
            self.padding = all
        if top is not ...:
            self._padding_top = top
        if right is not ...:
            self._padding_right = right
        if bottom is not ...:
            self._padding_bottom = bottom
        if left is not ...:
            self._padding_left = left
        return self

    def with_background(
        self,
        *,
        color=...,
        texture: Union[None, Texture, NinePatchTexture] = ...,  # type: ignore
    ) -> "UIWidget":

        """
        Set widgets background.

        A color or texture can be used for background,
        if a texture is given, start and end point can be added to use the texture as ninepatch.

        :param RGBA255 color: A color used as background
        :param arcade.Texture texture: A texture or ninepatch texture used as background
        :return: self
        """
        if color is not ...:
            self._bg_color = color

        if texture is not ...:
            self._bg_tex = texture

        return self

    @property
    def content_size(self):
        return self.content_width, self.content_height

    @property
    def content_width(self):
        return (
            self.rect.width
            - 2 * self._border_width
            - self._padding_left
            - self._padding_right
        )

    @property
    def content_height(self):
        return (
            self.rect.height
            - 2 * self._border_width
            - self._padding_top
            - self._padding_bottom
        )

    @property
    def content_rect(self):
        return Rect(
            self.left + self._border_width + self._padding_left,
            self.bottom + self._border_width + self._padding_bottom,
            self.content_width,
            self.content_height,
        )

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @property
    def size(self):
        return self.width, self.height

    def center_on_screen(self: W) -> W:
        """
        Places this widget in the center of the current window.
        """
        center_x = arcade.get_window().width // 2
        center_y = arcade.get_window().height // 2

        self.rect = self.rect.align_center(center_x, center_y)
        return self


class UIInteractiveWidget(UIWidget):
    """
    Base class for widgets which use mouse interaction (hover, pressed, clicked)

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel:param x: center x of widget
    :param style: not used
    """

    # States
    hovered = Property(False)
    pressed = Property(False)
    disabled = Property(False)

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float,
        height: float,
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
        self.register_event_type("on_click")

        bind(self, "pressed", self.trigger_render)
        bind(self, "hovered", self.trigger_render)
        bind(self, "disabled", self.trigger_render)

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if super().on_event(event):
            return EVENT_HANDLED

        if isinstance(event, UIMouseMovementEvent):
            self.hovered = self.rect.collide_with_point(event.x, event.y)

        if isinstance(event, UIMousePressEvent) and self.rect.collide_with_point(
            event.x, event.y
        ):
            self.pressed = True
            return EVENT_HANDLED

        if self.pressed and isinstance(event, UIMouseReleaseEvent):
            self.pressed = False
            if self.rect.collide_with_point(event.x, event.y):
                if not self.disabled:
                    # Dispatch new on_click event, source is this widget itself
                    self.dispatch_event(
                        "on_click", UIOnClickEvent(self, event.x, event.y)
                    )
                    # TODO unsure if it makes more sense to mark the event handled if the click event is handled.
                    return EVENT_HANDLED

        return EVENT_UNHANDLED

    def on_click(self, event: UIOnClickEvent):
        pass


class UIDummy(UIInteractiveWidget):
    """
    Solid color widget used for testing & examples

    It should not be subclassed for real-world usage.

    When clicked, it does the following:

    * Outputs its `rect` attribute to the console
    * Changes its color to a random fully opaque color

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param color: fill color for the widget
    :param width: width of widget
    :param height: height of widget
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(
        self,
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
        )
        self.color: RGBA255 = (randint(0, 255), randint(0, 255), randint(0, 255), 255)
        self.border_color = arcade.color.BATTLESHIP_GREY

        self.bg_color = (
            get_window().background_color
        )  # ensures a clean surface to draw on

    def on_click(self, event: UIOnClickEvent):
        print("UIDummy.rect:", self.rect)
        self.color = Color.random(a=255)

    def on_update(self, dt):
        self.border_width = 2 if self.hovered else 0
        self.border_color = (
            arcade.color.WHITE if self.pressed else arcade.color.BATTLESHIP_GREY
        )

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.clear(self.color)

        # if self.hovered:
        #     arcade.draw_xywh_rectangle_outline(
        #         0,
        #         0,
        #         self.width,
        #         self.height,
        #         color=arcade.color.BATTLESHIP_GREY,
        #         border_width=3,
        #     )


class UISpriteWidget(UIWidget):
    """Create a UI element with a sprite that controls what is displayed.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param sprite: Sprite to embed in gui
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(
        self,
        *,
        x=0,
        y=0,
        width=100,
        height=100,
        sprite: Optional[Sprite] = None,
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
            **kwargs
        )
        self._sprite = sprite

    def on_update(self, dt):
        if self._sprite:
            self._sprite.update()
            self._sprite.update_animation(dt)
            self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.clear(color=TRANSPARENT_BLACK)
        surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class UILayout(UIWidget):
    """
    Base class for widgets, which position themselves or their children.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param children: Child widgets of this group
    :param size_hint: A hint for :class:`UILayout`, if this :class:`UIWidget` would like to grow
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def do_layout(self):
        """
        Triggered by the UIManager before rendering, :class:`UILayout` s should place themselves and/or children.
        Do layout will be triggered on children afterwards.

        Use :meth:`UIWidget.trigger_render` to trigger a rendering before the next frame, this will happen automatically
        if the position or size of this widget changed.
        """

    def _do_layout(self):
        # rect change will trigger full render automatically
        self.do_layout()

        # Continue do_layout within subtree
        super()._do_layout()


class UISpace(UIWidget):
    """
    Widget reserving space, can also have a background color.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param color: Color for widget area
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(
        self,
        x=0,
        y=0,
        width=100,
        height=100,
        color=TRANSPARENT_BLACK,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style=None,
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
        )
        self._color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.clear(self._color)
