import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """
        Initializer
        """
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        """
        Render the screen.
        """

        # Start the render process. This must be done before any drawing commands.
        arcade.start_render()

        radius = 50
        width = radius * 2
        x = 200
        y = 100
        arcade.draw_rectangle_outline(x, y, width, width, arcade.color.BLACK, 2)
        arcade.draw_circle_outline(x, y, radius, arcade.color.BLACK, 2)
        arcade.draw_line(x - radius, y, x + radius, y, arcade.color.BLACK, 2)

        x = 200
        y = 300
        width = 150
        half_width = width / 2
        arcade.draw_rectangle_outline(x, y, width, 50, arcade.color.BLACK, 2)
        arcade.draw_ellipse_outline(x, y, width, 50, arcade.color.AFRICAN_VIOLET, 2)
        arcade.draw_line(x - half_width, y, x + half_width, y, arcade.color.RED, 2)

        x = 200
        y = 500
        width = 150
        half_width = width / 2
        arcade.draw_rectangle_outline(x, y, width, 50, arcade.color.BLACK, 2)
        arcade.draw_arc_outline(x, y, width, 50, arcade.color.AFRICAN_VIOLET, 0, 180, 5)
        arcade.draw_line(x - half_width, y, x + half_width, y, arcade.color.RED, 2)

        radius = 50
        width = radius * 2
        x = 400
        y = 100
        arcade.draw_rectangle_outline(x, y, width, width, arcade.color.BLACK, 2)
        arcade.draw_circle_filled(x, y, radius, arcade.color.AFRICAN_VIOLET)
        arcade.draw_line(x - radius, y, x + radius, y, arcade.color.BLACK, 2)

        x = 400
        y = 300
        width = 150
        half_width = width / 2
        arcade.draw_rectangle_outline(x, y, width, 50, arcade.color.BLACK, 2)
        arcade.draw_ellipse_filled(x, y, width, 50, arcade.color.AFRICAN_VIOLET, 2)
        arcade.draw_line(x - half_width, y, x + half_width, y, arcade.color.RED, 2)

        x = 400
        y = 500
        width = 150
        half_width = width / 2
        arcade.draw_rectangle_outline(x, y, width, 50, arcade.color.BLACK, 2)
        arcade.draw_arc_filled(x, y, width, 50, arcade.color.AFRICAN_VIOLET, 0, 180)
        arcade.draw_line(x - half_width, y, x + half_width, y, arcade.color.RED, 2)


def test_main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.test(100)
    window.close()
