import warnings
from copy import deepcopy
from dataclasses import dataclass
from typing import Literal

import pyglet
from pyglet.event import EVENT_HANDLED, EVENT_UNHANDLED
from pyglet.text.caret import Caret
from pyglet.text.document import AbstractDocument
from typing_extensions import override

import arcade
from arcade import uicolor
from arcade.gui.events import (
    UIEvent,
    UIKeyEvent,
    UIMouseDragEvent,
    UIMouseEvent,
    UIMousePressEvent,
    UIMouseReleaseEvent,
    UIMouseScrollEvent,
    UIOnChangeEvent,
    UIOnClickEvent,
    UITextInputEvent,
    UITextMotionEvent,
    UITextMotionSelectEvent,
)
from arcade.gui.property import Property, bind
from arcade.gui.style import UIStyleBase, UIStyledWidget
from arcade.gui.surface import Surface
from arcade.gui.widgets import UIInteractiveWidget, UIWidget
from arcade.gui.widgets.layout import UIAnchorLayout
from arcade.text import FontNameOrNames
from arcade.types import LBWH, RGBA255, Color, RGBOrA255


class UILabel(UIWidget):
    """A simple text label. This widget is meant to display user instructions or
    information. This label supports multiline text.

    If you want to make a scrollable viewing text box, use a
    :py:class:`~arcade.gui.UITextArea`.

    By default, a label will fit its initial content. If the text is changed use
    :py:meth:`~arcade.gui.UILabel.fit_content` to adjust the size.

    If the text changes frequently, ensure to set a background color or texture, which will
    prevent a full rendering of the whole UI and only render the label itself.

    Args:
        text: Text displayed on the label.
        x: x position (default anchor is bottom-left).
        y: y position (default anchor is bottom-left).
        width: Width of the label. Defaults to text width if not
            specified. See
            :py:meth:`~pyglet.text.layout.TextLayout.content_width`.
        height: Height of the label. Defaults to text height if not
            specified. See
            :py:meth:`~pyglet.text.layout.TextLayout.content_height`.
        font_name: A list of fonts to use. Arcade will start at the
            beginning of the tuple and keep trying to load fonts until
            success.
        font_size: Font size of font.
        text_color: Color of the text.
        bold: If enabled, the label's text will be in a **bold** style.
        italic: If enabled, the label's text will be in an *italic*
            style.
        stretch: Stretch font style.
        align: Horizontal alignment of text on a line. This only applies
            if a width is supplied. Valid options include ``"left"``,
            ``"center"`` or ``"right"``.
        dpi: Resolution of the fonts in the layout. Defaults to 96.
        multiline: If enabled, a ``\\n`` will start a new line. Changing
            text or font will require a manual call of
            :py:meth:`~arcade.gui.UILabel.fit_content` to prevent text
            line wrap.
        size_hint: A tuple of floats between 0 and 1 defining the amount
            of space of the parent should be requested. Default (0, 0)
            which fits the content.
        size_hint_max: Maximum size hint width and height in pixel.
    """

    ADAPTIVE_MULTILINE_WIDTH = 999999

    def __init__(
        self,
        text: str = "",
        *,
        x: float = 0,
        y: float = 0,
        width: float | None = None,
        height: float | None = None,
        font_name=("calibri", "arial"),
        font_size: float = 12,
        text_color: RGBOrA255 = arcade.color.WHITE,
        bold: str | bool = False,
        italic=False,
        align="left",
        multiline: bool = False,
        size_hint=(0, 0),
        size_hint_max=None,
        **kwargs,
    ):
        # If multiline is enabled and no width is given, we need to fit the
        # size to the text. This is done by setting the width to a very
        # large value and then fitting the size.
        adaptive_multiline = False
        if multiline and not width:
            width = self.ADAPTIVE_MULTILINE_WIDTH
            adaptive_multiline = True

        # Use Arcade Text wrapper of pyglet.Label for text rendering
        self._label = arcade.Text(
            x=0,
            y=0,
            text=text,
            font_name=font_name,
            font_size=font_size,
            color=text_color,
            width=int(width) if width else None,
            bold=bold,
            italic=italic,
            align=align,
            anchor_y="bottom",  # Position text bottom left to fit into scissor area
            multiline=multiline,
            **kwargs,
        )
        self._strong_background = True

        if adaptive_multiline:
            # +1 is required to prevent line wrap, +1 is required to prevent issues with kerning
            width = self._label.content_width + 2

        super().__init__(
            x=x,
            y=y,
            width=width or self._label.content_width,
            height=height or self._label.content_height,
            size_hint=size_hint,
            size_hint_max=size_hint_max,
            **kwargs,
        )

        # Set the label size. If the width or height was given because border
        # and padding can only be applied later, we can avoid ``fit_content``
        # and set with and height separately.
        if width:
            self._label.width = int(width)
        if height:
            self._label.height = int(height)

        bind(self, "rect", UILabel._update_label)

        # update size hint when border or padding changes
        bind(self, "_border_width", UILabel._update_size_hint_min)
        bind(self, "_padding_left", UILabel._update_size_hint_min)
        bind(self, "_padding_right", UILabel._update_size_hint_min)
        bind(self, "_padding_top", UILabel._update_size_hint_min)
        bind(self, "_padding_bottom", UILabel._update_size_hint_min)

        self._update_size_hint_min()

    def fit_content(self):
        """Manually set the width and height of the label to contain the whole text.
        Based on the size_hint_min.

        If multiline is enabled, the width will be calculated based on longest line of the text.
        And size_hint_min will be updated.
        """

        if self.multiline:
            self._label.width = self.ADAPTIVE_MULTILINE_WIDTH
            self._update_size_hint_min()

        min_width, min_height = self.size_hint_min or (1, 1)
        self.rect = self.rect.resize(
            width=min_width,
            height=min_height,
        )
        # rect changes to trigger resizing of the _label automatically

    @property
    def text(self):
        """Text of the label."""
        return self._label.text

    @text.setter
    def text(self, value):
        """Update text of the label.

        This triggers a full render to ensure that previous text is cleared out.
        """

        if self._label.text != value:
            self._label.text = value
            self._update_size_hint_min()

            if self._bg_color or self._bg_tex:
                self.trigger_render()
            else:
                self.trigger_full_render()

    @property
    def font_name(self) -> FontNameOrNames:
        """Font name of the label. Use :py:meth:`~arcade.gui.UILabel.update_font` to change."""
        return self._label.font_name

    @property
    def font_size(self) -> float:
        """Font size of the label. Use :py:meth:`~arcade.gui.UILabel.update_font` to change."""
        return self._label.font_size

    @property
    def font_color(self) -> Color:
        """Font color of the label. Use :py:meth:`~arcade.gui.UILabel.update_font` to change."""
        return self._label.color

    @property
    def bold(self) -> bool | str:
        """Return if the label is in bold style.
        Use :py:meth:`~arcade.gui.UILabel.update_font` to change."""
        return self._label.bold

    @property
    def italic(self) -> bool | str:
        """Return if the label is in italic style.
        Use :py:meth:`~arcade.gui.UILabel.update_font` to change."""
        return self._label.italic

    def _update_label(self):
        """Update the position and size of the label.

        So it fits into the content area of the widget.
        Should always be called after the content area changed.
        """
        # Update Pyglet label size
        label = self._label
        layout_size = label.width, label.height

        if layout_size != self.content_size or label.position != (0, 0):
            label.position = 0, 0, 0  # label always drawn in scissor box
            label.width = int(self.content_width)
            label.height = int(self.content_height)

    def _update_size_hint_min(self):
        """Update the minimum size hint based on the label content size."""
        # +1 is required to prevent line wrap, +1 is required to prevent issues with kerning
        min_width = self._label.content_width + 2
        min_width += self._padding_left + self._padding_right + 2 * self._border_width

        min_height = self._label.content_height
        min_height += self._padding_top + self._padding_bottom + 2 * self._border_width

        self.size_hint_min = (min_width, min_height)

    def update_font(
        self,
        font_name: FontNameOrNames | None = None,
        font_size: float | None = None,
        font_color: Color | None = None,
        bold: bool | str | None = None,
        italic: bool | None = None,
    ):
        """Update font of the label.

        Args:
            font_name: A list of fonts to use. Arcade will start at the
                beginning of the tuple and keep trying to load fonts until
                success.
            font_size: Font size of font.
            font_color: Color of the text.
            bold: May be any value in :py:obj:`pyglet.text.Weight`,
                ``True`` (converts to ``"bold"``), or ``False``
                (converts to ``"regular"``).
            italic: If enabled, the label's text will be in an *italic*
        """
        font_name = font_name or self._label.font_name
        font_size = font_size or self._label.font_size
        font_color = font_color or self._label.color
        font_bold = bold if bold is not None else self._label.bold
        font_italic = italic if italic is not None else self._label.italic

        # ensure type of font_color, label will allways be a color
        font_color = Color.from_iterable(font_color)

        # Check if values actually changed, if then update and trigger render
        font_name_changed = self._label.font_name != font_name
        font_size_changed = self._label.font_size != font_size
        font_color_changed = self._label.color != font_color
        font_bold_changed = self._label.bold != font_bold
        font_italic_changed = self._label.italic != font_italic
        if (
            font_name_changed
            or font_size_changed
            or font_color_changed
            or font_bold_changed
            or font_italic_changed
        ):
            with self._label:
                self._label.font_name = font_name
                self._label.font_size = font_size
                self._label.color = font_color
                self._label.bold = font_bold
                self._label.italic = font_italic
            self._update_size_hint_min()

            # Optimised render behaviour
            if self._bg_color or self._bg_tex:
                self.trigger_render()
            else:
                self.trigger_full_render()

    @property
    def multiline(self) -> bool:
        """Return if the label is in multiline mode."""
        return self._label.multiline

    def do_render(self, surface: Surface):
        """Render the label via py:class:`~arcade.Text`."""
        self.prepare_render(surface)

        # pyglet rendering automatically applied by arcade.Text
        self._label.draw()


class UITextWidget(UIAnchorLayout):
    """Adds the ability to add text to a widget.
    Use this to create subclass widgets, which have text.

    The text can be placed within the widget using
    :py:class:`~arcade.gui.UIAnchorLayout` parameters with
    :py:meth:`~arcade.gui.UITextWidget.place_text`.

    The widget holds reference to one primary :py:class:`~arcade.gui.UILabel`, which is placed in
    the widget's layout. This label can be accessed
    via :py:attr:`~arcade.gui.UITextWidget.ui_label`.

    To change font, font size, or text color, use py:meth:`~arcade.gui.UILabel.update_font`.

    Args:
        text: Text displayed on the label.
        multiline: If enabled, a ``\\n`` will start a new line.
        **kwargs: passed to :py:class:`~arcade.gui.UIWidget`.

    """

    def __init__(self, *, text: str, multiline: bool = False, **kwargs):
        super().__init__(text=text, **kwargs)
        self._restrict_child_size = True
        self._label = UILabel(
            text=text, multiline=multiline
        )  # UILabel supports width=None for multiline
        self.add(self._label)

    def place_text(
        self,
        anchor_x: str | None = None,
        align_x: float = 0,
        anchor_y: str | None = None,
        align_y: float = 0,
        **kwargs,
    ) -> UILabel:
        """Place widget's text within the widget using
        :py:class:`~arcade.gui.UIAnchorLayout` parameters.

        Args:
            anchor_x: Horizontal anchor. Valid options are ``left``,
                ``right``, and ``center``.
            align_x: Offset or padding for the horizontal anchor.
            anchor_y: Vertical anchor. Valid options are ``top``,
                ``center``, and ``bottom``.
            align_y: Offset or padding for the vertical anchor.
            **kwargs: Additional keyword arguments passed to the layout function.
        """
        self.remove(self._label)
        return self.add(
            child=self._label,
            anchor_x=anchor_x,
            align_x=align_x,
            anchor_y=anchor_y,
            align_y=align_y,
            **kwargs,
        )

    @property
    def text(self):
        """Text of the widget. Modifying this repeatedly will cause significant
        lag; calculating glyph position is very expensive.
        """
        return self.ui_label.text

    @text.setter
    def text(self, value):
        self.ui_label.text = value
        self.trigger_render()

    @property
    def multiline(self):
        """Get or set the multiline mode.

        Newline characters (``"\\n"``) will only be honored when this is set to ``True``.
        If you want a scrollable text widget, please use :py:class:`~arcade.gui.UITextArea`
        instead.
        """
        return self.ui_label.multiline

    @property
    def ui_label(self) -> UILabel:
        """Internal py:class:`~arcade.gui.UILabel` used for rendering the text."""
        return self._label


@dataclass
class UIInputTextStyle(UIStyleBase):
    """Used to style the UITextWidget for different states. Below is its use case.

    .. code:: py

        button = UIInputText(style={"normal": UIInputText.UIStyle(...),})

    Args:
        bg: Background color.
        border: Border color.
        border_width: Width of the border.

    """

    bg: RGBA255 | None = None
    border: RGBA255 | None = uicolor.WHITE
    border_width: int = 2


class UIInputText(UIStyledWidget[UIInputTextStyle], UIInteractiveWidget):
    """An input field the user can type text into.

    This is useful in returning
    string input from the user. A caret is displayed, which the user can move
    around with a mouse or keyboard.

    A mouse drag selects text, a mouse press moves the caret, and keys can move
    around the caret. Arcade confirms that the field is active before allowing
    users to type, so it is okay to have multiple of these.

    By default, a border is drawn around the input field.

    The widget emits a :py:class:`~arcade.gui.UIOnChangeEvent` event when the text changes.

    Args:
        x: x position (default anchor is bottom-left).
        y: y position (default anchor is bottom-left).
        width: Width of the text field.
        height: Height of the text field.
        text: Initial text displayed. This can be modified later
            programmatically or by the user's interaction with the
            caret.
        font_name: A list of fonts to use. Arcade will start at the
            beginning of the tuple and keep trying to load fonts until
            success.
        font_size: Font size of font.
        text_color: Color of the text.
        multiline: If enabled, a ``\\n`` will start a new line. A
            :py:class:`~arcade.gui.UITextWidget`  ``multiline`` of True
            is the same thing as a :py:class:`~arcade.gui.UITextArea`.
        caret_color: An RGBA or RGB color for the caret with each
            channel between 0 and 255, inclusive.
        size_hint: A tuple of floats between 0 and 1 defining the amount
            of space of the parent should be requested.
        size_hint_min: Minimum size hint width and height in pixel.
        size_hint_max: Maximum size hint width and height in pixel.
        **kwargs: passed to :py:class:`~arcade.gui.UIWidget`.

    """

    # Move layout one pixel into the scissor box so the caret is also shown at
    # position 0.
    LAYOUT_OFFSET = 1

    # Style
    UIStyle = UIInputTextStyle

    DEFAULT_STYLE = {
        "normal": UIStyle(),
        "hover": UIStyle(
            border=uicolor.WHITE_CLOUDS,
        ),
        "press": UIStyle(
            border=uicolor.WHITE_SILVER,
        ),
        "disabled": UIStyle(
            bg=uicolor.WHITE_SILVER,
        ),
        "invalid": UIStyle(
            bg=uicolor.RED_ALIZARIN.replace(a=42),
            border=uicolor.RED_ALIZARIN,
        ),
    }

    # Properties
    invalid = Property(False)

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 25,  # required height for font size 12 + border width 1
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: RGBOrA255 = arcade.color.WHITE,
        multiline=False,
        caret_color: RGBOrA255 = arcade.color.WHITE,
        border_color: Color | None = arcade.color.WHITE,
        border_width: int = 2,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        style: dict[str, UIInputTextStyle] | None = None,
        **kwargs,
    ):
        if border_color != arcade.color.WHITE or border_width != 2:
            warnings.warn(
                "UIInputText is now a UIStyledWidget. "
                "Use the style dict to set the border color and width.",
                DeprecationWarning,
                stacklevel=1,
            )

            # adjusting style to set border color and width
            style = style or UIInputText.DEFAULT_STYLE
            style = deepcopy(style)

            style["normal"].border = border_color
            style["normal"].border_width = border_width

        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            style=style or UIInputText.DEFAULT_STYLE,
            **kwargs,
        )

        self._text_color = Color.from_iterable(text_color)

        self.doc: AbstractDocument = pyglet.text.decode_text(text)
        self.doc.set_style(
            0,
            len(text),
            dict(font_name=font_name, font_size=font_size, color=self._text_color),
        )

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.doc,
            x=0 + self.LAYOUT_OFFSET,
            y=0,
            z=0.0,  # Position
            width=int(width - self.LAYOUT_OFFSET),
            height=int(height),  # Size
            multiline=multiline,
        )
        self.caret = Caret(self.layout, color=Color.from_iterable(caret_color))
        self.caret.visible = False

        self._blink_state = self._get_caret_blink_state()

        self.register_event_type("on_change")

        bind(self, "hovered", UIInputText._apply_style)
        bind(self, "pressed", UIInputText._apply_style)
        bind(self, "invalid", UIInputText._apply_style)
        bind(self, "disabled", UIInputText._apply_style)
        bind(self, "focused", UIInputText._on_focus_change)
        bind(self, "_active", UIInputText._on_active_changed)

        # initial style application
        self._apply_style()

    def _on_focus_change(self):
        if self.focused:
            self.activate()
        elif self.active:
            self.deactivate()

    def _on_active_changed(self):
        """Handle the active state change of the input
        text field to care about loosing active state."""
        if not self._active:
            self.deactivate()

    def _apply_style(self):
        style = self.get_current_style()

        self.with_background(
            color=Color.from_iterable(style.bg) if style.bg else None,
        )
        self.with_border(
            color=Color.from_iterable(style.border) if style.border else None,
            width=style.border_width,
        )
        self.trigger_full_render()

    @override
    def get_current_state(self) -> str:
        """Get the current state of the slider.

        Returns:
            ""normal"", ""hover"", ""press"" or ""disabled"".
        """
        if self.disabled:
            return "disabled"
        elif self.pressed:
            return "press"
        elif self.hovered:
            return "hover"
        elif self.invalid:
            return "invalid"
        else:
            return "normal"

    def _get_caret_blink_state(self):
        """Check whether or not the caret is currently blinking or not."""
        return self.caret.visible and self._active and self.caret._blink_visible

    @override
    def on_update(self, dt):
        """Update the caret blink state."""
        # Only trigger render if blinking state changed
        current_state = self._get_caret_blink_state()
        if self._blink_state != current_state:
            self._blink_state = current_state
            self.trigger_full_render()

    def on_click(self, event: UIOnClickEvent):
        self.activate()

    @override
    def on_event(self, event: UIEvent) -> bool | None:
        """Handle events for the text input field.

        Text input is only active when the user clicks on the input field."""
        # If active check to deactivate
        if self._active and isinstance(event, UIMouseEvent):
            event_in_rect = self.rect.point_in_rect(event.pos)

            # mouse press
            if isinstance(event, UIMousePressEvent):
                # inside the input field
                if event_in_rect:
                    x = int(event.x - self.left - self.LAYOUT_OFFSET)
                    y = int(event.y - self.bottom)
                    self.caret.on_mouse_press(x, y, event.button, event.modifiers)
                else:
                    # outside the input field
                    self.deactivate()
                    # return unhandled to allow other widgets to activate
                    return EVENT_UNHANDLED

            # mouse release outside the input field,
            # which could be a click on another widget, which handles the press event
            if isinstance(event, UIMouseReleaseEvent) and not event_in_rect:
                self.deactivate()
                # return unhandled to allow other widgets to activate
                return EVENT_UNHANDLED

        # If active pass all non press events to caret
        if self._active:
            old_text = self.text

            if self.focused and isinstance(event, UIKeyEvent) and event.symbol == arcade.key.SPACE:
                # if widget is focused, we consume the space key
                # to prevent flickering of the focus
                return EVENT_HANDLED

            # Act on events if active
            if isinstance(event, UITextInputEvent):
                self.caret.on_text(event.text)
                self.trigger_full_render()
            elif isinstance(event, UITextMotionEvent):
                self.caret.on_text_motion(event.motion)
                self.trigger_full_render()
            elif isinstance(event, UITextMotionSelectEvent):
                self.caret.on_text_motion_select(event.selection)
                self.trigger_full_render()

            if isinstance(event, UIMouseEvent) and self.rect.point_in_rect(event.pos):
                x = int(event.x - self.left - self.LAYOUT_OFFSET)
                y = int(event.y - self.bottom)
                if isinstance(event, UIMouseDragEvent):
                    self.caret.on_mouse_drag(
                        x, y, event.dx, event.dy, event.buttons, event.modifiers
                    )
                    self.trigger_full_render()
                elif isinstance(event, UIMouseScrollEvent):
                    self.caret.on_mouse_scroll(x, y, event.scroll_x, event.scroll_y)
                    self.trigger_full_render()

            if old_text != self.text:
                self.dispatch_event("on_change", UIOnChangeEvent(self, old_text, self.text))

        return super().on_event(event)

    @property
    def active(self) -> bool:
        """Return if the text input field is active.

        An active text input field will show a caret and accept text input."""
        return self._active

    def activate(self):
        """Programmatically activate the text input field."""
        if self._active:
            return

        self._grap_active()  # will set _active to True
        self.trigger_full_render()
        self.caret.on_activate()
        self.caret.position = len(self.doc.text)

    def deactivate(self):
        """Programmatically deactivate the text input field."""

        if self._active:
            self._release_active()  # will set _active to False

        self.trigger_full_render()
        self.caret.on_deactivate()

    def _update_layout(self):
        # Update Pyglet layout size
        layout = self.layout
        layout_size = layout.width - self.LAYOUT_OFFSET, layout.height

        if layout_size != self.content_size:
            layout.begin_update()
            layout.width = int(self.content_width - self.LAYOUT_OFFSET)
            layout.height = int(self.content_height)

            # should not be required, but the caret does not show up on first click without text
            layout.x = self.LAYOUT_OFFSET
            layout.y = 0
            layout.end_update()

            # manually update caret position
            self.caret.on_layout_update()

    @property
    def text(self):
        """Text of the input field."""
        return self.doc.text

    @text.setter
    def text(self, value):
        if value != self.doc.text:
            old_text = self.doc.text
            self.doc.text = value
            self.dispatch_event("on_change", UIOnChangeEvent(self, old_text, self.text))

            # if bg color or texture is set, render this widget only
            if self._bg_color or self._bg_tex:
                self.trigger_render()
            else:
                self.trigger_full_render()

    @override
    def do_render(self, surface: Surface):
        """Render the text input field."""
        self._update_layout()
        self.prepare_render(surface)

        self.layout.draw()

    def on_change(self, event: UIOnChangeEvent):
        """Event handler for text change."""
        pass


class UITextArea(UIWidget):
    """A text area that allows users to view large documents of text by scrolling
    the mouse.

    Args:
        x: x position (default anchor is bottom-left).
        y: y position (default anchor is bottom-left).
        width: Width of the text area.
        height: Height of the text area.
        text: Initial text displayed.
        font_name: A list of fonts to use. Arcade will start at the
            beginning of the tuple and keep trying to load fonts until
            success.
        font_size: Font size of font.
        text_color: Color of the text.
        bold: If enabled, the label's text will be in a **bold** style.
        italic: If enabled, the label's text will be in an *italic*
        multiline: If enabled, a ``\\n`` will start a new line.
        scroll_speed: Speed of mouse scrolling.
        size_hint: A tuple of floats between 0 and 1 defining the amount
            of space of the parent should be requested.
        size_hint_min: Minimum size hint width and height in pixel.
        size_hint_max: Maximum size hint width and height in pixel.
        document_mode: Mode of the document. Can be "PLAIN", "ATTRIBUTED", or "HTML".
            PLAIN will decode the text as plain text, ATTRIBUTED and HTML will
            decode the text as pyglet documents here
            https://pyglet.readthedocs.io/en/latest/programming_guide/text.html
        **kwargs: passed to :py:class:`~arcade.gui.UIWidget`.
    """

    def __init__(
        self,
        *,
        x: float = 0,
        y: float = 0,
        width: float = 400,
        height: float = 40,
        text: str = "",
        font_name=("arial", "calibri"),
        font_size: float = 12,
        bold=False,
        italic=False,
        text_color: RGBA255 = arcade.color.WHITE,
        multiline: bool = True,
        scroll_speed: float | None = None,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        document_mode: Literal["PLAIN", "ATTRIBUTED", "HTML"] = "PLAIN",
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

        self.doc: AbstractDocument
        if document_mode == "PLAIN":
            self.doc = pyglet.text.decode_text(text)
        elif document_mode == "ATTRIBUTED":
            self.doc = pyglet.text.decode_attributed(text)
        elif document_mode == "HTML":
            self.doc = pyglet.text.decode_html(text)

        self.doc.set_style(
            0,
            len(text),
            dict(
                font_name=font_name,
                font_size=font_size,
                color=Color.from_iterable(text_color),
                bold=bold,
                italic=italic,
            ),
        )

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.doc,
            width=int(self.content_width),
            height=int(self.content_height),
            multiline=multiline,
        )

        bind(self, "rect", UITextArea._update_layout)

    def fit_content(self):
        """Set the width and height of the text area to contain the whole text."""
        self.rect = LBWH(
            self.left,
            self.bottom,
            self.layout.content_width,
            self.layout.content_height,
        )

    @property
    def text(self):
        """Text of the text area."""
        return self.doc.text

    @text.setter
    def text(self, value):
        self.doc.text = value
        self.trigger_render()

    def _update_layout(self):
        # Update Pyglet layout size
        layout = self.layout

        # Convert from local float coords to ints to avoid jitter
        # since pyglet imposes int-only coordinates as of pyglet 2.0
        content_width, content_height = map(int, self.content_size)
        if content_width != layout.width or content_height != layout.height:
            layout.begin_update()
            layout.width = content_width
            layout.height = content_height
            layout.y = 0  # reset y position to 0 (Required by IncrementalTextLayout)
            layout.end_update()

    @override
    def do_render(self, surface: Surface):
        """Render the text area."""
        self._update_layout()
        self.prepare_render(surface)
        self.layout.draw()

    @override
    def on_event(self, event: UIEvent) -> bool | None:
        """Handle scrolling of the widget."""
        if isinstance(event, UIMouseScrollEvent):
            if self.rect.point_in_rect(event.pos):
                self.layout.view_y = round(self.layout.view_y + event.scroll_y * self.scroll_speed)
                self.trigger_full_render()

        if super().on_event(event):
            return EVENT_HANDLED

        return EVENT_UNHANDLED
