from abc import abstractmethod, ABC
from random import randint
from typing import NamedTuple, Iterable

import pyglet
from pyglet.event import EventDispatcher

import arcade
from arcade import Texture, Sprite
from arcade.experimental.gui_v2 import Surface
from arcade.experimental.gui_v2.events import Event, MouseMovement, MousePress, MouseRelease, Text, MouseDrag, \
    MouseScroll, TextMotion, TextMotionSelect


def point_in_rect(x, y, rx, ry, rw, rh):
    return rx < x < rx + rw and ry < y < ry + rh


class Rect(NamedTuple):
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

    def align_top(self, value: int) -> "Rect":
        """Returns new Rect, which is aligned to the top"""
        diff_y = value - self.top
        return self.move(dy=diff_y)

    def align_bottom(self, value: int) -> "Rect":
        """Returns new Rect, which is aligned to the bottom"""
        diff_y = value - self.bottom
        return self.move(dy=diff_y)

    def align_left(self, value: int) -> "Rect":
        """Returns new Rect, which is aligned to the left"""
        diff_x = value - self.left
        return self.move(dx=diff_x)

    def align_right(self, value: int) -> "Rect":
        """Returns new Rect, which is aligned to the right"""
        diff_x = value - self.right
        return self.move(dx=diff_x)

    def align_center_x(self, value: int) -> "Rect":
        """Returns new Rect, which is aligned to the center_x"""
        diff_x = value - self.center_x
        return self.move(dx=diff_x)

    def align_center_y(self, value: int) -> "Rect":
        """Returns new Rect, which is aligned to the center_y"""
        diff_y = value - self.center_y
        return self.move(dy=diff_y)


class WidgetParent:
    rect: Rect


class Widget(EventDispatcher, WidgetParent, ABC):
    def __init__(self,
                 x=0,
                 y=0,
                 width=100,
                 height=100,
                 ):
        self._rect = Rect(x, y, width, height)
        self.rendered = False
        self.parent: WidgetParent = None

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

    def on_event(self, event: Event):
        pass

    def with_border(self, width=2, color=(0, 0, 0)):
        """
        Wraps this Widget with a border
        :param width: border width
        :param color: border color
        :return: Wrapping Border with self as child
        """
        return Border(self, border_width=width, border_color=color)

    def with_padding(self, top=0, right=0, bottom=0, left=0, bg_color=None):
        """
        Wraps this Widget with a border
        :param top: Top Padding
        :param right: Right Padding
        :param bottom: Bottom Padding
        :param left: Left Padding
        :param bg_color: Background color
        :return: Wrapping Padding with self as child
        """
        return Padding(self, pad=(top, right, bottom, left), bg_color=bg_color)

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.rendered = False

    @property
    def left(self):
        return self.rect.x

    @property
    def right(self):
        rect = self.rect
        return rect.x + rect.width

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


class InteractiveWidget(Widget):
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

    def on_event(self, event: Event):
        if isinstance(event, MouseMovement):
            self.hover = point_in_rect(event.x, event.y, *self.rect)

        if isinstance(event, MousePress):
            if self.rect.collide_with_point(event.x, event.y):
                self.pressed = True
                return True

        if self.pressed and isinstance(event, MouseRelease):
            self.pressed = False
            if self.rect.collide_with_point(event.x, event.y):
                self.dispatch_event("on_click", self, event)
                return True

    def on_click(self, source, event: MouseRelease):
        pass


class Dummy(InteractiveWidget):
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


class SpriteWidget(Widget):
    def __init__(self, *, x=0, y=0, width=100, height=100, sprite: Sprite = None):
        super().__init__(x, y, width, height)
        self._sprite = sprite

    def on_update(self, dt):
        self._sprite.update()
        self._sprite.update_animation(dt)  # ?

    def render(self, surface: Surface, force=False):
        surface.clear((0, 0, 0, 0))
        surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class TextureButton(InteractiveWidget):
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
            border_color = self._style.get("border_color", None)
            bg_color = self._style.get("bg_color", (21, 19, 21))

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


class TextArea(Widget):
    def __init__(self, x=0, y=0, width=100, height=200, text="",
                 font_name=('Arial',),
                 font_size=12,
                 text_color=(255, 255, 255, 255),
                 style=None):
        super().__init__(x, y, width, height)

        self.doc = pyglet.text.decode_text(text)
        self.doc.set_style(0, 12, dict(
            font_name=font_name,
            font_size=font_size,
            color=text_color
        ))

        self.layout = pyglet.text.layout.ScrollableTextLayout(self.doc,
                                                              width=self.width,
                                                              height=self.height,
                                                              multiline=True,
                                                              )

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.rendered = False

        # Update Pyglet layout
        l = self.layout
        l.x, l.y, l.width, l.height = self.rect

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        self.rendered = True

        # surface.clear()
        with surface.ctx.pyglet_rendering():
            self.layout.default_group_class.scissor_area = self.rect.scale(surface.pixel_ratio)
            self.layout.draw()

    def on_event(self, event: Event):
        if isinstance(event, MouseScroll):
            if point_in_rect(event.x, event.y, *self.rect):
                self.layout.view_y += event.scroll_y
                self.rendered = False


class InputText(Widget):
    def __init__(self, x=0, y=0, width=100, height=50, text="", style=None):
        super().__init__(x, y, width, height)

        self.doc = pyglet.text.document.FormattedDocument()
        self.doc = pyglet.text.decode_text(text)
        self.doc.set_style(0, 12, dict(font_name='Arial', font_size=12,
                                       color=(255, 255, 255, 255)))

        self.layout = pyglet.text.layout.IncrementalTextLayout(self.doc, width, height)
        self.caret = pyglet.text.caret.Caret(self.layout)
        self.caret.on_activate()
        self.caret.visible = True

    def on_event(self, event: Event):
        if isinstance(event, Text):
            self.caret.on_text(event.text)
        elif isinstance(event, MousePress):
            self.caret.on_mouse_press(event.x, event.y, event.button, event.modifiers)
        elif isinstance(event, MouseDrag):
            self.caret.on_mouse_drag(event.x, event.y, event.dx, event.dy, event.buttons, event.modifiers)
        elif isinstance(event, TextMotion):
            self.caret.on_text_motion(event.motion)
        elif isinstance(event, TextMotionSelect):
            self.caret.on_text_motion_select(event.motion)
        elif isinstance(event, MouseScroll):
            self.caret.on_mouse_scroll(event.x, event.y, event.scroll_x, event.scroll_y)
        self.rendered = False
        self.parent.rendered = False

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, value):
        self._rect = value
        self.rendered = False

        # Update Pyglet layout
        l = self.layout
        l.x, l.y, l.width, l.height = self.rect

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        self.rendered = True

        with surface.ctx.pyglet_rendering():
            self.layout.default_group_class.scissor_area = self.rect.scale(surface.pixel_ratio)
            self.layout.draw()


class FlatButton(InteractiveWidget):
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


class Wrapper(Widget):
    """
    Wraps a Widget and reserves space around
    """

    def __init__(self, *, child: Widget, pad=(0, 0, 0, 0)):
        """
        :param child: Child Widget which will be wrapped
        :param pad: Space between top, right, bottom, left
        """
        if isinstance(child, PlacedWidget):
            raise Exception("Wrapping PlaceWidget into a Wrapper is not supported")

        self.child = child
        child.parent = self
        super().__init__(*child.rect)

        self._pad = pad

    @property
    def rect(self) -> Rect:
        # Adjust Rect to consume _pad more then child
        x, y, w, h = self.child.rect
        pt, pr, pb, pl = self._pad
        return Rect(x - pl, y - pb, w + pl + pr, h + pb + pt)

    @rect.setter
    def rect(self, value: Rect):
        # Child Rect has to be _pad smaller
        x, y, w, h = value
        pt, pr, pb, pl = self._pad
        self.child.rect = Rect(x + pl, y + pb, w - pl - pr, h - pb - pt)
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

    def on_event(self, event: Event):
        self.child.on_event(event)

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return

        surface.limit(*self.child.rect)
        self.child.render(surface, force=force)


class PlacedWidget(Wrapper):
    """
    Widget, which places itself relative to the window.
    """

    def __init__(self,
                 *,
                 x_align=0,
                 y_align=0,
                 x_anchor="left",
                 y_anchor="bottom",
                 child: Widget,
                 ):
        super().__init__(child=child)
        self.x_align = x_align
        self.y_align = y_align
        self.x_anchor = x_anchor
        self.y_anchor = y_anchor

    def do_layout(self):
        request_rerender = super().do_layout()

        rect = self.rect
        parent_rect = self.parent.rect

        own_x_anchor_value = getattr(rect, self.x_anchor)
        par_x_anchor_value = getattr(parent_rect, self.x_anchor)
        diff_x = par_x_anchor_value + self.x_align - own_x_anchor_value

        own_y_anchor_value = getattr(rect, self.y_anchor)
        par_y_anchor_value = getattr(parent_rect, self.y_anchor)
        diff_y = par_y_anchor_value + self.y_align - own_y_anchor_value

        if diff_x or diff_y:
            self.rect = self.rect.move(diff_x, diff_y)
            request_rerender = True

        return request_rerender


class Space(Widget):
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


class Border(Wrapper):
    """
    Wraps a Widget with a border of given color.
    """

    def __init__(self, child: Widget, border_width=2, border_color=(0, 0, 0, 255)):
        super().__init__(
            child=child,
            pad=(border_width, border_width, border_width, border_width)
        )
        self._border_color = border_color

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return

        surface.clear(self._border_color)
        surface.limit(*self.child.rect)
        surface.clear()
        self.child.render(surface, force=True)


class TexturePane(Wrapper):
    """
    Wraps a Widget with a border of given color.
    """

    def __init__(self, child: Widget, tex: Texture, pad=(0, 0, 0, 0)):
        super().__init__(
            child=child,
            pad=pad
        )
        self._tex = tex

    def render(self, surface: Surface, force=False):
        if self.rendered and not force:
            return
        surface.draw_texture(0, 0, self.width, self.height, tex=self._tex)
        surface.limit(*self.child.rect)
        self.child.render(surface, force=True)


class Padding(Wrapper):
    """Wraps a Widget and applies padding"""

    def __init__(self, child: Widget, pad=(0, 0, 0, 0), bg_color=None):
        """
        :arg pad: Padding - top, right, bottom, left
        """
        super().__init__(
            child=child,
            pad=pad
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


class BoxWidget(Widget):
    """
    Places Widgets next to each other.
    Depending on the vertical attribute, the Widgets are placed top to bottom or left to right.
    """

    def __init__(self, x=0, y=0, vertical=True, align="center", children: Iterable[Widget] = tuple()):
        super().__init__(x, y, 1, 1)
        self._children = list(children)

        self.align = align
        self.vertical = vertical
        self._children_modified = False

    def add(self, child: Widget):
        self._children.append(child)
        self._children_modified = True

    def remove(self, child: Widget):
        self._children.remove(child)
        self._children_modified = True

    def __contains__(self, item):
        return item in self._children

    def on_update(self, dt):
        for child in self._children:
            child.on_update(dt)

    def render(self, surface: Surface, force=False):
        for child in self._children:
            surface.limit(*child.rect)
            child.render(surface, force=force)

    def do_layout(self):
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

        self.rect = Rect(self.left, self.bottom, new_width, new_height)

        if self._children_modified:
            self._children_modified = False
            # Requires rerender
            return True
