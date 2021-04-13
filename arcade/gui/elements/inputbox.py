from typing import Optional, Tuple

import arcade
from arcade.gui import text_utils
from arcade.gui.elements import UIClickable
from arcade.gui.events import UIEvent, TEXT_INPUT, TEXT_MOTION
from arcade.gui.style import UIStyle
from arcade.gui.text_utils import Padding
from arcade.key import (
    MOTION_UP,
    MOTION_RIGHT,
    MOTION_DOWN,
    MOTION_LEFT,
    MOTION_END_OF_LINE,
    MOTION_NEXT_PAGE,
    MOTION_PREVIOUS_PAGE,
    MOTION_BEGINNING_OF_FILE,
    MOTION_END_OF_FILE,
    MOTION_BACKSPACE,
    MOTION_DELETE,
    MOTION_BEGINNING_OF_LINE,
)


class _KeyAdapter:
    """
    Handles the text and key inputs, primary storage of text and cursor_index.
    """

    def __init__(self, text=""):
        self._text = text
        self._cursor_index = len(text)
        self.state_changed = True

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if text != self._text:
            self.state_changed = True

        self._text = text

    @property
    def cursor_index(self):
        return self._cursor_index

    @cursor_index.setter
    def cursor_index(self, index):
        if index != self._cursor_index:
            self.state_changed = True

        index = min(len(self.text), index)
        index = max(0, index)

        self._cursor_index = index

    def reset_state_changed(self):
        self.state_changed = False

    def on_ui_event(self, event):
        if event.type == TEXT_INPUT:
            text = event.get("text")
            if text == "\r":
                return

            self.text = (
                self.text[: self.cursor_index] + text + self.text[self.cursor_index :]
            )
            self.cursor_index += len(text)

        elif event.type == TEXT_MOTION:
            motion = event.get("motion")

            if motion == MOTION_UP:
                self.cursor_index = 0
            elif motion == MOTION_RIGHT:
                self.cursor_index += 1
            elif motion == MOTION_DOWN:
                self.cursor_index = len(self.text)
            elif motion == MOTION_LEFT:
                self.cursor_index -= 1
            # elif motion == MOTION_NEXT_WORD:
            #     pass
            # elif motion == MOTION_PREVIOUS_WORD:
            #     pass
            elif motion == MOTION_BEGINNING_OF_LINE:
                self.cursor_index = 0
            elif motion == MOTION_END_OF_LINE:
                self.cursor_index = len(self.text)
            elif motion == MOTION_NEXT_PAGE:
                self.cursor_index = len(self.text)
            elif motion == MOTION_PREVIOUS_PAGE:
                self.cursor_index = 0
            elif motion == MOTION_BEGINNING_OF_FILE:
                self.cursor_index = 0
            elif motion == MOTION_END_OF_FILE:
                self.cursor_index = len(self.text)
            elif motion == MOTION_BACKSPACE:
                self.text = (
                    self.text[: self.cursor_index - 1] + self.text[self.cursor_index :]
                )
                self.cursor_index -= 1
            elif motion == MOTION_DELETE:
                self.text = (
                    self.text[: self.cursor_index] + self.text[self.cursor_index + 1 :]
                )


class UIInputBox(UIClickable):
    """
    Provides an input field for the user. If it gets focus, user clicks on it,
    it will show a cursor and will react to keystrokes, changing the text and cursor position.

    Style attributes:
    * font_name
    * font_size
    * font_color
    * font_color_hover
    * font_color_focus
    * border_width
    * border_color
    * border_color_hover
    * border_color_focus
    * bg_color
    * bg_color_hover
    * bg_color_focus
    * vpadding - Vertical padding around text
    * padding_left
    """

    ENTER = "ENTER"

    def __init__(
        self,
        text="",
        center_x=0,
        center_y=0,
        min_size: Optional[Tuple] = (200, 30),
        size_hint: Optional[Tuple] = None,
        id: Optional[str] = None,
        style: UIStyle = None,
        **kwargs
    ):
        """
        :param center_x: center X of element
        :param center_y: center y of element
        :param width: width of element
        :param height: height of element
        :param text: text
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
        self.register_event_type("on_enter")
        self.style_classes.append("inputbox")

        self.symbol = "|"
        self.text_adapter = _KeyAdapter(text)

        self.normal_texture = None
        self.hover_texture = None
        self.focus_texture = None

        self.render()

    def render(self):
        font_name = self.style_attr("font_name", ["Calibri", "Arial"])
        font_size = self.style_attr("font_size", 22)

        font_color = self.style_attr("font_color", arcade.color.WHITE)
        font_color_hover = self.style_attr("font_color_hover", None)
        font_color_focus = self.style_attr("font_color_focus", None)

        if font_color_hover is None:
            font_color_hover = font_color
        if font_color_focus is None:
            font_color_focus = font_color_hover

        border_width = self.style_attr("border_width", 2)
        border_color = self.style_attr("border_color", arcade.color.WHITE)
        border_color_hover = self.style_attr("border_color_hover", arcade.color.WHITE)
        border_color_focus = self.style_attr("border_color_focus", arcade.color.WHITE)

        bg_color = self.style_attr("bg_color", arcade.color.GRAY)
        bg_color_hover = self.style_attr("bg_color_hover", arcade.color.GRAY)
        bg_color_focus = self.style_attr("bg_color_focus", arcade.color.GRAY)

        # TODO fix overdraw behavior
        # -> textures are growing, but hitbox stays, does not shrink -.-
        v_align = "center"
        h_align = "left"
        padding = Padding(left=border_width)

        # text
        text_image_normal, text_image_normal_uuid = text_utils.create_text(
            text=self.text,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color,
            bg_color=bg_color,
            min_width=self.width,
            min_height=self.height,
            v_align=v_align,
            h_align=h_align,
            padding=padding,
            border_width=border_width,
            border_color=border_color,
        )
        text_image_hover, text_image_hover_uuid = text_utils.create_text(
            text=self.text,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color_hover,
            bg_color=bg_color_hover,
            min_width=self.width,
            min_height=self.height,
            v_align=v_align,
            h_align=h_align,
            padding=padding,
            border_width=border_width,
            border_color=border_color_hover,
        )

        text_with_cursor = (
            self.text[: self.cursor_index]
            + self.symbol
            + self.text[self.cursor_index :]
        )
        text_image_focus, text_image_focus_uuid = text_utils.create_text(
            text=text_with_cursor,
            font_name=font_name,
            font_size=font_size,
            font_color=font_color_focus,
            bg_color=bg_color_focus,
            min_width=self.width,
            min_height=self.height,
            v_align=v_align,
            h_align=h_align,
            padding=padding,
            border_width=border_width,
            border_color=border_color_focus,
        )

        # draw outline
        self.normal_texture = arcade.Texture(
            image=text_image_normal,
            name=text_image_normal_uuid,
            hit_box_algorithm="None",
        )
        self.hover_texture = arcade.Texture(
            image=text_image_hover, name=text_image_hover_uuid, hit_box_algorithm="None"
        )
        self.focus_texture = arcade.Texture(
            image=text_image_focus, name=text_image_focus_uuid, hit_box_algorithm="None"
        )

    @property
    def cursor_index(self):
        """
        Current index of cursor
        """
        return self.text_adapter.cursor_index

    @cursor_index.setter
    def cursor_index(self, value):
        self.text_adapter.cursor_index = value

    @property
    def text(self):
        """
        Stored text
        """
        return self.text_adapter.text

    @text.setter
    def text(self, value):
        self.text_adapter.text = value
        self.render()

    def on_ui_event(self, event: UIEvent):
        super().on_ui_event(event)

        if self.focused:
            if event.type == TEXT_INPUT and event.get("text") == "\r":
                self.dispatch_event("on_enter")
                if self.mng:
                    self.mng.dispatch_ui_event(
                        UIEvent(UIInputBox.ENTER, ui_element=self)
                    )
                return

            self.text_adapter.on_ui_event(event)

        if self.text_adapter.state_changed:
            self.text_adapter.reset_state_changed()
            self.render()
