"""
This simple animation example shows how to bounce a rectangle
on the screen.

If Python and Arcade are installed, this example can be run
from the command line with:
python -m arcade.examples.bouncing_rectangle
"""

import arcade

# --- Set up the constants

# Size of the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Bouncing Rectangle Example"

# Rectangle info
RECT_WIDTH = 50
RECT_HEIGHT = 50
RECT_COLOR = arcade.color.DARK_BROWN

BACKGROUND_COLOR = arcade.color.ALMOND


class Item:
    """ This class represents our rectangle """

    def __init__(self):

        # Set up attribute variables

        # Where we are
        self.center_x = 0
        self.center_y = 0

        # Where we are going
        self.change_x = 0
        self.change_y = 0

    def update(self):
        # Move the rectangle
        self.center_x += self.change_x
        self.center_y += self.change_y
        # Check if we need to bounce of right edge
        if self.center_x > SCREEN_WIDTH - RECT_WIDTH / 2:
            self.change_x *= -1
        # Check if we need to bounce of top edge
        if self.center_y > SCREEN_HEIGHT - RECT_HEIGHT / 2:
            self.change_y *= -1
        # Check if we need to bounce of left edge
        if self.center_x < RECT_WIDTH / 2:
            self.change_x *= -1
        # Check if we need to bounce of bottom edge
        if self.center_y < RECT_HEIGHT / 2:
            self.change_y *= -1

    def draw(self):
        # Draw the rectangle
        arcade.draw_rectangle_filled(self.center_x,
                                     self.center_y,
                                     RECT_WIDTH,
                                     RECT_HEIGHT,
                                     RECT_COLOR)


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Create our rectangle
        self.item = Item()
        self.item.center_x = 200
        self.item.center_y = 300
        self.item.change_x = 2
        self.item.change_y = 3

        # Set background color
        self.background_color = BACKGROUND_COLOR

    def on_update(self, delta_time):
        # Move the rectangle
        self.item.update()

    def on_draw(self):
        """ Render the screen. """

        # Clear screen
        self.clear()
        # Draw the rectangle
        self.item.draw()


def main():
    """ Main function """
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
