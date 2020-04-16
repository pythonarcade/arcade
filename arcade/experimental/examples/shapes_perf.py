"""
This is for testing geometry shader shapes. Please keep.
"""
import time
import random
import arcade
from pyglet import gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Line Test"

# line / lines
# rectangle_filled / rectangle_outline / rectangle_textured
# parabola


def random_pos():
    return random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT)


def random_color(alpha=127):
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), alpha


def random_radius(start=5, end=25):
    return random.randrange(start, end)


class TestWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=False, resizable=True)
        # Single lines
        self.single_lines_calls = [(*random_pos(), *random_pos(), random_color()) for _ in range(600)]
        # Line list
        self.line_list = [(random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT)) for _ in range(2 * 10000)]

        # Single circle draw calls
        self.single_circle_calls = [(*random_pos(), random_radius(), random_color()) for _ in range(200)]

        self.frames = 0
        self.elapsed = 0
        self.execution_time = 0

    def do_draw_line(self):
        for l in self.single_lines_calls:
            arcade.draw_line(l[0], l[1], l[2], l[3], l[4], 10)

    def do_draw_lines(self):
        arcade.draw_lines(self.line_list, (255, 0, 0, 10))

    def do_draw_circle_filled(self):
        # for c in self.single_circle_calls:
        #     arcade.draw_circle_filled(c[0], c[1], c[2], c[3])
        arcade.draw_circle_filled(400, 300, 300, arcade.color.AZURE)

    def do_draw_ellipse_filled(self):
        arcade.draw_ellipse_filled(400, 300, 100, 200, arcade.color.AZURE, self.elapsed * 10)

    def do_draw_circle_outline(self):
        pass

    def on_draw(self):
        try:
            self.clear()

            start = time.time()

            # Toggle what to test here
            # self.do_draw_line()
            # self.do_draw_lines()
            self.do_draw_circle_filled()
            # self.do_draw_ellipse_filled()

            self.execution_time += time.time() - start
            self.frames += 1

            if self.execution_time > 1.0 and self.frames > 0:
                print((
                    f"frames {self.frames}, "
                    f"execution time {round(self.execution_time, 3)}, "
                    f"frame time {round(self.execution_time / self.frames, 3)}"
                ))
                self.execution_time = 0
                self.frames = 0
        except Exception:
            import traceback
            traceback.print_exc()
            exit(0)

    def on_resize(self, width, height):
        gl.glViewport(0, 0, *self.get_framebuffer_size())

    def on_update(self, dt):
        self.elapsed += dt


if __name__ == '__main__':
    window = TestWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    arcade.run()
