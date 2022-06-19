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

    :param width float: The width of the message box.
    :param height float: The height of the message box.
    :param message_text str: The text to display.
    :param text_color int: The color of the text in the box.
    :param background_color arcade.Color: The color of the background of the box.
    :param disappear_time float: The time before the box should disappear.
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
    ) -> None:
        super().__init__(size_hint=(1, 1))
        anchor_offset = 10

        # Store various variables needed for this box to function
        self._time_counter: float = disappear_time

        # Set up the box
        disappearing_box = UIAnchorLayout(width=width, height=height)
        disappearing_box.with_padding(all=anchor_offset)
        disappearing_box.with_background(
            texture=arcade.Texture.create_filled(
                "background color", (int(width), int(height)), background_color,
            )
        )
        disappearing_box.add(
            UITextArea(
                text=message_text,
                width=width - anchor_offset,
                height=height - anchor_offset,
                text_color=text_color,
            ),
            anchor_x="center",
            anchor_y="top",
        )
        disappearing_box.center_on_screen()

        # Add the box to the ui
        self.add(
            disappearing_box,
            anchor_x="center",
            anchor_y="bottom",
            align_y=anchor_offset,
        )

    def on_update(self, delta_time: float) -> None:
        self._time_counter -= delta_time

        # Check if the box should disappear
        if self._time_counter <= 0:
            self.remove_box(UIBoxDisappearEvent(self))

    def remove_box(self, _) -> None:
        if self.parent is not None:
            self.parent.remove(self)
