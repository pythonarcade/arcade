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
import time
import collections
import pyglet.gl as gl
import matplotlib.pyplot as plt

# --- Constants ---
SPRITE_SCALING_COIN = 0.09
COIN_COUNT_INCREMENT = 15000

SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "Static Sprite Stress Test"


class FPSCounter:
    def __init__(self):
        self.time = time.perf_counter()
        self.frame_times = collections.deque(maxlen=60)

    def tick(self):
        t1 = time.perf_counter()
        dt = t1 - self.time
        self.time = t1
        self.frame_times.append(dt)

    def get_fps(self):
        total_time = sum(self.frame_times)
        if total_time == 0:
            return 0
        else:
            return len(self.frame_times) / sum(self.frame_times)


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.coin_list = None

        self.processing_time = 0
        self.draw_time = 0
        self.program_start_time = timeit.default_timer()
        self.sprite_count_list = []
        self.fps_list = []
        self.processing_time_list = []
        self.drawing_time_list = []
        self.last_fps_reading = 0
        self.fps = FPSCounter()

        arcade.set_background_color(arcade.color.AMAZON)

    def add_coins(self):

        # Create the coins
        for i in range(COIN_COUNT_INCREMENT):
            # Create the coin instance
            # Coin image from kenney.nl
            coin = arcade.Sprite("images/coin_01.png", SPRITE_SCALING_COIN)

            # Position the coin
            coin.center_x = random.randrange(SCREEN_WIDTH)
            coin.center_y = random.randrange(SCREEN_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.coin_list = arcade.SpriteList(use_spatial_hash=False, is_static=True)

    def on_draw(self):
        """ Draw everything """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        arcade.start_render()

        # Display sprites
        self.coin_list.draw()

        # Display info on sprites
        output = f"Sprite count: {len(self.coin_list):,}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.BLACK, 16)

        # Display timings
        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.BLACK, 16)

        fps = self.fps.get_fps()
        output = f"FPS: {fps:3.0f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.BLACK, 16)

        self.draw_time = timeit.default_timer() - draw_start_time
        self.fps.tick()

        gl.glFlush()

    def update(self, delta_time):

        # Total time program has been running
        total_program_time = int(timeit.default_timer() - self.program_start_time)

        # Print out stats, or add more sprites
        if total_program_time > self.last_fps_reading:
            self.last_fps_reading = total_program_time

            # It takes the program a while to "warm up", so the first
            # few seconds our readings will be off. So wait some time
            # before taking readings
            if total_program_time > 5:

                # We want the program to run for a while before taking
                # timing measurements. We don't want the time it takes
                # to add new sprites to be part of that measurement. So
                # make sure we have a clear second of nothing but
                # running the sprites, and not adding the sprites.
                if total_program_time % 5 == 1:

                    # Take timings
                    print(f"{total_program_time}, {len(self.coin_list)}, {self.fps.get_fps():.1f}, {self.processing_time:.4f}, {self.draw_time:.4f}")
                    self.sprite_count_list.append(len(self.coin_list))
                    self.fps_list.append(round(self.fps.get_fps(), 1))
                    self.processing_time_list.append(self.processing_time)
                    self.drawing_time_list.append(self.draw_time)

                    # Now add the coins
                    self.add_coins()


def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()

    # Plot our results
    plt.plot(window.sprite_count_list, window.drawing_time_list, label="Drawing Time")

    plt.legend(loc='upper left', shadow=True, fontsize='x-large')

    plt.ylabel('Time')
    plt.xlabel('Sprite Count')

    plt.show()

    # Plot our results
    plt.plot(window.sprite_count_list, window.fps_list)

    plt.ylabel('FPS')
    plt.xlabel('Sprite Count')

    plt.show()


if __name__ == "__main__":
    main()
