"""
Example shows how to use UIAnchorWidget to position widgets on screen.
Dummy widgets indicate hovered, pressed and clicked.
"""

import arcade
from arcade import load_texture
from arcade.gui import UIManager, UITextureButton, UIGridLayout, NinePatchTexture, UILabel, UITextureToggle
from arcade.gui.examples.textured_slider import UITextureSlider
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

        grid.add(
            child=UILabel(text="abcdefghijklmnopqrstuvwäöüABCDEFG"),
            col_num=0,
            row_num=2)

        grid.add(
            child=UITextureToggle(
                on_texture=load_texture(":resources:gui_basic_assets/toggle/switch_green.png"),
                off_texture=load_texture(":resources:gui_basic_assets/toggle/switch_red.png")
            ),
            col_num=0,
            row_num=3)
        grid.add(
            child=UITextureSlider(
                bar=arcade.load_texture(":resources:gui_basic_assets/slider_bar.png"),
                thumb=arcade.load_texture(":resources:gui_basic_assets/slider_thumb.png"),
            ),
            col_num=0,
            row_num=4)

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = UIMockup()
arcade.run()
