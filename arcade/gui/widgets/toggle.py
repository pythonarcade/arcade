from PIL import ImageEnhance
from arcade.gui.surface import Surface

from arcade.gui.events import UIOnClickEvent, UIOnChangeEvent

from arcade import Texture
from arcade.gui.property import Property, bind

from arcade.gui.widgets import UIInteractiveWidget


class UITextureToggle(UIInteractiveWidget):
    """
    A toggel button switching between on (True) and off (False) state.

    on_texture and off_texture are required.
    """

    # Experimental ui class
    value: bool = Property(False)  # type: ignore

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 50,
        on_texture: Texture = None,
        off_texture: Texture = None,
        value=False,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style=None,
        **kwargs
    ):
        # Generate hover and pressed texture by changing the brightness
        if on_texture is None:
            raise ValueError("You have to provide a `on_texture`")
        self.normal_on_tex = on_texture
        enhancer = ImageEnhance.Brightness(self.normal_on_tex.image)
        self.hover_on_tex = Texture(
            name=self.normal_on_tex.name + "_brighter", image=enhancer.enhance(1.5)
        )
        self.pressed_on_tex = Texture(
            name=self.normal_on_tex.name + "_darker", image=enhancer.enhance(0.5)
        )

        if off_texture is None:
            raise ValueError("You have to provide a `off_texture`")
        self.normal_off_tex = off_texture
        enhancer = ImageEnhance.Brightness(self.normal_off_tex.image)
        self.hover_off_tex = Texture(
            name=self.normal_off_tex.name + "_brighter", image=enhancer.enhance(1.5)
        )
        self.pressed_off_tex = Texture(
            name=self.normal_off_tex.name + "_darker", image=enhancer.enhance(0.5)
        )

        self.value = value
        self.register_event_type("on_change")

        bind(self, "value", self.trigger_render)
        bind(self, "value", self._dispatch_on_change_event)

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style,
            **kwargs
        )

    def _dispatch_on_change_event(self):
        self.dispatch_event(
            "on_change", UIOnChangeEvent(self, not self.value, self.value)
        )

    def on_click(self, event: UIOnClickEvent):
        self.value = not self.value

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        tex = self.normal_on_tex if self.value else self.normal_off_tex
        if self.pressed:
            tex = self.pressed_on_tex if self.value else self.pressed_off_tex
        elif self.hovered:
            tex = self.hover_on_tex if self.value else self.hover_off_tex
        surface.draw_texture(0, 0, self.width, self.height, tex)

    def on_change(self, event: UIOnChangeEvent):
        pass
