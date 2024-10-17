"""
Show a timer on-screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.timer
"""
import arcade
from arcade.clock import GLOBAL_CLOCK

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Timer Example"


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__()
        # What time to start the timer
        self.start_time: float = 0.0
        self.timer_text = arcade.Text(
            text="00:00:00",
            x=WINDOW_WIDTH // 2,
            y=WINDOW_HEIGHT // 2 - 50,
            color=arcade.color.WHITE,
            font_size=100,
            anchor_x="center",
        )
        self.background_color = arcade.color.ALABAMA_CRIMSON

    def reset(self):
        self.start_time = GLOBAL_CLOCK.time

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
        elapsed = GLOBAL_CLOCK.time_since(self.start_time)

        # Calculate minutes
        minutes = int(elapsed) // 60

        # Calculate seconds by using a modulus (remainder)
        seconds = int(elapsed) % 60

        # Calculate 100ths of a second
        seconds_100s = int((elapsed - seconds) * 100)

        # Use string formatting to create a new text string for our timer
        self.timer_text.text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"

def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()
    game.reset()

    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
