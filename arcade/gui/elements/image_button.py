import warnings
from typing import Optional, Tuple

import arcade
from arcade import Texture
from arcade.gui import UIClickable, text_utils
from arcade.gui.style import UIStyle


class UIImageButton(UIClickable):
    def __init__(
        self,
        normal_texture: Texture,
        hover_texture: Optional[Texture] = None,
        press_texture: Optional[Texture] = None,
        text="",
        center_x=0,
        center_y=0,
        # TODO min_size in ImageButton, how to handle this?
        min_size: Optional[Tuple] = None,
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs
    ):
        """
        :param center_x: center X of element
        :param center_y: center y of element
        :param normal_texture: texture shown in normal state
        :param hover_texture: texture shown if hovered
        :param press_texture: texture shown if pressed
        :param text: text drawn on top of textures, only the modified textures are kept
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        if min_size or size_hint:
            warnings.warn(
                "min_size and size_hint not taken in effect, size of the textures is used"
            )

        super().__init__(
            center_x=center_x,
            center_y=center_y,
            min_size=min_size,
            size_hint=size_hint,
            id=id,
            style=style,
            **kwargs
        )
        self.style_classes.append("imagebutton")

        self._normal_texture: Texture = normal_texture
        self._hover_texture: Optional[Texture] = hover_texture
        self._press_texture: Optional[Texture] = press_texture
        self._text = text
        self.write_text(text=text)
        self.set_proper_texture()

    @property
    def normal_texture(self):
        return self._normal_texture

    @normal_texture.setter
    def normal_texture(self, texture: Texture):
        self._normal_texture = texture
        self.write_text(text=self._text)
        self.set_proper_texture()
        # raise Exception("Change texture not supported")

    @property
    def hover_texture(self):
        return self._hover_texture

    @hover_texture.setter
    def hover_texture(self, texture: Texture):
        self._hover_texture = texture
        self.write_text(text=self._text)
        self.set_proper_texture()
        # raise Exception("Change texture not supported")

    @property
    def press_texture(self):
        return self._press_texture

    @press_texture.setter
    def press_texture(self, texture: Texture):
        self._press_texture = texture
        self.write_text(text=self._text)
        self.set_proper_texture()
        # raise Exception("Change texture not supported")

    def render(self):
        self.set_proper_texture()

    def write_text(self, text: str):
        """
        Writes text on top of the normal, hover and press texture.
        The original textures will be replaced by copies with the given text
        :param text: Text to write
        """
        font_name = self.style_attr("font_name", ["Calibri", "Arial"])
        font_size = self.style_attr("font_size", 22)
        font_color = self.style_attr("font_color", arcade.color.GRAY)
        font_color_hover = self.style_attr("font_color_hover", arcade.color.GRAY)
        font_color_press = self.style_attr("font_color_press", arcade.color.GRAY)

        if not font_color_hover:
            font_color_hover = font_color
        if not font_color_press:
            font_color_press = font_color_hover

        normal_image = text_utils.create_raw_text_image(
            text=text,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color,
            bg_image=self._normal_texture.image,
        )
        normal_image_uuid = text_utils.generate_uuid_from_kwargs(
            text=text,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color,
            image=self._normal_texture.image,
        )
        self._normal_texture = Texture(
            self._normal_texture.name + normal_image_uuid, image=normal_image, hit_box_algorithm="None"
        )

        if self._hover_texture:
            hover_image = text_utils.create_raw_text_image(
                text=text,
                font_name=font_name,
                font_size=font_size,
                font_color=font_color_hover,
                bg_image=self._hover_texture.image,
            )
            hover_image_uuid = text_utils.generate_uuid_from_kwargs(
                text=text,
                font_name=font_name,
                font_size=font_size,
                font_color=font_color_hover,
                image=self._hover_texture.image,
            )
            self._hover_texture = Texture(
                self._hover_texture.name + hover_image_uuid, image=hover_image, hit_box_algorithm="None"
            )

        if self._press_texture:
            press_image = text_utils.create_raw_text_image(
                text=text,
                font_name=font_name,
                font_size=font_size,
                font_color=font_color_press,
                bg_image=self._press_texture.image,
            )
            press_image_uuid = text_utils.generate_uuid_from_kwargs(
                text=text,
                font_name=font_name,
                font_size=font_size,
                font_color=font_color_press,
                image=self._press_texture.image,
            )
            self._press_texture = Texture(
                self._press_texture.name + press_image_uuid, image=press_image, hit_box_algorithm="None"
            )
