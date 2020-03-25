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

        point_list = ([0, 100],
                     [100, 100],
                      [100, 300],
                      [300, 300])
        self.line_strip = arcade.create_line_strip(point_list, arcade.csscolor.BLACK, 10)

    def on_draw(self):
        arcade.start_render()
        self.line_strip.draw()
        p = arcade.get_pixel(0, 100)
        assert p == (0, 0, 0)
        p = arcade.get_pixel(0, 96)
        assert p == (0, 0, 0)
        p = arcade.get_pixel(0, 94)
        assert p == (255, 255, 255)
        p = arcade.get_pixel(50, 100)
        assert p == (0, 0, 0)
        p = arcade.get_pixel(100, 200)
        assert p == (0, 0, 0)
        p = arcade.get_pixel(150, 300)
        assert p == (0, 0, 0)
        p = arcade.get_pixel(301, 300)
        assert p == (255, 255, 255)


def test_main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.test()
    window.close()
