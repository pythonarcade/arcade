""" Test for sound in Arcade.
(May only work for windows at current time)
"""

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

window = None


class MyGame(arcade.Window):
    """ Main sound test class """

    def setup(self):

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
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
