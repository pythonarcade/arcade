"""
Use a custom texture for a toggle button.

The current theme is a 90s sci-fi style, but you can replace the textures
to match the theme of your game.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.toggle
"""

from __future__ import annotations

import arcade
from arcade import View, load_texture
from arcade.gui import UIManager, UIAnchorLayout
from arcade.gui.events import UIOnChangeEvent
from arcade.gui.widgets.toggle import UITextureToggle


class MyView(View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        on_texture = load_texture(":resources:gui_basic_assets/toggle/switch_green.png")
        off_texture = load_texture(":resources:gui_basic_assets/toggle/switch_red.png")
        self.toggle = UITextureToggle(on_texture=on_texture, off_texture=off_texture)

        # Add toggle to UIManager, use UIAnchorLayout to center on screen
        self.ui.add(UIAnchorLayout(children=[self.toggle]))

        # Listen for value changes
        @self.toggle.event("on_change")
        def print_oon_change(event: UIOnChangeEvent):
            print(f"New value {event.new_value}")

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.ui.draw()


if __name__ == "__main__":
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()
