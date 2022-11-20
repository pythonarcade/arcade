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
from arcade.gui.widgets import UIWidget, Surface, Rect


class UILabel(UIWidget):
    """A simple text label. Also supports multiline text.
    In case you want to scroll text use a :class:`UITextArea`
    By default a :class:`UILabel` will fit its initial content,
    if the text changed use :meth:`UILabel.fit_content` to adjust the size.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param float width: width of widget. Defaults to text width if not specified.
    :param float height: height of widget. Defaults to text height if not specified.
    :param str text: text of the label.
    :param font_name: a list of fonts to use. Program will start at the beginning of the list
                      and keep trying to load fonts until success.
    :param float font_size: size of font.
    :param arcade.Color text_color: Color of font.
    :param bool bold: Bold font style.
    :param bool italic: Italic font style.
    :param bool stretch: Stretch font style.
    :param str align: Horizontal alignment of text on a line, only applies if a width is supplied.
                      One of ``"left"``, ``"center"`` or ``"right"``.
    :param float dpi: Resolution of the fonts in this layout.  Defaults to 96.
    :param bool multiline: if multiline is true, a \\n will start a new line.
                           A UITextWidget with multiline of true is the same thing as UITextArea.

    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: Not used.
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
        text_color: arcade.Color = (255, 255, 255, 255),
        bold=False,
        italic=False,
        stretch=False,
        align="left",
        dpi=None,
        multiline: bool = False,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        # Use Pyglet's Label for text rendering
        self.layout = pyglet.text.Label(
            text=text,
            font_name=font_name,
            font_size=font_size,
            color=arcade.get_four_byte_color(text_color),
            width=None,
            height=None,
            bold=bold,
            italic=italic,
            stretch=stretch,
            align=align,
            anchor_y="bottom",  # position text bottom left, to fit into scissor box
            dpi=dpi,
            multiline=multiline,
            **kwargs,
        )

        super().__init__(
            x=x,
            y=y,
            width=width or self.layout.content_width,
            height=height or self.layout.content_height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )

        self.layout.width = width
        self.layout.height = height

        bind(self, "rect", self._update_layout)

    def fit_content(self):
        """
        Sets the width and height of this UIWidget to contain the whole text.
        """
        base_width = self._padding_left + self._padding_right + 2 * self._border_width
        base_height = self._padding_top + self._padding_bottom + 2 * self._border_width

        self.rect = self.rect.resize(
            self.layout.content_width + base_width,
            self.layout.content_height + base_height,
        )

    @property
    def text(self):
        return self.layout.text

    @text.setter
    def text(self, value):
        self.layout.text = value
        self._update_layout()
        self.trigger_full_render()

    def _update_layout(self):
        # Update Pyglet layout size
        layout = self.layout
        layout_size = layout.width, layout.height

        if layout_size != self.content_size:
            layout.begin_update()
            layout.position = 0, 0, 0  # layout always drawn in scissor box
            layout.width = self.content_width
            layout.height = self.content_height
            layout.end_update()

    def do_render(self, surface: Surface):
        self.prepare_render(surface)
        with surface.ctx.pyglet_rendering():
            self.layout.draw()


class UIInputText(UIWidget):
    """
    An input field the user can type text into.

    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param text: Text to show
    :param font_name: string or tuple of font names, to load
    :param font_size: size of the text
    :param text_color: color of the text
    :param multiline: support for multiline
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
    """

    # move layout one pixel into the scissor box, so the caret is also shown at position 0
    LAYOUT_OFFSET = 1

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 50,
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: arcade.Color = (0, 0, 0, 255),
        multiline=False,
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
        self.caret = Caret(self.layout, color=(0, 0, 0))
        self.caret.visible = False

        self._blink_state = self._get_caret_blink_state()

    def _get_caret_blink_state(self):
        return self.caret.visible and self._active and self.caret._blink_visible

    def on_update(self, dt):
        # Only trigger render if blinking state changed
        current_state = self._get_caret_blink_state()
        if self._blink_state != current_state:
            self._blink_state = current_state
            self.trigger_full_render()

    def on_event(self, event: UIEvent) -> Optional[bool]:
        # if not active, check to activate, return
        if not self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                self._active = True
                self.trigger_full_render()
                self.caret.on_activate()
                self.caret.position = len(self.doc.text)
                return EVENT_UNHANDLED

        # if active check to deactivate
        if self._active and isinstance(event, UIMousePressEvent):
            if self.rect.collide_with_point(event.x, event.y):
                x, y = event.x - self.x - self.LAYOUT_OFFSET, event.y - self.y
                self.caret.on_mouse_press(x, y, event.button, event.modifiers)
            else:
                self._active = False
                self.trigger_full_render()
                self.caret.on_deactivate()
                return EVENT_UNHANDLED

        # if active pass all non press events to caret
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

            if isinstance(event, UIMouseEvent) and self.rect.collide_with_point(
                event.x, event.y
            ):
                x, y = event.x - self.x - self.LAYOUT_OFFSET, event.y - self.y
                if isinstance(event, UIMouseDragEvent):
                    self.caret.on_mouse_drag(
                        x, y, event.dx, event.dy, event.buttons, event.modifiers
                    )
                    self.trigger_full_render()
                elif isinstance(event, UIMouseScrollEvent):
                    self.caret.on_mouse_scroll(x, y, event.scroll_x, event.scroll_y)
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

    def do_render(self, surface: Surface):
        self._update_layout()
        self.prepare_render(surface)

        with surface.ctx.pyglet_rendering():
            self.layout.draw()


class UITextArea(UIWidget):
    """
    A text area for scrollable text.


    :param float x: x coordinate of bottom left
    :param float y: y coordinate of bottom left
    :param width: width of widget
    :param height: height of widget
    :param text: Text to show
    :param font_name: string or tuple of font names, to load
    :param font_size: size of the text
    :param text_color: color of the text
    :param multiline: support for multiline
    :param scroll_speed: speed of scrolling
    :param size_hint: Tuple of floats (0.0-1.0), how much space of the parent should be requested
    :param size_hint_min: min width and height in pixel
    :param size_hint_max: max width and height in pixel
    :param style: not used
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
        text_color: arcade.Color = (255, 255, 255, 255),
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
        self.scroll_speed = scroll_speed if scroll_speed is not None else font_size

        self.doc: AbstractDocument = pyglet.text.decode_text(text)
        self.doc.set_style(
            0,
            12,
            dict(
                font_name=font_name,
                font_size=font_size,
                color=arcade.get_four_byte_color(text_color),
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
        Sets the width and height of this UIWidget to contain the whole text.
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
                self.layout.view_y += event.scroll_y * self.scroll_speed
                self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED
