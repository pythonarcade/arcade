from __future__ import annotations

from typing import Optional

import pyglet
from pyglet.event import EVENT_UNHANDLED, EVENT_HANDLED
from pyglet.text.caret import Caret
from pyglet.text.document import AbstractDocument

import arcade
from arcade.gui.events import (
    UIEvent,
    UIMousePressEvent,
    UITextEvent,
    UITextMotionEvent,
    UITextMotionSelectEvent,
    UIMouseEvent,
    UIMouseDragEvent,
    UIMouseScrollEvent,
)
from arcade.gui.property import bind
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIWidget, Rect
from arcade.gui.widgets.layout import UIAnchorLayout
from arcade.types import RGBA255, Color, RGBOrA255, RGB


class UILabel(UIWidget):
    """A simple text label. This widget is meant to display user instructions or
    information. This label supports multiline text.

    If you want to make a scrollable viewing text box, use a
    :py:class:`~arcade.gui.UITextArea`.

    By default, a label will fit its initial content. If the text is changed use
    :py:meth:`~arcade.gui.UILabel.fit_content` to adjust the size.

    :param float x: x position (default anchor is bottom-left).
    :param float y: y position (default anchor is bottom-left).
    :param float width: Width of the label. Defaults to text width if not
                        specified. See
                        :py:meth:`~pyglet.text.layout.TextLayout.content_width`.
    :param float height: Height of the label. Defaults to text height if not
                         specified. See
                         :py:meth:`~pyglet.text.layout.TextLayout.content_height`.
    :param str text: Text displayed on the label.
    :param font_name: A list of fonts to use. Arcade will start at the beginning
                      of the tuple and keep trying to load fonts until success.
    :param float font_size: Font size of font.
    :param RGBA255 text_color: Color of the text.
    :param bool bold: If enabled, the label's text will be in a **bold** style.
    :param bool italic: If enabled, the label's text will be in an *italic*
                        style.
    :param bool stretch: Stretch font style.
    :param str align: Horizontal alignment of text on a line. This only applies
                      if a width is supplied. Valid options include ``"left"``,
                      ``"center"`` or ``"right"``.
    :param float dpi: Resolution of the fonts in the layout. Defaults to 96.
    :param bool multiline: If enabled, a ``\\n`` will start a new line. A
                           :py:class:`~arcade.gui.UITextWidget` with
                           ``multiline`` of True is the same thing as
                           a :py:class:`~arcade.gui.UITextArea`.
    :param size_hint: A tuple of floats between 0 and 1 defining the amount of
                      space of the parent should be requested.
    :param size_hint_min: Minimum size hint width and height in pixel.
    :param size_hint_max: Maximum size hint width and height in pixel.
    :param style: Not used. Labels will have no need for a style; they are too
                  simple (just a text display).
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: Optional[float] = None,
        height: Optional[float] = None,
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: RGBOrA255 = (255, 255, 255, 255),
        bold=False,
        italic=False,
        align="left",
        multiline: bool = False,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        # Use Arcade Text wrapper of pyglet.Label for text rendering
        self.label = arcade.Text(
            start_x=0,
            start_y=0,
            text=text,
            font_name=font_name,
            font_size=font_size,
            color=text_color,
            width=int(width) if width else None,
            bold=bold,
            italic=italic,
            align=align,
            anchor_y="bottom",   # Position text bottom left to fit into scissor
            multiline=multiline, # area
            **kwargs,
        )

        super().__init__(
            x=x,
            y=y,
            width=width or self.label.content_width,
            height=height or self.label.content_height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )

        # Set the label size. If the width or height was given because border
        # and padding can only be applied later, we can avoid ``fit_content``
        # and set with and height separately.
        if width:
            self.label.width = int(width)
        if height:
            self.label.height = int(height)

        bind(self, "rect", self._update_layout)

    def fit_content(self):
        """
        Set the width and height of the label to contain the whole text.
        """
        base_width = self._padding_left + self._padding_right + 2 * self._border_width
        base_height = self._padding_top + self._padding_bottom + 2 * self._border_width

        self.rect = self.rect.resize(
            self.label.content_width + base_width + 1,
            self.label.content_height + base_height + 1,
        )

    @property
    def text(self):
        return self.label.text

    @text.setter
    def text(self, value):
        """
        Update text of the label.

        This triggers a full render to ensure that previous text is cleared out.
        """

        if self.label.text != value:
            self.label.text = value
            self._update_layout()
            self.trigger_full_render()

    def _update_layout(self):
        # Update Pyglet layout size
        layout = self.label
        layout_size = layout.width, layout.height

        if layout_size != self.content_size:
            layout.position = 0, 0, 0  # layout always drawn in scissor box
            layout.width = int(self.content_width)
            layout.height = int(self.content_height)

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        with surface.ctx.pyglet_rendering():
            self.label.draw()


class UITextWidget(UIAnchorLayout):
    """
    Adds the ability to add text to a widget.

    The text can be placed within the widget using
    :py:class:`~arcade.gui.UIAnchorLayout` parameters with
    :py:meth:`~arcade.gui.UITextWidget.place_text`.
    """

    def __init__(self, text: str = "", multiline: bool = False, **kwargs):
        super().__init__(text=text, **kwargs)

        self._label = UILabel(
            text=text,
            multiline=multiline,
            width=1000 if multiline else None
        )  # width 1000 try to prevent line wrap if multiline is enabled

        self.add(self._label)
        self.ui_label.fit_content()

        bind(self, "rect", self.ui_label.fit_content)

    def place_text(self,
                   anchor_x: Optional[str] = None,
                   align_x: float = 0,
                   anchor_y: Optional[str] = None,
                   align_y: float = 0,
                   **kwargs):
        """
        Place widget's text within the widget using
        :py:class:`~arcade.gui.UIAnchorLayout` parameters.
        """
        self.remove(self._label)
        self.add(
            child=self._label,
            anchor_x=anchor_x,
            align_x=align_x,
            anchor_y=anchor_y,
            align_y=align_y,
            **kwargs
        )

    @property
    def text(self):
        """
        Text of the widget. Modifying this repeatedly will cause significant
        lag; calculating glyph position is very expensive.
        """
        return self._label.text

    @text.setter
    def text(self, value):
        self.ui_label.text = value
        self.ui_label.fit_content()
        self.trigger_render()

    @property
    def multiline(self):
        """
        Get or set the multiline mode.

        Newline characters (``"\\n"``) will only be honored when this is set to ``True``.
        If you want a scrollable text widget, please use :py:class:`~arcade.gui.UITextArea`
        instead.
        """
        return self.label.multiline

    @multiline.setter
    def multiline(self, value):
        self.label.multiline = value
        self.ui_label.fit_content()
        self.trigger_render()

    @property
    def ui_label(self) -> UILabel:
        """
        Internal py:class:`~arcade.gui.UILabel` used for rendering the text.
        """
        return self._label

    @property
    def label(self) -> arcade.Text:
        return self._label.label


class UIInputText(UIWidget):
    """
    An input field the user can type text into. This is useful in returning
    string input from the user. A caret is displayed, which the user can move
    around with a mouse or keyboard.

    A mouse drag selects text, a mouse press moves the caret, and keys can move
    around the caret. Arcade confirms that the field is active before allowing
    users to type, so it is okay to have multiple of these.

    :param float x: x position (default anchor is bottom-left).
    :param float y: y position (default anchor is bottom-left).
    :param width: Width of the text field.
    :param height: Height of the text field.
    :param text: Initial text displayed. This can be modified later
                 programmatically or by the user's interaction with the caret.
    :param font_name: A list of fonts to use. Arcade will start at the beginning
                      of the tuple and keep trying to load fonts until success.
    :param font_size: Font size of font.
    :param text_color: Color of the text.
    :param multiline: If enabled, a ``\\n`` will start a new line. A
                      :py:class:`~arcade.gui.UITextWidget`  ``multiline`` of
                      True is the same thing as
                      a :py:class:`~arcade.gui.UITextArea`.
    :param caret_color: RGB color of the caret.
    :param size_hint: A tuple of floats between 0 and 1 defining the amount of
                      space of the parent should be requested.
    :param size_hint_min: Minimum size hint width and height in pixel.
    :param size_hint_max: Maximum size hint width and height in pixel.
    :param style: Style has not been implemented for this widget, however it
                  will be added in the near future.
    """

    # Move layout one pixel into the scissor box so the caret is also shown at
    # position 0.
    LAYOUT_OFFSET = 1

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 24,
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: RGBOrA255 = (0, 0, 0, 255),
        multiline=False,
        caret_color: RGB = (0, 0, 0),
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
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
            **kwargs,
        )

        self._active = False
        self._text_color = text_color if len(text_color) == 4 else (*text_color, 255)

        self.doc: AbstractDocument = pyglet.text.decode_text(text)
        self.doc.set_style(
            0,
            len(text),
            dict(font_name=font_name, font_size=font_size, color=self._text_color),
        )

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.doc, width - self.LAYOUT_OFFSET, height, multiline=multiline
        )
        self.layout.x += self.LAYOUT_OFFSET
        self.caret = Caret(self.layout, color=caret_color)
        self.caret.visible = False

        self._blink_state = self._get_caret_blink_state()

    def _get_caret_blink_state(self):
        """Check whether or not the caret is currently blinking or not."""
        return self.caret.visible and self._active and \
               self.caret._blink_visible

    def on_update(self, dt):
        # Only trigger render if blinking state changed
        current_state = self._get_caret_blink_state()
        if self._blink_state != current_state:
            self._blink_state = current_state
            self.trigger_full_render()

    def on_event(self, event: UIEvent) -> Optional[bool]:
        # If not active, check to activate, return
        if not self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                self._active = True
                self.trigger_full_render()
                self.caret.on_activate()
                self.caret.position = len(self.doc.text)
                return EVENT_UNHANDLED

        # If active check to deactivate
        if self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                x, y = event.x - self.x - self.LAYOUT_OFFSET, event.y - self.y
                self.caret.on_mouse_press(x, y, event.button, event.modifiers)
            else:
                self._active = False
                self.trigger_full_render()
                self.caret.on_deactivate()
                return EVENT_UNHANDLED

        # If active pass all non press events to caret
        if self._active:
            # Act on events if active
            if isinstance(event, UITextEvent):
                self.caret.on_text(event.text)
                self.trigger_full_render()
            elif isinstance(event, UITextMotionEvent):
                self.caret.on_text_motion(event.motion)
                self.trigger_full_render()
            elif isinstance(event, UITextMotionSelectEvent):
                self.caret.on_text_motion_select(event.selection)
                self.trigger_full_render()

            if isinstance(event, UIMouseEvent) and \
               self.rect.collide_with_point(
                event.x, event.y
            ):
                x, y = event.x - self.x - self.LAYOUT_OFFSET, event.y - self.y
                if isinstance(event, UIMouseDragEvent):
                    self.caret.on_mouse_drag(
                        x, y, event.dx, event.dy,
                        event.buttons, event.modifiers
                    )
                    self.trigger_full_render()
                elif isinstance(event, UIMouseScrollEvent):
                    self.caret.on_mouse_scroll(
                        x, y, event.scroll_x, event.scroll_y)
                    self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED

    def _update_layout(self):
        # Update Pyglet layout size
        layout = self.layout
        layout_size = layout.width - self.LAYOUT_OFFSET, layout.height

        if layout_size != self.content_size:
            layout.begin_update()
            layout.width = self.content_width - self.LAYOUT_OFFSET
            layout.height = self.content_height
            layout.end_update()

    @property
    def text(self):
        return self.doc.text

    @text.setter
    def text(self, value):
        self.doc.text = value
        self.trigger_full_render()

    def do_render(self, surface: Surface):
        self._update_layout()
        self.prepare_render(surface)

        with surface.ctx.pyglet_rendering():
            self.layout.draw()


class UITextArea(UIWidget):
    """
    A text area that allows users to view large documents of text by scrolling
    the mouse.

    :param float x: x position (default anchor is bottom-left).
    :param float y: y position (default anchor is bottom-left).
    :param width: Width of the text area.
    :param height: Height of the text area.
    :param text: Initial text displayed.
    :param font_name: A list of fonts to use. Arcade will start at the beginning
                      of the tuple and keep trying to load fonts until success.
    :param font_size: Font size of font.
    :param text_color: Color of the text.
    :param multiline: If enabled, a ``\\n`` will start a new line.
    :param scroll_speed: Speed of mouse scrolling.
    :param size_hint: A tuple of floats between 0 and 1 defining the amount of
                      space of the parent should be requested.
    :param size_hint_min: Minimum size hint width and height in pixel.
    :param size_hint_max: Maximum size hint width and height in pixel.
    :param style: Style has not been implemented for this widget, however it
                  will be added in the near future.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 400,
        height: float = 40,
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: RGBA255 = (255, 255, 255, 255),
        multiline: bool = True,
        scroll_speed: Optional[float] = None,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
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
            **kwargs,
        )

        # Set how fast the mouse scroll wheel will scroll text in the pane.
        # Measured in pixels per 'click'
        self.scroll_speed = (
            scroll_speed if scroll_speed is not None
            else font_size
        )

        self.doc: AbstractDocument = pyglet.text.decode_text(text)
        self.doc.set_style(
            0,
            12,
            dict(
                font_name=font_name,
                font_size=font_size,
                color=Color.from_iterable(text_color),
            ),
        )

        self.layout = pyglet.text.layout.ScrollableTextLayout(
            self.doc,
            width=self.content_width,
            height=self.content_height,
            multiline=multiline,
        )

        # bind(self, "rect", self._update_layout)

    def fit_content(self):
        """
        Set the width and height of the text area to contain the whole text.
        """
        self.rect = Rect(
            self.x,
            self.y,
            self.layout.content_width,
            self.layout.content_height,
        )

    @property
    def text(self):
        return self.doc.text

    @text.setter
    def text(self, value):
        self.doc.text = value
        self.trigger_render()

    def _update_layout(self):
        # Update Pyglet layout size
        layout = self.layout
        layout_size = layout.width, layout.height

        if layout_size != self.content_size:
            layout.begin_update()
            layout.width = self.content_width
            layout.height = self.content_height
            layout.end_update()

    def do_render(self, surface: Surface):
        self._update_layout()
        self.prepare_render(surface)
        with surface.ctx.pyglet_rendering():
            self.layout.draw()

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UIMouseScrollEvent):
            if self.rect.collide_with_point(event.x, event.y):
                self.layout.view_y += event.scroll_y * self.scroll_speed   # type: ignore  # pending https://github.com/pyglet/pyglet/issues/916
                self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED
