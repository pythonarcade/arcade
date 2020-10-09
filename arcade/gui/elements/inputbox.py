from typing import Optional
from uuid import uuid4

from PIL import ImageDraw

import arcade
from arcade.gui import UIEvent, TEXT_INPUT, TEXT_MOTION, UIClickable
from arcade.gui.ui_style import UIStyle
from arcade.gui.utils import get_text_image
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
    MOTION_DELETE, MOTION_BEGINNING_OF_LINE,
)


class _KeyAdapter:
    """
    Handles the text and key inputs, primary storage of text and cursor_index.
    """

    def __init__(self, text=''):
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
            text = event.get('text')
            if text == '\r':
                return

            self.text = self.text[:self.cursor_index] + text + self.text[self.cursor_index:]
            self.cursor_index += len(text)

        elif event.type == TEXT_MOTION:
            motion = event.get('motion')

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
                self.text = self.text[:self.cursor_index - 1] + self.text[self.cursor_index:]
                self.cursor_index -= 1
            elif motion == MOTION_DELETE:
                self.text = self.text[:self.cursor_index] + self.text[self.cursor_index + 1:]


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
    * vmargin - Vertical margin around text
    * margin_left
    """

    ENTER = 'ENTER'

    def __init__(self,
                 center_x=0,
                 center_y=0,
                 width=0,
                 height=0,
                 text='',
                 id: Optional[str] = None,
                 style: UIStyle = None,
                 **kwargs):
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
            id=id,
            style=style,
            **kwargs
        )
        self.register_event_type('on_enter')
        self.style_classes.append('inputbox')

        self.width = width if width is not None else 200
        self.height = height

        self.symbol = '|'
        self.text_adapter = _KeyAdapter(text)

        self.normal_texture = None
        self.hover_texture = None
        self.focus_texture = None

        self.render()

    def render(self):
        font_name = self.style_attr('font_name', ['Calibri', 'Arial'])
        font_size = self.style_attr('font_size', 22)

        font_color = self.style_attr('font_color', arcade.color.WHITE)
        font_color_hover = self.style_attr('font_color_hover', None)
        if font_color_hover is None:
            font_color_hover = font_color
        font_color_focus = self.style_attr('font_color_focus', None)
        if font_color_focus is None:
            font_color_focus = font_color_hover

        border_width = self.style_attr('border_width', 2)
        border_color = self.style_attr('border_color', arcade.color.WHITE)
        border_color_hover = self.style_attr('border_color_hover', arcade.color.WHITE)
        border_color_focus = self.style_attr('border_color_focus', arcade.color.WHITE)

        bg_color = self.style_attr('bg_color', arcade.color.GRAY)
        bg_color_hover = self.style_attr('bg_color_hover', arcade.color.GRAY)
        bg_color_focus = self.style_attr('bg_color_focus', arcade.color.GRAY)

        width = int(self.width)
        vmargin = self.style_attr('vmargin', 0)
        height = self.height if self.height else font_size + vmargin

        align = "left"
        margin_left = self.style_attr('margin_left', 10)

        # text
        text_image_normal = get_text_image(text=self.text,
                                           font_color=font_color,
                                           font_size=font_size,
                                           font_name=font_name,
                                           align=align,
                                           width=width,
                                           height=height,
                                           valign='middle',
                                           indent=margin_left,
                                           background_color=bg_color
                                           )
        text_image_hover = get_text_image(text=self.text,
                                          font_color=font_color_hover,
                                          font_size=font_size,
                                          font_name=font_name,
                                          align=align,
                                          width=width,
                                          height=height,
                                          valign='middle',
                                          indent=margin_left,
                                          background_color=bg_color_hover
                                          )

        text_to_show = self.text[:self.cursor_index] + self.symbol + self.text[self.cursor_index:]
        text_image_focus = get_text_image(text=text_to_show,
                                          font_color=font_color_focus,
                                          font_size=font_size,
                                          font_name=font_name,
                                          align=align,
                                          width=width,
                                          height=height,
                                          valign='middle',
                                          indent=margin_left,
                                          background_color=bg_color_focus
                                          )

        # draw outline
        rect = [0, 0, text_image_normal.width - border_width / 2, text_image_normal.height - border_width / 2]

        if border_color and border_width:
            d = ImageDraw.Draw(text_image_normal)
            d.rectangle(rect, fill=None, outline=border_color, width=border_width)

        if border_color_hover:
            d = ImageDraw.Draw(text_image_hover)
            d.rectangle(rect, fill=None, outline=border_color_hover, width=border_width)

        if border_color_focus:
            d = ImageDraw.Draw(text_image_focus)
            d.rectangle(rect, fill=None, outline=border_color_focus, width=border_width)

        self.normal_texture = arcade.Texture(image=text_image_normal, name=str(uuid4()))
        self.hover_texture = arcade.Texture(image=text_image_hover, name=str(uuid4()))
        self.focus_texture = arcade.Texture(image=text_image_focus, name=str(uuid4()))

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
            if event.type == TEXT_INPUT and event.get('text') == '\r':
                self.dispatch_event('on_enter')
                if self.mng:
                    self.mng.dispatch_ui_event(UIEvent(UIInputBox.ENTER, ui_element=self))
                return

            self.text_adapter.on_ui_event(event)

        if self.text_adapter.state_changed:
            self.text_adapter.reset_state_changed()
            self.render()
