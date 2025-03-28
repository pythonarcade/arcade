"""
This is for testing geometry shader shapes. Please keep.
"""

import math
import random
import time

from pyglet.math import Mat4

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TITLE = "Shape Test"

# [x] draw_line
# [x] draw_lines
# [x] draw_circle_filled
# [x] draw_ellipse_filled
# [x] draw_circle_outline
# [x] draw_ellipse_outline
# [ ] draw_arc_filled
# [ ] draw_arc_outline
# [ ] draw_parabola_filled
# [ ] draw_parabola_outline
# [ ] draw_line_strip
# [x] draw_point
# [x] draw_points
# [ ] draw_polygon_filled
# [ ] draw_polygon_outline
# [x] draw_triangle_filled
# [x] draw_triangle_outline
# [x] draw_rectangle_outline
# [x] draw_xywh_rectangle_outline
# [x] draw_lrbt_rectangle_filled
# [x] draw_xywh_rectangle_filled
# [x] draw_rectangle_filled
# [x] draw_scaled_texture_rectangle
# [x] draw_texture_rectangle
# [x] draw_lrwh_rectangle_textured

# --- Buffered
# create_line
# create_line_generic_with_colors
# create_line_generic
# create_line_strip
# create_line_loop
# create_lines
# create_lines_with_colors
# create_polygon
# create_rectangle_filled
# create_rectangle_outline
# create_rectangle
# create_rectangle_filled_with_colors
# create_rectangles_filled_with_colors
# create_triangles_filled_with_colors
# create_ellipse_filled
# create_ellipse_outline
# create_ellipse
# create_ellipse_filled_with_colors


def random_pos():
    return random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT)


def random_color(alpha=127):
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), alpha


def random_radius(start=5, end=25):
    return random.randrange(start, end)


class GameWindow(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title, antialiasing=True, resizable=True)
        self.set_vsync(False)

        # Single lines
        self.single_lines_calls = [
            (*random_pos(), *random_pos(), random_color()) for _ in range(600)
        ]
        # Line list
        self.line_list = [
            (random.randrange(0, SCREEN_WIDTH), random.randrange(0, SCREEN_HEIGHT))
            for _ in range(2 * 10000)
        ]

        # Single circle draw calls
        self.single_circle_calls = [
            (*random_pos(), random_radius(), random_color()) for _ in range(200)
        ]

        # line strip
        self.line_strip = [
            (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(10)
        ]
        # Random list of points
        self.points = [
            (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            for _ in range(10_000)
        ]

        self.frames = 0
        self.elapsed = 0
        self.execution_time = 0

    def do_draw_line(self):
        for ln in self.single_lines_calls:
            arcade.draw_line(ln[0], ln[1], ln[2], ln[3], ln[4], 10)

    def do_draw_lines(self):
        arcade.draw_lines(self.line_list, (255, 0, 0, 10))

    def draw_line_strip(self):
        arcade.draw_line_strip(self.line_strip, arcade.color.WHITE, 20.0)

    def do_draw_circle_filled(self):
        for c in self.single_circle_calls:
            arcade.draw_circle_filled(c[0], c[1], c[2], c[3])

    def do_draw_ellipse_filled(self):
        arcade.draw_ellipse_filled(400, 300, 100, 200, arcade.color.AZURE, self.elapsed * 10)

    def do_draw_circle_outline(self):
        arcade.draw_circle_outline(400, 300, 200, arcade.color.AZURE, 10)

    def do_draw_ellipse_outline(self):
        arcade.draw_ellipse_outline(400, 300, 230, 100, arcade.color.AZURE, 10, 45)

    def do_draw_rectangle(self):
        # 0.1 : 1600
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                arcade.draw_rectangle_filled(x + 10, y + 8, 10, 10, arcade.color.AZURE)

    def do_draw_arc_filled(self):
        arcade.draw_arc_filled(
            400,
            300,
            200,
            200,
            arcade.color.AZURE,
            30.0 - math.sin(self.elapsed) * 20.0,
            340.0 + math.sin(self.elapsed) * 20.0,
            0,
        )

    def do_draw_point(self):
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                arcade.draw_point(x, y, arcade.color.WHITE, 1)

    def do_draw_points(self):
        arcade.draw_points(self.points, arcade.color.WILLPOWER_ORANGE, 1.0)

    def do_draw_rectangle_outline(self):
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                arcade.draw_rectangle_outline(
                    x, y, 10, 10, arcade.color.AERO_BLUE, 5, self.elapsed * 100
                )

    def do_draw_xywh_rectangle_outline(self):
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                arcade.draw_xywh_rectangle_outline(x, y, 10, 10, arcade.color.AERO_BLUE, 5)

    def do_draw_triangle_outline(self):
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                arcade.draw_triangle_outline(
                    x, y, x + 10, y, x + 5, y + 10, arcade.color.AERO_BLUE, 2
                )

    def do_draw_triangle_filled(self):
        for x in range(0, SCREEN_WIDTH, 20):
            for y in range(0, SCREEN_HEIGHT, 20):
                arcade.draw_triangle_filled(x, y, x + 10, y, x + 5, y + 10, arcade.color.AERO_BLUE)

    def do_draw_polygon_outline(self):
        arcade.draw_polygon_outline(self.points, arcade.color.AERO_BLUE)

    def on_draw(self):
        self.clear()

        start = time.time()

        # Toggle what to test here
        # self.do_draw_line()
        # self.do_draw_lines()
        # self.draw_line_strip()
        # self.do_draw_circle_filled()
        # self.do_draw_ellipse_filled()
        # self.do_draw_circle_outline()
        # self.do_draw_ellipse_outline()
        # self.do_draw_rectangle()
        # self.do_draw_arc_filled()
        # self.do_draw_point()
        # self.do_draw_points()
        # self.do_draw_rectangle_outline()  # 0.33
        # self.do_draw_xywh_rectangle_outline()
        # self.do_draw_triangle_outline()  # 0.42
        # self.do_draw_triangle_filled()  # 0.26
        self.do_draw_polygon_outline()

        self.ctx.finish()
        self.execution_time += time.time() - start
        self.frames += 1

        if self.execution_time > 1.0 and self.frames > 0:
            print(
                (
                    f"frames {self.frames}, "
                    f"execution time {round(self.execution_time, 3)}, "
                    f"frame time {round(self.execution_time / self.frames, 3)}"
                )
            )
            self.execution_time = 0
            self.frames = 0

    def on_update(self, dt):
        self.elapsed += dt

    def on_resize(self, width: float, height: float):
        w, h = self.get_framebuffer_size()
        self.ctx.viewport = 0, 0, w, h
        self.ctx.projection_matrix = Mat4.orthogonal_projection(0, 800, 0, 600, -100, 100)


if __name__ == "__main__":
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    arcade.run()
