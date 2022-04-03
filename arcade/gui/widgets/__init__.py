from abc import abstractmethod, ABC
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
)

from pyglet.event import EventDispatcher, EVENT_HANDLED, EVENT_UNHANDLED

import arcade
from arcade import Sprite
from arcade.gui.events import (
    UIEvent,
    UIMouseMovementEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIOnClickEvent,
    UIOnUpdateEvent,
)
from arcade.gui.property import Property, bind, ListProperty
from arcade.gui.surface import Surface

if TYPE_CHECKING:
    from arcade.gui.ui_manager import UIManager


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
        width = width or self.width
        height = height or self.height
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
        return self.left, self.bottom

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


W = TypeVar("W", bound="UIWidget")


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

    children: List = ListProperty()  # type: ignore

    rect: Rect = Property(Rect(0, 0, 1, 1))  # type: ignore
    visible: bool = Property(True)  # type: ignore
    border_width: int = Property(0)  # type: ignore
    border_color: Optional[arcade.Color] = Property(arcade.color.BLACK)  # type: ignore
    bg_color: Optional[arcade.Color] = Property(None)  # type: ignore
    bg_texture: Optional[arcade.Texture] = Property(None)  # type: ignore
    padding_top: int = Property(0)  # type: ignore
    padding_right: int = Property(0)  # type: ignore
    padding_bottom: int = Property(0)  # type: ignore
    padding_left: int = Property(0)  # type: ignore

    # TODO add padding, bg, border to constructor
    def __init__(
            self,
            x: float = 0,
            y: float = 0,
            width: float = 100,
            height: float = 100,
            children: Iterable["UIWidget"] = tuple(),
            # Properties which might be used by layouts
            size_hint=None,  # in percentage
            size_hint_min=None,  # in pixel
            size_hint_max=None,  # in pixel
            style=None,
            **kwargs,
    ):
        self.style = style or {}

        self._rendered = False
        self.rect = Rect(x, y, width, height)
        self.parent: Optional[UIWidgetParent] = None

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
        bind(self, "children", self.trigger_render)
        bind(self, "border_width", self.trigger_render)
        bind(self, "border_color", self.trigger_render)
        bind(self, "bg_color", self.trigger_render)
        bind(self, "bg_texture", self.trigger_render)
        bind(self, "padding_top", self.trigger_render)
        bind(self, "padding_right", self.trigger_render)
        bind(self, "padding_bottom", self.trigger_render)
        bind(self, "padding_left", self.trigger_render)

    def trigger_render(self):
        """
        This will delay a render right before the next frame is rendered, so that :meth:`UIWidget.do_render`
        is not called multiple times.
        """
        self._rendered = False

    def add(self, child: W, *, index=None) -> W:
        """
        Add a widget to this :class:`UIWidget` as a child.
        Added widgets will receive ui events and be rendered.

        By default, the latest added widget will receive ui events first and will be rendered on top of others.

        :param child: widget to add
        :param index: position a widget is added, None has the highest priority
        :return: given child
        """
        child.parent = self
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(max(len(self.children), index), child)
        # TODO check: done by children listener
        # self.trigger_full_render()
        return child

    def remove(self, child: "UIWidget"):
        child.parent = None
        self.children.remove(child)
        # TODO check: done by children listener
        # self.trigger_full_render()

    def clear(self):
        for child in self.children:
            child.parent = None

        self.children.clear()
        # TODO check: done by children listener
        # self.trigger_full_render()

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

    def trigger_full_render(self):
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

    def _do_render(self, surface: Surface, force=False):
        """Helper function to trigger :meth:`UIWidget.do_render` through the widget tree,
        should only be used by UIManager!
        """
        should_render = force or not self._rendered
        if should_render and self.visible:
            self.do_render_base(surface)
            self.do_render(surface)
            self._rendered = True

        # only render children if self is visible
        if self.visible:
            for child in self.children:
                child._do_render(surface, should_render)

    def do_render_base(self, surface: Surface):
        """
        Renders background, border and "padding"
        """
        surface.limit(*self.rect)

        # draw background
        if self.bg_color:
            surface.clear(self.bg_color)

        if self.bg_texture:
            surface.draw_texture(0, 0, self.width, self.height, tex=self.bg_texture)

        # draw border
        if self.border_width and self.border_color:
            arcade.draw_xywh_rectangle_outline(
                0,
                0,
                self.width,
                self.height,
                color=self.border_color,
                border_width=self.border_width * 2,
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
            self.padding_top,
            self.padding_right,
            self.padding_bottom,
            self.padding_left,
        )

    @padding.setter
    def padding(self, args: Union[int, Tuple[int, int], Tuple[int, int, int, int]]):
        if isinstance(args, int):  # self.padding = 10 -> 10, 10, 10, 10
            args = (args, args, args, args)

        elif len(args) == 2:  # self.padding = 10, 20 -> 10, 20, 10, 20
            args = args + args  # type: ignore

        pt, pr, pb, pl = args  # type: ignore # self.padding = 10, 20, 30, 40
        self.padding_top = pt
        self.padding_right = pr
        self.padding_bottom = pb
        self.padding_left = pl

    def with_border(self, width=2, color=(0, 0, 0)) -> "UIWidget":
        """
        Sets border properties
        :param width: border width
        :param color: border color
        :return: self
        """
        self.border_width = width
        self.border_color = color
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
            self.padding_top = top
        if right is not ...:
            self.padding_right = right
        if bottom is not ...:
            self.padding_bottom = bottom
        if left is not ...:
            self.padding_left = left
        return self

    def with_background(self, color=..., texture=...) -> "UIWidget":
        """
        Convenience function to set background color or texture.
        :return: self
        """
        if color is not ...:
            self.bg_color = color
        if texture is not ...:
            self.bg_texture = texture
        return self

    @property
    def content_size(self):
        return self.content_width, self.content_height

    @property
    def content_width(self):
        return (
                self.rect.width
                - 2 * self.border_width
                - self.padding_left
                - self.padding_right
        )

    @property
    def content_height(self):
        return (
                self.rect.height
                - 2 * self.border_width
                - self.padding_top
                - self.padding_bottom
        )

    @property
    def content_rect(self):
        return Rect(
            self.left + self.border_width + self.padding_left,
            self.bottom + self.border_width + self.padding_bottom,
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


class UIWidgetParent(ABC):
    rect: Rect

    def trigger_render(self):
        """Widget might request parent to rerender due to transparent part of the widget"""
        pass

    @abstractmethod
    def remove(self, child: UIWidget):
        pass


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
    _hovered = False
    _pressed = False

    def __init__(
            self,
            x=0,
            y=0,
            width=100,
            height=100,
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            style=None,
            **kwargs,
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style,
        )
        self.register_event_type("on_click")

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        if self._pressed != value:
            self._pressed = value
            self.trigger_render()

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        if value != self._hovered:
            self._hovered = value
            self.trigger_render()

    def on_event(self, event: UIEvent) -> Optional[bool]:
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
                # Dispatch new on_click event, source is this widget itself
                self.dispatch_event("on_event", UIOnClickEvent(self, event.x, event.y))  # type: ignore
                return EVENT_HANDLED

        if isinstance(event, UIOnClickEvent) and self.rect.collide_with_point(
                event.x, event.y
        ):
            return self.dispatch_event("on_click", event)

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED

    def on_click(self, event: UIOnClickEvent):
        pass


class UIDummy(UIInteractiveWidget):
    """
    Solid color widget, used for testing.

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
            color=arcade.color.BLACK,
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            style=None,
            **kwargs,
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
        )
        self.color = color
        self.frame = randint(0, 255)

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        self.frame += 1
        frame = self.frame % 256
        surface.clear((self.color[0], self.color[1], self.color[2], frame))

        if self.hovered:
            arcade.draw_xywh_rectangle_outline(
                0,
                0,
                self.width,
                self.height,
                color=arcade.color.BATTLESHIP_GREY,
                border_width=3,
            )


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
            sprite: Sprite = None,
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            style=None,
            **kwargs,
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
        )
        self._sprite = sprite

    def on_update(self, dt):
        self._sprite.update()
        self._sprite.update_animation(dt)
        self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.clear(color=(0, 0, 0, 0))
        surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class UILayout(UIWidget, UIWidgetParent):
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

    def __init__(
            self,
            x=0,
            y=0,
            width=100,
            height=100,
            children: Iterable[UIWidget] = tuple(),
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            style=None,
            **kwargs,
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            children=children,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style,
            **kwargs,
        )

    def add(self, child: "UIWidget", **kwargs) -> "UIWidget":
        super().add(child)
        self.do_layout()
        return child

    def remove(self, child: "UIWidget"):
        super().remove(child)
        self.do_layout()

    def clear(self):
        super().clear()
        self.do_layout()

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


class UIWrapper(UILayout, UIWidgetParent):
    """
    # TODO Should this stay?
    DEPRECATED - UIWrapper will be removed in an upcoming release, please use UILayout instead.

    Wraps a :class:`arcade.gui.UIWidget`.

    :param child: Single child of this wrapper
    :param padding: space around (top, right, bottom, left)
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(
            self,
            *,
            child: UIWidget,
    ):
        """
        :param child: Child Widget which will be wrapped
        :param padding: Space between top, right, bottom, left
        """
        super().__init__(
            *child.rect,
            children=[child],
        )

    @property
    def child(self) -> UIWidget:
        return self.children[0]

    @child.setter
    def child(self, value: UIWidget):
        self.children[0] = value


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
            color=(0, 0, 0, 0),
            size_hint=None,
            size_hint_min=None,
            size_hint_max=None,
            style=None,
            **kwargs,
    ):
        super().__init__(
            x,
            y,
            width,
            height,
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
