"""
This simple animation example shows how to move an item with the joystick.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.joystick
"""

import arcade

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Joystick Control Example"

RECT_WIDTH = 50
RECT_HEIGHT = 50

MOVEMENT_MULTIPLIER = 5
DEAD_ZONE = 0.05


class MyGame(arcade.Window):
    """
    Main application class.
    """
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.player = None
        self.left_down = False

        joysticks = arcade.get_joysticks()
        if joysticks:
            self.joystick = joysticks[0]
            self.joystick.open()
            self.joystick.on_joybutton_press = self.on_joybutton_press
            self.joystick.on_joybutton_release = self.on_joybutton_release
            self.joystick.on_joyhat_motion = self.on_joyhat_motion
        else:
            print("There are no Joysticks")
            self.joystick = None

    def on_joybutton_press(self, joystick, button):
        print("Button {} down".format(button))

    def on_joybutton_release(self, joystick, button):
        print("Button {} up".format(button))

    def on_joyhat_motion(self, joystick, hat_x, hat_y):
        print("Hat ({}, {})".format(hat_x, hat_y))

    def setup(self):
        """ Set up the game and initialize the variables. """
        width = RECT_WIDTH
        height = RECT_HEIGHT
        x = SCREEN_WIDTH // 2
        y = SCREEN_HEIGHT // 2
        angle = 0
        color = arcade.color.WHITE
        self.player = Rectangle(x, y, width, height, angle, color)
        self.left_down = False

    def update(self, dt):
        # Grab the position of the joystick
        # This will be between -1.0 and +1.0

        if self.joystick:
            self.player.delta_x = self.joystick.x * MOVEMENT_MULTIPLIER
            # Set a "dead zone" to prevent drive from a centered joystick
            if abs(self.player.delta_x) < DEAD_ZONE:
                self.player.delta_x = 0

            self.player.delta_y = -self.joystick.y * MOVEMENT_MULTIPLIER
            # Set a "dead zone" to prevent drive from a centered joystick
            if abs(self.player.delta_y) < DEAD_ZONE:
                self.player.delta_y = 0

        """ Move everything """
        self.player.move()

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()

        self.player.draw()


class Rectangle:

    """ Class to represent a rectangle on the screen """

    def __init__(self, x, y, width, height, angle, color):
        """ Initialize our rectangle variables """

        # Position
        self.x = x
        self.y = y

        # Vector
        self.delta_x = 0
        self.delta_y = 0

        # Size and rotation
        self.width = width
        self.height = height
        self.angle = angle

        # Color
        self.color = color

    def draw(self):
        """ Draw our rectangle """
        arcade.draw_rectangle_filled(self.x, self.y, self.width, self.height,
                                     self.color, self.angle)

    def move(self):

        """ Move our rectangle """

        # Move left/right
        self.x += self.delta_x

        # See if we've gone beyond the border. If so, reset our position
        # back to the border.
        if self.x < RECT_WIDTH // 2:
            self.x = RECT_WIDTH // 2
        if self.x > SCREEN_WIDTH - (RECT_WIDTH // 2):
            self.x = SCREEN_WIDTH - (RECT_WIDTH // 2)

        # Move up/down
        self.y += self.delta_y

        # Check top and bottom boundaries
        if self.y < RECT_HEIGHT // 2:
            self.y = RECT_HEIGHT // 2
        if self.y > SCREEN_HEIGHT - (RECT_HEIGHT // 2):
            self.y = SCREEN_HEIGHT - (RECT_HEIGHT // 2)


def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
