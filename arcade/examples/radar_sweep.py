"""
This animation example shows how perform a radar sweep animation.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.radar_sweep
"""
import arcade
import math

# Set up the constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Radar Sweep Example"

# These constants control the particulars about the radar
CENTER_X = WINDOW_WIDTH // 2
CENTER_Y = WINDOW_HEIGHT // 2
RADIANS_PER_FRAME = 0.02
SWEEP_LENGTH = 250


class Radar:
    def __init__(self):
        self.angle = 0

    def update(self, delta_time=0):
        # Move the angle of the sweep.
        self.angle += RADIANS_PER_FRAME * delta_time

    def draw(self):
        """ Use this function to draw everything to the screen. """

        # Calculate the end point of our radar sweep. Using math.
        x = SWEEP_LENGTH * math.sin(self.angle) + CENTER_X
        y = SWEEP_LENGTH * math.cos(self.angle) + CENTER_Y

        # Draw the radar line
        arcade.draw_line(CENTER_X, CENTER_Y, x, y, arcade.color.OLIVE, 4)

        # Draw the outline of the radar
        arcade.draw_circle_outline(CENTER_X,
                                   CENTER_Y,
                                   SWEEP_LENGTH,
                                   arcade.color.DARK_GREEN,
                                   border_width=10,
                                   num_segments=60)


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()

        # Create our rectangle
        self.radar = Radar()

        # Set background color
        self.background_color = arcade.color.BLACK

    def on_update(self, delta_time):
        # Move the rectangle
        self.radar.update(delta_time * 60)

    def on_draw(self):
        """Draw the screen"""
        # Clear screen
        self.clear()
        # Draw the rectangle
        self.radar.draw()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
