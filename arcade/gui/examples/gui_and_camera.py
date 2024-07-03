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

        # in-game counter
        self._total_time = 0
        self._last_coin_spawn = 0
        self._coins_collected = 0

        # upgradable player values
        self._player_speed = 5

        # setup in-game objects
        self.sprites = arcade.SpriteList()

        self.game_area = arcade.SpriteSolidColor(
            width=1300,
            height=730,
            color=arcade.color.GRAY_ASPARAGUS,
            center_x=1280 / 2,
            center_y=720 / 2,
        )

        self.sprites.append(self.game_area)

        self.player = arcade.Sprite(
            ":resources:/images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            scale=0.5,
            center_x=1280 / 2,
            center_y=720 / 2,
        )
        self.sprites.append(self.player)

        self.coins = arcade.SpriteList()
        for i in range(9):
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                scale=0.5,
                center_x=150 * i,
                center_y=720 / 2,
            )
            self.coins.append(coin)

        # UI setup, we use UIView, which automatically adds UIManager as self.ui
        anchor = self.ui.add(UIAnchorLayout())
        button = UIFlatButton(text="Get faster: 5 Coins", width=200, height=40)
        anchor.add(button, anchor_x="center_x", anchor_y="bottom", align_y=10)

        @button.event("on_click")
        def upgrade_speed(event: UIOnClickEvent):
            cost = self._player_speed
            if self._coins_collected >= cost:
                self._coins_collected -= cost
                self._player_speed += 1
                button.text = f"Get faster: {self._player_speed} Coins"
                print("Speed upgraded")

        # position top center, with a 40px offset
        self.out_of_game_area = anchor.add(
            UILabel(text="Out of game area", font_size=32),
            anchor_x="center",
            anchor_y="top",
            align_y=-40,
        )
        self.out_of_game_area.visible = False

        self.coin_counter = anchor.add(
            UILabel(text="Collected coins 0"),
            anchor_x="left",
            anchor_y="top",
            align_y=-10,
            align_x=10,
        )
        self.coin_counter.with_background(
            color=arcade.color.TRANSPARENT_BLACK
            # giving a background will make the label way more performant,
            # because it will not re-render the whole UI after a text change
        )

    def on_draw_before_ui(self):
        self.ingame_camera.use()  # use the in-game camera to draw in-game objects
        self.sprites.draw()
        self.coins.draw()

    def on_update(self, delta_time: float) -> Optional[bool]:
        self._total_time += delta_time
        self._last_coin_spawn += delta_time

        # spawn new coins
        if self._last_coin_spawn > 3:
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                scale=0.5,
                center_x=random.randint(0, 1280),
                center_y=random.randint(0, 720),
            )
            self.coins.append(coin)
            self._last_coin_spawn = 0

        # move the player sprite
        if {arcade.key.LEFT, arcade.key.A} & self.keys:
            self.player.left -= self._player_speed
        if {arcade.key.RIGHT, arcade.key.D} & self.keys:
            self.player.left += self._player_speed
        if {arcade.key.UP, arcade.key.W} & self.keys:
            self.player.top += self._player_speed
        if {arcade.key.DOWN, arcade.key.S} & self.keys:
            self.player.top -= self._player_speed

        # move the camera with the player
        self.ingame_camera.position = self.player.position

        # collect coins
        collisions = self.player.collides_with_list(self.coins)
        for coin in collisions:
            coin.remove_from_sprite_lists()
            self._coins_collected += 1
            print("Coin collected")

        # update the coin counter
        self.coin_counter.text = f"Collected coins {self._coins_collected}"
        self.coin_counter.fit_content()

        # inform player if they are out of the game area
        if not self.game_area.collides_with_sprite(self.player):
            self.out_of_game_area.visible = True
        else:
            self.out_of_game_area.visible = False

        # test to rotate the UI camera
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
