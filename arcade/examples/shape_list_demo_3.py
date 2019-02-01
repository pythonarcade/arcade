"""
This demo shows drawing a grid of squares using a single buffer.

We calculate the points of each rectangle and add them to a point list.
We create a list of colors for each point.
We then draw all the squares with one drawing command.

This runs in about 0.000 seconds for me. It is much more complex in code
than the prior two examples, but the pay-off in speed is huge.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shape_list_demo_3
"""

import arcade
import timeit

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Shape List Demo 3"

HALF_SQUARE_WIDTH = 2.5
HALF_SQUARE_HEIGHT = 2.5
SQUARE_SPACING = 10


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.draw_time = 0
        self.shape_list = None


    def setup(self):
        self.shape_list = arcade.ShapeElementList()

        # --- Create all the rectangles

        # We need a list of all the points and colors
        point_list = []
        color_list = []

        # Now calculate all the points
        for x in range(0, SCREEN_WIDTH, SQUARE_SPACING):
            for y in range(0, SCREEN_HEIGHT, SQUARE_SPACING):

                # Calculate where the four points of the rectangle will be if
                # x and y are the center
                top_left = (x - HALF_SQUARE_WIDTH, y + HALF_SQUARE_HEIGHT)
                top_right = (x + HALF_SQUARE_WIDTH, y + HALF_SQUARE_HEIGHT)
                bottom_right = (x + HALF_SQUARE_WIDTH, y - HALF_SQUARE_HEIGHT)
                bottom_left = (x - HALF_SQUARE_WIDTH, y - HALF_SQUARE_HEIGHT)

                # Add the points to the points list.
                # ORDER MATTERS!
                # Rotate around the rectangle, don't append points caty-corner
                point_list.append(top_left)
                point_list.append(top_right)
                point_list.append(bottom_right)
                point_list.append(bottom_left)

                # Add a color for each point. Can be different colors if you want
                # gradients.
                for i in range(4):
                    color_list.append(arcade.color.DARK_BLUE)

        shape = arcade.create_rectangles_filled_with_colors(point_list, color_list)
        self.shape_list.append(shape)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # --- Draw all the rectangles
        self.shape_list.draw()

        output = f"Drawing time: {self.draw_time:.3f} seconds per frame."
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)

        self.draw_time = timeit.default_timer() - draw_start_time



def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
