from dataclasses import dataclass
from typing import Optional, Dict, Union

import arcade
from arcade import Texture, Color
from arcade.gui.nine_patch import NinePatchTexture
from arcade.gui.property import Property, bind, DictProperty
from arcade.gui.widgets import UIInteractiveWidget, Surface
from arcade.gui.style import UIStyleBase, UIStyledWidget
from arcade.text import FontNameOrNames


class UITextureButton(UIInteractiveWidget, UIStyledWidget):
    """
    A button with an image for the face of the button.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float width: width of widget. Defaults to texture width if not specified.
    :param float height: height of widget. Defaults to texture height if not specified.
    :param Texture texture: texture to display for the widget.
    :param Texture texture_hovered: different texture to display if mouse is hovering over button.
    :param Texture texture_pressed: different texture to display if mouse button is pressed while hovering over button.
    :param str text: text to add to the button.
    :param style: style information for the button.
    :param float scale: scale the button, based on the base texture size.
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    """

    text: Optional[str] = Property()  # type: ignore

    _textures: Dict[str, Union[Texture, NinePatchTexture]] = DictProperty()  # type: ignore

    @dataclass
    class UIStyle(UIStyleBase):
        font_size: int = 12
        font_name: FontNameOrNames = ("calibri", "arial")
        font_color: Color = arcade.color.WHITE
        border_width: int = 2

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(

            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            border_width=2,
        ),
        "press": UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.BLACK,
            border_width=2,
        ),
        "disabled": UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            border_width=2,
        )
    }

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: Optional[float] = None,
        height: Optional[float] = None,
        texture: Union[None, Texture, NinePatchTexture] = None,
        texture_hovered: Union[None, Texture, NinePatchTexture] = None,
        texture_pressed: Union[None, Texture, NinePatchTexture] = None,
        texture_disabled: Union[None, Texture, NinePatchTexture] = None,
        text: str = "",
        scale: Optional[float] = None,
        style: Optional[Dict[str, UIStyleBase]] = None,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):

        if width is None and texture is not None:
            width = texture.size[0]

        if height is None and texture is not None:
            height = texture.size[1]

        if scale is not None and texture is not None:
            width = texture.size[0] * scale
            height = texture.size[1] * scale

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            style=style or self.DEFAULT_STYLE,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )

        self._textures = {}

        if texture:
            self._textures["normal"] = texture
        if texture_hovered:
            self._textures["hover"] = texture_hovered
        if texture_pressed:
            self._textures["press"] = texture_pressed
        if texture_disabled:
            self._textures["disabled"] = texture_disabled

        self.text = text

        bind(self, "_textures", self.trigger_render)
        bind(self, "text", self.trigger_render)

    def get_current_state(self) -> str:
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        else:
            return "normal"

    @property
    def texture(self):
        return self._textures["normal"]

    @texture.setter
    def texture(self, value: Texture):
        self._textures["normal"] = value
        self.trigger_render()

    @property
    def texture_hovered(self):
        return self._textures["hover"]

    @texture_hovered.setter
    def texture_hovered(self, value: Texture):
        self._textures["hover"] = value
        self.trigger_render()

    @property
    def texture_pressed(self):
        return self._textures["press"]

    @texture_pressed.setter
    def texture_pressed(self, value: Texture):
        self._textures["press"] = value
        self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        current_state = self.get_current_state()
        current_texture = self._textures.get(current_state)
        if current_texture:
            surface.draw_texture(0, 0, self.width, self.height, current_texture)

        if self.text:
            text_margin = 2
            style = self.get_current_style()

            # border_color = self._style.get("border_color", None)
            # bg_color = self._style.get("bg_color", (21, 19, 21))

            start_x = self.width // 2
            start_y = self.height // 2 + 4

            if self.pressed:
                start_y -= 2

            arcade.draw_text(
                text=self.text,
                start_x=start_x,
                start_y=start_y,
                font_size=style.get("font_size", 15),
                font_name=style.get("font_name", 15),
                color=style.get("font_color", arcade.color.WHITE),
                align="center",
                anchor_x="center",
                anchor_y="center",
                width=self.width - 2 * style.get("border_width", 2) - 2 * text_margin,
            )


class UIFlatButton(UIInteractiveWidget, UIStyledWidget):
    """
    A text button, with support for background color and a border.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float width: width of widget. Defaults to texture width if not specified.
    :param float height: height of widget. Defaults to texture height if not specified.
    :param str text: text to add to the button.
    :param style: Used to style the button

    """

    text = Property("")

    @dataclass
    class UIStyle(UIStyleBase):
        font_size: int = 12
        font_name: FontNameOrNames = ("calibri", "arial")
        font_color: Color = arcade.color.WHITE
        bg: Color = (21, 19, 21)
        border: Optional[Color] = None
        border_width: int = 0

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=(21, 19, 21),
            border=(77, 81, 87),
            border_width=2,
        ),
        "press": UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.BLACK,
            bg=arcade.color.WHITE,
            border=arcade.color.WHITE,
            border_width=2,
        ),
        "disabled": UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=arcade.color.GRAY,
            border=None,
            border_width=2,
        )
    }

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 50,
        text="",
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style=None,
        **kwargs,
    ):
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style or self.DEFAULT_STYLE,
            **kwargs
        )

        self.text = text
        bind(self, "text", self.trigger_render)

    def get_current_state(self) -> str:
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        else:
            return "normal"

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        style = self.get_current_style()

        # Render button
        font_name = style.get("font_name")
        font_size = style.get("font_size")
        font_color = style.get("font_color")

        border_width = style.get("border_width")
        border_color = style.get("border")
        bg_color = style.get("bg")
        if bg_color:
            surface.clear(bg_color)

        # render button border (which is not the widgets border)
        if border_color and border_width:
            arcade.draw_xywh_rectangle_outline(
                border_width,
                border_width,
                self.content_width - 2 * border_width,
                self.content_height - 2 * border_width,
                color=border_color,
                border_width=border_width,
            )

        # render text
        if self.text and font_color:
            start_x = self.content_width // 2
            start_y = self.content_height // 2

            text_margin = 2
            arcade.draw_text(
                text=self.text,
                start_x=start_x,
                start_y=start_y,
                font_name=font_name,
                font_size=font_size,
                color=font_color,
                align="center",
                anchor_x="center",
                anchor_y="center",
                width=self.content_width - 2 * (border_width or 0) - 2 * text_margin,
            )
