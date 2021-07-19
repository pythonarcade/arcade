from contextlib import contextmanager
from dataclasses import dataclass
from random import randint, choice
from typing import List, Tuple

from pyglet.event import EventDispatcher

import arcade
from arcade import Color
from arcade.examples.perf_test.stress_test_draw_shapes import FPSCounter
from arcade.gl import geometry, Framebuffer


def point_in_rect(x, y, rx, ry, rw, rh):
    return rx < x < rx + rw and ry < y < ry + rh


class Event:
    pass


@dataclass
class MouseMovement(Event):
    x: float
    y: float
    dx: float
    dy: float


@dataclass
class MousePress(Event):
    x: float
    y: float
    button: int
    modifiers: int


@dataclass
class MouseRelease(Event):
    x: float
    y: float
    button: int
    modifiers: int


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

    def render(self, surface: "Surface"):
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

    def render(self, surface: "Surface"):
        self.frame += 1
        frame = self.frame % 256
        surface.clear((*self.color[:3], frame))

        if self.hover:
            arcade.draw_xywh_rectangle_outline(0, 0,
                                               self.width, self.height,
                                               color=arcade.color.BATTLESHIP_GREY,
                                               border_width=3)


class FlatButton(InteractiveWidget):
    def __init__(self, x=0, y=0, width=100, height=50, text="", style=None):
        super().__init__(x, y, width, height)
        self._text = text
        self._style = style or {}

    def render(self, surface: "Surface"):
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
            arcade.draw_xywh_rectangle_filled(*self.rect(), color=bg_color)

        # render border
        if border_color and border_width:
            x, y, w, h = self.rect()
            arcade.draw_xywh_rectangle_outline(
                x + border_width,
                y + border_width,
                w - 2 * border_width,
                h - 2 * border_width,
                color=border_color,
                border_width=border_width)

        # render text
        text_margin = 2
        if self.text:
            start_x = self.x + self.width // 2
            start_y = self.y + self.height // 2

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

    def render(self, surface: "Surface"):
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


class Surface:
    """
    Holds a FBO and abstracts the drawing on it.
    """

    def __init__(self):
        self.window = arcade.get_window()
        self.ctx = self.window.ctx

        self.texture = self.ctx.texture(self.window.get_framebuffer_size(), components=4)
        self.fbo: Framebuffer = self.ctx.framebuffer(color_attachments=[self.texture])
        self.fbo.clear()

        # fullscreen quad geometry
        self._quad = geometry.quad_2d_fs()
        self._program = self.ctx.program(
            vertex_shader="""
                    #version 330
                    in vec2 in_vert;
                    in vec2 in_uv;
                    out vec2 uv;
                    void main() {
                        gl_Position = vec4(in_vert, 0.0, 1.0);
                        uv = in_uv;                
                    }
                    """,
            fragment_shader="""
                    #version 330
                    uniform sampler2D ui_texture;
                    in vec2 uv;
                    out vec4 fragColor;
                    void main() {
                        fragColor = texture(ui_texture, uv);
                    }
                    """,
        )
        self.frame = 0

    @contextmanager
    def activate(self):
        """
        Save and restore projection and viewport, activate Surface Buffer to draw on.
        """
        with self.fbo.activate():
            proj = self.ctx.projection_2d
            view = self.fbo.ctx.viewport
            yield self

        self.fbo.viewport = view
        self.ctx.projection_2d = proj

    def clear(self, color: Color = arcade.color.BLACK):
        self.fbo.clear(color=color)

    def limit(self, x, y, width, height):
        """Reduces the draw area to the given rect"""
        self.fbo.viewport = x, y, width, height
        self.ctx.projection_2d = 0, width, 0, height

    def draw(self):
        """Draws the current buffer on screen"""
        self.texture.use(0)
        self._quad.render(self._program)


class UIManager:
    def __init__(self) -> None:
        self._surface = Surface()
        self._children: List[Widget] = []

    def add(self, widget: Widget) -> Widget:
        self._children.append(widget)
        return widget

    def render(self):
        with self._surface.activate():
            for child in self._children:
                self._surface.limit(*child.rect())
                child.render(self._surface)

    def on_update(self, time_delta):
        for child in self._children:
            child.on_update(time_delta)

    def draw(self):
        self._surface.draw()

    def on_event(self, event):
        for child in self._children:
            if child.on_event(event):
                # child can consume an event by returning True
                break

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.on_event(MouseMovement(x, y, dx, dy))

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.on_event(MousePress(x, y, button, modifiers))

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.on_event(MouseRelease(x, y, button, modifiers))


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Mockup")
        self.manager = UIManager()
        self.fps = FPSCounter()

        size = 50
        for y in range(0, self.height, size):
            for x in range(0, self.width, size):
                button = Button(x, y, size, size)
                self.change_color(button)
                button.on_click = self.change_color
                self.manager.add(button)

        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # for y in range(0, self.height, 40):
        #     for x in range(0, self.width, 90):
        #         self.manager.add(
        #             FlatButton(x, y, 80, 30, text="Hello", style={"font_size": 10})
        #         ).on_click = self.on_button_click

        print(f"Render {len(self.manager._children)} widgets")

    def on_button_click(self, button, *args):
        print(button)

    def change_color(self, button: Button, *args):
        colors = [arcade.color.RED,
                  arcade.color.BLACK,
                  arcade.color.GREEN,
                  arcade.color.BLUE,
                  arcade.color.YELLOW,
                  arcade.color.BAZAAR]
        colors.remove(button.color)
        button.color = choice(colors)

    def on_draw(self):
        self.fps.tick()
        arcade.start_render()
        self.manager.draw()
        arcade.draw_text(f"{self.fps.get_fps():.0f}", self.width // 2, self.height // 2, color=arcade.color.RED,
                         font_size=20)

    def on_update(self, time_delta):
        self.manager.on_update(time_delta)
        self.manager.render()

    # TODO These can be registered by UIManager
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_release(x, y, button, modifiers)


window = UIMockup()
arcade.run()
