"""
Turn and Move Example.

Right-click to cause the tank to move to that point.
"""


import math
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Turn and Move Example"

# Image might not be lined up right, set this to offset
IMAGE_ROTATION = 90


class Player(arcade.Sprite):
    """
    Sprite that turns and moves
    """
    def __init__(self):
        super().__init__(":resources:images/topdown_tanks/tank_green.png")

        # Destination point is where we are going
        self._destination_point = None

        # Max speed
        self.speed = 5

        # Max speed we can rotate
        self.rot_speed = 5

    @property
    def destination_point(self):
        return self._destination_point

    @destination_point.setter
    def destination_point(self, destination_point):
        self._destination_point = destination_point

    def on_update(self, delta_time: float = 1 / 60):
        """ Update the player """

        # If we have no destination, don't go anywhere.
        if not self._destination_point:
            self.change_x = 0
            self.change_y = 0
            return

        # Position the start at our current location
        start_x = self.center_x
        start_y = self.center_y

        # Get the destination location
        dest_x = self._destination_point[0]
        dest_y = self._destination_point[1]

        # Do math to calculate how to get the sprite to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the player will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        target_angle_radians = math.atan2(y_diff, x_diff)
        if target_angle_radians < 0:
            target_angle_radians += 2 * math.pi

        # What angle are we at now in radians?
        actual_angle_radians = math.radians(self.angle - IMAGE_ROTATION)

        # How fast can we rotate?
        rot_speed_radians = math.radians(self.rot_speed)

        # What is the difference between what we want, and where we are?
        angle_diff_radians = target_angle_radians - actual_angle_radians

        # Figure out if we rotate clockwise or counter-clockwise
        if abs(angle_diff_radians) <= rot_speed_radians:
            # Close enough, let's set our angle to the target
            actual_angle_radians = target_angle_radians
            clockwise = None
        elif angle_diff_radians > 0 and abs(angle_diff_radians) < math.pi:
            clockwise = False
        elif angle_diff_radians > 0 and abs(angle_diff_radians) >= math.pi:
            clockwise = True
        elif angle_diff_radians < 0 and abs(angle_diff_radians) < math.pi:
            clockwise = True
        else:
            clockwise = False

        # Rotate the proper direction if needed
        if actual_angle_radians != target_angle_radians and clockwise:
            actual_angle_radians -= rot_speed_radians
        elif actual_angle_radians != target_angle_radians:
            actual_angle_radians += rot_speed_radians

        # Keep in a range of 0 to 2pi
        if actual_angle_radians > 2 * math.pi:
            actual_angle_radians -= 2 * math.pi
        elif actual_angle_radians < 0:
            actual_angle_radians += 2 * math.pi

        # Convert back to degrees
        self.angle = math.degrees(actual_angle_radians) + IMAGE_ROTATION

        # Are we close to the correct angle? If so, move forward.
        if abs(angle_diff_radians) < math.pi / 4:
            self.change_x = math.cos(actual_angle_radians) * self.speed
            self.change_y = math.sin(actual_angle_radians) * self.speed

        # Fine-tune our change_x/change_y if we are really close to destination
        # point and just need to set to that location.
        traveling = False
        if abs(self.center_x - dest_x) < abs(self.change_x):
            self.center_x = dest_x
        else:
            self.center_x += self.change_x
            traveling = True

        if abs(self.center_y - dest_y) < abs(self.change_y):
            self.center_y = dest_y
        else:
            self.center_y += self.change_y
            traveling = True

        # If we have arrived, then cancel our destination point
        if not traveling:
            self._destination_point = None


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)

        arcade.set_background_color(arcade.color.SAND)

        self.player_sprite = None

        # Sprite Lists
        self.player_list = None

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """

        # Sprite Lists
        self.player_list = arcade.SpriteList()
        self.player_sprite = Player()
        self.player_sprite.center_x = 300
        self.player_sprite.center_y = 300
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        self.player_list.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """
        self.player_list.on_update(delta_time)

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player_sprite.destination_point = x, y


def main():
    """ Main function """
    game = MyGame()
    game.center_window()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
