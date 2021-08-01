"""
Constructs, are prepared widget combinations, you can use for common usecases
"""
import arcade
from arcade.experimental.gui_v2.widgets import Group, AnchorWidget, TextArea, FlatButton


class OKMessageBox(AnchorWidget):
    def __init__(self, *, width: float, height: float, text: str):
        space = 5

        self._text_area = TextArea(text=text, width=height - space, height=width - space, text_color=arcade.color.BLACK)
        self._ok_button = FlatButton(text="OK")

        self._bg_tex = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")

        group = Group(width=width, height=height, children=[
            AnchorWidget(child=self._text_area, anchor_x="left", anchor_y="top", align_x=10, align_y=-10),
            AnchorWidget(child=self._ok_button, anchor_x="right", anchor_y="bottom", align_x=-10, align_y=10)
        ]).with_background(self._bg_tex)

        # TODO schedule on_ok event
        self._ok_button.on_click = self.on_ok

        super().__init__(child=group)

    def on_ok(self, event):
        self.parent.remove(self)
