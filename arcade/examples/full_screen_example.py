"""
Use sprites to scroll around a large screen.

Simple program to show basic sprite usage.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.full_screen_example
"""

import arcade
import os

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Full Screen Example"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 40

MOVEMENT_SPEED = 5


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        # Open a window in full screen mode. Remove fullscreen=True if
        # you don't want to start this way.
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=True)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # This will get the size of the window, and set the viewport to match.
        # So if the window is 1000x1000, then so will our viewport. If
        # you want something different, then use those coordinates instead.
        width, height = self.get_size()
        self.set_viewport(0, width, 0, height)
        arcade.set_background_color(arcade.color.AMAZON)
        self.example_image = arcade.load_texture("images/boxCrate_double.png")

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()

        # Get viewport dimensions
        left, screen_width, bottom, screen_height = self.get_viewport()

        text_size = 18
        # Draw text on the screen so the user has an idea of what is happening
        arcade.draw_text("Press F to toggle between full screen and windowed mode, unstretched.",
                         screen_width // 2, screen_height // 2 - 20,
                         arcade.color.WHITE, text_size, anchor_x="center")
        arcade.draw_text("Press S to toggle between full screen and windowed mode, stretched.",
                         screen_width // 2, screen_height // 2 + 20,
                         arcade.color.WHITE, text_size, anchor_x="center")

        # Draw some boxes on the bottom so we can see how they change
        for x in range(64, 800, 128):
            y = 64
            width = 128
            height = 128
            arcade.draw_texture_rectangle(x, y, width, height, self.example_image)


    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.F:
            # User hits f. Flip between full and not full screen.
            self.set_fullscreen(not self.fullscreen)

            # Get the window coordinates. Match viewport to window coordinates
            # so there is a one-to-one mapping.
            width, height = self.get_size()
            self.set_viewport(0, width, 0, height)

        if key == arcade.key.S:
            # User hits s. Flip between full and not full screen.
            self.set_fullscreen(not self.fullscreen)

            # Instead of a one-to-one mapping, stretch/squash window to match the
            # constants. This does NOT respect aspect ratio. You'd need to
            # do a bit of math for that.
            self.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)


def main():
    """ Main method """
    MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
