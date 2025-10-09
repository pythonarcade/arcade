"""
Example showing how to use the easing functions for position.

See:
https://easings.net/
...for a great guide on the theory behind how easings can work.

See example 2 for how to use easings for angles.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.easing_example_1
"""

import arcade
from arcade import easing
from arcade.types import Color

SPRITE_SCALING = 0.5

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Easing Example"

BACKGROUND_COLOR = "#F5D167"
TEXT_COLOR = "#4B1DF2"
BALL_COLOR = "#42B5EB"
LINE_COLOR = "#45E6D0"
LINE_WIDTH = 3

X_START = 40
X_END = 1200
Y_INTERVAL = 60
BALL_RADIUS = 13
TIME = 3.0


class EasingCircle(arcade.SpriteCircle):
    """Player class"""

    def __init__(self, radius, color, center_x: float = 0, center_y: float = 0):
        """Set up the player"""

        # Call the parent init
        super().__init__(radius, color, center_x=center_x, center_y=center_y)

        self.easing_x_data = None
        self.easing_y_data = None

    def update(self, delta_time: float = 1 / 60):
        if self.easing_x_data is not None:
            done, self.center_x = easing.ease_update(self.easing_x_data, delta_time)
            if done:
                x = X_START
                if self.center_x < WINDOW_WIDTH / 2:
                    x = X_END
                ex, ey = easing.ease_position(
                    self.position,
                    (x, self.center_y),
                    rate=180,
                    ease_function=self.easing_x_data.ease_function,
                )
                self.easing_x_data = ex

        if self.easing_y_data is not None:
            done, self.center_y = easing.ease_update(self.easing_y_data, delta_time)
            if done:
                self.easing_y_data = None


class GameView(arcade.View):
    """Main application class."""

    def __init__(self):
        """Initializer"""

        # Call the parent class initializer
        super().__init__()

        # Set the background color
        self.background_color = Color.from_hex_string(BACKGROUND_COLOR)

        self.ball_list = None
        self.text_list = []
        self.lines = None

    def setup(self):
        """Set up the game and initialize the variables."""

        # Sprite lists
        self.ball_list = arcade.SpriteList()
        self.lines = arcade.shape_list.ShapeElementList()
        color = Color.from_hex_string(BALL_COLOR)
        shared_ball_kwargs = dict(radius=BALL_RADIUS, color=color)

        def create_ball(ball_y, ease_function):
            ball = EasingCircle(**shared_ball_kwargs, center_x=X_START, center_y=ball_y)
            p1 = ball.position
            p2 = (X_END, ball_y)
            ex, ey = easing.ease_position(p1, p2, time=TIME, ease_function=ease_function)
            ball.ease_function = ease_function
            ball.easing_x_data = ex
            ball.easing_y_data = ey
            return ball

        def create_line(line_y):
            line = arcade.shape_list.create_line(
                X_START,
                line_y - BALL_RADIUS - LINE_WIDTH,
                X_END,
                line_y - BALL_RADIUS,
                line_color,
                line_width=LINE_WIDTH,
            )
            return line

        def create_text(text_string):
            text = arcade.Text(
                text_string,
                x=X_START,
                y=y - BALL_RADIUS,
                color=text_color,
                font_size=24,
            )
            return text

        def add_item(item_y, ease_function, text):
            ball = create_ball(item_y, ease_function)
            self.ball_list.append(ball)
            text = create_text(text)
            self.text_list.append(text)
            line = create_line(item_y)
            self.lines.append(line)

        text_color = Color.from_hex_string(TEXT_COLOR)
        line_color = Color.from_hex_string(LINE_COLOR)

        y = Y_INTERVAL
        add_item(y, easing.linear, "Linear")

        y += Y_INTERVAL
        add_item(y, easing.ease_out, "Ease out")

        y += Y_INTERVAL
        add_item(y, easing.ease_in, "Ease in")

        y += Y_INTERVAL
        add_item(y, easing.smoothstep, "Smoothstep")

        y += Y_INTERVAL
        add_item(y, easing.ease_in_out, "Ease in/out")

        y += Y_INTERVAL
        add_item(y, easing.ease_out_elastic, "Ease out elastic")

        y += Y_INTERVAL
        add_item(y, easing.ease_in_back, "Ease in back")

        y += Y_INTERVAL
        add_item(y, easing.ease_out_back, "Ease out back")

        y += Y_INTERVAL
        add_item(y, easing.ease_in_sin, "Ease in sin")

        y += Y_INTERVAL
        add_item(y, easing.ease_out_sin, "Ease out sin")

        y += Y_INTERVAL
        add_item(y, easing.ease_in_out_sin, "Ease in out sin")

    def on_draw(self):
        """Render the screen."""

        # This command has to happen before we start drawing
        self.clear()

        self.lines.draw()

        # Draw all the sprites.
        self.ball_list.draw()

        for text in self.text_list:
            text.draw()

    def on_update(self, delta_time):
        """Movement and game logic"""

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.ball_list.update(delta_time)


def main():
    """Main function"""
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
