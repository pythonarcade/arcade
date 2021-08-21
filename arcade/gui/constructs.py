"""
Constructs, are prepared widget combinations, you can use for common usecases
"""
import arcade
from arcade.gui.widgets import UIGroup, UIAnchorWidget, UITextArea, UIFlatButton


class UIMessageBox(UIAnchorWidget):
    """
    A simple dialog box that pops up a message with buttons to close.
    """
    def __init__(self,
                 *,
                 width: float,
                 height: float,
                 message_text: str,
                 buttons=("Ok",),
                 callback=None):
        """
        A simple dialog box that pops up a message with buttons to close.

        :param width: Width of the message box
        :param height: Height of the message box
        :param message_text:
        :param buttons: List of strings, which are shown as buttons
        :param callback: Callback method, will receive the text of the clicked button
        """

        space = 5

        self._text_area = UITextArea(text=message_text,
                                     width=height - space,
                                     height=width - space,
                                     text_color=arcade.color.BLACK)

        button_group = arcade.gui.UIBoxGroup(vertical=False)
        for button_text in buttons:
            button = UIFlatButton(text=button_text)
            button_group.add(button.with_space_around(left=10))
            button.on_click = self.on_ok

        self._bg_tex = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")

        self._callback = callback

        group = UIGroup(width=width, height=height, children=[
            UIAnchorWidget(child=self._text_area, anchor_x="left", anchor_y="top", align_x=10, align_y=-10),
            UIAnchorWidget(child=button_group, anchor_x="right", anchor_y="bottom", align_x=-10, align_y=10)
        ]).with_background(self._bg_tex)

        super().__init__(child=group)

    def on_ok(self, event):
        self.parent.remove(self)
        if self._callback is not None:
            self._callback(event.source.text)
