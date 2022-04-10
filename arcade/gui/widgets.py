from abc import abstractmethod, ABC
from random import randint
from typing import NamedTuple, Iterable, Optional, List, Union, TYPE_CHECKING, TypeVar

import pyglet
from pyglet.event import EventDispatcher, EVENT_HANDLED, EVENT_UNHANDLED
from pyglet.text.caret import Caret
from pyglet.text.document import AbstractDocument

import arcade
from arcade import Texture, Sprite
from arcade.gui.events import UIEvent, UIMouseMovementEvent, UIMousePressEvent, UIMouseReleaseEvent, \
    UITextEvent, \
    UIMouseDragEvent, \
    UIMouseScrollEvent, UITextMotionEvent, UITextMotionSelectEvent, UIMouseEvent, UIOnClickEvent, UIOnUpdateEvent
from arcade.gui.surface import Surface

if TYPE_CHECKING:
    from arcade.gui.ui_manager import UIManager


class _Rect(NamedTuple):
    x: float
    y: float
    width: float
    height: float

    def move(self, dx: float = 0, dy: float = 0):
        """Returns new Rect which is moved by dx and dy"""
        return _Rect(self.x + dx, self.y + dy, self.width, self.height)

    def collide_with_point(self, x, y):
        left, bottom, width, height = self
        return left < x < left + width and bottom < y < bottom + height

    def scale(self, scale: float) -> "_Rect":
        """Returns a new rect with scale applied"""
        return _Rect(
            int(self.x * scale),
            int(self.y * scale),
            int(self.width * scale),
            int(self.height * scale),
        )

    def resize(self, width=None, height=None):
        width = width or self.width
        height = height or self.height
        return _Rect(self.x, self.y, width, height)

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

    def align_top(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the top"""
        diff_y = value - self.top
        return self.move(dy=diff_y)

    def align_bottom(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the bottom"""
        diff_y = value - self.bottom
        return self.move(dy=diff_y)

    def align_left(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the left"""
        diff_x = value - self.left
        return self.move(dx=diff_x)

    def align_right(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the right"""
        diff_x = value - self.right
        return self.move(dx=diff_x)

    def align_center(self, center_x, center_y):
        """Returns new Rect, which is aligned to the center x and y"""
        diff_x = center_x - self.center_x
        diff_y = center_y - self.center_y
        return self.move(dx=diff_x, dy=diff_y)

    def align_center_x(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the center_x"""
        diff_x = value - self.center_x
        return self.move(dx=diff_x)

    def align_center_y(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the center_y"""
        diff_y = value - self.center_y
        return self.move(dy=diff_y)


W = TypeVar('W', bound="UIWidget")


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

    def __init__(self,
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
                 **kwargs
                 ):
        self.style = style or {}
        self.children: List[UIWidget] = []

        self._rendered = False
        self._rect = _Rect(x, y, width, height)
        self.parent: Optional[UIWidgetParent] = None

        # Size hints are properties that can be used by layouts
        self.size_hint = size_hint
        self.size_hint_min = size_hint_min
        self.size_hint_max = size_hint_max

        self.register_event_type("on_event")
        self.register_event_type("on_update")

        for child in children:
            self.add(child)

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
        self.trigger_full_render()
        return child

    def remove(self, child: "UIWidget"):
        """Removes the given child from children list."""
        child.parent = None
        self.children.remove(child)
        self.trigger_full_render()

    def clear(self):
        """Clears the child list."""
        for child in self.children:
            child.parent = None

        self.children.clear()
        self.trigger_full_render()

    def __contains__(self, item):
        return item in self.children

    def on_update(self, dt):
        """Custom logic which will be triggered."""
        pass

    def on_event(self, event: UIEvent) -> Optional[bool]:
        """Passes :class:`UIEvent` s through the widget tree."""
        if isinstance(event, UIOnUpdateEvent):
            self.dispatch_event("on_update", event.dt)

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
            rect = child.rect
            child._do_layout()

            if rect != child.rect:
                # Rerender in case the child rect has changed
                # TODO use Arcade Property instead
                self.trigger_full_render()

    def _do_render(self, surface: Surface, force=False):
        """Helper function to trigger :meth:`UIWidget.do_render` through the widget tree,
        should only be used by UIManager!
        """
        should_render = force or not self._rendered
        if should_render:
            self.do_render(surface)
            self._rendered = True

        for child in self.children:
            child._do_render(surface, should_render)

    def prepare_render(self, surface):
        """
        Helper for rendering, the drawing area will be adjusted to the own position and size.
        Draw calls have to be relative to 0,0.
        This will also prevent any overdraw outside of the widgets area

        :param surface: Surface used for rendering
        """
        surface.limit(*self.rect)

    def do_render(self, surface: Surface):
        """Render the widgets graphical representation, use :meth:`UIWidget.prepare_render` to limit the drawing area
        to the widgets rect and draw relative to 0,0."""
        pass

    def dispatch_ui_event(self, event: UIEvent):
        """Dispatch a :class:`UIEvent` using pyglet event dispatch mechanism"""
        return self.dispatch_event("on_event", event)

    def with_border(self, width=2, color=(0, 0, 0)) -> "UIBorder":
        """
        Wraps this widget with a border

        :param width: Border width
        :param color: Border color

        :return: Wrapped Border with self as child
        """
        return UIBorder(self, border_width=width, border_color=color)

    def with_space_around(self,
                          top: float = 0,
                          right: float = 0,
                          bottom: float = 0,
                          left: float = 0,
                          bg_color: Optional[arcade.Color] = None) -> "UIPadding":
        """
        Wraps this widget and applies padding

        :param top: Top padding
        :param right: Right padding
        :param bottom: Bottom padding
        :param left: Left padding
        :param bg_color: Background color

        :return: Wrapped Padding with self as child
        """
        return UIPadding(self, padding=(top, right, bottom, left), bg_color=bg_color)

    def with_background(self, texture: Texture, top=0, right=0, bottom=0, left=0) -> "UITexturePane":
        """
        Wraps the widget with a background

        :param texture: Background texture
        :param top: Top padding
        :param right: Right padding
        :param bottom: Bottom padding
        :param left: Left padding

        :return: Wrapped Texture with self as child
        """
        return UITexturePane(self, tex=texture, padding=(top, right, bottom, left))

    @property
    def rect(self) -> _Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.trigger_full_render()

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
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @property
    def size(self):
        return self.width, self.height

    @property
    def center_x(self):
        return self.rect.center_x

    @property
    def center_y(self):
        return self.rect.center_y

    @property
    def center(self):
        return self.center_x, self.center_y

    def center_on_screen(self: W) -> W:
        """
        Places this widget in the center of the current window.
        """
        center_x = arcade.get_window().width // 2
        center_y = arcade.get_window().height // 2

        self.rect = self.rect.align_center(center_x, center_y)
        return self


class UIWidgetParent(ABC):
    @property
    @abstractmethod
    def rect(self) -> _Rect:
        pass

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

    def __init__(self, x=0, y=0, width=100, height=100,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max,
                         style=style
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

        if isinstance(event, UIOnClickEvent) and self.rect.collide_with_point(event.x, event.y):
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

    def __init__(self, x=0, y=0, width=100, height=100, color=arcade.color.BLACK,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)
        self.color = color
        self.frame = randint(0, 255)

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        self.frame += 1
        frame = self.frame % 256
        surface.clear((self.color[0], self.color[1], self.color[2], frame))

        if self.hovered:
            arcade.draw_xywh_rectangle_outline(0, 0,
                                               self.width, self.height,
                                               color=arcade.color.BATTLESHIP_GREY,
                                               border_width=3)


class UISpriteWidget(UIWidget):
    """ Create a UI element with a sprite that controls what is displayed.

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

    def __init__(self, *, x=0, y=0, width=100, height=100,
                 sprite: Sprite = None,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)
        self._sprite = sprite

    def on_update(self, dt):
        self._sprite.update()
        self._sprite.update_animation(dt)
        self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.clear(color=(0, 0, 0, 0))
        surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class UITextureButton(UIInteractiveWidget):
    """
    A button with an image for the face of the button.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float width: width of widget. Defaults to texture width if not specified.
    :param float height: height of widget. Defaults to texture height if not specified.
    :param Texture texture: texture to display for the widget.
    :param Texture texture_hovered: different texture to display if mouse is hovering over button.
    :param Texture texture_pressed: different texture to display if mouse button is pressed while hovering over button.
    :param str text: text to add to the button.
    :param style: style information for the button.
    :param float scale: scale the button, based on the base texture size.
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    """

    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: float = None,
                 height: float = None,
                 texture: Texture = None,
                 texture_hovered: Texture = None,
                 texture_pressed: Texture = None,
                 text: str = "",
                 scale: float = None,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):

        if width is None and texture is not None:
            width = texture.width

        if height is None and texture is not None:
            height = texture.height

        if scale is not None and texture is not None:
            height = texture.height * scale
            width = texture.width * scale

        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)

        self._tex = texture
        self._tex_hovered = texture_hovered
        self._tex_pressed = texture_pressed
        self._style = style or {}
        self._text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.trigger_render()

    @property
    def texture(self):
        return self._tex

    @texture.setter
    def texture(self, value: Texture):
        self._tex = value
        self.trigger_render()

    @property
    def texture_hovered(self):
        return self._tex_hovered

    @texture_hovered.setter
    def texture_hovered(self, value: Texture):
        self._tex_hovered = value
        self.trigger_render()

    @property
    def texture_pressed(self):
        return self._tex_pressed

    @texture_pressed.setter
    def texture_pressed(self, value: Texture):
        self._tex_pressed = value
        self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        tex = self._tex
        if self.pressed and self._tex_pressed:
            tex = self._tex_pressed
        elif self.hovered and self._tex_hovered:
            tex = self._tex_hovered

        if tex:
            surface.draw_texture(0, 0, self.width, self.height, tex)

        if self.text:
            text_margin = 2
            font_size = self._style.get("font_size", 15)
            font_color = self._style.get("font_color", arcade.color.WHITE)
            border_width = self._style.get("border_width", 2)
            # border_color = self._style.get("border_color", None)
            # bg_color = self._style.get("bg_color", (21, 19, 21))

            start_x = self.width // 2
            start_y = self.height // 2 + 4

            if self.pressed:
                start_y -= 2

            arcade.draw_text(
                text=self.text,
                start_x=start_x,
                start_y=start_y,
                font_size=font_size,
                color=font_color,
                align="center",
                anchor_x='center', anchor_y='center',
                width=self.width - 2 * border_width - 2 * text_margin
            )


class UILabel(UIWidget):
    """ A simple text label. Also supports multiline text.
    In case you want to scroll text use a :class:`UITextArea`
    By default a :class:`UILabel` will fit its initial content,
    if the text changed use :meth:`UILabel.fit_content` to adjust the size.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float width: width of widget. Defaults to text width if not specified.
    :param float height: height of widget. Defaults to text height if not specified.
    :param str text: text of the label.
    :param font_name: a list of fonts to use. Program will start at the beginning of the list
                      and keep trying to load fonts until success.
    :param float font_size: size of font.
    :param arcade.Color text_color: Color of font.
    :param bool bold: Bold font style.
    :param bool italic: Italic font style.
    :param bool stretch: Stretch font style.
    :param str anchor_x: Anchor point of the X coordinate: one of ``"left"``, 
                         ``"center"`` or ``"right"``.
    :param str anchor_y: Anchor point of the Y coordinate: one of ``"bottom"``,
                         ``"baseline"``, ``"center"`` or ``"top"``.
    :param str align: Horizontal alignment of text on a line, only applies if a width is supplied.
                      One of ``"left"``, ``"center"`` or ``"right"``.
    :param float dpi: Resolution of the fonts in this layout.  Defaults to 96.
    :param bool multiline: if multiline is true, a \\n will start a new line.
                           A UITextWidget with multiline of true is the same thing as UITextArea.

    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: Not used.
    """

    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: Optional[float] = None,
                 height: Optional[float] = None,
                 text: str = "",
                 font_name=('Arial',),
                 font_size: float = 12,
                 text_color: arcade.Color = (255, 255, 255, 255),
                 bold=False,
                 italic=False,
                 stretch=False,
                 anchor_x='left',
                 anchor_y='bottom',
                 align='left',
                 dpi=None,
                 multiline: bool = False,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):

        # Use Pyglet's Label for text rendering
        self.label = pyglet.text.Label(text=text,
                                       font_name=font_name,
                                       font_size=font_size,
                                       color=arcade.get_four_byte_color(text_color),
                                       width=None,
                                       height=None,
                                       bold=bold,
                                       italic=italic,
                                       stretch=stretch,
                                       anchor_x=anchor_x,
                                       anchor_y=anchor_y,
                                       align=align,
                                       dpi=dpi,
                                       multiline=multiline,
                                       )

        if not height:
            height = self.label.content_height

        if not width:
            width = self.label.content_width

        super().__init__(x, y, width, height,  # type: ignore
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)

        self.label.width = width
        self.label.height = height

    def fit_content(self):
        """
        Sets the width and height of this UIWidget to contain the whole text.
        """
        self.rect = self.x, self.y, self.label.content_width, self.label.content_height

    @property
    def text(self):
        return self.label.text

    @text.setter
    def text(self, value):
        self.label.text = value
        self.trigger_full_render()

    @property
    def rect(self) -> _Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = _Rect(*value)
        self.trigger_full_render()

        # Update Pyglet layout
        label = self.label

        label.begin_update()
        label.x, label.y, label.width, label.height = 0, 0, self.width, self.height
        label.end_update()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        with surface.ctx.pyglet_rendering():
            self.label.draw()


class UITextArea(UIWidget):
    """
    A text area for scrollable text.


    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param text: Text to show
    :param font_name: string or tuple of font names, to load
    :param font_size: size of the text
    :param text_color: color of the text
    :param multiline: support for multiline
    :param scroll_speed: speed of scrolling
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: float = 400,
                 height: float = 40,
                 text: str = "",
                 font_name=('Arial',),
                 font_size: float = 12,
                 text_color: arcade.Color = (255, 255, 255, 255),
                 multiline: bool = True,
                 scroll_speed: float = None,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)

        # Set how fast the mouse scroll wheel will scroll text in the pane.
        # Measured in pixels per 'click'
        self.scroll_speed = scroll_speed if scroll_speed is not None else font_size

        self.doc: AbstractDocument = pyglet.text.decode_text(text)
        self.doc.set_style(0, 12, dict(
            font_name=font_name,
            font_size=font_size,
            color=arcade.get_four_byte_color(text_color)
        ))

        self.layout = pyglet.text.layout.ScrollableTextLayout(self.doc,
                                                              width=self.width,
                                                              height=self.height,
                                                              multiline=multiline,
                                                              )

    def fit_content(self):
        """
        Sets the width and height of this UIWidget to contain the whole text.
        """
        self.rect = self.x, self.y, self.layout.content_width, self.layout.content_height

    @property
    def text(self):
        return self.doc.text

    @text.setter
    def text(self, value):
        self.doc.text = value
        self.trigger_full_render()

    @property
    def rect(self) -> _Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = _Rect(*value)
        self.trigger_full_render()

        # Update Pyglet layout
        my_layout = self.layout

        my_layout.begin_update()
        my_layout.x, my_layout.y, my_layout.width, my_layout.height = 0, 0, self.width, self.height
        my_layout.end_update()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        with surface.ctx.pyglet_rendering():
            self.layout.draw()

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UIMouseScrollEvent):
            if self.rect.collide_with_point(event.x, event.y):
                self.layout.view_y += event.scroll_y * self.scroll_speed
                self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED


class _Arcade_Caret(Caret):
    def _update(self, line=None, update_ideal_x=True):
        if line is None:
            line = self._layout.get_line_from_position(self._position)
            self._ideal_line = None
        else:
            self._ideal_line = line
        x, y = self._layout.get_point_from_position(self._position, line)
        if update_ideal_x:
            self._ideal_x = x

        # x -= self._layout.view_x
        # y -= self._layout.view_y
        # add 1px offset to make caret visible on line start
        x += self._layout.x + 1

        y += self._layout.y + self._layout.height

        font = self._layout.document.get_font(max(0, self._position - 1))
        self._list.position[:] = [x, y + font.descent, x, y + font.ascent]

        if self._mark is not None:
            self._layout.set_selection(min(self._position, self._mark), max(self._position, self._mark))

        self._layout.ensure_line_visible(line)
        self._layout.ensure_x_visible(x)


class UIInputText(UIWidget):
    """
    An input field the user can type text into.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param text: Text to show
    :param font_name: string or tuple of font names, to load
    :param font_size: size of the text
    :param text_color: color of the text
    :param multiline: support for multiline
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: float = 100,
                 height: float = 50,
                 text: str = "",
                 font_name=('Arial',),
                 font_size: float = 12,
                 text_color: arcade.Color = (0, 0, 0, 255),
                 multiline=False,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs
                 ):
        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)
        # fixme workaround for https://github.com/pyglet/pyglet/issues/529
        init_text = False
        if text == "":
            init_text = True
            text = " "

        self._active = False
        self._text_color = text_color if len(text_color) == 4 else (*text_color, 255)

        self.doc: AbstractDocument = pyglet.text.decode_text(text)
        self.doc.set_style(0, len(text), dict(font_name=font_name,
                                              font_size=font_size,
                                              color=self._text_color))

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.doc, width, height, multiline=multiline)
        self.caret = _Arcade_Caret(self.layout, color=(0, 0, 0))

        self._blink_state = self._get_caret_blink_state()

        if init_text:
            self.text = ""

    def _get_caret_blink_state(self):
        return self.caret._visible and self._active and self.caret._blink_visible

    def on_update(self, dt):
        # Only trigger render if blinking state changed
        current_state = self._get_caret_blink_state()
        if self._blink_state != current_state:
            self._blink_state = current_state
            self.trigger_full_render()

    def on_event(self, event: UIEvent) -> Optional[bool]:
        # if not active, check to activate, return
        if not self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                self._active = True
                self.trigger_full_render()
                self.caret.on_activate()
                self.caret.position = len(self.doc.text)
                return EVENT_UNHANDLED

        # if active check to deactivate
        if self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                x, y = event.x - self.x, event.y - self.y
                self.caret.on_mouse_press(x, y, event.button, event.modifiers)
            else:
                self._active = False
                self.trigger_full_render()
                self.caret.on_deactivate()
                return EVENT_UNHANDLED

        # if active pass all non press events to caret
        if self._active:
            # Act on events if active
            if isinstance(event, UITextEvent):
                self.caret.on_text(event.text)
                self.trigger_full_render()
            elif isinstance(event, UITextMotionEvent):
                self.caret.on_text_motion(event.motion)
                self.trigger_full_render()
            elif isinstance(event, UITextMotionSelectEvent):
                self.caret.on_text_motion_select(event.selection)
                self.trigger_full_render()

            if isinstance(event, UIMouseEvent) and self.rect.collide_with_point(event.x, event.y):
                x, y = event.x - self.x, event.y - self.y
                if isinstance(event, UIMouseDragEvent):
                    self.caret.on_mouse_drag(x, y, event.dx, event.dy, event.buttons, event.modifiers)
                    self.trigger_full_render()
                elif isinstance(event, UIMouseScrollEvent):
                    self.caret.on_mouse_scroll(x, y, event.scroll_x, event.scroll_y)
                    self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED

    @property
    def rect(self) -> _Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = _Rect(*value)
        self.trigger_full_render()

        # Update Pyglet layout
        my_layout = self.layout
        my_layout.begin_update()
        my_layout.x, my_layout.y, my_layout.width, my_layout.height = 0, 0, self.width, self.height
        my_layout.end_update()

    @property
    def text(self):
        return self.doc.text

    @text.setter
    def text(self, value):
        self.doc.text = value

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        with surface.ctx.pyglet_rendering():
            self.layout.draw()


class UIFlatButton(UIInteractiveWidget):
    """
    A text button, with support for background color and a border.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float width: width of widget. Defaults to texture width if not specified.
    :param float height: height of widget. Defaults to texture height if not specified.
    :param str text: text to add to the button.
    :param style: Used to style the button

    """

    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: float = 100,
                 height: float = 50,
                 text="",
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)
        self._text = text
        self._style = style or {}

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        # Render button
        font_name = self._style.get("font_name", ("calibri", "arial"))
        font_size = self._style.get("font_size", 15)
        font_color = self._style.get("font_color", arcade.color.WHITE)
        border_width = self._style.get("border_width", 2)
        border_color = self._style.get("border_color", None)
        bg_color = self._style.get("bg_color", (21, 19, 21))

        if self.pressed:
            bg_color = self._style.get("bg_color_pressed", arcade.color.WHITE)
            border_color = self._style.get("border_color_pressed", arcade.color.WHITE)
            font_color = self._style.get("font_color_pressed", arcade.color.BLACK)
        elif self.hovered:
            border_color = self._style.get("border_color_pressed", arcade.color.WHITE)

        # render BG
        if bg_color:
            arcade.draw_xywh_rectangle_filled(0, 0, self.width, self.height, color=bg_color)

        # render border
        if border_color and border_width:
            arcade.draw_xywh_rectangle_outline(
                border_width,
                border_width,
                self.width - 2 * border_width,
                self.height - 2 * border_width,
                color=border_color,
                border_width=border_width)

        # render text
        if self.text:
            start_x = self.width // 2
            start_y = self.height // 2

            text_margin = 2
            arcade.draw_text(
                text=self.text,
                start_x=start_x,
                start_y=start_y,
                font_name=font_name,
                font_size=font_size,
                color=font_color,
                align="center",
                anchor_x='center', anchor_y='center',
                width=self.width - 2 * border_width - 2 * text_margin
            )

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.trigger_render()


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

    def __init__(self, x=0, y=0, width=100, height=100,
                 children: Iterable[UIWidget] = tuple(),
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height,
                         children=children,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max,
                         style=style,
                         **kwargs)

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
        # do layout, detect changed rect
        rect = self.rect
        self.do_layout()
        if rect != self.rect:
            self.trigger_render()

        # Continue do_layout within subtree
        super()._do_layout()


class UIWrapper(UILayout, UIWidgetParent):
    """
    Wraps a :class:`arcade.gui.UIWidget` and reserves space around it, exactly one child supported.

    :param child: Single child of this wrapper
    :param padding: space around (top, right, bottom, left)
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(self,
                 *,
                 child: UIWidget,
                 padding=(0, 0, 0, 0),
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 ):
        """
        :param child: Child Widget which will be wrapped
        :param padding: Space between top, right, bottom, left
        """
        self._pad = padding
        super().__init__(*child.rect,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max,
                         children=[child])

    @property
    def rect(self) -> _Rect:
        # Adjust Rect to consume _pad more then child
        x, y, w, h = self.child.rect
        pt, pr, pb, pl = self._pad
        return _Rect(x - pl, y - pb, w + pl + pr, h + pb + pt)

    @rect.setter
    def rect(self, value: _Rect):
        # Child Rect has to be _pad smaller
        x, y, w, h = value
        pt, pr, pb, pl = self._pad
        self.child.rect = _Rect(x + pl, y + pb, w - pl - pr, h - pb - pt)

    @property
    def child(self) -> UIWidget:
        return self.children[0]

    @child.setter
    def child(self, value: UIWidget):
        self.children[0] = value


class UIAnchorWidget(UIWrapper):
    """
    Widget, which places itself relative to the parent.

    :param child: Child of this wrapper
    :param anchor_x: Which anchor to use for x axis (left, center, right)
    :param align_x: offset for x value (- = left, + = right)
    :param anchor_y: Which anchor to use for y axis (top, center, bottom)
    :param align_y: offset for y value (- = down, + = up)
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(self,
                 *,
                 child: UIWidget,
                 anchor_x: str = "center",
                 align_x: float = 0,
                 anchor_y: str = "center",
                 align_y: float = 0,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs
                 ):
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.align_x = align_x
        self.align_y = align_y
        super().__init__(child=child,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)

    def do_layout(self):
        rect = self.rect
        parent_rect = self.parent.rect if self.parent else _Rect(0, 0, *arcade.get_window().get_size())

        anchor_x = "center_x" if self.anchor_x == "center" else self.anchor_x
        own_anchor_x_value = getattr(rect, anchor_x)
        par_anchor_x_value = getattr(parent_rect, anchor_x)
        diff_x = par_anchor_x_value + self.align_x - own_anchor_x_value

        anchor_y = "center_y" if self.anchor_y == "center" else self.anchor_y
        own_anchor_y_value = getattr(rect, anchor_y)
        par_anchor_y_value = getattr(parent_rect, anchor_y)
        diff_y = par_anchor_y_value + self.align_y - own_anchor_y_value

        if diff_x or diff_y:
            self.rect = self.rect.move(diff_x, diff_y)


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

    def __init__(self, x=0, y=0, width=100, height=100, color=(0, 0, 0, 0),
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max)
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


class UIBorder(UIWrapper):
    """
    Wraps a Widget with a border of given color.


    :param child: Child of this wrapper
    :param border_width: Width of the border
    :param border_color: Color of the border
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(self, child: UIWidget, border_width=2, border_color=(0, 0, 0, 255),
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(
            child=child,
            padding=(border_width, border_width, border_width, border_width),
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max
        )
        self._border_color = border_color
        self._border_width = border_width

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        arcade.draw_xywh_rectangle_outline(0, 0, self.width, self.height,
                                           color=self._border_color,
                                           border_width=self._border_width)


class UITexturePane(UIWrapper):
    """
    This wrapper draws a background before child widget is rendered

    :param child: Child of this wrapper
    :param tex: Texture to use as background
    :param padding: Space between the outer border of this widget and the child
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(self, child: UIWidget,
                 tex: Texture,
                 padding=(0, 0, 0, 0),
                 size_hint=(1, 1),
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(
            child=child,
            padding=padding,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max
        )
        self._tex = tex

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        surface.draw_texture(0, 0, self.width, self.height, tex=self._tex)


class UIPadding(UIWrapper):
    """Wraps a Widget and applies padding.

    :param child: Child of this wrapper
    :param bg_color: background color
    :param padding: Space between the outer border of this widget and the child
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    def __init__(self, child: UIWidget,
                 padding=(0, 0, 0, 0),
                 bg_color=None,
                 size_hint=(1, 1),
                 size_hint_min=None,
                 size_hint_max=None,
                 **kwargs):
        """
        :arg padding: Padding - top, right, bottom, left
        :param size_hint: A hint for :class:`UILayout`, if this :class:`UIWidget` would
                          like to grow (default: (1, 1) -> full size of parent)
        """
        super().__init__(
            child=child,
            padding=padding,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max
        )
        self._bg_color = bg_color

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        if self._bg_color:
            # clear with bg color if set
            surface.clear(self._bg_color)


class UIBoxLayout(UILayout):
    """
    Places widgets next to each other.
    Depending on the vertical attribute, the Widgets are placed top to bottom or left to right.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param vertical: Layout children vertical (True) or horizontal (False)
    :param align: Align children in orthogonal direction (x: left, center, right / y: top, center, bottom)
    :param children: Initial children, more can be added
    :param size_hint: A hint for :class:`UILayout`, if this :class:`UIWidget` would like to grow
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param space_between: Space between the children
    """

    def __init__(self, x=0, y=0,
                 vertical=True,
                 align="center",
                 children: Iterable[UIWidget] = tuple(),
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 space_between=0,
                 style=None,
                 **kwargs):
        self.align = align
        self.vertical = vertical
        self._space_between = space_between
        super().__init__(x=x,
                         y=y,
                         width=0,
                         height=0,
                         children=children,
                         size_hint=size_hint,
                         size_hint_min=size_hint_min,
                         size_hint_max=size_hint_max,
                         style=style,
                         **kwargs)

    def do_layout(self):
        # TODO support self.align and self.spacing
        initial_top = self.top
        start_y = self.top
        start_x = self.left

        # min_height = sum(map(attrgetter("height"), self.children))
        # min_width = sum(map(attrgetter("width"), self.children))

        if not self.children:
            self.rect = _Rect(self.left, self.bottom, 0, 0)
            return

        required_space_between = max(0, len(self.children) - 1) * self._space_between

        if self.vertical:
            new_height = sum(child.height for child in self.children) + required_space_between
            new_width = max(child.width for child in self.children)
            center_x = start_x + new_width // 2
            for child in self.children:
                if self.align == "left":
                    new_rect = child.rect.align_left(start_x)
                elif self.align == "right":
                    new_rect = child.rect.align_right(start_x + new_width)
                else:
                    new_rect = child.rect.align_center_x(center_x)

                new_rect = new_rect.align_top(start_y)
                if new_rect != child.rect:
                    child.rect = new_rect
                start_y -= child.height
                start_y -= self._space_between
        else:
            new_height = max(child.height for child in self.children)
            new_width = sum(child.width for child in self.children) + required_space_between
            center_y = start_y - new_height // 2

            for child in self.children:
                if self.align == "top":
                    new_rect = child.rect.align_top(start_y)
                elif self.align == "bottom":
                    new_rect = child.rect.align_bottom(start_y - new_height)
                else:
                    new_rect = child.rect.align_center_y(center_y)

                new_rect = new_rect.align_left(start_x)
                if new_rect != child.rect:
                    child.rect = new_rect
                start_x += child.width
                start_x += self._space_between

        self._rect = _Rect(self.left, self.bottom, new_width, new_height).align_top(initial_top)
