"""
Constructs, are prepared widget combinations, you can use for common use-cases
"""
from arcade.gui.nine_patch import NinePatchTexture

import arcade
from arcade.gui.events import UIOnActionEvent
from arcade.gui.mixins import UIMouseFilterMixin
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout, UIAnchorLayout
from arcade.gui.widgets.text import UITextArea


class UIMessageBox(UIMouseFilterMixin, UIAnchorLayout):
    """
    A simple dialog box that pops up a message with buttons to close.
    Subclass this class or overwrite the 'on_action' event handler with

    .. code-block:: python

        box = UIMessageBox(...)
        @box.event("on_action")
        def on_action(event: UIOnActionEvent):
            pass


    :param width: Width of the message box
    :param height: Height of the message box
    :param message_text: Text to show as message to the user
    :param buttons: List of strings, which are shown as buttons
    """

    def __init__(
        self,
        *,
        width: float,
        height: float,
        message_text: str,
        buttons=("Ok",),
    ):
        if not buttons:
            raise ValueError("At least a single value has to be available for `buttons`")

        super().__init__(size_hint=(1, 1))
        self.register_event_type("on_action")

        space = 20

        # setup frame which will act like the window
        frame = self.add(UIAnchorLayout(width=width, height=height, size_hint=None))
        frame.with_padding(all=space)

        frame.with_background(texture=NinePatchTexture(
            start=(7, 7),
            end=(93, 93),
            texture=arcade.load_texture(
                ":resources:gui_basic_assets/window/grey_panel.png"
            )
        ))

        # Setup text
        frame.add(
            child=UITextArea(
                text=message_text,
                width=width - space,
                height=height - space,
                text_color=arcade.color.BLACK,
            ),
            anchor_x="center",
            anchor_y="top",
        )

        # setup buttons
        button_group = UIBoxLayout(vertical=False, space_between=10)
        for button_text in buttons:
            button = UIFlatButton(text=button_text)
        button_group.add(button)
        button.on_click = self._on_choice  # type: ignore

        frame.add(
            child=button_group,
            anchor_x="right",
            anchor_y="bottom",
        )

    def _on_choice(self, event):
        self.parent.remove(self)
        self.dispatch_event("on_action", UIOnActionEvent(self, event.source.text))

    def on_action(self, event: UIOnActionEvent):
        """Called when button was pressed"""
        pass
