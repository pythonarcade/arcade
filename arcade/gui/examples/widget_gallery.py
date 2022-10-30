"""
Example shows how to use UIAnchorWidget to position widgets on screen.
Dummy widgets indicate hovered, pressed and clicked.
"""

import arcade
from arcade import load_texture
from arcade.gui import UIManager, UITextureButton, UIGridLayout, NinePatchTexture
from arcade.gui.widgets.layout import UIAnchorLayout


class UIMockup(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "UI Gallery", resizable=True)
        self.manager = UIManager()
        self.manager.enable()
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        anchor = self.manager.add(UIAnchorLayout())
        grid = anchor.add(UIGridLayout(
            size_hint=(0.9, 0.9),
            column_count=2,
            row_count=5,
            vertical_spacing=5,
            horizontal_spacing=5
        ))

        grid.add(
            child=UITextureButton(
                texture=load_texture(":resources:gui_basic_assets/red_button_normal.png"),
                texture_hovered=load_texture(":resources:gui_basic_assets/red_button_hover.png"),
                texture_pressed=load_texture(":resources:gui_basic_assets/red_button_press.png"),
            ))
        grid.add(
            child=UITextureButton(
                texture=NinePatchTexture(texture=load_texture(":resources:gui_basic_assets/red_button_normal.png"),
                                         start=(0, 0), end=(190, 49)),
                texture_hovered=NinePatchTexture(
                    texture=load_texture(":resources:gui_basic_assets/red_button_hover.png"),
                    start=(100, 50), end=(190, 49)),
                texture_pressed=NinePatchTexture(
                    texture=load_texture(":resources:gui_basic_assets/red_button_press.png"),
                    start=(100, 50), end=(190, 49)),
            ),
            col_num=0,
            row_num=1)

        button = UITextureButton(
            texture=load_texture(":resources:gui_basic_assets/red_button_normal.png"),
            texture_hovered=load_texture(":resources:gui_basic_assets/red_button_hover.png"),
            texture_pressed=load_texture(":resources:gui_basic_assets/red_button_press.png"),
        )
        button.rect = button.rect.resize(width=150, height=80)

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = UIMockup()
arcade.run()
