"""
Unit tests
Sprites with texture transformations
"""

import arcade
from arcade import Matrix3x3
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SHIP_SPEED = 5
ASPECT = SCREEN_HEIGHT / SCREEN_WIDTH
SCREEN_TITLE = "Texture transformations"


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """
        Initializer
        """
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.ship = None
        self.camera_x = 0
        self.t = 0
        self.xy_square = None

    def setup(self):
        """ Setup """
        self.ship = arcade.Sprite(":resources:images/space_shooter/playerShip1_orange.png", 0.5)
        self.ship.center_x = SCREEN_WIDTH / 2
        self.ship.center_y = SCREEN_HEIGHT / 2
        self.ship.angle = 270
        self.xy_square = arcade.load_texture(":resources:images/test_textures/xy_square.png")

        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        print()

        tests = [
            ['identity', Matrix3x3(), (14, 14, 0)],
            ['rotate(30)', Matrix3x3().rotate(30), (230, 87, 0)],
            ['scale(0.8, 0.5)', Matrix3x3().scale(0.8, 0.5), (242, 158, 0)],
            ['translate(0.3, 0.1)', Matrix3x3().translate(0.3, 0.1), (194, 245, 0)],
            ['rotate(10).\nscale(0.33, 0.33)', Matrix3x3().rotate(10).scale(0.7, 0.7), (252, 255, 244)],
            ['scale(-1, 1)', Matrix3x3().scale(-1, 1), (243, 14, 0)],
            ['shear(0.3, 0.1)', Matrix3x3().shear(0.3, 0.1), (48, 26, 0)],
            [f'rotate({int(self.t) % 360})', Matrix3x3().rotate(self.t), (14, 14, 0)],
            ]

        for i, test_data in enumerate(tests):
            x = 80 + 180 * (i % 4)
            y = 420 - (i // 4) * 320
            text, texture, desired_color = test_data
            arcade.draw_text(text, x, y - 20 - text.count('\n') * 10, arcade.color.WHITE, 10)
            self.xy_square.draw_transformed(x, y, 100, 100, 0, 255, texture)

            test_x = x + 5
            test_y = y + 5
            actual_color = arcade.get_pixel(test_x, test_y)

            # Mac, with its retina scaling, doesn't match other platforms.
            import sys
            if sys.platform != "darwin":
                # print(actual_color, desired_color)
                assert actual_color[0] == desired_color[0]
                assert actual_color[1] == desired_color[1]
                assert actual_color[2] == desired_color[2]


def test_texture_transform():
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    window.test()
    window.close()
    # arcade.run()
    arcade.cleanup_texture_cache()
