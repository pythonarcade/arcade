""" Test for sound in Arcade.
(May only work for windows at current time)

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sound_test
"""

import arcade
import os


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sound Test Example"

window = None


class MyGame(arcade.Window):
    """ Main sound test class """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Set background color to black
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """Render the screen"""

        arcade.start_render()

        # Text on screen
        text = "Press left mouse to make noise"

        # Render text
        arcade.draw_text(text, 150, 300, arcade.color.WHITE, 30)

    def on_mouse_press(self, x, y, button, modifiers):
        """Plays sound on key press"""

        # Load sound
        loaded_sound = arcade.sound.load_sound("sounds/laser1.wav")

        # Play Sound
        arcade.sound.play_sound(loaded_sound)

    def update(self, delta_time):
        """animations"""


def main():
    MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
