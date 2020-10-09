from typing import Optional
from uuid import uuid4

import arcade
from arcade import Texture
from arcade.gui import UIClickable, utils
from arcade.gui.ui_style import UIStyle


class UIImageButton(UIClickable):
    def __init__(self,
                 normal_texture: Texture,
                 hover_texture: Optional[Texture] = None,
                 press_texture: Optional[Texture] = None,
                 center_x=0,
                 center_y=0,
                 text='',
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
        :param text: text drawn on top of image
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            id=id,
            style=style,
            **kwargs
        )
        self.style_classes.append('imagebutton')

        self._normal_texture: Texture = normal_texture
        self._hover_texture: Optional[Texture] = hover_texture
        self._press_texture: Optional[Texture] = press_texture

        self.text = text
        # self.render implicitly called through setting self.text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.render()

    def render(self):
        if self.text:
            self.render_with_text(self.text)
        else:
            self.normal_texture = self._normal_texture
            self.hover_texture = self._hover_texture
            self.press_texture = self._press_texture

    def render_with_text(self, text: str):
        font_size = self.style_attr('font_size', 22)
        font_color = self.style_attr('font_color', arcade.color.GRAY)
        font_color_hover = self.style_attr('font_color_hover', arcade.color.GRAY)
        font_color_press = self.style_attr('font_color_press', arcade.color.GRAY)

        if not font_color_hover:
            font_color_hover = font_color
        if not font_color_press:
            font_color_press = font_color_hover

        normal_image = utils.get_image_with_text(text,
                                                 background_image=self._normal_texture.image,
                                                 font_color=font_color,
                                                 font_size=font_size,
                                                 align='center',
                                                 valign='middle'
                                                 )
        self.normal_texture = Texture(str(uuid4()), image=normal_image)

        if self._hover_texture:
            hover_image = utils.get_image_with_text(text,
                                                    background_image=self._hover_texture.image,
                                                    font_color=font_color_hover,
                                                    font_size=font_size,
                                                    align='center',
                                                    valign='middle'
                                                    )
            self.hover_texture = Texture(str(uuid4()), image=hover_image)

        if self._press_texture:
            press_image = utils.get_image_with_text(text,
                                                    background_image=self._press_texture.image,
                                                    font_color=font_color_press,
                                                    font_size=font_size,
                                                    align='center',
                                                    valign='middle'
                                                    )
            self.press_texture = Texture(str(uuid4()), image=press_image)
