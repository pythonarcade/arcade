"""
Decorator Test

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.decorator_test
"""

import arcade


class Ball:
    def __init__(self, radius=20, velocity=20, initial_x=20):
        self.x_position = initial_x
        self.velocity = velocity
        self.radius = radius


WIDTH = 700
HEIGHT = 600
window = arcade.open_window(WIDTH, HEIGHT, "Decorator Test")

ball = Ball()


def setup():
    arcade.set_background_color(arcade.color.MAHOGANY)
    arcade.schedule(update, 1/60)
    arcade.run()


def update(delta_time):
    move_ball()


def move_ball():
    global ball
    ball.x_position += ball.velocity

    # Did the ball hit the right side of the screen while moving right?
    if ball.x_position > WIDTH - ball.radius and ball.velocity > 0:
        ball.velocity *= -1

    # Did the ball hit the left side of the screen while moving left?
    if ball.x_position < ball.radius and ball.velocity < 0:
        ball.velocity *= -1


@window.event
def on_draw():
    arcade.start_render()
    draw_the_ball()
    draw_some_text()


def draw_the_ball():
    arcade.draw_circle_filled(ball.x_position, HEIGHT // 2, ball.radius, arcade.color.GREEN)


def draw_some_text():
    arcade.draw_text("This is some text.", 10, HEIGHT // 2, arcade.color.BLACK, 20)


@window.event
def on_key_press(key, modifiers):
    if key == arcade.key.SPACE:
        print("You pressed the space bar.")


@window.event
def on_mouse_press(x, y, button, modifiers):
    print(f"on_mouse_press - x: {x}, y: {y}, button: {button}, modifiers: {modifiers}")


if __name__ == "__main__":
    setup()
