from typing import Optional
from uuid import uuid4

from PIL import Image, ImageDraw

from arcade import Texture
from arcade.gui import UIClickable
from arcade.gui.ui_style import UIStyle


class UIAbstractToggle(UIClickable):
    _value: bool
    _true_texture: Optional[Texture]
    _false_texture: Optional[Texture]

    def __init__(
            self,
            value: bool = True,
            center_x: int = 0,
            center_y: int = 0,
            **kwargs):
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            **kwargs
        )

        self.register_event_type('on_toggle')

        self._value = value

    @property
    def value(self) -> bool:
        """
        current value
        """
        return self._value

    @value.setter
    def value(self, value: bool):
        self._value = value
        self.dispatch_event('on_toggle', value)
        self.set_proper_texture()

    def set_proper_texture(self):
        preserve_scale = self.scale

        if self.value:
            self.texture = self._true_texture
        else:
            self.texture = self._false_texture

        self.scale = preserve_scale

    def toggle(self):
        """
        Toggles current value (True => False, False => True)
        """
        self.value = not self.value

    def on_click(self):
        self.value = not self.value

    def on_toggle(self, value):
        """
        Called if value changes through programmatic change or user interaction.
        """
        pass


class UIImageToggle(UIAbstractToggle):
    """
    A toggle which can be `true` or `false`.

    Switches between two images. Useful for switches like fullscreen or sound mute/unmute.
    """

    def __init__(self,
                 true_texture: Texture,
                 false_texture: Texture,
                 center_x: int = 0,
                 center_y: int = 0,
                 value: bool = True,
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        """
        :param true_texture: displayed if value is True
        :param false_texture: displayed if value is False
        :param center_x: center X of element
        :param center_y: center y of element
        :param value: initial value
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            value=value,
            id=id,
            style=style,
            **kwargs)
        self.style_classes.append('image-toggle')

        self._true_texture = true_texture
        self._false_texture = false_texture

        self.set_proper_texture()

    def render(self):
        self.set_proper_texture()


class UIToggle(UIAbstractToggle):
    """
    A toggle which can be `true` or `false`.

    Style attributes:
    * color_true: color of the lever when value is `true`
    * bg_color_true: color of the background when value is `true`
    * color_false: color of the lever when value is `false`
    * bg_color_false: color of the background when value is `false`
    """

    def __init__(self,
                 center_x: int = 0,
                 center_y: int = 0,
                 height: int = 0,
                 value: bool = True,
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        """
        :param center_x: center X of element
        :param center_y: center y of element
        :param height: height of element, width depends on height
        :param value: initial value
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            value=value,
            id=id,
            style=style,
            **kwargs
        )
        self.style_classes.append('toggle')
        self._height = height

        self.render()

    @staticmethod
    def _round_corner(radius, fill):
        """Draw a round corner"""
        corner = Image.new('RGBA', (radius, radius), (0, 0, 0, 0))
        draw = ImageDraw.Draw(corner)
        draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
        return corner

    @staticmethod
    def _round_rectangle(size, radius, fill):
        """Draw a rounded rectangle"""
        width, height = size
        rectangle = Image.new('RGBA', size, fill)
        corner = UIToggle._round_corner(radius, fill)
        rectangle.paste(corner, (0, 0))
        rectangle.paste(corner.rotate(90), (0, height - radius))  # Rotate the corner and paste it
        rectangle.paste(corner.rotate(180), (width - radius, height - radius))
        rectangle.paste(corner.rotate(270), (width - radius, 0))
        return rectangle

    def _render_toggle(self, right: bool, color, bg_color) -> Texture:
        height = self._height
        width = self._height * 2

        border_radius = height // 2
        radius = height * 0.42
        padding = radius * 0.16
        pos_y = height // 2
        pos_x = width - radius - padding if right else radius + padding

        # Scale to look pretty
        SCALE = 2
        width *= SCALE
        height *= SCALE
        border_radius *= SCALE
        radius *= SCALE
        padding *= SCALE
        pos_x *= SCALE
        pos_y *= SCALE

        # False
        switch = UIToggle._round_rectangle((width, height), border_radius, bg_color)
        d = ImageDraw.Draw(switch)
        d.ellipse((pos_x - radius, pos_y - radius, pos_x + radius, pos_y + radius), fill=color)
        switch = switch.resize((switch.width // SCALE, switch.height // SCALE), resample=Image.LANCZOS)
        return Texture(name=str(uuid4()), image=switch)

    def render(self):
        color_true = self.style_attr('color_true')
        bg_color_true = self.style_attr('bg_color_true')
        self._true_texture = self._render_toggle(True, color_true, bg_color_true)

        color_false = self.style_attr('color_false')
        bg_color_false = self.style_attr('bg_color_false')
        self._false_texture = self._render_toggle(False, color_false, bg_color_false)

        self.set_proper_texture()
