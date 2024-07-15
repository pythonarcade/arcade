from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

import arcade
from arcade import Texture
from arcade.gui.nine_patch import NinePatchTexture
from arcade.gui.property import DictProperty, bind
from arcade.gui.style import UIStyleBase, UIStyledWidget
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIInteractiveWidget
from arcade.gui.widgets.text import UITextWidget
from arcade.text import FontNameOrNames
from arcade.types import RGBA255


@dataclass
class UITextureButtonStyle(UIStyleBase):
    """
    Used to style the texture button. Below is its use case.

    .. code:: py

        button = UITextureButton(style={"normal": UITextureButton.UIStyle(...),})
    """

    font_size: int = 12
    font_name: FontNameOrNames = ("calibri", "arial")
    font_color: RGBA255 = arcade.color.WHITE
    border_width: int = 2


class UITextureButton(UIInteractiveWidget, UIStyledWidget[UITextureButtonStyle], UITextWidget):
    """
    A button with an image for the face of the button.

    There are four states of the UITextureButton i.e normal, hovered, pressed and disabled.

    :param x: x coordinate of bottom left
    :param y: y coordinate of bottom left
    :param width: width of widget. Defaults to texture width if not specified.
    :param height: height of widget. Defaults to texture height if not specified.
    :param texture: texture to display for the widget.
    :param texture_hovered: different texture to display if mouse is hovering over button.
    :param texture_pressed: different texture to display if mouse button is pressed
        while hovering over button.
    :param text: text to add to the button.
    :param multiline: allows to wrap text, if not enough width available
    :param style: Used to style the button for different states.
    :param scale: scale the button, based on the base texture size.
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    """

    _textures: dict[str, Union[Texture, NinePatchTexture]] = DictProperty()  # type: ignore

    UIStyle = UITextureButtonStyle

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
        ),
    }

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: Optional[float] = None,
        height: Optional[float] = None,
        texture: Union[None, Texture, NinePatchTexture] = None,
        texture_hovered: Union[None, Texture, NinePatchTexture] = None,
        texture_pressed: Union[None, Texture, NinePatchTexture] = None,
        texture_disabled: Union[None, Texture, NinePatchTexture] = None,
        text: str = "",
        multiline: bool = False,
        scale: Optional[float] = None,
        style: Optional[dict[str, UIStyleBase]] = None,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        if width is None and texture is not None:
            width = texture.size[0]

        if height is None and texture is not None:
            height = texture.size[1]

        if width is None:
            raise ValueError("Unable to determine a width.")
        if height is None:
            raise ValueError("Unable to determine a height.")

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
            text=text,
            multiline=multiline,
            **kwargs,
        )

        self._textures = {}

        if texture:
            self._textures["normal"] = texture
            self._textures["hover"] = texture
            self._textures["press"] = texture
            self._textures["disabled"] = texture
        if texture_hovered:
            self._textures["hover"] = texture_hovered
        if texture_pressed:
            self._textures["press"] = texture_pressed
        if texture_disabled:
            self._textures["disabled"] = texture_disabled

        bind(self, "_textures", self.trigger_render)

    def get_current_state(self) -> str:
        """Returns the current state of the button i.e disabled, press, hover or normal."""
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
        """Returns the normal texture for the face of the button."""
        return self._textures["normal"]

    @texture.setter
    def texture(self, value: Texture):
        self._textures["normal"] = value
        self.trigger_render()

    @property
    def texture_hovered(self):
        """Returns the hover texture for the face of the button."""
        return self._textures["hover"]

    @texture_hovered.setter
    def texture_hovered(self, value: Texture):
        self._textures["hover"] = value
        self.trigger_render()

    @property
    def texture_pressed(self):
        """Returns the pressed texture for the face of the button."""
        return self._textures["press"]

    @texture_pressed.setter
    def texture_pressed(self, value: Texture):
        self._textures["press"] = value
        self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        style = self.get_current_style()

        # update label
        self._apply_style(style)

        current_state = self.get_current_state()
        current_texture = self._textures.get(current_state)
        if current_texture:
            surface.draw_texture(0, 0, self.content_width, self.content_height, current_texture)

    def _apply_style(self, style: UITextureButtonStyle):
        """
        Callback which is called right before rendering to apply changes for rendering.
        """
        font_name = style.get("font_name", UIFlatButton.UIStyle.font_name)
        font_size = style.get("font_size", UIFlatButton.UIStyle.font_size)
        font_color = style.get("font_color", UIFlatButton.UIStyle.font_color)
        self.ui_label.update_font(font_name, font_size, font_color)

        self.ui_label.rect = self.ui_label.rect.max_size(self.content_width, self.content_height)


class UIFlatButton(UIInteractiveWidget, UIStyledWidget, UITextWidget):
    """
    A text button, with support for background color and a border.

    There are four states of the UITextureButton i.e normal, hovered, pressed and disabled.

    :param x: x coordinate of bottom left
    :param y: y coordinate of bottom left
    :param width: width of widget. Defaults to texture width if not specified.
    :param height: height of widget. Defaults to texture height if not specified.
    :param text: text to add to the button.
    :param multiline: allows to wrap text, if not enough width available
    :param style: Used to style the button

    """

    @dataclass
    class UIStyle(UIStyleBase):
        """
        Used to style the button. Below is its use case.

        .. code:: py

            button = UIFlatButton(style={"normal": UIFlatButton.UIStyle(...),})
        """

        font_size: int = 12
        font_name: FontNameOrNames = ("calibri", "arial")
        font_color: RGBA255 = arcade.color.WHITE
        bg: RGBA255 = (21, 19, 21, 255)
        border: Optional[RGBA255] = None
        border_width: int = 0

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            font_size=12,
            font_name=("calibri", "arial"),
            font_color=arcade.color.WHITE,
            bg=(21, 19, 21, 255),
            border=(77, 81, 87, 255),
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
        ),
    }

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 50,
        text="",
        multiline=False,
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
            text=text,
            multiline=multiline,
            **kwargs,
        )

    def get_current_state(self) -> str:
        """Returns the current state of the button i.e disabled, press, hover or normal."""
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
        style: UIFlatButton.UIStyle = self.get_current_style()

        # update label
        # this might trigger another render run, due to label size change
        self._apply_style(style)

        # Render button
        border_width = style.get("border_width", UIFlatButton.UIStyle.border_width)
        border_color = style.get("border", UIFlatButton.UIStyle.border)
        bg_color = style.get("bg", UIFlatButton.UIStyle.bg)
        if bg_color:
            surface.clear(bg_color)

        # render button border (which is not the widgets border)
        if border_color and border_width:
            arcade.draw_lbwh_rectangle_outline(
                border_width,
                border_width,
                self.content_width - 2 * border_width,
                self.content_height - 2 * border_width,
                color=border_color,
                border_width=border_width,
            )

    def _apply_style(self, style: UIStyle):
        """
        Callback which is called right before rendering to apply changes for rendering.
        """
        font_name = style.get("font_name", UIFlatButton.UIStyle.font_name)
        font_size = style.get("font_size", UIFlatButton.UIStyle.font_size)
        font_color = style.get("font_color", UIFlatButton.UIStyle.font_color)
        self.ui_label.update_font(font_name, font_size, font_color)
