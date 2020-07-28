from typing import Optional
from uuid import uuid4

import arcade

from arcade.gui import UIClickable
from arcade.gui.ui_style import UIStyle
from arcade.gui.utils import render_text_image


class UIAbstractFlatButton(UIClickable):
    """
    Style attributes:
    * font_name - List of font names
    * font_size
    * font_color
    * font_color_hover
    * font_color_press
    * border_width
    * border_color
    * border_color_hover
    * border_color_press
    * bg_color
    * bg_color_hover
    * bg_color_press
    * vmargin - vertical margin around the text
    """

    def __init__(self,
                 text: str,
                 center_x: int = 0,
                 center_y: int = 0,
                 width: int = None,
                 height: int = None,

                 align="center",
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        """
        :param text:
        :param center_x: center X of element
        :param center_y: center y of element
        :param width:
        :param height:
        :param align:
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

        self.text = text
        self.align = align
        self.width = width
        self.height = height

    def render(self):
        font_name = self.style_attr('font_name', ['Calibri', 'Arial'])
        font_size = self.style_attr('font_size', 12)

        font_color = self.style_attr('font_color', arcade.color.WHITE)
        font_color_hover = self.style_attr('font_color_hover', None)
        if font_color_hover is None:
            font_color_hover = font_color
        font_color_press = self.style_attr('font_color_press', None)
        if font_color_press is None:
            font_color_press = font_color_hover

        border_width = self.style_attr('border_width', 0)
        border_color = self.style_attr('border_color', None)
        border_color_hover = self.style_attr('border_color_hover', None)
        border_color_press = self.style_attr('border_color_press', None)

        bg_color = self.style_attr('bg_color', None)
        bg_color_hover = self.style_attr('bg_color_hover', None)
        bg_color_press = self.style_attr('bg_color_press', None)

        vmargin = self.style_attr('vmargin', 0)
        height = self.height if self.height else font_size + vmargin

        text_image_normal = render_text_image(
            self.text,
            font_size=font_size,
            font_name=font_name,
            align=self.align,
            valign='middle',
            bg_image=None,
            width=int(self.width),
            height=height,
            indent=0,

            font_color=font_color,
            border_width=border_width,
            border_color=border_color,
            bg_color=bg_color,
        )
        text_image_hover = render_text_image(
            self.text,
            font_size=font_size,
            font_name=font_name,
            align=self.align,
            valign='middle',
            bg_image=None,
            width=int(self.width),
            height=height,
            indent=0,

            font_color=font_color_hover,
            border_width=border_width,
            border_color=border_color_hover,
            bg_color=bg_color_hover,
        )
        text_image_press = render_text_image(
            self.text,
            font_size=font_size,
            font_name=font_name,
            align=self.align,
            valign='middle',
            bg_image=None,
            width=int(self.width),
            height=height,
            indent=0,

            font_color=font_color_press,
            border_width=border_width,
            border_color=border_color_press,
            bg_color=bg_color_press,
        )

        self.normal_texture = arcade.Texture(image=text_image_normal, name=str(uuid4()))
        self.hover_texture = arcade.Texture(image=text_image_hover, name=str(uuid4()))
        self.press_texture = arcade.Texture(image=text_image_press, name=str(uuid4()))


class UIFlatButton(UIAbstractFlatButton):
    def __init__(self,
                 text: str,
                 center_x: int = 0,
                 center_y: int = 0,
                 width: int = 0,
                 height: int = 0,
                 align="center",
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        """
        :param text: Text
        :param center_x: center X of element
        :param center_y: center y of element
        :param width: width of element
        :param height: height of element
        :param align: align of text, requires set width
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(text, center_x, center_y, width, height, align, id=id, style=style, **kwargs)
        self.style_classes.append('flatbutton')
        self.render()


class UIGhostFlatButton(UIAbstractFlatButton):
    def __init__(self,
                 text: str,
                 center_x: int = 0,
                 center_y: int = 0,
                 width: int = 0,
                 height: int = 0,
                 align="center",
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
        """
        :param text: Text
        :param center_x: center X of element
        :param center_y: center y of element
        :param width: width of element
        :param height: height of element
        :param align: align of text, requires set width
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(text, center_x, center_y, width, height, align, id=id, style=style, **kwargs)
        self.style_classes.append('ghostflatbutton')
        self.render()
