"""
This demo shows using buffered rectangles to draw a grid of squares on the
screen.

For me this starts at 0.500 seconds and goes down to 0.220 seconds after the
graphics card figures out some optimizations.

It is faster than demo 1 because we aren't loading the vertices and color
to the card again and again. It isn't very fast because we are still sending
individual draw commands to the graphics card for each square.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shape_list_demo_2
"""

import arcade
import timeit

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Shape List Demo 2"

SQUARE_WIDTH = 5
SQUARE_HEIGHT = 5
SQUARE_SPACING = 10


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.draw_time = 0
        self.shape_list = None


    def setup(self):
        # --- Create the vertex buffers objects for each square before we do
        # any drawing.
        self.shape_list = arcade.ShapeElementList()
        for x in range(0, SCREEN_WIDTH, SQUARE_SPACING):
            for y in range(0, SCREEN_HEIGHT, SQUARE_SPACING):
                shape = arcade.create_rectangle_filled(x, y, SQUARE_WIDTH, SQUARE_HEIGHT, arcade.color.DARK_BLUE)
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
