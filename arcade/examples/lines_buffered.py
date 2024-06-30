"""
Using a Vertex Buffer Object With Lines

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.lines_buffered
"""
import random
import arcade
from arcade.shape_list import (
    ShapeElementList,
    create_line_strip,
)
from inspect import getmembers
from arcade.types import Color

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Vertex Buffer Object With Lines Example"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title)
        self.set_vsync(True)

        self.shape_list = ShapeElementList()
        point_list = ((0, 50),
                      (10, 10),
                      (50, 0),
                      (10, -10),
                      (0, -50),
                      (-10, -10),
                      (-50, 0),
                      (-10, 10),
                      (0, 50))

        # Filter out anything other than a Color, such as imports and
        # helper functions.
        colors = [
            color for name, color in
            getmembers(arcade.color, lambda c: isinstance(c, Color))]

        for i in range(200):
            x = SCREEN_WIDTH // 2 - random.randrange(SCREEN_WIDTH)
            y = SCREEN_HEIGHT // 2 - random.randrange(SCREEN_HEIGHT)
            color = random.choice(colors)
            points = [(px + x, py + y) for px, py in point_list]

            my_line_strip = create_line_strip(points, color, 5)
            self.shape_list.append(my_line_strip)

        self.shape_list.center_x = SCREEN_WIDTH // 2
        self.shape_list.center_y = SCREEN_HEIGHT // 2
        self.shape_list.angle = 0

        self.background_color = arcade.color.BLACK

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        self.clear()

        self.shape_list.draw()

    def on_update(self, delta_time):
        self.shape_list.angle += 1 * 60 * delta_time
        self.shape_list.center_x += 0.1 * 60 * delta_time
        self.shape_list.center_y += 0.1 * 60 * delta_time


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
