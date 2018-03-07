"""

"""

import arcade
import timeit

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        self.draw_time = 0
        self.shape_list = None


    def setup(self):
        SPACING = 10
        self.shape_list = arcade.ShapeElementList()
        for x in range(0, SCREEN_WIDTH, SPACING):
            for y in range(0, SCREEN_HEIGHT, SPACING):
                shape = arcade.create_rectangle_filled(x, y, 5, 5, arcade.color.DARK_BLUE)
                self.shape_list.append(shape)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        self.shape_list.draw()

        output = f"Drawing time: {self.draw_time:.3f} seconds per frame."
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 18)

        self.draw_time = timeit.default_timer() - draw_start_time



def main():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
