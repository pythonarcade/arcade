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
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Vertex Buffer Object With Lines Example"


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):
        """
        Set up the application.
        """
        super().__init__()

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
            x = WINDOW_WIDTH // 2 - random.randrange(WINDOW_WIDTH)
            y = WINDOW_HEIGHT // 2 - random.randrange(WINDOW_HEIGHT)
            color = random.choice(colors)
            points = [(px + x, py + y) for px, py in point_list]

            my_line_strip = create_line_strip(points, color, 5)
            self.shape_list.append(my_line_strip)

        self.shape_list.center_x = WINDOW_WIDTH // 2
        self.shape_list.center_y = WINDOW_HEIGHT // 2
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
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, vsync=True)

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
