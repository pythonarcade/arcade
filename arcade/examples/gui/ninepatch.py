"""Create custom scalable UI themes with NinePatchTexture

Nine-patch textures are a technique for scalable custom borders and
frames for UI elements. Widgets which support a background texture can
also use a NinePatchTexture to support scaling where the corners stay the
same, like a window.

If Arcade and Python are properly installed, you can run this example with:
python -m arcade.examples.gui.ninepatch
"""

import arcade
from arcade import load_texture
from arcade.gui import UIManager, UIAnchorLayout, UIWidget, NinePatchTexture


class MyView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui = UIManager()

        # Setup widget and use background with ninepatch information
        self.nine_patch_widget = UIWidget(size_hint=(0.5, 0.5))
        self.nine_patch_widget.with_background(
            texture=NinePatchTexture(
                texture=load_texture(":resources:gui_basic_assets/window/grey_panel.png"),
                left=7,
                right=7,
                bottom=7,
                top=7,
            )
        )

        self.ui.add(UIAnchorLayout(children=[self.nine_patch_widget]))

    def on_show_view(self):
        self.window.background_color = arcade.color.DARK_BLUE_GRAY
        # Enable UIManager when view is shown to catch window events
        self.ui.enable()

    def on_hide_view(self):
        self.ui.disable()

    def on_draw(self):
        self.clear()
        self.ui.draw()


def main():
    window = arcade.Window(800, 600, "UIExample", resizable=True)
    window.show_view(MyView())
    window.run()


if __name__ == "__main__":
    main()
