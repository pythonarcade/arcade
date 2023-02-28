from typing import Iterable, Optional

from PIL import Image, ImageOps
from pyglet.event import EVENT_UNHANDLED

import arcade
from arcade import Window, Texture
from arcade.gui import UIManager, UIWidget, Property, Surface, UIDummy, UIEvent, bind, \
    UIMouseDragEvent, UIMouseScrollEvent, UIMouseEvent, UIBoxLayout, UIFlatButton, UIInputText


class VerboseInputText(UIInputText):

    def on_event(self, event: UIEvent) -> Optional[bool]:
        on_event = super().on_event(event)
        return on_event


class UIScrollArea(UIWidget):
    scroll_x = Property(default=0)
    scroll_y = Property(default=0)
    canvas_size = Property(default=(300, 300))

    scroll_speed = 1.3
    invert_scroll = False

    def __init__(self, *, x: float = 0, y: float = 0, width: float = 300, height: float = 300,
                 children: Iterable["UIWidget"] = tuple(), size_hint=None, size_hint_min=None, size_hint_max=None,
                 **kwargs):
        super().__init__(x=x, y=y, width=width, height=height, children=children, size_hint=size_hint,
                         size_hint_min=size_hint_min, size_hint_max=size_hint_max, **kwargs)
        self.surface = Surface(
            size=(300, 300),
        )

        bind(self, "scroll_x", self.trigger_full_render)
        bind(self, "scroll_y", self.trigger_full_render)

    def _do_render(self, surface: Surface, force=False) -> bool:
        if not self.visible:
            return False

        should_render = force or not self._rendered
        rendered = False

        with self.surface.activate():
            if should_render:
                surface.clear()

            if self.visible:
                for child in self.children:
                    rendered |= child._do_render(self.surface, should_render)

        if should_render or rendered:
            rendered = True
            self.do_render_base(surface)
            self.do_render(surface)
            self._rendered = True

        return rendered

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        width, height = self.content_size

        tex_2d = self.surface.texture
        image = Image.frombytes("RGBA", tex_2d.size, tex_2d.read())
        view = image.crop((self.scroll_x, self.scroll_y, self.scroll_x + width, self.scroll_y + height))
        surface.draw_texture(0, 0, width, height, tex=Texture(ImageOps.flip(view)))

    def on_event(self, event: UIEvent) -> Optional[bool]:

        if isinstance(event, UIMouseDragEvent) and not self.rect.collide_with_point(event.x, event.y):
            return EVENT_UNHANDLED

        # drag scroll area around with middle mouse button
        if isinstance(event, UIMouseDragEvent) and event.buttons & arcade.MOUSE_BUTTON_MIDDLE:
            self.scroll_x -= event.dx
            self.scroll_y -= event.dy
            return True

        if isinstance(event, UIMouseScrollEvent):
            invert = -1 if self.invert_scroll else 1

            self.scroll_x -= event.scroll_x * self.scroll_speed * invert
            self.scroll_y -= event.scroll_y * self.scroll_speed * invert
            return True

        child_event = event
        if isinstance(event, UIMouseEvent):
            child_event = type(event)(**event.__dict__)  # type: ignore
            child_event.x = event.x - self.x + self.scroll_x
            child_event.y = event.y - self.y + self.scroll_y

        on_event = super().on_event(child_event)

        # if isinstance(event, UIMouseEvent):
            # print(f"{on_event=}")
        return on_event


class MyWindow(Window):

    def __init__(self):
        super().__init__()

        self.manager = UIManager()
        self.manager.enable()
        self.background_color = arcade.color.WHITE
        self.input = self.manager.add(VerboseInputText(x=450, y=300).with_border())

        self.scroll_area = UIScrollArea(x=100, y=100).with_border()
        self.manager.add(self.scroll_area)

        anchor = self.scroll_area.add(UIBoxLayout(width=300, height=300, space_between=20))
        anchor.add(UIDummy(height=50))
        anchor.add(UIFlatButton(text="Hello from scroll area", multiline=True))
        anchor.add(UIInputText().with_border())

    def on_draw(self):
        arcade.start_render()
        self.manager.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        self.manager.trigger_render()
        print(self.input.text)


if __name__ == "__main__":
    MyWindow().run()
