"""
Sprite Rotation Around a Point, With A Tank

Games often include elements that rotate toward targets. Common
examples include gun turrets on vehicles and towers. In 2D games,
these rotating parts are usually implemented as sprites that move
relative to whatever they're attached to.

There's a catch to this: you have to rotate these parts around their
attachment points rather than the centers of their sprites. Otherwise,
the rotation will look wrong!

To illustrate the difference, this example uses a player-controllable
tank with a barrel that follows the mouse. You can press P to switch
between two ways of rotating the barrel:
1. Correctly, with the barrel's rear against the tank's center
2. Incorrectly, around the barrel's center pinned to the tank's

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_rotate_around_tank
"""
import math
import arcade
from arcade.types import Point
from arcade.math import (
    get_angle_radians,
    rotate_point,
    get_angle_degrees,
)

TANK_SPEED_PIXELS = 64  # How many pixels per second the tank travels
TANK_TURN_SPEED_DEGREES = 70  # How fast the tank's body can turn


# This is half the length of the barrel sprite.
# We use it to ensure the barrel's rear sits in the middle of the tank
TANK_BARREL_LENGTH_HALF = 15


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Rotating Tank Example"


# These paths are built-in resources included with arcade
TANK_BODY = ":resources:images/topdown_tanks/tankBody_dark_outline.png"
TANK_BARREL = ":resources:images/topdown_tanks/tankDark_barrel3_outline.png"


class RotatingSprite(arcade.Sprite):
    """
    Sprite subclass which can be rotated around a point.

    This version of the class always changes the angle of the sprite.
    Other games might not rotate the sprite. For example, moving
    platforms in a platformer wouldn't rotate.
    """
    def rotate_around_point(self, point: Point, degrees: float):
        """
        Rotate the sprite around a point by the set amount of degrees

        Args:
            point: The point that the sprite will rotate about
            degrees: How many degrees to rotate the sprite
        """

        # Make the sprite turn as its position is moved
        self.angle += degrees

        # Move the sprite along a circle centered around the passed point
        self.position = rotate_point(
            self.center_x, self.center_y,
            point[0], point[1], degrees)

    def face_point(self, point: Point):
        self.angle = get_angle_degrees(*self.position, *point)


class GameView(arcade.View):

    def __init__(self):
        super().__init__()

        # Set Background to be green
        self.window.background_color = arcade.csscolor.SEA_GREEN

        # The tank and barrel sprite
        self.tank = arcade.Sprite(TANK_BODY)
        self.tank.position = self.window.center

        self.barrel = RotatingSprite(TANK_BARREL)
        self.barrel.position = (
            self.tank.center_x, self.tank.center_y - TANK_BARREL_LENGTH_HALF
        )

        self.tank_direction = 0.0  # Forward & backward throttle
        self.tank_turning = 0.0  # Turning strength to the left or right

        self.mouse_pos = 0, 0

        self.tank_sprite_list = arcade.SpriteList()
        self.tank_sprite_list.extend([self.tank, self.barrel])

        self._correct = True
        self.correct_text = arcade.Text(
            "If the turret rotation is incorrect press P to reset it",
            self.window.center_x, WINDOW_HEIGHT - 25,
            anchor_x='center')

        self.control_text = arcade.Text(
            "WASD to move tank, Mouse to aim",
            self.window.center_x, 15,
            anchor_x='center')

    def on_draw(self):
        self.clear()
        self.tank_sprite_list.draw()

        self.control_text.draw()
        self.correct_text.draw()

    def on_update(self, delta_time: float):
        self.move_tank(delta_time)

    def move_tank(self, delta_time):
        """
        Perform all calculations for moving the tank's body and barrel
        """

        # Rotate the tank's body in place without changing position
        # We'll rotate the barrel after updating the entire tank's x & y
        self.tank.angle += (
            TANK_TURN_SPEED_DEGREES * self.tank_turning * delta_time
        )

        # Calculate how much the tank should move forward or back
        move_magnitude = self.tank_direction * TANK_SPEED_PIXELS * delta_time
        x_dir = math.sin(self.tank.radians) * move_magnitude
        y_dir = math.cos(self.tank.radians) * move_magnitude

        # Move the tank's body
        self.tank.position = (
            self.tank.center_x + x_dir,
            self.tank.center_y + y_dir
        )

        # Move the barrel with the body
        self.barrel.position = (
            self.barrel.center_x + x_dir,
            self.barrel.center_y + y_dir
        )

        # Begin rotating the barrel by finding the angle to the mouse
        mouse_angle = get_angle_degrees(
            self.tank.center_x, self.tank.center_y,
            self.mouse_pos[0], self.mouse_pos[1])

        # Compensate for fact that the barrel sits horzontally rather than virtically
        mouse_angle -= 90

        # Rotate the barrel sprite with one end at the tank's center
        # Subtract the old angle to get the change in angle
        angle_change = mouse_angle - self.barrel.angle

        self.barrel.rotate_around_point(self.tank.position, angle_change)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.tank_direction += 1
        elif symbol == arcade.key.S:
            self.tank_direction -= 1
        elif symbol == arcade.key.A:
            self.tank_turning -= 1
        elif symbol == arcade.key.D:
            self.tank_turning += 1
        elif symbol == arcade.key.P:
            angle = self.barrel.angle
            self.barrel.angle = 0
            self.barrel.position = (
                self.tank.center_x,
                self.tank.center_y - TANK_BARREL_LENGTH_HALF
            )
            self.barrel.rotate_around_point(self.tank.position, angle)

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.tank_direction -= 1
        elif symbol == arcade.key.S:
            self.tank_direction += 1
        elif symbol == arcade.key.A:
            self.tank_turning += 1
        elif symbol == arcade.key.D:
            self.tank_turning -= 1

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = x, y

    @property
    def correct(self):
        return self._correct

    @correct.setter
    def correct(self, correct: bool):
        """
        Move the tank's barrel between correct rotation and incorrect positions
        """
        self._correct = correct
        if correct:
            angle = get_angle_radians(
                self.tank.center_y, self.tank.center_x,
                self.mouse_pos[1], self.mouse_pos[0])

            self.barrel.position = (
                self.barrel.center_x + math.sin(angle) * TANK_BARREL_LENGTH_HALF,
                self.barrel.center_y + math.cos(angle) * TANK_BARREL_LENGTH_HALF,
            )

        else:
            self.barrel.position = self.tank.position


def main():
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    game = GameView()

    window.show_view(game)
    window.run()


if __name__ == '__main__':
    main()
