"""
Sprites with texture transformations

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_texture_transform
"""

import arcade
from arcade import Matrix3x3
import math
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
        self.stars = None
        self.xy_square = None

    def setup(self):
        """ Setup """
        self.ship = arcade.Sprite(":resources:images/space_shooter/playerShip1_orange.png", 0.5)
        self.ship.center_x = SCREEN_WIDTH / 2
        self.ship.center_y = SCREEN_HEIGHT / 2
        self.ship.angle = 270
        self.stars = arcade.load_texture(":resources:images/backgrounds/stars.png")
        self.xy_square = arcade.load_texture(":resources:images/test_textures/xy_square.png")

        # Set the background color
        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, delta_time: float):
        """ Update """
        self.ship.update()
        self.camera_x += 2
        self.t += delta_time * 60

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        for z in [300, 200, 150, 100]:
            opacity = int(math.exp(-z / 1000) * 255)
            angle = z
            scale = 150 / z
            translate = scale / 500
            self.stars.draw_transformed(
                0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, opacity,
                Matrix3x3().rotate(angle).scale(scale * ASPECT, scale).translate(-self.camera_x * translate, 0))
        self.ship.draw()

        for i, pair in enumerate([
            ['identity', Matrix3x3()],
            ['rotate(30)', Matrix3x3().rotate(30)],
            ['scale(0.8, 0.5)', Matrix3x3().scale(0.8, 0.5)],
            ['translate(0.3, 0.1)', Matrix3x3().translate(0.3, 0.1)],
            ['rotate(10).\nscale(0.33, 0.33)', Matrix3x3().rotate(10).scale(0.7, 0.7)],
            ['scale(-1, 1)', Matrix3x3().scale(-1, 1)],
            ['shear(0.3, 0.1)', Matrix3x3().shear(0.3, 0.1)],
            [f'rotate({int(self.t) % 360})', Matrix3x3().rotate(self.t)],
        ]):
            x = 80 + 180 * (i % 4)
            y = 420 - (i // 4) * 320
            arcade.draw_text(pair[0], x, y - 20 - pair[0].count('\n') * 10, arcade.color.WHITE, 10)
            self.xy_square.draw_transformed(x, y, 100, 100, 0, 255, pair[1])


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
