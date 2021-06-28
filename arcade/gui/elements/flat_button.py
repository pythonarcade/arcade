from typing import Optional, Tuple

import arcade
from arcade.gui import UIClickable, text_utils
from arcade.gui.style import UIStyle


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
    * vpadding - vertical padding around the text
    """

    def __init__(
        self,
        text: str,
        center_x: int = 0,
        center_y: int = 0,
        min_size: Optional[Tuple] = None,
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs
    ):
        """
        :param text:
        :param center_x: center X of element
        :param center_y: center y of element
        :param align:
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(
            center_x=center_x,
            center_y=center_y,
            min_size=min_size,
            size_hint=size_hint,
            id=id,
            style=style,
            **kwargs
        )

        self._text = text

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
        font_name = self.style_attr("font_name", ["Calibri", "Arial"])
        font_size = self.style_attr("font_size", 12)

        font_color = self.style_attr("font_color", arcade.color.WHITE)
        font_color_hover = self.style_attr("font_color_hover", None)
        if font_color_hover is None:
            font_color_hover = font_color
        font_color_press = self.style_attr("font_color_press", None)
        if font_color_press is None:
            font_color_press = font_color_hover

        border_width = self.style_attr("border_width", 0)
        border_color = self.style_attr("border_color", None)
        border_color_hover = self.style_attr("border_color_hover", None)
        border_color_press = self.style_attr("border_color_press", None)

        bg_color = self.style_attr("bg_color", None)
        bg_color_hover = self.style_attr("bg_color_hover", None)
        bg_color_press = self.style_attr("bg_color_press", None)

        v_align = self.style_attr("v_align", "center")
        h_align = self.style_attr("h_align", "center")

        # Process padding
        padding_value = self.style_attr("padding", 0)
        if padding_value:
            padding: text_utils.Padding = text_utils.Padding(padding_value, padding_value, padding_value, padding_value)
        else:
            padding: text_utils.Padding = text_utils.Padding(0, 0, 0, 0)

        padding_value = self.style_attr("padding_left", None)
        if padding_value is not None:
            padding.left = padding_value

        padding_value = self.style_attr("padding_right", None)
        if padding_value is not None:
            padding.right = padding_value

        padding_value = self.style_attr("padding_top", None)
        if padding_value is not None:
            padding.top = padding_value

        padding_value = self.style_attr("padding_bottom", None)
        if padding_value is not None:
            padding.bottom = padding_value

        text_image_normal, text_image_normal_uuid = text_utils.create_text(
            text=self._text,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color,
            bg_color=bg_color,
            min_width=self.width - border_width,
            min_height=self.height - border_width,
            v_align=v_align,
            h_align=h_align,
            border_width=border_width,
            border_color=border_color,
            padding=padding,
        )
        text_image_hover, text_image_hover_uuid = text_utils.create_text(
            text=self.text,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color_hover,
            bg_color=bg_color_hover,
            min_width=self.width - border_width,
            min_height=self.height - border_width,
            v_align=v_align,
            h_align=h_align,
            border_width=border_width,
            border_color=border_color_hover,
            padding=padding,
        )
        text_image_press, text_image_press_uuid = text_utils.create_text(
            text=self.text,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color_press,
            bg_color=bg_color_press,
            min_width=self.width - border_width,
            min_height=self.height - border_width,
            v_align=v_align,
            h_align=h_align,
            border_width=border_width,
            border_color=border_color_press,
            padding=padding,
        )

        self.normal_texture = arcade.Texture(
            image=text_image_normal,
            name=text_image_normal_uuid,
            hit_box_algorithm="None",
        )
        self.hover_texture = arcade.Texture(
            image=text_image_hover,
            name=text_image_hover_uuid,
            hit_box_algorithm="None",
        )
        self.press_texture = arcade.Texture(
            image=text_image_press,
            name=text_image_press_uuid,
            hit_box_algorithm="None",
        )


class UIFlatButton(UIAbstractFlatButton):
    def __init__(
        self,
        text: str,
        center_x: int = 0,
        center_y: int = 0,
        min_size: Optional[Tuple] = None,
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs
    ):
        """
        :param text: Text
        :param center_x: center X of element
        :param center_y: center y of element
        :param min_size: min_size of the element
        :param size_hint: size_hint to grow/shrink within UILayout
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(
            text,
            center_x=center_x,
            center_y=center_y,
            min_size=min_size,
            size_hint=size_hint,
            id=id,
            style=style,
            **kwargs
        )
        self.style_classes.append("flatbutton")
        self.render()


class UIGhostFlatButton(UIAbstractFlatButton):
    def __init__(
        self,
        text: str,
        center_x: int = 0,
        center_y: int = 0,
        min_size: Optional[Tuple] = None,
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs
    ):
        """
        :param text: Text
        :param center_x: center X of element
        :param center_y: center y of element
        :param min_size: min_size of the element
        :param size_hint: size_hint to grow/shrink within UILayout
        :param id: id of :py:class:`arcade.gui.UIElement`
        :param style: style of :py:class:`arcade.gui.UIElement`
        :param kwargs: catches unsupported named parameters
        """
        super().__init__(
            text,
            center_x=center_x,
            center_y=center_y,
            min_size=min_size,
            size_hint=size_hint,
            id=id,
            style=style,
            **kwargs
        )
        self.style_classes.append("ghostflatbutton")
        self.render()
