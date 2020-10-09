from typing import Optional
from uuid import uuid4

import arcade
from arcade.gui.elements import UIClickable
from arcade.gui.ui_style import UIStyle
from arcade.gui.utils import get_text_image


class UILabel(UIClickable):
    """
    :py:class:`arcade.gui.UIElement` for showing text.
    """
    def __init__(self,
                 text: str,
                 center_x=0,
                 center_y=0,
                 width: int = 0,
                 align='center',
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        """
        :param text: Text to show
        :param center_x: center X of element
        :param center_y: center y of element
        :param width: width, 0 will use the width of the rendered text
        :param align: position of the text, requires a fix width
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
        self.style_classes.append('label')

        self._target_width = width

        self.align = align
        self.text = text
        # self.render already implicitly called through setting text

    @property
    def text(self):
        """
        Text of the label
        """
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.render()

    def render(self):
        font_name = self.style_attr('font_name', ['Calibri', 'Arial'])
        font_size = self.style_attr('font_size', 12)

        font_color = self.style_attr('font_color', arcade.color.GRAY)
        font_color_hover = self.style_attr('font_color_hover', None)
        font_color_press = self.style_attr('font_color_press', None)

        if font_color_hover is None:
            font_color_hover = font_color
        if font_color_press is None:
            font_color_press = font_color_hover

        text_image_normal = get_text_image(text=self.text,
                                           font_color=font_color,
                                           font_size=font_size,
                                           font_name=font_name,
                                           align=self.align,
                                           width=int(self._target_width),
                                           )
        text_image_mouse_over = get_text_image(text=self.text,
                                               font_color=font_color_hover,
                                               font_size=font_size,
                                               font_name=font_name,
                                               align=self.align,
                                               width=int(self._target_width),
                                               )
        text_image_mouse_press = get_text_image(text=self.text,
                                                font_color=font_color_press,
                                                font_size=font_size,
                                                font_name=font_name,
                                                align=self.align,
                                                width=int(self._target_width),
                                                )

        self.normal_texture = arcade.Texture(image=text_image_normal, name=str(uuid4()), hit_box_algorithm="None")
        self.press_texture = arcade.Texture(image=text_image_mouse_press, name=str(uuid4()), hit_box_algorithm="None")
        self.hover_texture = arcade.Texture(image=text_image_mouse_over, name=str(uuid4()), hit_box_algorithm="None")
