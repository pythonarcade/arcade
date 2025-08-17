import pathlib

import arcade
from arcade import SpriteList, Sprite
from arcade.gui import UIView

root = pathlib.Path(__file__).parent.resolve()


class MyView(UIView):
    def __init__(self):
        super().__init__()
        self.sprites = SpriteList()

        print("Loading sprites...")
        print(pathlib.Path().absolute())
        print(list(pathlib.Path().glob("*")))
        self.sprites.append(Sprite(root / "cat.png"))

    def on_draw_before_ui(self):
        self.sprites.draw()


def main():
    window = arcade.Window()
    window.run(MyView())


if __name__ == "__main__":
    main()
