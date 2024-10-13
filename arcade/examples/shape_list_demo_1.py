"""
This demo shows the speed of drawing a full grid of squares using no buffering.

For me this takes about 0.16 seconds per frame.

It is slow because we load all the points and all the colors to the card every
time.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shape_list_demo_1
"""

import arcade
import timeit

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Shape List Demo 1"

SQUARE_WIDTH = 5
SQUARE_HEIGHT = 5
SQUARE_SPACING = 10


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.DARK_SLATE_GRAY

        self.draw_time = 0

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # --- Draw all the rectangles
        for x in range(0, WINDOW_WIDTH, SQUARE_SPACING):
            for y in range(0, WINDOW_HEIGHT, SQUARE_SPACING):
                arcade.draw_rect_filled(arcade.rect.XYWH(x, y, SQUARE_WIDTH, SQUARE_HEIGHT),
                                        arcade.color.DARK_BLUE)

        # Print the timing
        output = f"Drawing time: {self.draw_time:.3f} seconds per frame."
        arcade.draw_text(output, 20, WINDOW_HEIGHT - 40, arcade.color.WHITE, 18)

        self.draw_time = timeit.default_timer() - draw_start_time


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
