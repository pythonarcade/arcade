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
            row_count=6,
            vertical_spacing=5,
            horizontal_spacing=5
        ))

        # Texture buttons using nine patch textures
        grid.add(
            child=UITextureButton(
                texture=load_texture(":resources:gui_basic_assets/red_button_normal.png"),
                texture_hovered=load_texture(":resources:gui_basic_assets/red_button_hover.png"),
                texture_pressed=load_texture(":resources:gui_basic_assets/red_button_press.png"),
            ))

        # Texture buttons using nine patch textures
        grid.add(
            child=UITextureButton(
                texture=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=load_texture(":resources:gui_basic_assets/red_button_normal.png")),
                texture_hovered=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=load_texture(":resources:gui_basic_assets/red_button_hover.png")),
                texture_pressed=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=load_texture(":resources:gui_basic_assets/red_button_press.png"),
                )
            ),
            col_num=0,
            row_num=1)

        # Some text
        grid.add(
            child=UILabel(text="abcdefghijklmnopqrstuvwäöüABCDEFG"),
            col_num=0,
            row_num=2)

        # Simple toggle
        grid.add(
            child=UITextureToggle(
                on_texture=load_texture(":resources:gui_basic_assets/toggle/switch_green.png"),
                off_texture=load_texture(":resources:gui_basic_assets/toggle/switch_red.png")
            ),
            col_num=0,
            row_num=3)

        # Simple slider
        grid.add(
            child=UITextureSlider(
                bar=arcade.load_texture(":resources:gui_basic_assets/slider_bar.png"),
                thumb=arcade.load_texture(":resources:gui_basic_assets/slider_thumb.png"),
            ),
            col_num=0,
            row_num=4)

        # Scaled slider using ninepatch texture
        grid.add(
            child=UITextureSlider(
                bar=NinePatchTexture(
                    texture=arcade.load_texture(":resources:gui_basic_assets/slider_bar.png"),
                    left=30,
                    right=33,
                    bottom=18,
                    top=18,
                ),
                thumb=arcade.load_texture(":resources:gui_basic_assets/slider_thumb.png"),
                height=40
            ),
            col_num=0,
            row_num=5)

    def on_draw(self):
        self.clear()
        self.manager.draw()


window = UIMockup()
arcade.run()
