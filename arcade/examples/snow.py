"""
Simple Snow
Based primarily on:
https://api.arcade.academy/en/latest/examples/sprite_collect_coins_move_down.html

Contributed to Python Arcade Library by Nicholas Hartunian

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.snow
"""

import random
import math
import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Snow"
SNOWFLAKE_COUNT = 800


class Snowflake(arcade.SpriteCircle):
    """
    Each instance of this class represents a single snowflake.
    Based on drawing filled-circles.
    """

    def __init__(self, size, speed, drift):
        super().__init__(size, arcade.color.WHITE)
        self.speed = speed
        self.drift = drift

    def reset_pos(self):
        # Reset flake to random position above screen
        self.position = (
            random.randrange(SCREEN_WIDTH),
            random.randrange(SCREEN_HEIGHT, SCREEN_HEIGHT + 100),
        )

    def on_update(self, delta_time: float = 1/60) -> None:
        self.center_y -= self.speed * delta_time

        # Check if snowflake has fallen below screen
        if self.center_y < 0:
            self.reset_pos()

        # Some math to make the snowflakes move side to side
        self.center_x += self.speed * math.cos(self.drift) * delta_time
        self.drift += 1 * delta_time


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """ Initializer """
        # Calls "__init__" of parent class (arcade.Window) to setup screen
        super().__init__(width, height, title)

        self.snowflake_list = arcade.SpriteList()

        # Don't show the mouse pointer
        self.set_mouse_visible(False)

        # Set the background color
        self.background_color = arcade.color.BLACK

    def start_snowfall(self):
        """ Set up snowfall and initialize variables. """
        for i in range(SNOWFLAKE_COUNT):
            # Create snowflake instance
            snowflake = Snowflake(
                size=random.randrange(1, 4),
                speed=random.randrange(20, 40),
                drift=random.uniform(math.pi, math.pi * 2),
            )
            # Randomly position snowflake
            snowflake.position = (
                random.randrange(SCREEN_WIDTH),
                random.randrange(SCREEN_HEIGHT + 200),
            )
            # Add snowflake to snowflake list
            self.snowflake_list.append(snowflake)

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen to the background color
        self.clear()

        # Draw the current position of each snowflake
        self.snowflake_list.draw()

    def on_update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        # Call update on all the snowflakes
        self.snowflake_list.on_update(delta_time)


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.start_snowfall()
    arcade.run()


if __name__ == "__main__":
    main()
