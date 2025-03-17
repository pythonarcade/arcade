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

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Full Screen Example"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 40

MOVEMENT_SPEED = 5


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        # Open a window in full screen mode. Remove fullscreen=True if
        # you don't want to start this way.
        super().__init__()

        # This will get the size of the window, and set the viewport to match.
        # So if the window is 1000x1000, then so will our viewport. If
        # you want something different, then use those coordinates instead.
        self.background_color = arcade.color.AMAZON
        self.example_image = arcade.load_texture(":resources:images/tiles/boxCrate_double.png")

        # The camera used to update the viewport and projection on screen resize.
        self.camera = arcade.Camera2D(
            position=(0, 0),
            projection=LRBT(left=0, right=WINDOW_WIDTH, bottom=0, top=WINDOW_HEIGHT),
            viewport=self.window.rect
        )

    def on_draw(self):
        """
        Render the screen.
        """

        self.clear()
        with self.camera.activate():
            # Draw some boxes on the bottom so we can see how they change
            for count in range(20):
                x = count * 128
                y = count * 128
                width = 128
                height = 128
                arcade.draw_texture_rect(self.example_image, arcade.XYWH(x, y, width, height))

            arcade.draw_rect_outline(
                LRBT(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT),
                color=arcade.color.WHITE,
                border_width=5,
            )

            # Draw text on the screen so the user has an idea of what is happening
            text_size = 18
            arcade.draw_text(
                "Press F to toggle between full screen and windowed mode, unstretched.",
                x=WINDOW_WIDTH // 2,
                y=WINDOW_HEIGHT // 2 - 20,
                color=arcade.color.WHITE,
                font_size=text_size,
                anchor_x="center",
            )
            arcade.draw_text(
                "Press S to toggle between full screen and windowed mode, stretched.",
                x=WINDOW_WIDTH // 2,
                y=WINDOW_HEIGHT // 2 + 20,
                color=arcade.color.WHITE,
                font_size=text_size,
                anchor_x="center",
            )

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.F:
            # User hits f. Flip between full and not full screen.
            self.window.set_fullscreen(not self.window.fullscreen)

            # Get the window coordinates. Match viewport to window coordinates
            # so there is a one-to-one mapping.
            self.camera.viewport = self.window.rect
            self.camera.projection = arcade.LRBT(0.0, self.width, 0.0, self.height)

        if key == arcade.key.S:
            # User hits s. Flip between full and not full screen.
            self.window.set_fullscreen(not self.window.fullscreen)

            # Instead of a one-to-one mapping, stretch/squash window to match the
            # constants. This does NOT respect aspect ratio. You'd need to
            # do a bit of math for that.
            self.camera.projection = LRBT(
                left=0,
                right=WINDOW_WIDTH,
                bottom=0,
                top=WINDOW_HEIGHT,
            )
            self.camera.viewport = self.window.rect

        if key == arcade.key.ESCAPE:
            self.window.close()


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on f
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
