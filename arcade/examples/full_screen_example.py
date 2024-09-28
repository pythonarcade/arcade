"""
Use sprites to scroll around a large screen.

Simple program to show basic sprite usage.

Artwork from https://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.full_screen_example
"""

import arcade
from arcade.types import LRBT

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

        # This will get the size of the window, and set the viewport to match.
        # So if the window is 1000x1000, then so will our viewport. If
        # you want something different, then use those coordinates instead.
        self.background_color = arcade.color.AMAZON
        self.example_image = arcade.load_texture(":resources:images/tiles/boxCrate_double.png")

        # The camera used to update the viewport and projection on screen resize.
        self.camera = arcade.camera.Camera2D(position=(0, 0))
        self.camera.projection = LRBT(left=0, right=self.width, bottom=0, top=self.height)
        self.camera.viewport = LRBT(left=0, right=self.width, bottom=0, top=self.height)

    def on_draw(self):
        """
        Render the screen.
        """

        self.clear()
        self.camera.use()
        self.camera.position = 0, 0
        # Draw some boxes on the bottom so we can see how they change
        for count in range(20):
            x = count * 128
            y = count * 128
            width = 128
            height = 128
            arcade.draw_texture_rect(self.example_image, arcade.XYWH(x, y, width, height))

        arcade.draw_rect_outline(
            LRBT(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT),
            color=arcade.color.WHITE,
            border_width=5,
        )

        # Draw text on the screen so the user has an idea of what is happening
        text_size = 18
        arcade.draw_text(
            "Press F to toggle between full screen and windowed mode, unstretched.",
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2 - 20,
            color=arcade.color.WHITE,
            font_size=text_size,
            anchor_x="center",
        )
        arcade.draw_text(
            "Press S to toggle between full screen and windowed mode, stretched.",
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2 + 20,
            color=arcade.color.WHITE,
            font_size=text_size,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.F:
            # User hits f. Flip between full and not full screen.
            self.set_fullscreen(not self.fullscreen)

            # Get the window coordinates. Match viewport to window coordinates
            # so there is a one-to-one mapping.
            self.camera.projection = LRBT(left=0, right=self.width, bottom=0, top=self.height)
            self.camera.viewport = LRBT(left=0, right=self.width, bottom=0, top=self.height)

        if key == arcade.key.S:
            # User hits s. Flip between full and not full screen.
            self.set_fullscreen(not self.fullscreen)

            # Instead of a one-to-one mapping, stretch/squash window to match the
            # constants. This does NOT respect aspect ratio. You'd need to
            # do a bit of math for that.
            self.camera.projection = LRBT(
                left=0,
                right=SCREEN_WIDTH,
                bottom=0,
                top=SCREEN_HEIGHT,
            )
            self.camera.viewport = LRBT(
                left=0,
                right=self.width,
                bottom=0,
                top=self.height,
            )

        if key == arcade.key.ESCAPE:
            self.close()


def main():
    """ Main function """
    MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
