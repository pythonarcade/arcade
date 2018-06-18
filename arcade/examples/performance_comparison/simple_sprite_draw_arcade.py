"""
Sprite Stress Test

Simple program to test how fast we can draw sprites that aren't moving

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.stress_test_draw_simple
"""

import arcade
import timeit

# --- Constants ---

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Sprite Example")

        self.draw_time = 0

        arcade.set_background_color(arcade.color.WHITE)

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()

        # Create the coins
        for x in range(0, SCREEN_WIDTH, 10):
            for y in range(0, SCREEN_HEIGHT, 10):

                # Create the coin instance
                # Coin image from kenney.nl
                coin = arcade.Sprite("../images/coin_01.png", 0.05)

                # Position the coin
                coin.center_x = x
                coin.center_y = y

                # Add the coin to the lists
                self.all_sprites_list.append(coin)

    def on_draw(self):
        """ Draw everything """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        arcade.start_render()
        self.all_sprites_list.draw()

        self.draw_time = timeit.default_timer() - draw_start_time

        # Display timings
        sprite_count = len(self.all_sprites_list)
        output = f"Drawing time: {self.draw_time:.4f} for {sprite_count} sprites."
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.BLACK, 16)



def main():
    """ Main method """
    window = MyGame()
    arcade.run()

if __name__ == "__main__":
    main()
