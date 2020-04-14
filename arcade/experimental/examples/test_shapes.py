"""
This is for testing geometry shader shapes. Please keep.
"""

import random
import arcade
from pyglet import gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TTTLE = "Line Test"


class TestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(800, 600, "Test", antialiasing=True, resizable=True, fullscreen=False)
        self.lines = [
            (
                random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT),
                random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT),
                (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    127
                )
            )
            for _ in range(600)
        ]

    def on_draw(self):
        self.clear()
        # arcade.draw_point(155, 150, arcade.color.WHITE, 4)
        # arcade.draw_circle_filled(400, 300, 250, arcade.color.GREEN)
        for l in self.lines:
            arcade.draw_line(l[0], l[1], l[2], l[3], l[4], 10)

    def on_resize(self, width, height):
        gl.glViewport(0, 0, *self.get_framebuffer_size())


if __name__ == '__main__':
    window = TestWindow(SCREEN_HEIGHT, SCREEN_HEIGHT, TTTLE)
    arcade.run()
