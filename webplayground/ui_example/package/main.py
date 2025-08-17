import arcade
from arcade.gui import UIView, UILabel, UIAnchorLayout, NinePatchTexture

TEX_NINEPATCH_BASE = arcade.load_texture(":resources:gui_basic_assets/window/grey_panel.png")


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.background_color = arcade.color.GREEN

        root = self.ui.add(UIAnchorLayout())
        root.with_background(
            texture=NinePatchTexture(
                texture=TEX_NINEPATCH_BASE,
                left=7,
                right=7,
                bottom=7,
                top=7,
            )
        )
        root.with_border(width=2, color=arcade.color.RED)

        root.add(UILabel(text="Hello World")).with_background(color=(255, 0, 0, 255))

    def on_key_press(self, symbol, mod):
        print(self.window.size)


def main():
    window = arcade.Window()
    window.run(MyView())


if __name__ == "__main__":
    main()
