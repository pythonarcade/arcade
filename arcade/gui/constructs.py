"""
Constructs, are prepared widget combinations, you can use for common use-cases
"""
import arcade
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
        super().__init__(
            size_hint=(1, 1)
        )
        self._callback = callback  # type: ignore

        space = 10

        # setup frame which will act like the window
        frame = self.add(UIAnchorLayout(
            width=width,
            height=height
        ))
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
