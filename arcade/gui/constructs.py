"""
Constructs, are prepared widget combinations, you can use for common use-cases
"""
import arcade
from arcade.gui.events import UIBoxDisappearEvent
from arcade.gui.mixins import UIMouseFilterMixin
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout, UIAnchorLayout
from arcade.gui.widgets.text import UITextArea


class UIMessageBox(UIMouseFilterMixin, UIAnchorLayout):
    """
    A simple dialog box that pops up a message with buttons to close.

    :param width: Width of the message box
    :param height: Height of the message box
    :param message_text:
    :param buttons: List of strings, which are shown as buttons
    :param callback: Callback function, will receive the text of the clicked button
    """

    def __init__(
        self,
        *,
        width: float,
        height: float,
        message_text: str,
        buttons=("Ok",),
        callback=None
    ):
        super().__init__(size_hint=(1, 1))
        self._callback = callback  # type: ignore

        space = 10

        # setup frame which will act like the window
        frame = self.add(UIAnchorLayout(width=width, height=height))
        frame.with_padding(all=space)

        self._bg_tex = arcade.load_texture(
            ":resources:gui_basic_assets/window/grey_panel.png"
        )
        frame.with_background(texture=self._bg_tex)

        # Setup text
        self._text_area = UITextArea(
            text=message_text,
            width=width - space,
            height=height - space,
            text_color=arcade.color.BLACK,
        )
        frame.add(
            child=self._text_area,
            anchor_x="center",
            anchor_y="top",
        )

        # setup buttons
        button_group = UIBoxLayout(vertical=False, space_between=10)
        for button_text in buttons:
            button = UIFlatButton(text=button_text)
            button_group.add(button)
            button.on_click = self.on_ok  # type: ignore

        frame.add(
            child=button_group,
            anchor_x="right",
            anchor_y="bottom",
        )

    def on_ok(self, event):
        self.parent.remove(self)
        if self._callback is not None:
            self._callback(event.source.text)


class UIDisappearingInfoBox(UIMouseFilterMixin, UIAnchorLayout):
    """
    Represents a simple dialog box that pops up with a message and disappears after a
    certain amount of time.

    Parameters
    ----------
    width: float
        The width of the message box.
    height: float
        The height of the message box.
    message_text: str
        The text to display.
    text_color: int
        The color of the text in the box.
    background_color: arcade.Color
        The color of the background of the box..
    disappear_time: float
        The time before the box should disappear.
    fit: bool
        Whether the size of the box should be fit to the text inside.
    """

    def __init__(
        self,
        *,
        width: float = 400,
        height: float = 150,
        message_text: str,
        text_color: arcade.Color = arcade.color.BLACK,
        background_color: arcade.Color = arcade.color.BABY_BLUE,
        disappear_time: float = 3,
        fit: bool = False
    ) -> None:
        super().__init__(size_hint=(1, 1))
        anchor_offset = 10

        # Store various variables needed for this box to function
        self._time_counter: float = disappear_time

        # Set up the box and its attributes
        box = self.add(UIAnchorLayout(width=width, height=height))
        box.with_padding(all=anchor_offset)
        box.with_background(
            texture=arcade.Texture.create_filled(
                "background color", (int(width), int(height)), background_color
            )
        )
        box.add(
            child=UITextArea(
                text=message_text,
                width=width - anchor_offset,
                height=height - anchor_offset,
                text_color=text_color,
            )
        )

        # Fit the box to the text if needed
        if fit:
            box.center_on_screen()

    def on_update(self, delta_time: float) -> None:
        self._time_counter -= delta_time

        # Check if the box should disappear
        if self._time_counter <= 0:
            self.remove_box(UIBoxDisappearEvent(self))

    def remove_box(self, _) -> None:
        self.parent.remove(self)
