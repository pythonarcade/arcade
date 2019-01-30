"""
Show a timer on-screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.timer
"""

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Timer Example"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.total_time = 0.0

    def setup(self):
        """
        Set up the application.
        """
        arcade.set_background_color(arcade.color.WHITE)
        self.total_time = 0.0

    def on_draw(self):
        """ Use this function to draw everything to the screen. """

        # Start the render. This must happen before any drawing
        # commands. We do NOT need an stop render command.
        arcade.start_render()

        # Calculate minutes
        minutes = int(self.total_time) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60

        # Figure out our output
        output = f"Time: {minutes:02d}:{seconds:02d}"

        # Output the timer text.
        arcade.draw_text(output, 300, 300, arcade.color.BLACK, 30)

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        self.total_time += delta_time


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
