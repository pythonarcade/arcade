"""Take screenshots for debugging.

This example shows you how to take debug screenshots by:

1. Setting the window's background to a non-transparent color
2. Randomly arranging sprites to display a pattern over it
3. Using arcade.save_screenshot

After installing arcade version 3.0.0 or higher, this example can be run
from the command line with:
python -m arcade.examples.debug_screenshot
"""
import random
import arcade
from arcade.types import Color


SCREENSHOT_FILE_NAME = "debug_screenshot_image.png"

# How many sprites to draw and how big they'll be
NUM_SPRITES = 100
MIN_RADIUS_PX = 5
MAX_RADIUS_PX = 50

# Window size
WIDTH_PX = 800
HEIGHT_PX = 600


class ScreenshotWindow(arcade.Window):

    def __init__(self):
        super().__init__(WIDTH_PX, HEIGHT_PX, "Press space to save a screenshot")

        # Important: we have to set a non-transparent background color,
        # or else the screenshot will have a transparent background.
        self.background_color = arcade.color.AMAZON

        # Randomize circle sprite positions, sizes, and colors
        self.sprites = arcade.SpriteList()
        for i in range(NUM_SPRITES):
            sprite = arcade.SpriteCircle(
                random.randint(MIN_RADIUS_PX, MAX_RADIUS_PX),
                Color.random(a=255)
            )
            sprite.position = (
                random.uniform(0, self.width),
                random.uniform(0, self.height)
            )
            self.sprites.append(sprite)

    def on_draw(self):
        self.clear()
        self.sprites.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            arcade.save_screenshot(SCREENSHOT_FILE_NAME)
            # You can also use the format below instead.
            # self.save_screenshot(SCREENSHOT_FILE_NAME)


if __name__ == "__main__":
    window = ScreenshotWindow()
    arcade.run()
