"""
This example procedurally develops a random cave based on cellular automata.

For more information, see:
https://gamedevelopment.tutsplus.com/tutorials/generate-random-cave-levels-using-cellular-automata--gamedev-9664
"""

import random
import arcade
import timeit

# How big the window is
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, resizable=True)

        self.draw_time = 0.0
        self.processing_time = 0.0
        self.program_start_time = timeit.default_timer()
        self.run_time = 0.0
        self.y = 0

        self.line = arcade.create_line(500, 50, 0, 700, (255, 255, 0, 200), 10)
        arcade.set_background_color(arcade.color.BLACK)


    def on_draw(self):
        """ Render the screen. """

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        arcade.draw_line(0, 0, 500, 500, arcade.color.WHITE, 10)
        arcade.draw_line(0, 50, 500, 550, arcade.color.RED, 10)
        arcade.draw_line(0, 100, 500, 600, arcade.color.GREEN, 10)
        arcade.draw_line(0, 150, 500, 650, arcade.color.BLUE, 10)
        arcade.draw_line(500, 0, 0, 650, (255, 0, 0, 127), 10)
        self.line.draw()

        self.draw_time = timeit.default_timer() - draw_start_time


    def on_resize(self, width, height):

        arcade.set_viewport(0,
                            self.width,
                            0,
                            self.height)

    def update(self, delta_time):
        """ Movement and game logic """

        start_time = timeit.default_timer()

        self.run_time = timeit.default_timer() - self.program_start_time

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


def main():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
