"""
Constructs, are prepared widget combinations, you can use for common usecases
"""
import arcade
from arcade.gui.widgets import UIGroup, UIAnchorWidget, UITextArea, UIFlatButton


class OKMessageBox(UIAnchorWidget):
    def __init__(self, *, width: float, height: float, text: str):
        space = 5

        self._text_area = UITextArea(text=text, width=height - space, height=width - space, text_color=arcade.color.BLACK)
        self._ok_button = UIFlatButton(text="OK")

        self._bg_tex = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")

        group = UIGroup(width=width, height=height, children=[
            UIAnchorWidget(child=self._text_area, anchor_x="left", anchor_y="top", align_x=10, align_y=-10),
            UIAnchorWidget(child=self._ok_button, anchor_x="right", anchor_y="bottom", align_x=-10, align_y=10)
        ]).with_background(self._bg_tex)

        # TODO schedule on_ok event
        self._ok_button.on_click = self.on_ok

        super().__init__(child=group)

    def on_ok(self, event):
        self.parent.remove(self)
