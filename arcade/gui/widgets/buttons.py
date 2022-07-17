import arcade
from arcade import Texture
from arcade.experimental.uistyle import UIFlatButtonStyle_default
from arcade.gui.property import Property, bind
from arcade.gui.widgets import UIInteractiveWidget, Surface


class UITextureButton(UIInteractiveWidget):
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

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = None,
        height: float = None,
        texture: Texture = None,
        texture_hovered: Texture = None,
        texture_pressed: Texture = None,
        text: str = "",
        scale: float = None,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style=None,
        **kwargs,
    ):

        if width is None and texture is not None:
            width = texture.width

        if height is None and texture is not None:
            height = texture.height

        if scale is not None and texture is not None:
            height = texture.height * scale
            width = texture.width * scale

        super().__init__(
            x,
            y,
            width,
            height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
        )

        self._tex = texture
        self._tex_hovered = texture_hovered
        self._tex_pressed = texture_pressed
        self._style = style or {}
        self._text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.trigger_render()

    @property
    def texture(self):
        return self._tex

    @texture.setter
    def texture(self, value: Texture):
        self._tex = value
        self.trigger_render()

    @property
    def texture_hovered(self):
        return self._tex_hovered

    @texture_hovered.setter
    def texture_hovered(self, value: Texture):
        self._tex_hovered = value
        self.trigger_render()

    @property
    def texture_pressed(self):
        return self._tex_pressed

    @texture_pressed.setter
    def texture_pressed(self, value: Texture):
        self._tex_pressed = value
        self.trigger_render()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)

        tex = self._tex
        if self.pressed and self._tex_pressed:
            tex = self._tex_pressed
        elif self.hovered and self._tex_hovered:
            tex = self._tex_hovered

        if tex:
            surface.draw_texture(0, 0, self.width, self.height, tex)

        if self.text:
            text_margin = 2
            font_size = self._style.get("font_size", 15)
            font_color = self._style.get("font_color", arcade.color.WHITE)
            border_width = self._style.get("border_width", 2)
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
                font_size=font_size,
                color=font_color,
                align="center",
                anchor_x="center",
                anchor_y="center",
                width=self.width - 2 * border_width - 2 * text_margin,
            )


class UIFlatButton(UIInteractiveWidget):
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
        style=UIFlatButtonStyle_default,
        **kwargs,
    ):
        super().__init__(
            x,
            y,
            width,
            height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style
        )

        self.text = text
        bind(self, "text", self.trigger_render)

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        if self.disabled:
            state = "disabled"
        elif self.pressed:
            state = "press"
        elif self.hovered:
            state = "hover"
        else:
            state = "normal"

        style = self.style[state]

        # Render button
        font_name = style.get("font_name")
        font_size = style.get("font_size")
        font_color = style.get("font_color")

        border_width = style.get("border_width")
        border_color = style.get("border")
        if bg_color := style.get("bg"):
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
                font_name=font_name,  # type: ignore
                font_size=font_size,  # type: ignore
                color=font_color,  # type: ignore
                align="center",
                anchor_x="center",
                anchor_y="center",
                width=self.content_width - 2 * (border_width or 0) - 2 * text_margin,
            )
