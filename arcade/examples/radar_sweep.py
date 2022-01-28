"""
This animation example shows how perform a radar sweep animation.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.radar_sweep
"""

import arcade
import math

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Radar Sweep Example"

# These constants control the particulars about the radar
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2
RADIANS_PER_FRAME = 0.02
SWEEP_LENGTH = 250


class Radar:
    def __init__(self):
        self.angle = 0

    def update(self):

        # Move the angle of the sweep.
        self.angle += RADIANS_PER_FRAME

    def draw(self):
        """ Use this function to draw everything to the screen. """

        # Calculate the end point of our radar sweep. Using math.
        x = SWEEP_LENGTH * math.sin(self.angle) + CENTER_X
        y = SWEEP_LENGTH * math.cos(self.angle) + CENTER_Y

        # Start the render. This must happen before any drawing
        # commands. We do NOT need an stop render command.
        arcade.start_render()

        # Draw the radar line
        arcade.draw_line(CENTER_X, CENTER_Y, x, y, arcade.color.OLIVE, 4)

        # Draw the outline of the radar
        arcade.draw_circle_outline(CENTER_X,
                                   CENTER_Y,
                                   SWEEP_LENGTH,
                                   arcade.color.DARK_GREEN,
                                   border_width=10,
                                   num_segments=60)


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Create our rectangle
        self.radar = Radar()

        # Set background color
        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, delta_time):
        # Move the rectangle
        self.radar.update()

    def on_draw(self):
        """ Render the screen. """

        # Clear screen
        self.clear()
        # Draw the rectangle
        self.radar.draw()


def main():
    """ Main function """
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
