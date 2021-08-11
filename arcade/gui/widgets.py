from abc import abstractmethod, ABC
from random import randint
from typing import NamedTuple, Iterable, Optional

import pyglet
from pyglet.event import EventDispatcher
from pyglet.text.document import AbstractDocument

import arcade
from arcade import Texture, Sprite
from arcade.gui import Surface
from arcade.gui.events import UIEvent, UIMouseMovementEvent, UIMousePressEvent, UIMouseReleaseEvent, \
    UITextEvent, \
    UIMouseDragEvent, \
    UIMouseScrollEvent, UITextMotionEvent, UITextMotionSelectEvent, UIMouseEvent, UIOnClickEvent


def _point_in_rect(x, y, rx, ry, rw, rh):
    return rx < x < rx + rw and ry < y < ry + rh


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
    def width(self):
        return self.width

    @property
    def height(self):
        return self.height

    @property
    def center_x(self):
        return self.x + self.width / 2

    @property
    def center_y(self):
        return self.y + self.height / 2

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

    def align_center_x(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the center_x"""
        diff_x = value - self.center_x
        return self.move(dx=diff_x)

    def align_center_y(self, value: float) -> "_Rect":
        """Returns new Rect, which is aligned to the center_y"""
        diff_y = value - self.center_y
        return self.move(dy=diff_y)


class UIWidget(EventDispatcher, ABC):
    """ Base class for UI widgets. """
    def __init__(self,
                 x=0,
                 y=0,
                 width=100,
                 height=100,
                 ):
        self._rect = _Rect(x, y, width, height)
        self.rendered = False
        self.parent: Optional[UIWidgetParent] = None

        self.register_event_type("on_event")

    @abstractmethod
    def render(self, surface: Surface, force=False):
        """
        Render the widget with arcade.draw commands or using the surface methods.
        """

    def on_update(self, dt):
        pass

    def do_layout(self) -> bool:
        """
        Called by the UIManager before rendering, Widgets should place themselves or children
        :return: in case of any change, which requires a forced rerender of the UI return True
        """

    def dispatch_ui_event(self, event):
        self.dispatch_event("on_event", event)

    def on_event(self, event: UIEvent):
        pass

    def with_border(self, width=2, color=(0, 0, 0)):
        """
        Wraps this Widget with a border
        :param width: border width
        :param color: border color
        :return: Wrapping Border with self as child
        """
        return UIBorder(self, border_width=width, border_color=color)

    def with_space_around(self, top=0, right=0, bottom=0, left=0, bg_color=None):
        """
        Wraps this Widget with a border
        :param top: Top Padding
        :param right: Right Padding
        :param bottom: Bottom Padding
        :param left: Left Padding
        :param bg_color: Background color
        :return: Wrapping Padding with self as child
        """
        return UIPadding(self, padding=(top, right, bottom, left), bg_color=bg_color)

    def with_background(self, texture: Texture, top=0, right=0, bottom=0, left=0):
        return UITexturePane(self, tex=texture, padding=(top, right, bottom, left))

    @property
    def rect(self) -> _Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.rendered = False

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
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height

    @property
    def center_x(self):
        return self.rect.center_x

    @property
    def center_y(self):
        return self.rect.center_y


class UIWidgetParent(ABC):
    @property
    @abstractmethod
    def rect(self) -> _Rect:
        pass

    @abstractmethod
    def remove(self, child: UIWidget):
        pass


class UIInteractiveWidget(UIWidget):
    # States
    _hover = False
    _pressed = False

    def __init__(self, x=0, y=0, width=100, height=100):
        super().__init__(x, y, width, height)
        self.register_event_type("on_click")

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        if self._pressed != value:
            self._pressed = value
            self.rendered = False

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, value):
        if value != self._hover:
            self._hover = value
            self.rendered = False

    def on_event(self, event: UIEvent):
        super().on_event(event)

        if isinstance(event, UIMouseMovementEvent):
            self.hover = _point_in_rect(event.x, event.y, *self.rect)

        if isinstance(event, UIMousePressEvent) and self.rect.collide_with_point(
                event.x, event.y
        ):
            self.pressed = True
            return True

        if self.pressed and isinstance(event, UIMouseReleaseEvent):
            self.pressed = False
            if self.rect.collide_with_point(event.x, event.y):
                # Dispatch new on_click event, source is this widget itself
                self.dispatch_event("on_event", UIOnClickEvent(self, event.x, event.y))
                return True

        if isinstance(event, UIOnClickEvent) and self.rect.collide_with_point(event.x, event.y):
            self.dispatch_event("on_click", event)

    def on_click(self, event: UIOnClickEvent):
        pass


class UIDummy(UIInteractiveWidget):
    def __init__(self, x=0, y=0, width=100, height=100, color=arcade.color.BLACK):
        super().__init__(x, y, width, height)
        self.color = color
        self.frame = randint(0, 255)

    def render(self, surface: Surface, force=False):
        self.frame += 1
        frame = self.frame % 256
        surface.clear((*self.color[:3], frame))

        if self.hover:
            arcade.draw_xywh_rectangle_outline(0, 0,
                                               self.width, self.height,
                                               color=arcade.color.BATTLESHIP_GREY,
                                               border_width=3)


class UISpriteWidget(UIWidget):
    """ Create a UI element with a sprite that controls what is displayed. """
    def __init__(self, *, x=0, y=0, width=100, height=100, sprite: Sprite = None):
        super().__init__(x, y, width, height)
        self._sprite = sprite

    def on_update(self, dt):
        self._sprite.update()
        self._sprite.update_animation(dt)  # ?

    def render(self, surface: Surface, force=False):
        surface.clear((0, 0, 0, 0))
        surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class UITextureButton(UIInteractiveWidget):
    """ A button with an image for the face of the button. """
    def __init__(self,
                 x=0, y=0,
                 width=100, height=50,
                 texture: Texture = None,
                 texture_hover: Texture = None,
                 texture_pressed: Texture = None,
                 text="",
                 style=None):
        super().__init__(x, y, width, height)
        self._tex = texture
        self._tex_hover = texture_hover
        self._tex_pressed = texture_pressed
        self._style = style or {}
        self._text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.rendered = False

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        self.rendered = True

        tex = self._tex
        if self.pressed and self._tex_pressed:
            tex = self._tex_pressed
        elif self.hover and self._tex_hover:
            tex = self._tex_hover

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


class UITextWidget(UIWidget):
    """ A text label. """
    def __init__(self, x=0, y=0, width=100, height=200, text="",
                 font_name=('Arial',),
                 font_size=12,
                 text_color=(255, 255, 255, 255),
                 style=None,
                 multiline=False):
        super().__init__(x, y, width, height)

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

    @property
    def text(self):
        return self.doc.text

    @text.setter
    def text(self, value):
        self.doc.text = value

    @property
    def rect(self) -> _Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.rendered = False

        # Update Pyglet layout
        my_layout = self.layout

        my_layout.begin_update()
        my_layout.x, my_layout.y, my_layout.width, my_layout.height = 0, 0, self.width, self.height
        my_layout.end_update()

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        self.rendered = True

        with surface.ctx.pyglet_rendering():
            self.layout.default_group_class.scissor_area = self.rect.scale(surface.pixel_ratio)
            self.layout.draw()

    def on_event(self, event: UIEvent):
        super().on_event(event)

        if isinstance(event, UIMouseScrollEvent):
            if _point_in_rect(event.x, event.y, *self.rect):
                self.layout.view_y += event.scroll_y
                self.rendered = False


class UITextArea(UITextWidget):
    """ A multi-line text display. """
    def __init__(self, x=0, y=0, width=100, height=200, text="",
                 font_name=('Arial',),
                 font_size=12,
                 text_color=(255, 255, 255, 255),
                 style=None):
        super().__init__(
            text=text,
            x=x,
            y=y,
            width=width,
            height=height,
            font_name=font_name,
            font_size=font_size,
            text_color=text_color,
            style=style,
            multiline=True
        )


class UIInputText(UIWidget):
    """ An input field the user can type text into. """
    def __init__(self, x=0, y=0, width=100, height=50, text="",
                 font_name=('Arial',),
                 font_size=12,
                 text_color=(0, 0, 0, 255),
                 ):
        super().__init__(x, y, width, height)

        self._active = False

        self.doc = pyglet.text.document.FormattedDocument()
        self.doc = pyglet.text.decode_text(text)
        self.doc.set_style(0, 12, dict(font_name=font_name,
                                       font_size=font_size,
                                       color=text_color))

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.doc, width, height)
        self.caret = pyglet.text.caret.Caret(self.layout, color=(0, 0, 0))

    def on_event(self, event: UIEvent):
        super().on_event(event)
        self.rendered = False
        self.parent.rendered = False  # TODO we could have a method to request enforced rendering

        # if not active, check to activate, return
        if not self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                self._active = True
                self.caret.on_activate()
                print("activate")
                return

        # if active check to deactivate
        if self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                x, y = event.x - self.x, event.y - self.y
                self.caret.on_mouse_press(x, y, event.button, event.modifiers)
            else:
                self._active = False
                self.caret.on_deactivate()
                return

        # if active pass all non press events to caret
        if self._active:
            # Act on events if active
            if isinstance(event, UITextEvent):
                self.caret.on_text(event.text)
            elif isinstance(event, UITextMotionEvent):
                self.caret.on_text_motion(event.motion)
            elif isinstance(event, UITextMotionSelectEvent):
                self.caret.on_text_motion_select(event.motion)

            if isinstance(event, UIMouseEvent) and self.rect.collide_with_point(event.x, event.y):
                x, y = event.x - self.x, event.y - self.y
                if isinstance(event, UIMouseDragEvent):
                    self.caret.on_mouse_drag(x, y, event.dx, event.dy, event.buttons, event.modifiers)
                elif isinstance(event, UIMouseScrollEvent):
                    self.caret.on_mouse_scroll(x, y, event.scroll_x, event.scroll_y)

    @property
    def rect(self) -> _Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.rendered = False

        # Update Pyglet layout
        my_layout = self.layout
        my_layout.x, my_layout.y, my_layout.width, my_layout.height = self.rect

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        self.rendered = True

        with surface.ctx.pyglet_rendering():
            self.layout.default_group_class.scissor_area = self.rect.scale(surface.pixel_ratio)
            self.layout.draw()


class UIFlatButton(UIInteractiveWidget):
    """ A text button, with support for background color and a border. """
    def __init__(self, x=0, y=0, width=100, height=50, text="", style=None):
        super().__init__(x, y, width, height)
        self._text = text
        self._style = style or {}

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        self.rendered = True

        # Render button
        font_size = self._style.get("font_size", 15)
        font_color = self._style.get("font_color", arcade.color.WHITE)
        border_width = self._style.get("border_width", 2)
        border_color = self._style.get("border_color", None)
        bg_color = self._style.get("bg_color", (21, 19, 21))

        if self.pressed:
            bg_color = self._style.get("bg_color_pressed", arcade.color.WHITE)
            border_color = self._style.get("border_color_pressed", arcade.color.WHITE)
            font_color = self._style.get("font_color_pressed", arcade.color.BLACK)
        elif self.hover:
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
        text_margin = 2
        if self.text:
            start_x = self.width // 2
            start_y = self.height // 2

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

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.rendered = False


class UIWrapper(UIWidget, UIWidgetParent):
    """
    Wraps a :class:`arcade.gui.Widget` and reserves space around it.
    """

    def __init__(self, *, child: UIWidget, padding=(0, 0, 0, 0)):
        """
        :param child: Child Widget which will be wrapped
        :param padding: Space between top, right, bottom, left
        """
        if isinstance(child, UIAnchorWidget):
            raise Exception("Wrapping PlaceWidget into a Wrapper is not supported")

        self.child = child
        child.parent = self
        super().__init__(*child.rect)

        self._pad = padding

    def remove(self, child: UIWidget):
        self.parent.remove(self)

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
        self.rendered = False

    @property
    def rendered(self):
        return self.child.rendered

    @rendered.setter
    def rendered(self, value):
        self.child.rendered = value

    def on_update(self, dt):
        self.child.on_update(dt)

    def do_layout(self) -> bool:
        return self.child.do_layout()

    def on_event(self, event: UIEvent):
        super().on_event(event)
        self.child.dispatch_event("on_event", event)

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return

        surface.limit(*self.child.rect)
        self.child.render(surface, force=force)


class UIAnchorWidget(UIWrapper):
    """
    Widget, which places itself relative to the parent.
    """

    def __init__(self,
                 *,
                 child: UIWidget,
                 anchor_x="center",
                 align_x=0,
                 anchor_y="center",
                 align_y=0,
                 ):
        super().__init__(child=child)
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.align_x = align_x
        self.align_y = align_y

    def do_layout(self):
        request_rerender = super().do_layout()

        rect = self.rect
        parent_rect = self.parent.rect

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
            request_rerender = True

        return request_rerender


class UISpace(UIWidget):
    def __init__(self, x=0, y=0, width=10, height=10, color=(0, 0, 0, 0)):
        super().__init__(x, y, width, height)
        self._color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.rendered = False

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return

        surface.clear(self._color)


class UIBorder(UIWrapper):
    """
    Wraps a Widget with a border of given color.
    """

    def __init__(self, child: UIWidget, border_width=2, border_color=(0, 0, 0, 255)):
        super().__init__(
            child=child,
            padding=(border_width, border_width, border_width, border_width)
        )
        self._border_color = border_color

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return

        surface.clear(self._border_color)
        surface.limit(*self.child.rect)
        surface.clear()
        self.child.render(surface, force=True)


class UITexturePane(UIWrapper):
    """
    Wraps a Widget and underlays a background texture.
    """

    def __init__(self, child: UIWidget, tex: Texture, padding=(0, 0, 0, 0)):
        super().__init__(
            child=child,
            padding=padding
        )
        self._tex = tex

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        surface.draw_texture(0, 0, self.width, self.height, tex=self._tex)
        surface.limit(*self.child.rect)
        self.child.render(surface, force=True)


class UIPadding(UIWrapper):
    """Wraps a Widget and applies padding"""

    def __init__(self, child: UIWidget, padding=(0, 0, 0, 0), bg_color=None):
        """
        :arg padding: Padding - top, right, bottom, left
        """
        super().__init__(
            child=child,
            padding=padding
        )
        self._bg_color = bg_color

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return

        if self._bg_color:
            # clear with bg color if set
            surface.clear(self._bg_color)
        surface.limit(*self.child.rect)
        self.child.render(surface, force=True)


class UIGroup(UIWidget, UIWidgetParent):
    """
    Group of Widgets
    """

    def __init__(self, x=0, y=0, width=100, height=100, children: Iterable[UIWidget] = tuple()):
        super().__init__(x, y, width, height)
        self._children = list(children)
        self._children_modified = True

        for child in self._children:
            child.parent = self

    def add(self, child: UIWidget):
        self._children.append(child)
        self._children_modified = True

        child.parent = self

    def remove(self, child: UIWidget):
        self._children.remove(child)
        self._children_modified = True

        child.parent = None

    def __contains__(self, item):
        return item in self._children

    def on_update(self, dt):
        for child in self._children:
            child.on_update(dt)

    def on_event(self, event: UIEvent):
        super().on_event(event)
        for child in self._children:
            child.dispatch_ui_event(event)

    def render(self, surface: Surface, force=False):
        for child in self._children:
            surface.limit(*child.rect)
            child.render(surface, force=force)

    def do_layout(self) -> bool:
        result = False
        for child in self._children:
            result |= bool(child.do_layout())

        return result


class UIBoxGroup(UIGroup):
    """
    Places Widgets next to each other.
    Depending on the vertical attribute, the Widgets are placed top to bottom or left to right.
    """

    def __init__(self, x=0, y=0, vertical=True, align="center", children: Iterable[UIWidget] = tuple()):
        """

        :param x: x coordinate of bottom left
        :param y: x coordinate of bottom left
        :param vertical: Layout children vertical (True) or horizontal (False)
        :param align: Align children in orthogonal direction
        :param children: Initial children, more can be added
        """
        super().__init__(x=x, y=y, width=0, height=0, children=children)
        self.align = align
        self.vertical = vertical

    def do_layout(self):
        # TODO use alignment
        initial_top = self.top
        start_y = self.top
        start_x = self.left

        if self.vertical:
            new_height = sum(child.height for child in self._children)
            new_width = max(child.width for child in self._children)
            center_x = start_x + new_width // 2
            for child in self._children:
                child.rect = child.rect.align_top(start_y).align_center_x(center_x)
                start_y -= child.height
        else:
            new_height = max(child.height for child in self._children)
            new_width = sum(child.width for child in self._children)
            center_y = start_y - new_height // 2
            for child in self._children:
                child.rect = child.rect.align_left(start_x).align_center_y(center_y)
                start_x += child.width

        self.rect = _Rect(self.left, self.bottom, new_width, new_height).align_top(initial_top)

        if self._children_modified:
            self._children_modified = False
            # Requires rerender
            return True


class UIDraggableMixin(UIWidget):
    def render(self, surface: Surface, force=False):
        super().render(surface, force)

    def on_event(self, event):
        super().on_event(event)
        if isinstance(event, UIMouseDragEvent) and self.rect.collide_with_point(event.x, event.y):
            self.rect = self.rect.move(event.dx, event.dy)
