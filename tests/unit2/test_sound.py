import arcade
import os

from pathlib import Path

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """
        Initializer
        """
        super().__init__(width, height)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        # noinspection PyUnresolvedReferences
        os.chdir(file_path / Path("../../arcade/examples"))

        arcade.set_background_color(arcade.color.WHITE)
        self.laser_wav = arcade.load_sound("sounds/laser1.wav")
        self.laser_mp3 = arcade.load_sound("sounds/laser1.mp3")
        self.laser_ogg = arcade.load_sound("sounds/laser1.ogg")
        self.frame_count = 0

    def update(self, dt):
        self.frame_count += 1

        if self.frame_count == 1:
            print(f"Play {self.frame_count}")
            arcade.play_sound(self.laser_wav)

        if self.frame_count == 60:
            print(f"Play {self.frame_count}")
            arcade.play_sound(self.laser_ogg)

        if self.frame_count == 90:
            print(f"Play {self.frame_count}")
            arcade.play_sound(self.laser_mp3)

    def on_draw(self):
        """
        Render the screen.
        """

        # Start the render process. This must be done before any drawing commands.
        arcade.start_render()


def test_main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.test(180)
    window.close()
