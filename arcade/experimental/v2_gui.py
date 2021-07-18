from contextlib import contextmanager
from dataclasses import dataclass
from random import randint, choice
from typing import List, Tuple

from pyglet.event import EventDispatcher

import arcade
from arcade.examples.perf_test.stress_test_draw_shapes import FPSCounter
from arcade.gl import geometry


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

        self.register_event_type("on_click")

    def render(self):
        pass

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
    _press = False

    @property
    def hover(self):
        return self._hover

    @hover.setter
    def hover(self, value):
        self._hover = value

    def on_event(self, event: Event):
        if isinstance(event, MouseMovement):
            self.hover = point_in_rect(event.x, event.y, *self.rect())

        if isinstance(event, MousePress):
            self._press = point_in_rect(event.x, event.y, *self.rect())

        if self._press and isinstance(event, MouseRelease):
            self._press = False
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

    def render(self):
        self.frame += 1
        frame = self.frame % 256
        arcade.draw_xywh_rectangle_filled(*self.rect(), color=(*self.color[:3], frame))

        if self.hover:
            arcade.draw_xywh_rectangle_outline(*self.rect(), color=arcade.color.BATTLESHIP_GREY, border_width=3)


class Surface:
    """
    Holds a FBO and abstracts the drawing on it.
    """

    def __init__(self, ):
        self.window = arcade.get_window()
        self.ctx = self.window.ctx

        self.texture = self.ctx.texture(self.window.get_framebuffer_size(), components=4)
        self.fbo = self.ctx.framebuffer(color_attachments=[self.texture])
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
    def limit(self, x, y, w, h):
        # TODO ask einarf to apply magic
        # self.fbo.scissor = x, y, w, h
        yield self
        # self.fbo.scissor = 0, 0, *self.fbo.size

    def __enter__(self):
        self.fbo.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fbo.__exit__(exc_type, exc_val, exc_tb)

    def draw(self):
        self.texture.use(0)
        self._quad.render(self._program)


class UIManager:
    def __init__(self) -> None:
        self._surface = Surface()
        self.children: List[Widget] = []

    def render(self):
        with self._surface:
            for child in self.children:
                with self._surface.limit(*child.rect()):
                    child.render()

    def on_update(self, time_delta):
        for child in self.children:
            child.on_update(time_delta)

    def draw(self):
        self._surface.draw()

    def on_event(self, event):
        for child in self.children:
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

        size = 100
        for y in range(0, self.height, size):
            for x in range(0, self.width, size):
                button = Button(x, y, size, size)
                self.change_color(button)
                button.on_click = self.change_color
                self.manager.children.append(button)

        print(f"Render {len(self.manager.children)} widgets")

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
        arcade.start_render()
        self.manager.draw()
        arcade.draw_text(f"{self.fps.get_fps():.0f}", self.width // 2, self.height // 2, color=arcade.color.RED,
                         font_size=20)

    def on_update(self, time_delta):
        self.manager.on_update(time_delta)
        self.manager.render()
        self.fps.tick()

    # These can be registered by UIManager
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.manager.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        self.manager.on_mouse_release(x, y, button, modifiers)


window = UIMockup()
arcade.run()
