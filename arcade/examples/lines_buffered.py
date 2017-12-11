"""
Array Backed Grid

Show how to use a two-dimensional list/array to back the display of a
grid on-screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.lines_buffered
"""
import arcade

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Set up the application.
        """
        super().__init__(width, height)

        self.shape_list = arcade.ShapeElementList()

        point_list = ((0, 50),
                      (10, 10),
                      (50, 0),
                      (10, -10),
                      (0, -50),
                      (-10, -10),
                      (-50, 0),
                      (-10, 10),
                      (0, 50))
        my_line_strip = arcade.create_line_strip(point_list, arcade.color.RED, 5)
        self.shape_list.append(my_line_strip)

        self.shape_list.center_x = 100
        self.shape_list.center_y = 100

        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.shape_list.draw()

    def update(self, delta_time):
        self.shape_list.angle += 1
        self.shape_list.center_x += 1
        self.shape_list.center_y += 1


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.run()


if __name__ == "__main__":
    main()
