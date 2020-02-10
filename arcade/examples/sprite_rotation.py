"""
Sprite Collect Coins

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_collect_coins
"""

import random
import arcade
import os

# --- Constants ---
SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = .5
COIN_COUNT = 50

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sprite Collect Coins Example"


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Variables that will hold sprite lists
        self.coin_list = None

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.coin_list = arcade.SpriteList()

        # --- Rotate in place
        coin = arcade.Sprite(":resources:images/items/coinGold.png",
                             SPRITE_SCALING_COIN)

        # Position the coin
        coin.center_x = 50
        coin.center_y = SCREEN_HEIGHT / 2
        coin.change_angle = 1

        # Add the coin to the lists
        self.coin_list.append(coin)

        # --- Rotate around relative center
        coin = arcade.Sprite(":resources:images/items/coinGold.png",
                             SPRITE_SCALING_COIN)

        # Position the coin
        coin.center_x = 150
        coin.center_y = SCREEN_HEIGHT / 2
        coin.rotation_point = (25, 0)
        coin.rot_point_relative = True
        coin.change_angle = 1

        # Add the coin to the lists
        self.coin_list.append(coin)

        # --- Rotate around absolute center
        coin = arcade.Sprite(":resources:images/items/coinGold.png",
                             SPRITE_SCALING_COIN)

        # Position the coin
        coin.center_x = 250
        coin.center_y = SCREEN_HEIGHT / 2
        coin.rotation_point = (250 + 10, SCREEN_HEIGHT / 2)
        coin.rot_point_relative = False
        coin.change_angle = 1

        # Add the coin to the lists
        self.coin_list.append(coin)


    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        self.coin_list.draw()

    def on_update(self, delta_time):
        """ Movement and game logic """

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.coin_list.update()


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
