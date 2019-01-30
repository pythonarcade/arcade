"""
Mountains Random Walk

Idea and algorithm from:
https://hackernoon.com/a-procedural-landscape-experiment-4efe1826906f

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.mountains_random_walk
"""

# Library imports
import arcade
import random
import pyglet

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Mountains Random Walk Example"


def create_mountain_range(height_min, height_max, color_start, color_end):

    shape_list = arcade.ShapeElementList()

    step_max = 1.5
    step_change = 0.5

    height = random.random() * height_max
    slope = (random.random() * step_max * 2) - step_max

    line_point_list = []
    line_color_list = []

    for x in range(SCREEN_WIDTH):
        height += slope
        slope += (random.random() * step_change * 2) - step_change

        if slope > step_max:
            slope = step_max
        elif slope < -step_max:
            slope = -step_max

        if height > height_max:
            height = height_max
            slope *= -1
        elif height < height_min:
            height = height_min
            slope *= -1

        line_point_list.extend( ((x, height), (x, 0)) )
        line_color_list.extend( (color_start, color_end) )

    lines = arcade.create_lines_with_colors(line_point_list, line_color_list)
    shape_list.append(lines)

    return shape_list


def create_line_strip():
    shape_list = arcade.ShapeElementList()

    line_strip = arcade.create_lines_with_colors(([10, 10], [500, 10],
                                                  [10, 250], [500, 250],
                                                  [10, 500], [500, 500]),
                                                 (arcade.color.RED, arcade.color.BLACK, arcade.color.GREEN, arcade.color.BLACK, arcade.color.BLUE, arcade.color.BLACK), line_width=4)

    shape_list.append(line_strip)

    return shape_list


@arcade.decorator.setup
def setup(window):
    """
    This, and any function with the arcade.decorator.init decorator,
    is run automatically on start-up.
    """

    window.mountains = []

    background = arcade.ShapeElementList()

    points = (0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)
    colors = (arcade.color.SKY_BLUE, arcade.color.SKY_BLUE, arcade.color.BLUE, arcade.color.BLUE)
    rect = arcade.create_rectangles_filled_with_colors(points, colors)

    background.append(rect)
    window.mountains.append(background)

    for i in range(1, 4):
        color_start = (i * 10, i * 30, i * 10)
        color_end = (i * 20, i * 40, i * 20)
        min_y = 0 + 70 * (3-i)
        max_y = 120 + 70 * (3-i)
        mountain_range = create_mountain_range(min_y, max_y, color_start, color_end)
        window.mountains.append(mountain_range)


@arcade.decorator.draw
def draw(window):
    """
    This is called every time we need to update our screen. About 60
    times per second.

    Just draw things in this function, don't update where they are.
    """
    # Call our drawing functions.

    for mountain_range in window.mountains:
        mountain_range.draw()

    # window.line_strip.draw()


if __name__ == "__main__":
    arcade.decorator.run(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, background_color=arcade.color.WHITE)

