from typing import Callable, Generic, Type, TypeVar, cast

import arcade
from arcade.color import BLACK, RED, WHITE
from arcade.gui import UIEvent, UIInputText, UILabel, UITextInputEvent
from arcade.types import Color, RGBOrA255
from arcade.utils import type_name

__all__ = ("UITypedTextInput",)


T = TypeVar("T")


# This is almost certainly doing at least one thing wrong
class UITypedTextInput(UIInputText, Generic[T]):
    """A text box which auto-converts to and from a :py:class:`type`.

    The simplest usage is passing a :py:func:`type` which supports
    :py:func:`repr` and allows a single :py:class:`str` as an argument:

    .. code-block:: python

       self.float_input = UITypedTextInput(float, text="0.0")

    In the example above, setting :py:attr:`self.float_input.text` to
    ``"string"`` will:

    #. Set both the text and the caret to the ``error_color`` passed at
       creation
    #. Re-raise the :py:class:`ValueError` from ``float("string")``

    To stop error propagation, pass
    You can customize your conversion to and from strings by overriding
    the following arguments with custom :py:class:`callable` objects:

    .. list-table::
       :header-rows: 1

       * - Argument
         - Default

       * - ``to_str``
         - :py:func:`repr`

       * - ``from_str``
         - the ``parsed_type``

    .. important:: This class is meant to handle simple types in simple
                   dev and test tools.

                   As a general rule, if you need to highlight a specific
                   syntax error, this class is not the right tool.

    Args:
        parsed_type:
            The :py:class:`type` to require. This is not meant to
            be changed after creation.
        from_str:
            A type or other :py:func:`callable` which converts a
            :py:class:`str` to an instance of :py:class:`parsed_type`.
            It may raise exceptions and perform cleaning of text.
        to_str:
            A :py:func:`callable` which converts ``parsed_type``
            instances to :py:class:`str`.
        x: an X position (see :py:class:`.UIInputText`).
        y: an X position (see :py:class:`.UIInputText`).
        width: an X axis width (see :py:class:`.UIInputText`).
        height: a Y axis height (see :py:class:`.UIInputText`).
        text: The initial text to display.
        font_name: (see :py:class:`.UIInputText`).
        text_color: The color to use for non-error text.
        error_color: The color to use when ``to_str`` or ``from_str``
            raised an exception.
        multiline: See :py:class:`.UIInputText`.
        size_hint:  See :py:class:`.UIInputText`.
        size_hint_min:  See :py:class:`.UIInputText`.
        size_hint_max: See :py:class:`.UIInputText`.
    """

    def __init__(
        self,
        parsed_type: Type[T],
        *,
        to_str: Callable[[T], str] = repr,
        from_str: Callable[[str], T] | None = None,
        emit_parse_exceptions: bool = True,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 24,
        text: str = "",
        font_name=("Arial",),
        font_size: float = 12,
        text_color: RGBOrA255 = BLACK,
        error_color: RGBOrA255 = RED,
        multiline=False,
        size_hint=None,
        size_hint_min=None,
        size_hint_max=None,
        **kwargs,
    ):
        if not isinstance(type, type):
            raise TypeError(f"Expected a type, but got {parsed_type}")
        super().__init__(
            x=x,
            y=y,
            width=width,
            height=height,
            text=text,
            font_name=font_name,
            font_size=font_size,
            text_color=text_color,
            multiline=multiline,
            caret_color=text_color,
            size_hint=size_hint,
            size_hint_min=size_hint_min,
            size_hint_max=size_hint_max,
            **kwargs,
        )
        self.emit_parse_exceptions = emit_parse_exceptions
        self._error_color = error_color
        self._valid_color = text_color
        self._parsed_type: Type[T] = parsed_type
        self._to_str = to_str
        self._from_str: Callable[[str], T] = cast(Callable[[str], T], from_str or parsed_type)
        self._parsed_value: T = self._from_str(self.text)

    def _set_current_color(self, new_color: RGBOrA255) -> None:
        validated = Color.from_iterable(new_color)
        if self._text_color == validated:
            return

        self._text_color = validated
        self.caret.color = validated
        self.doc.set_style(0, len(self.text), dict(color=validated))
        self.trigger_full_render()

    def _checked_parse(self, text: str):
        try:
            self._parsed_value = self._from_str(text)
            self._set_current_color(self._valid_color)
        except Exception as e:
            # print(e)
            self._set_current_color(self._error_color)
            if self.emit_parse_exceptions:
                raise e

    def on_event(self, event: UIEvent) -> bool | None:
        # print(f"In {type_name(event)}")
        if isinstance(event, UITextInputEvent) and self._active:
            text = event.text.replace("\r", "").replace("\r", "")
            event.text = text

        handled = super().on_event(event)
        self._checked_parse(self.doc.text)
        return handled

    @property
    def parsed_type(self) -> Type[T]:
        """Get the type this input field expects to parse.

        .. note:: This is not meant to be changed after creation.
        """
        return self._parsed_type

    @property
    def value(self) -> T:
        """The current instance of :py:attr:`parsed_type`.

        Setting this automatically updates the text of the widget.
        """
        return self._parsed_value

    @value.setter
    def value(self, new_value: T) -> None:
        must_be = self._parsed_type
        if not isinstance(new_value, must_be):
            raise TypeError(
                # We pass self here to support subclasses
                f"This {type_name(self)} was created to expect {type_name(must_be)}"
                f", but got {new_value!r} (a {type_name(new_value)})"
            )
        self.doc.text = self._to_str(new_value)
        self._set_current_color(self._valid_color)

    @property
    def text(self) -> str:
        """Get/set the text of the widget.

        In addition to basic behavior from :py:class:`UITextWidget`,
        this also performs validation. To silence error propagation
        from validation, set :py:attr:`emit_parse_exceptions` to
        ``False``.
        """
        return self.doc.text

    @text.setter
    def text(self, new_text: str) -> None:
        self.doc.text = new_text
        self._checked_parse(new_text)


if __name__ == "__main__":
    width, height = 400, 400
    center = width / 2
    from arcade.gui import NinePatchTexture, UIView

    class MyView(UIView):
        def __init__(self):
            super().__init__()
            self.ninepatch = NinePatchTexture(
                left=5,
                right=5,
                top=5,
                bottom=5,
                texture=arcade.load_texture(":resources:gui_basic_assets/window/panel_gray.png"),
            )
            self.instructions = UILabel(
                text="Valid float values -> black text\nNon-float values -> red text",
                x=center - 150,
                height=center + 80,
                text_color=WHITE,
                multiline=True,
                font_size=16,
                width=300,
                align="center",
            )
            self.ui.add(self.instructions)

            self.float_box = UITypedTextInput(
                float,
                text="0.0",
                x=center - 100,
                y=height / 2,
                width=200,
                font_size=16,
                height=30,
                emit_parse_exceptions=False,
            ).with_background(texture=self.ninepatch)
            self.ui.add(self.float_box)

        def on_show_view(self):
            super().on_show_view()

    window = arcade.Window(width, height, "Typed input text test")
    window.show_view(MyView())
    window.run()
