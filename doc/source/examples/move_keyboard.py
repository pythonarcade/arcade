"""
This simple animation example shows how to move an item with the keyboard.
"""

import arcade
import random

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

RECT_WIDTH = 50
RECT_HEIGHT = 50

MOVEMENT_SPEED = 5


class Rectangle():
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
        arcade.draw_rect_filled(self.x, self.y, self.width, self.height,
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


class MyApplication(arcade.Window):
    """
    Main application class.
    """

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

    def animate(self, dt):
        """ Move everything """
        self.player.move()

    def on_draw(self):
        """
        Render the screen.
        """
        arcade.start_render()

        self.player.draw()

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.UP:
            self.player.delta_y = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player.delta_y = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player.delta_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.delta_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.delta_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.delta_x = 0


def main():
    window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT,
                           title="Keyboard control")
    window.setup()
    arcade.run()

main()
