"""
Sprite Stress Test

Simple program to test how fast we can draw sprites that aren't moving

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.stress_test_draw_simple
"""

import random
import arcade
import os
import timeit

# --- Constants ---
SPRITE_SCALING_COIN = 0.09
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING_COIN)
COIN_COUNT = 3000

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Sprite Example")

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.all_sprites_list = None
        self.coin_list = None

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        self.processing_time = 0
        self.draw_time = 0

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # Create the coins
        for i in range(COIN_COUNT):

            # Create the coin instance
            # Coin image from kenney.nl
            coin = arcade.Sprite("images/coin_01.png", SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(SPRITE_SIZE, SCREEN_WIDTH - SPRITE_SIZE)
            coin.center_y = random.randrange(SPRITE_SIZE, SCREEN_HEIGHT - SPRITE_SIZE)

            coin.change_x = random.randrange(-3, 4)
            coin.change_y = random.randrange(-3, 4)

            # Add the coin to the lists
            self.all_sprites_list.append(coin)
            self.coin_list.append(coin)

    def on_draw(self):
        """ Draw everything """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        arcade.start_render()
        self.all_sprites_list.draw()

        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.BLACK, 16)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.BLACK, 16)

        fps = 1 / (self.draw_time + self.processing_time)
        output = f"Max FPS: {fps:3.1f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.BLACK, 16)

        self.draw_time = timeit.default_timer() - draw_start_time

    def update(self, delta_time):
        start_time = timeit.default_timer()
        self.all_sprites_list.update()
        for sprite in self.all_sprites_list:

            # Using left/right/top/bottom can be 10 times slower than position[0]
            # for x, and position[1] for y.

            # if sprite.left < 0:
            #     sprite.change_x *= -1
            # if sprite.right > SCREEN_WIDTH:
            #     sprite.change_x *= -1
            # if sprite.bottom < 0:
            #     sprite.change_y *= -1
            # if sprite.top > SCREEN_HEIGHT:
            #     sprite.change_y *= -1

            if sprite.position[0] < 0:
                sprite.change_x *= -1
            if sprite.position[0] > SCREEN_WIDTH:
                sprite.change_x *= -1
            if sprite.position[1] < 0:
                sprite.change_y *= -1
            if sprite.position[1] > SCREEN_HEIGHT:
                sprite.change_y *= -1

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
