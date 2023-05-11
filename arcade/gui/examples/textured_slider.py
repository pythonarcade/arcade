"""
Create a slider using a custom texture subclass

The initial theme is a 90s sci-fi style, but you can replace the textures
in this example to match the theme of your project.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.textured_slider
"""
from typing import Union

import arcade
from arcade import Texture
from arcade.gui import UIManager
from arcade.gui.widgets.slider import UITextureSlider


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        bar_tex = arcade.load_texture(":resources:gui_basic_assets/slider_bar.png")
        thumb_tex = arcade.load_texture(":resources:gui_basic_assets/slider_thumb.png")
        self.slider = UITextureSlider(bar_tex, thumb_tex)

        # Add button to UIManager, use UIAnchorWidget defaults to center on screen
        self.ui.add(UIAnchorLayout(children=[self.slider]))

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.slider.disabled = not self.slider.disabled

    def on_draw(self):
        self.clear()
        self.ui.draw()


if __name__ == '__main__':
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
