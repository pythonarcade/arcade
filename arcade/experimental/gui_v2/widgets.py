from random import randint
from typing import Tuple

import pyglet
from pyglet.event import EventDispatcher

import arcade
from arcade import Texture, Sprite
from arcade.experimental.gui_v2 import Surface, MouseScroll
from arcade.experimental.gui_v2.events import Event, MouseMovement, MousePress, MouseRelease


def point_in_rect(x, y, rx, ry, rw, rh):
    return rx < x < rx + rw and ry < y < ry + rh


class Widget(EventDispatcher):
    def __init__(self,
                 x=0,
                 y=0,
                 width=100,
                 height=100,
                 ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.rendered = False

        self.register_event_type("on_click")

    def render(self, surface: Surface):
        self.rendered = True

    def on_update(self, dt):
        pass

    def rect(self) -> Tuple[int, int, int, int]:
        """
        Rectangle of the widget
        """
        return self.x, self.y, self.width, self.height

    def on_event(self, event: Event):
        pass


class InteractiveWidget(Widget):
    # Interaction
    _hover = False
    _pressed = False

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
            self.hover = point_in_rect(event.x, event.y, *self.rect())

        if isinstance(event, MousePress):
            self.pressed = point_in_rect(event.x, event.y, *self.rect())

        if self.pressed and isinstance(event, MouseRelease):
            self.pressed = False
            if point_in_rect(event.x, event.y, *self.rect()):
                self.dispatch_event("on_click", self, event)
                return True

    def on_click(self, source, event: MouseRelease):
        pass


class Button(InteractiveWidget):
    def __init__(self, x=0, y=0, width=100, height=100, color=arcade.color.BLACK):
        super().__init__(x, y, width, height)
        self.color = color
        self.frame = randint(0, 255)

    def render(self, surface: Surface):
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

    def render(self, surface: Surface):
        surface.clear((0, 0, 0, 0))
        surface.draw_sprite(0, 0, self.width, self.height, self._sprite)


class ImageButton(InteractiveWidget):
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

    def render(self, surface: Surface):
        if self.rendered:
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
    def __init__(self, x=0, y=0, width=100, height=50, text="", style=None):
        super().__init__(x, y, width, height)

        self.doc = pyglet.text.decode_text(text)
        self.doc.set_style(0, 12, dict(font_name='Arial', font_size=12,
                                       color=(255, 255, 255, 255)))

        self.layout = pyglet.text.layout.ScrollableTextLayout(self.doc,
                                                              width=self.width - 6,
                                                              height=self.height - 6,
                                                              multiline=True,
                                                              # batch=self.lbatch
                                                              )

    def render(self, surface: Surface):
        self.layout.x = 3
        self.layout.y = 3
        # self.layout.view_y = -80

        surface.clear((0, 100, 0, 255))
        # arcade.draw_xywh_rectangle_outline(2, 2, self.width-6, self.height-6, (0, 100, 0, 255), border_width=3)

        with surface.ctx.pyglet_rendering():
            self.layout.draw()

    def on_event(self, event: Event):
        if isinstance(event, MouseScroll):
            if point_in_rect(event.x, event.y, *self.rect()):
                self.layout.view_y += event.scroll_y

class FlatButton(InteractiveWidget):
    def __init__(self, x=0, y=0, width=100, height=50, text="", style=None):
        super().__init__(x, y, width, height)
        self._text = text
        self._style = style or {}

    def render(self, surface: Surface):
        if self.rendered:
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


class BoxLayout(Widget):
    def __init__(self, x=0, y=0, width=100, height=100):
        super().__init__(x, y, width, height)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.rendered = False

        self.register_event_type("on_click")

    def render(self, surface: Surface):
        self.rendered = True

    def on_update(self, dt):
        pass

    def rect(self) -> Tuple[int, int, int, int]:
        """
        Rectangle of the widget
        """
        return self.x, self.y, self.width, self.height

    def on_event(self, event: Event):
        pass
