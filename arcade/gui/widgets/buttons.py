from dataclasses import dataclass
from typing import Optional, Union

from typing_extensions import TypeAlias

import arcade
from arcade import Texture, color, uicolor
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
    """Used to style the texture button. Below is its use case.

    .. code:: py

        button = UITextureButton(style={"normal": UITextureButton.UIStyle(...),})
    """

    font_size: int = 12
    font_name: FontNameOrNames = ("Kenney Future", "arial", "calibri")
    font_color: RGBA255 = uicolor.WHITE


class UITextureButton(UIInteractiveWidget, UIStyledWidget[UITextureButtonStyle], UITextWidget):
    """A button with an image for the face of the button.

    There are four states of the UITextureButton i.e.normal, hovered, pressed and disabled.

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget. Defaults to texture width if not
            specified.
        height: height of widget. Defaults to texture height if not
            specified.
        texture: texture to display for the widget.
        texture_hovered: different texture to display if mouse is
            hovering over button.
        texture_pressed: different texture to display if mouse button is
            pressed while hovering over button.
        text: text to add to the button.
        multiline: allows to wrap text, if not enough width available
        style: Used to style the button for different states.
        scale: scale the button, based on the base texture size.
        size_hint: Tuple of floats (0.0-1.0), how much space of the
            parent should be requested
        size_hint_min: min width and height in pixel
        size_hint_max: max width and height in pixel
    """

    _textures = DictProperty[str, Union[Texture, NinePatchTexture]]()

    UIStyle = UITextureButtonStyle

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            font_color=uicolor.WHITE_CLOUDS,
        ),
        "press": UIStyle(
            font_color=uicolor.DARK_BLUE_MIDNIGHT_BLUE,
        ),
        "disabled": UIStyle(
            font_color=uicolor.WHITE_SILVER,
        ),
    }

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float | None = None,
        height: float | None = None,
        texture: Union[None, Texture, NinePatchTexture] = None,
        texture_hovered: Union[None, Texture, NinePatchTexture] = None,
        texture_pressed: Union[None, Texture, NinePatchTexture] = None,
        texture_disabled: Union[None, Texture, NinePatchTexture] = None,
        text: str = "",
        multiline: bool = False,
        scale: float | None = None,
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

        # prepare label with default style
        _style = self.get_current_style()
        if _style is None:
            raise ValueError(f"No style found for state {self.get_current_state()}")
        self._apply_style(_style)

    def get_current_state(self) -> str:
        """Returns the current state of the button i.e.disabled, press, hover or normal."""
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
        """Render the widgets graphical representation."""
        self.prepare_render(surface)

        style = self.get_current_style()

        # update label
        if style is None:
            raise ValueError(f"No style found for state {self.get_current_state()}")
        self._apply_style(style)

        current_state = self.get_current_state()
        current_texture = self._textures.get(current_state)
        if current_texture:
            surface.draw_texture(0, 0, self.content_width, self.content_height, current_texture)

    def _apply_style(self, style: UITextureButtonStyle):
        """Callback which is called right before rendering to apply changes for rendering."""
        font_name = style.get("font_name", UIFlatButton.UIStyle.font_name)
        font_size = style.get("font_size", UIFlatButton.UIStyle.font_size)
        font_color = style.get("font_color", UIFlatButton.UIStyle.font_color)
        self.ui_label.update_font(font_name, font_size, font_color)

        self.ui_label.rect = self.ui_label.rect.max_size(self.content_width, self.content_height)


@dataclass
class UIFlatButtonStyle(UIStyleBase):
    """Used to style the button. Below is its use case.

    .. code:: py

        button = UIFlatButton(style={"normal": UIFlatButton.UIStyle(...),})
    """

    font_size: int = 12
    font_name: FontNameOrNames = ("Kenney Future", "arial", "calibri")
    font_color: RGBA255 = color.WHITE
    bg: RGBA255 = uicolor.DARK_BLUE_MIDNIGHT_BLUE
    border: RGBA255 | None = None
    border_width: int = 0


class UIFlatButton(UIInteractiveWidget, UIStyledWidget[UIFlatButtonStyle], UITextWidget):
    """A text button, with support for background color and a border.

    There are four states of the UITextureButton i.e. normal, hovered, pressed and disabled.

    Args:
        x: x coordinate of bottom left
        y: y coordinate of bottom left
        width: width of widget. Defaults to texture width if not
            specified.
        height: height of widget. Defaults to texture height if not
            specified.
        text: text to add to the button.
        multiline: allows to wrap text, if not enough width available
        style: Used to style the button
    """

    UIStyle: TypeAlias = UIFlatButtonStyle

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            font_color=color.WHITE,
            bg=uicolor.DARK_BLUE_WET_ASPHALT,
            border=uicolor.GRAY_CONCRETE,
        ),
        "press": UIStyle(
            font_color=uicolor.DARK_BLUE_MIDNIGHT_BLUE,
            bg=uicolor.WHITE_CLOUDS,
            border=uicolor.GRAY_CONCRETE,
        ),
        "disabled": UIStyle(
            font_color=uicolor.WHITE_SILVER,
            bg=uicolor.GRAY_ASBESTOS,
        ),
    }

    STYLE_RED = {
        "normal": UIStyle(
            font_color=uicolor.WHITE_CLOUDS,
            bg=uicolor.RED_ALIZARIN,
            border=uicolor.RED_POMEGRANATE,
        ),
        "hover": UIStyle(
            bg=uicolor.RED_ALIZARIN,
            font_color=uicolor.WHITE_CLOUDS,
            border=uicolor.WHITE_SILVER,
            border_width=2,
        ),
        "press": UIStyle(
            bg=uicolor.RED_POMEGRANATE,
            font_color=uicolor.WHITE_CLOUDS,
            border=uicolor.WHITE_SILVER,
            border_width=2,
        ),
        "disabled": UIStyle(
            bg=uicolor.GRAY_ASBESTOS,
        ),
    }

    STYLE_BLUE = {
        "normal": UIStyle(bg=uicolor.BLUE_PETER_RIVER, font_color=uicolor.WHITE_CLOUDS),
        "hover": UIStyle(
            bg=uicolor.BLUE_BELIZE_HOLE,
            font_color=uicolor.WHITE_CLOUDS,
            border=uicolor.WHITE_SILVER,
            border_width=2,
        ),
        "press": UIStyle(
            bg=uicolor.DARK_BLUE_MIDNIGHT_BLUE,
            font_color=uicolor.WHITE_CLOUDS,
            border=uicolor.WHITE_SILVER,
            border_width=2,
        ),
        "disabled": UIStyle(bg=uicolor.GRAY_ASBESTOS),
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

        # prepare label with default style
        _style = self.get_current_style()
        if _style is None:
            raise ValueError(f"No style found for state {self.get_current_state()}")
        self._apply_style(_style)

    def get_current_state(self) -> str:
        """Returns the current state of the button i.e.disabled, press, hover or normal."""
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        else:
            return "normal"

    def do_render(self, surface: Surface):
        """Render a flat button, graphical representation depends on the current state."""
        self.prepare_render(surface)
        style = self.get_current_style()
        if style is None:
            raise ValueError(f"No style found for state {self.get_current_state()}")

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
        """Callback which is called right before rendering to apply changes for rendering."""
        font_name = style.get("font_name", UIFlatButton.UIStyle.font_name)
        font_size = style.get("font_size", UIFlatButton.UIStyle.font_size)
        font_color = style.get("font_color", UIFlatButton.UIStyle.font_color)
        self.ui_label.update_font(font_name, font_size, font_color)
