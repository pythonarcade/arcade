"""
A combination of multiple widgets from other examples

See the other GUI examples for more information.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.widget_gallery
"""

from __future__ import annotations

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
    UIBoxLayout,
    UISlider,
)
from arcade.gui.examples.textured_slider import UITextureSlider
from arcade.gui.widgets.layout import UIAnchorLayout

# Preload textures, because they are mostly used multiple times, so they are not
# loaded multiple times
TEX_RED_BUTTON_NORMAL = load_texture(":resources:gui_basic_assets/red_button_normal.png")
TEX_RED_BUTTON_HOVER = load_texture(":resources:gui_basic_assets/red_button_hover.png")
TEX_RED_BUTTON_PRESS = load_texture(":resources:gui_basic_assets/red_button_press.png")
TEX_SWITCH_RED = load_texture(":resources:gui_basic_assets/toggle/switch_red.png")
TEX_SWITCH_GREEN = load_texture(":resources:gui_basic_assets/toggle/switch_green.png")
TEX_SLIDER_THUMB = arcade.load_texture(":resources:gui_basic_assets/slider_thumb.png")
TEX_SLIDER_TRACK = arcade.load_texture(":resources:gui_basic_assets/slider_track.png")


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        anchor = self.ui.add(UIAnchorLayout())
        grid = anchor.add(
            UIGridLayout(
                size_hint=(0.9, 0.9),
                column_count=2,
                row_count=7,
                vertical_spacing=5,
                horizontal_spacing=5,
            )
        )

        # Texture buttons using nine patch textures
        grid.add(
            col_num=0,
            row_num=0,
            child=UITextureButton(
                texture=TEX_RED_BUTTON_NORMAL,
                texture_hovered=TEX_RED_BUTTON_HOVER,
                texture_pressed=TEX_RED_BUTTON_PRESS,
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
                    texture=TEX_RED_BUTTON_NORMAL,
                ),
                texture_hovered=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=TEX_RED_BUTTON_HOVER,
                ),
                texture_pressed=NinePatchTexture(
                    left=5,
                    right=5,
                    bottom=5,
                    top=5,
                    texture=TEX_RED_BUTTON_PRESS,
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

        toggles = grid.add(
            UIBoxLayout(space_between=10, vertical=False),
            col_num=0,
            row_num=3,
        )
        toggles.add(
            UITextureToggle(
                on_texture=TEX_SWITCH_GREEN,
                off_texture=TEX_SWITCH_RED,
            )
        )
        toggles.add(
            UITextureToggle(
                on_texture=TEX_SWITCH_GREEN,
                off_texture=TEX_SWITCH_RED,
            )
        ).disabled = True

        # Simple slider
        grid.add(
            col_num=0,
            row_num=4,
            child=UITextureSlider(
                track=TEX_SLIDER_TRACK,
                thumb=TEX_SLIDER_THUMB,
            ),
        )

        # Scaled slider using ninepatch texture
        grid.add(
            col_num=0,
            row_num=5,
            child=UITextureSlider(
                track=NinePatchTexture(
                    texture=TEX_SLIDER_TRACK,
                    left=30,
                    right=33,
                    bottom=18,
                    top=18,
                ),
                thumb=TEX_SLIDER_THUMB,
                height=40,
            ),
        )

        # Simple slider
        grid.add(
            col_num=0,
            row_num=6,
            child=UISlider(),
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


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
