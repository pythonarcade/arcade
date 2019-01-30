"""
Bounce balls on the screen.
Spawn a new ball for each mouse-click.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.bouncing_balls
"""

import arcade
import random

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Bouncing Balls Example"

class Ball:
    """
    Class to keep track of a ball's location and vector.
    """
    def __init__(self):
        self.x = 0
        self.y = 0
        self.change_x = 0
        self.change_y = 0
        self.size = 0


def make_ball():
    """
    Function to make a new, random ball.
    """
    ball = Ball()

    # Size of the ball
    ball.size = random.randrange(10, 30)

    # Starting position of the ball.
    # Take into account the ball size so we don't spawn on the edge.
    ball.x = random.randrange(ball.size, SCREEN_WIDTH - ball.size)
    ball.y = random.randrange(ball.size, SCREEN_HEIGHT - ball.size)

    # Speed and direction of rectangle
    ball.change_x = random.randrange(-2, 3)
    ball.change_y = random.randrange(-2, 3)

    # Color
    ball.color = (random.randrange(256), random.randrange(256), random.randrange(256))

    return ball


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.ball_list = []
        ball = make_ball()
        self.ball_list.append(ball)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        for ball in self.ball_list:
            arcade.draw_circle_filled(ball.x, ball.y, ball.size, ball.color)

        # Put the text on the screen.
        output = "Balls: {}".format(len(self.ball_list))
        arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)

    def update(self, delta_time):
        """ Movement and game logic """
        for ball in self.ball_list:
            ball.x += ball.change_x
            ball.y += ball.change_y

            if ball.x < ball.size:
                ball.change_x *= -1

            if ball.y < ball.size:
                ball.change_y *= -1

            if ball.x > SCREEN_WIDTH - ball.size:
                ball.change_x *= -1

            if ball.y > SCREEN_HEIGHT - ball.size:
                ball.change_y *= -1

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """
        ball = make_ball()
        self.ball_list.append(ball)


def main():
    MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
