from typing import Optional, Tuple

import arcade
from arcade.gui import text_utils, UIElement
from arcade.gui.style import UIStyle


class UILabel(UIElement):
    """
    :py:class:`arcade.gui.UIElement` for showing text.
    """

    def __init__(
        self,
        text: str,
        center_x=0,
        center_y=0,
        min_size: Optional[Tuple] = None,
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs
    ):
        """
        :param text: Text to show
        :param center_x: center X of element
        :param center_y: center y of element
        :param width: width, 0 will use the width of the rendered text
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
        self.style_classes.append("label")

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
        font_name = self.style_attr("font_name", ["Calibri", "Arial"])
        font_size = self.style_attr("font_size", 12)
        font_color = self.style_attr("font_color", arcade.color.WHITE)
        border_width = self.style_attr("border_width", 0)
        border_color = self.style_attr("border_color", None)
        bg_color = self.style_attr("bg_color", None)
        v_align = self.style_attr("v_align", "center")
        h_align = self.style_attr("h_align", "center")

        text_image_normal, text_image_normal_uuid = text_utils.create_text(
            text=self.text,
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
        )

        self.texture = arcade.Texture(
            image=text_image_normal,
            name=text_image_normal_uuid,
            hit_box_algorithm="None",
        )
