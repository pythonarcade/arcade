"""
Arrange widgets in vertical or horizontal lines with UIBoxLayout

The direction UIBoxLayout follows is controlled by the `vertical` keyword
argument. It is True by default. Pass False to it to arrange elements in
a horizontal line.

If arcade and Python are properly installed, you can run this example with:
python -m arcade.gui.examples.gui_and_camera
"""

from __future__ import annotations

import random
from typing import Optional

import arcade
from arcade.gui import UIView, UIFlatButton, UIOnClickEvent, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout


class MyCoinGame(UIView):
    """
    Main view of the game. This class is a subclass of UIView, which provides
    basic GUI setup. We add UIManager to the view under `self.ui`.

    The example showcases how to:
    - use UIView to setup a basic GUI
    - add a button to the view and connect it to a function
    - use camera to move the view

    """

    def __init__(self):
        super().__init__()

        # basic camera setup
        self.keys = set()
        self.ingame_camera = arcade.Camera2D()
        self.ingame_camera.bottom_left = 100, 100

        # timer setup
        self.total_time = 0

        # setup in-game objects
        self.sprites = arcade.SpriteList()

        self.game_area = arcade.SpriteSolidColor(
            width=1280,
            height=720,
            color=arcade.color.GRAY_ASPARAGUS,
            center_x=1280 / 2,
            center_y=720 / 2,
        )

        self.sprites.append(self.game_area)

        self.player = arcade.Sprite(
            ":resources:/images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=0.5,
            center_x=1280 / 2,
            center_y=720 / 2
        )
        self.sprites.append(self.player)

        self.coins = arcade.SpriteList()
        for i in range(9):
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                scale=0.5,
                center_x=150 * i,
                center_y=720 / 2
            )
            self.coins.append(coin)

        # UI setup, we use UIView, which automatically adds UIManager as self.ui
        anchor = self.ui.add(UIAnchorLayout())
        button = UIFlatButton(text="Add a coin")
        anchor.add(button, anchor_x="center_x", anchor_y="bottom", align_y=10)

        self.coin_counter = anchor.add(UILabel(text="Collected coins 0"), anchor_x="left", anchor_y="top", align_y=-10, align_x=10)
        self.coin_counter.with_background(color=arcade.color.TRANSPARENT_BLACK)


        # Connect button to a function
        @button.event("on_click")
        def add_coin(event: UIOnClickEvent):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", scale=0.5)
            coin.center_x = random.randint(0, 1280)
            coin.center_y = random.randint(0, 720)
            self.coins.append(coin)

    def on_draw_before_ui(self):
        self.ingame_camera.use()  # use the in-game camera to draw in-game objects
        self.sprites.draw()
        self.coins.draw()

    def on_update(self, delta_time: float) -> Optional[bool]:
        self.total_time += delta_time

        # move the player sprite
        if {arcade.key.LEFT, arcade.key.A} & self.keys:
            self.player.left -= 5
        if {arcade.key.RIGHT, arcade.key.D} & self.keys:
            self.player.left += 5
        if {arcade.key.UP, arcade.key.W} & self.keys:
            self.player.top += 5
        if {arcade.key.DOWN, arcade.key.S} & self.keys:
            self.player.top -= 5

        # move the camera with the player
        self.ingame_camera.position = self.player.position

        # collect coins
        collisions = self.player.collides_with_list(self.coins)
        for coin in collisions:
            coin.remove_from_sprite_lists()
            print("Coin collected")

        # self.ui.camera.angle = self.total_time * 100  # rotate the UI camera

        return False

    def on_key_press(self, symbol: int, modifiers: int) -> Optional[bool]:
        self.keys.add(symbol)
        return False

    def on_key_release(self, symbol: int, modifiers: int) -> Optional[bool]:
        self.keys.remove(symbol)
        return False


if __name__ == "__main__":
    window = arcade.Window(1280, 720, "CoinGame Example", resizable=True)
    window.background_color = arcade.color.DARK_BLUE_GRAY
    window.show_view(MyCoinGame())
    window.run()
