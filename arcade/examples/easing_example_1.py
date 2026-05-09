"""
Easing Example 1

Demonstrate the different easing functions available in :py:mod:`arcade.anim`.
Each ball uses a different easing curve to travel from left to right, making it
easy to compare the visual character of each curve.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.easing_example_1
"""

import arcade
from arcade.anim import ease, Easing

# --- Constants ---
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Easing Example 1"

X_START = 40
X_END = 1200
Y_INTERVAL = 60
BALL_RADIUS = 13
LINE_WIDTH = 1.0
TRAVEL_TIME = 3.0

BACKGROUND_COLOR = arcade.types.Color.from_hex_string("#F5D167")
TEXT_COLOR = arcade.types.Color.from_hex_string("#4B1DF2")
BALL_COLOR = arcade.types.Color.from_hex_string("#42B5EB")
LINE_COLOR = arcade.types.Color.from_hex_string("#45E6D0")

# Each entry is (label, easing function).
EASING_LIST = [
    ("LINEAR", Easing.LINEAR),
    ("QUAD_OUT", Easing.QUAD_OUT),
    ("QUAD_IN", Easing.QUAD_IN),
    ("SINE", Easing.SINE),
    ("QUAD", Easing.QUAD),
    ("ELASTIC_OUT", Easing.ELASTIC_OUT),
    ("BACK_IN", Easing.BACK_IN),
    ("BACK_OUT", Easing.BACK_OUT),
    ("SINE_IN", Easing.SINE_IN),
    ("SINE_OUT", Easing.SINE_OUT),
    ("BOUNCE_OUT", Easing.BOUNCE_OUT),
]


class EasingCircle(arcade.SpriteCircle):
    """A ball that eases along the x-axis using a specific curve."""

    def __init__(self, radius: int, color: arcade.types.RGBOrA255,
                 ease_function: Easing):
        super().__init__(radius, color)
        self.ease_function = ease_function
        self.start_time = 0.0


class GameView(arcade.View):
    """Main view showing all easing balls."""

    def __init__(self):
        super().__init__()
        self.background_color = BACKGROUND_COLOR
        self.ball_list: arcade.SpriteList[EasingCircle] | None = None
        self.time_elapsed = 0.0

    def setup(self):
        """Create one ball per easing function."""
        self.ball_list = arcade.SpriteList()
        self.time_elapsed = 0.0

        for index, (label, ease_func) in enumerate(EASING_LIST):
            ball = EasingCircle(BALL_RADIUS, BALL_COLOR, ease_func)
            ball_y = WINDOW_HEIGHT - (index + 1) * Y_INTERVAL
            ball.center_x = X_START
            ball.center_y = ball_y
            ball.start_time = 0.0
            self.ball_list.append(ball)

    def on_draw(self):
        """Render the scene."""
        self.clear()

        for index, (label, _ease_func) in enumerate(EASING_LIST):
            ball_y = WINDOW_HEIGHT - (index + 1) * Y_INTERVAL

            # Horizontal guide line
            arcade.draw_line(X_START, ball_y, X_END, ball_y, LINE_COLOR, LINE_WIDTH)

            # Label for this easing function
            arcade.draw_text(
                label,
                X_END + 10,
                ball_y,
                color=TEXT_COLOR,
                font_size=10,
                anchor_y="center",
            )

        # Draw all balls
        self.ball_list.draw()

        # Instructions
        arcade.draw_text(
            "Click to restart",
            WINDOW_WIDTH // 2,
            20,
            color=TEXT_COLOR,
            font_size=14,
            anchor_x="center",
            anchor_y="center",
        )

    def on_update(self, delta_time: float):
        """Update ball positions using the easing functions."""
        self.time_elapsed += delta_time

        for ball in self.ball_list:
            eased_x = ease(
                X_START, X_END,
                ball.start_time, ball.start_time + TRAVEL_TIME,
                self.time_elapsed,
                func=ball.ease_function,
            )
            ball.center_x = eased_x

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        """Restart the animation on click."""
        for ball in self.ball_list:
            ball.start_time = self.time_elapsed


def main():
    """Main function."""
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()
    game.setup()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
