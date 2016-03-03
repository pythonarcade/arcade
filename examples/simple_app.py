"""
Asteroid Smasher

Shoot space rocks in this demo program created with
Python and the Arcade library.

Artwork from http://kenney.nl
"""
import random
import math
import arcade


class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        pass

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()



    def animate(self, x):
        """ Move everything """

        print("animate")


window = MyApplication(1400, 1000)
window.setup()

arcade.run()
