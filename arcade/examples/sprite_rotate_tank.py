"""
Sprite Rotation With A Tank.

The problem often fis that vehicles or tower defense turrets can have parts that can rotate toward targets.
These parts are usually represented with separate sprites drawn relative to attachment points on the main body.

Because these sprites are usually asymmetrical, we have to rotate them around their attachment points on the main body,
or they will look wrong!

This example allows the player to switch between two ways of rotating a tank's turret and barrel:
1. correctly, around a point on the tank's body
2. incorrectly, around the center of the barrel.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_rotate_tank
"""

import arcade
import math

TANK_SPEED = 64  # How many pixels per second the tank travels
TANK_TURNING_SPEED = 60  # how many degrees per second the tank spins by.

# This is half the length of the barrel sprite. We use this value to ensure the end of the barrel sit in the middle of the tank.
TANK_BARREL_LENGTH_HALF = 15  

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Rotating Tank Example"


class RotatingSprite(arcade.Sprite):
    """
    This is an example sprite subclass which implements a rotate_around_point method
    which also rotates the sprites angle.
    """
    def rotate_around_point(self, point, degrees):
        """
        rotates the sprite around a defined point by the set amount of degrees

        :param point: The point that the sprite will rotate about
        :param degrees: How many degrees to rotate the sprite
        """

        # This is so the direction the sprite faces changes when rotating.
        # It isn't necessary to have this. For example, you would want a rotating platform to always face upwards.
        self.angle += degrees

        # use arcade.rotate_point to rotate the sprites center x and y by the point.
        self.center_x, self.center_y = arcade.rotate_point(self.center_x, self.center_y, point[0], point[1], degrees)


class ExampleWindow(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Generate a grassy background
        self.background = arcade.SpriteList()

        # since 64 is not a factor of SCREEN_WIDTH or SCREEN_HEIGHT add an extra to cover the gap
        for x in range(SCREEN_WIDTH // 64 + 1):
            for y in range(SCREEN_HEIGHT // 64 + 1):
                self.background.append(arcade.Sprite(":resources:images/topdown_tanks/tileGrass1.png",
                                                     center_x=x * 64, center_y=y * 64))

        # The tank and barrel sprite. These Can be all added to their own separate class in a more advanced program.
        self.tank = arcade.Sprite(":resources:images/topdown_tanks/tankBody_dark_outline.png",
                                  center_x=SCREEN_WIDTH // 2, center_y=SCREEN_HEIGHT // 2)
        self.barrel = RotatingSprite(":resources:images/topdown_tanks/tankDark_barrel3_outline.png",
                                     center_x=SCREEN_WIDTH // 2, center_y=SCREEN_HEIGHT // 2 - 13)

        self.tank_direction = 0.0  # If the tank is moving forward or backwards.
        self.tank_turning = 0.0  # If the tank is turning left or right.

        self.mouse_pos = [0, 0]

        self.tank_sprite_list = arcade.SpriteList()
        self.tank_sprite_list.extend([self.tank, self.barrel])

        self._correct = True
        self.correct_text = arcade.Text("Turret Rotation is Correct, Press P to Switch",
                                        SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25, anchor_x='center')

        self.control_text = arcade.Text("WASD to move tank, Mouse to aim", SCREEN_WIDTH // 2, 15, anchor_x='center')

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.tank_sprite_list.draw()

        self.control_text.draw()
        self.correct_text.draw()

    def on_update(self, delta_time: float):
        self.move_tank(delta_time)

    def move_tank(self, delta_time):
        """
        Perform all calculations about how to move the tank, including both the body and the barrel
        """

        # update the angle of the tank's body alone. The barrel will be updated after the body is moved
        self.tank.angle += TANK_SPEED * self.tank_turning * delta_time

        # find how much the tank's x and y should change to move forward or back.
        x_dir = math.cos(self.tank.radians - math.pi / 2) * self.tank_direction * TANK_SPEED * delta_time
        y_dir = math.sin(self.tank.radians - math.pi / 2) * self.tank_direction * TANK_SPEED * delta_time

        # we then move the tank and the barrel since they are connected together.
        self.tank.center_x += x_dir
        self.tank.center_y += y_dir

        self.barrel.center_x += x_dir
        self.barrel.center_y += y_dir

        if self.correct:
            # Rotate the barrel sprite around the center of the tank, not the center of the barrel sprite

            # we need to add 90 to the angle due to orientation of the barrel texture.
            # we need to remove the barrels angle as we only want the change in angle.
            angle_change = arcade.get_angle_degrees(self.tank.center_y, self.tank.center_x,
                                                    self.mouse_pos[1], self.mouse_pos[0]) - self.barrel.angle + 90
            self.barrel.rotate_around_point((self.tank.center_x, self.tank.center_y), angle_change)
        else:
            # In this situation we only change the angle without changing the position which is incorrect.

            # we need to add 90 to the angle due to orientation of the barrel texture.
            angle = arcade.get_angle_degrees(self.tank.center_y, self.tank.center_x,
                                             self.mouse_pos[1], self.mouse_pos[0]) + 90
            self.barrel.angle = angle

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.tank_direction += 1
        elif symbol == arcade.key.S:
            self.tank_direction -= 1
        elif symbol == arcade.key.A:
            self.tank_turning += 1
        elif symbol == arcade.key.D:
            self.tank_turning -= 1
        elif symbol == arcade.key.P:
            self.correct = bool(1 - self.correct)

            self.correct_text.text = f"Turret Rotation is {'Correct' if self.correct else 'Incorrect'}," \
                                     f" Press P to Switch"

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.W:
            self.tank_direction -= 1
        elif symbol == arcade.key.S:
            self.tank_direction += 1
        elif symbol == arcade.key.A:
            self.tank_turning -= 1
        elif symbol == arcade.key.D:
            self.tank_turning += 1

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_pos = x, y

    @property
    def correct(self):
        return self._correct

    @correct.setter
    def correct(self, value):
        if value:
            self._correct = True
            angle = math.radians(arcade.get_angle_degrees(self.tank.center_y, self.tank.center_x,
                                                          self.mouse_pos[1], self.mouse_pos[0]))
            self.barrel.center_x = self.tank.center_x + math.cos(angle) * TANK_BARREL_LENGTH_HALF
            self.barrel.center_y = self.tank.center_y + math.sin(angle) * TANK_BARREL_LENGTH_HALF
        else:
            self._correct = False
            self.barrel.center_x = self.tank.center_x
            self.barrel.center_y = self.tank.center_y


def main():
    window = ExampleWindow()
    window.run()


if __name__ == '__main__':
    main()
