"""
This demo shows using buffered rectangles to draw a grid of squares on the
screen.

For me this runs about 0.002 seconds per frame.

It is faster than demo 1 because we aren't loading the vertices and color
to the card again and again. It could be faster though, if we group all
rectangles together.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shape_list_demo_2
"""

import arcade
import timeit

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Shape List Demo 2"

SQUARE_WIDTH = 5
SQUARE_HEIGHT = 5
SQUARE_SPACING = 10


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.DARK_SLATE_GRAY

        self.draw_time = 0
        self.shape_list = None

    def setup(self):
        # --- Create the vertex buffers objects for each square before we do
        # any drawing.
        self.shape_list = arcade.shape_list.ShapeElementList()
        for x in range(0, WINDOW_WIDTH, SQUARE_SPACING):
            for y in range(0, WINDOW_HEIGHT, SQUARE_SPACING):
                shape = arcade.shape_list.create_rectangle_filled(
                    center_x=x,
                    center_y=y,
                    width=SQUARE_WIDTH,
                    height=SQUARE_HEIGHT,
                    color=arcade.color.DARK_BLUE,
                )
                self.shape_list.append(shape)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # --- Draw all the rectangles
        self.shape_list.draw()

        output = f"Drawing time: {self.draw_time:.3f} seconds per frame."
        arcade.draw_text(output, 20, WINDOW_HEIGHT - 40, arcade.color.WHITE, 18)

        self.draw_time = timeit.default_timer() - draw_start_time


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create and setup the GameView
    game = GameView()
    game.setup()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
