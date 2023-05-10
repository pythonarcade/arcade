"""
A combination of multiple widgets from other examples

See the other GUI examples for more information.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.widget_gallery
"""
from textwrap import dedent

import arcade
from arcade import load_texture
from arcade.gui import (
    UIManager,
    UITextureButton,
    UIGridLayout,
    NinePatchTexture,
    UILabel,
    UITextureToggle,
    UITextArea,
    UIInputText,
)
from arcade.gui.examples.textured_slider import UITextureSlider
from arcade.gui.widgets.layout import UIAnchorLayout


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        anchor = self.ui.add(UIAnchorLayout())
        grid = anchor.add(
            UIGridLayout(
                size_hint=(0.9, 0.9),
                column_count=2,
                row_count=6,
                vertical_spacing=5,
                horizontal_spacing=5,
            )
        )

        # Texture buttons using nine patch textures
        grid.add(
            col_num=0,
            row_num=0,
            child=UITextureButton(
                texture=load_texture(
                    ":resources:gui_basic_assets/red_button_normal.png"
                ),
                texture_hovered=load_texture(
                    ":resources:gui_basic_assets/red_button_hover.png"
                ),
                texture_pressed=load_texture(
                    ":resources:gui_basic_assets/red_button_press.png"
                ),
            ),
        )

        # Texture buttons using nine patch textures
        grid.add(
            col_num=0,
            row_num=1,
            child=UITextureButton(
                texture=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=load_texture(
                        ":resources:gui_basic_assets/red_button_normal.png"
                    ),
                ),
                texture_hovered=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=load_texture(
                        ":resources:gui_basic_assets/red_button_hover.png"
                    ),
                ),
                texture_pressed=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=load_texture(
                        ":resources:gui_basic_assets/red_button_press.png"
                    ),
                ),
            ),
        )

        # Some text
        grid.add(
            col_num=0,
            row_num=2,
            child=UILabel(text="abcdefghijklmnopqrstuvwäöüABCDEFG"),
        )

        # Simple toggle
        grid.add(
            col_num=0,
            row_num=3,
            child=UITextureToggle(
                on_texture=load_texture(
                    ":resources:gui_basic_assets/toggle/switch_green.png"
                ),
                off_texture=load_texture(
                    ":resources:gui_basic_assets/toggle/switch_red.png"
                ),
            ),
        )

        # Simple slider
        grid.add(
            col_num=0,
            row_num=4,
            child=UITextureSlider(
                bar=arcade.load_texture(":resources:gui_basic_assets/slider_bar.png"),
                thumb=arcade.load_texture(
                    ":resources:gui_basic_assets/slider_thumb.png"
                ),
            ),
        )

        # Scaled slider using ninepatch texture
        grid.add(
            col_num=0,
            row_num=5,
            child=UITextureSlider(
                bar=NinePatchTexture(
                    texture=arcade.load_texture(
                        ":resources:gui_basic_assets/slider_bar.png"
                    ),
                    left=30,
                    right=33,
                    bottom=18,
                    top=18,
                ),
                thumb=arcade.load_texture(
                    ":resources:gui_basic_assets/slider_thumb.png"
                ),
                height=40,
            ),
        )

        # Input text
        grid.add(col_num=1, row_num=0, child=UIInputText(width=300).with_border())

        example_text = dedent(
            """
        Gamers can feel when developers are passionate about their games.
        They can smell it like a dog smells fear.
        Don't be afraid to hold onto your unique vision:
        just be aware that it may not turn out exactly how you envisioned.
        """
        )

        grid.add(
            col_num=1,
            row_num=1,
            row_span=2,
            child=UITextArea(text=example_text, height=150).with_border(),
        )

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        # Disable UIManager when view gets inactive
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == '__main__':
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
