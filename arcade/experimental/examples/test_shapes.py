"""
This is for testing geometry shader shapes. Please keep.
"""
import time
import random
import arcade
from pyglet import gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TTTLE = "Line Test"

# 16.04
# 0.004


class TestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(800, 600, "Test", antialiasing=True, resizable=True, fullscreen=False)
        # Single lines
        self.single_lines_calls = [
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
        # Line list
        self.line_list = [(random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT)) for _ in range(2 * 10000)]

        self.frames = 0
        self.execution_time = 0

    def do_draw_line(self):
        for l in self.single_lines_calls:
            arcade.draw_line(l[0], l[1], l[2], l[3], l[4], 10)

    def do_draw_lines(self):
        arcade.draw_lines(self.line_list, (255, 0, 0, 10))

    def on_draw(self):
        self.clear()

        start = time.time()

        # Toggle what to test here
        # self.single_lines()
        self.do_draw_lines()

        self.execution_time += time.time() - start
        self.frames += 1

        if self.execution_time > 1.0 and self.frames > 0:
            print(self.frames, round(self.execution_time, 3), round(self.execution_time / self.frames, 3))
            self.execution_time = 0
            self.frames = 0

    def on_resize(self, width, height):
        gl.glViewport(0, 0, *self.get_framebuffer_size())

    def on_update(self, dt):
        pass


if __name__ == '__main__':
    window = TestWindow(SCREEN_HEIGHT, SCREEN_HEIGHT, TTTLE)
    arcade.run()
