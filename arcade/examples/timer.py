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
        self.timer_text = arcade.Text(
            text="00:00:00",
            start_x=SCREEN_WIDTH // 2,
            start_y=SCREEN_HEIGHT // 2 - 50,
            color=arcade.color.WHITE,
            font_size=100,
            anchor_x="center",
        )

    def setup(self):
        """
        Set up the application.
        """
        arcade.set_background_color(arcade.color.ALABAMA_CRIMSON)
        self.total_time = 0.0

    def on_draw(self):
        """ Use this function to draw everything to the screen. """
        # Clear all pixels in the window
        self.clear()

        # Draw the timer text
        self.timer_text.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        # Accumulate the total time
        self.total_time += delta_time

        # Calculate minutes
        minutes = int(self.total_time) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds = int(self.total_time) % 60

        # Calculate 100s of a second
        seconds_100s = int((self.total_time - seconds) * 100)

        # Use string formatting to create a new text string for our timer
        self.timer_text.text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
