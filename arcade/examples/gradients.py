"""
Drawing Gradients

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gradients
"""
import arcade

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Gradients Example"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Set up the application.
        """

        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)

        self.shapes = arcade.ShapeElementList()

        # This is a large rectangle that fills the whole
        # background. The gradient goes between the two colors
        # top to bottom.
        color1 = (215, 214, 165)
        color2 = (219, 166, 123)
        points = (0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)
        colors = (color1, color1, color2, color2)
        rect = arcade.create_rectangle_filled_with_colors(points, colors)
        self.shapes.append(rect)

        # Another rectangle, but in this case the color doesn't change. Just the
        # transparency. This time it goes from left to right.
        color1 = (165, 92, 85, 255)
        color2 = (165, 92, 85, 0)
        points = (100, 100), (SCREEN_WIDTH - 100, 100), (SCREEN_WIDTH - 100, 300), (100, 300)
        colors = (color2, color1, color1, color2)
        rect = arcade.create_rectangle_filled_with_colors(points, colors)
        self.shapes.append(rect)

        # Two lines
        color1 = (7, 67, 88)
        color2 = (69, 137, 133)
        points = (100, 400), (SCREEN_WIDTH - 100, 400), (SCREEN_WIDTH - 100, 500), (100, 500)
        colors = [color2, color1, color2, color1]
        shape = arcade.create_lines_with_colors(points, colors, line_width=5)
        self.shapes.append(shape)

        # Triangle
        color1 = (215, 214, 165)
        color2 = (219, 166, 123)
        color3 = (165, 92, 85)
        points = (SCREEN_WIDTH // 2, 500), (SCREEN_WIDTH // 2 - 100, 400), (SCREEN_WIDTH // 2 + 100, 400)
        colors = (color1, color2, color3)
        shape = arcade.create_triangles_filled_with_colors(points, colors)
        self.shapes.append(shape)

        # Ellipse, gradient between center and outside
        color1 = (69, 137, 133, 127)
        color2 = (7, 67, 88, 127)
        shape = arcade.create_ellipse_filled_with_colors(SCREEN_WIDTH // 2, 350, 50, 50,
                                                         inside_color=color1, outside_color=color2)
        self.shapes.append(shape)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()
        self.shapes.draw()
        # arcade.draw_rectangle_filled(500, 500, 50, 50, (255, 0, 0, 127))


def main():

    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
