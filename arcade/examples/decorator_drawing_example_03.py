"""
Example "Arcade" library code.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.decorator_drawing_example_02
"""

# Library imports
import arcade
import random
import pyglet
import bisect

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700


# Iterative midpoint vertical displacement
def midpoint_displacement(start, end, roughness, vertical_displacement=None,
                          num_of_iterations=16):
    """
    Given a straight line segment specified by a starting point and an endpoint
    in the form of [starting_point_x, starting_point_y] and [endpoint_x, endpoint_y],
    a roughness value > 0, an initial vertical displacement and a number of
    iterations > 0 applies the  midpoint algorithm to the specified segment and
    returns the obtained list of points in the form
    points = [[x_0, y_0],[x_1, y_1],...,[x_n, y_n]]
    """
    # Final number of points = (2^iterations)+1
    if vertical_displacement is None:
        # if no initial displacement is specified set displacement to:
        #  (y_start+y_end)/2
        vertical_displacement = (start[1]+end[1])/2
    # Data structure that stores the points is a list of lists where
    # each sublist represents a point and holds its x and y coordinates:
    # points=[[x_0, y_0],[x_1, y_1],...,[x_n, y_n]]
    #              |          |              |
    #           point 0    point 1        point n
    # The points list is always kept sorted from smallest to biggest x-value
    points = [start, end]
    iteration = 1
    while iteration <= num_of_iterations:
        # Since the list of points will be dynamically updated with the new computed
        # points after each midpoint displacement it is necessary to create a copy
        # of the state at the beginning of the iteration so we can iterate over
        # the original sequence.
        # Tuple type is used for security reasons since they are immutable in Python.
        points_tup = tuple(points)
        for i in range(len(points_tup)-1):
            # Calculate x and y midpoint coordinates:
            # [(x_i+x_(i+1))/2, (y_i+y_(i+1))/2]
            midpoint = list(map(lambda x: (points_tup[i][x]+points_tup[i+1][x])/2,
                                [0, 1]))
            # Displace midpoint y-coordinate
            midpoint[1] += random.choice([-vertical_displacement,
                                          vertical_displacement])
            # Insert the displaced midpoint in the current list of points
            bisect.insort(points, midpoint)
            # bisect allows to insert an element in a list so that its order
            # is preserved.
            # By default the maintained order is from smallest to biggest list first
            # element which is what we want.
        # Reduce displacement range
        vertical_displacement *= 2 ** (-roughness)
        # update number of iterations
        iteration += 1
    return points

def fix_points(points):
    last_y = None
    last_x = None
    new_list = []
    for point in points:
        x = int(point[0])
        y = int(point[1])

        if last_y is None or y != last_y:
            if last_y is None:
                last_x = x
                last_y = y

            x1 = last_x
            x2 = x
            y1 = last_y
            y2 = y

            new_list.append((x1, 0))
            new_list.append((x1, y1))
            new_list.append((x2, y2))
            new_list.append((x2, 0))

            last_x = x
            last_y = y

    return new_list

def create_mountain_range(height_min, height_max, color_start, color_end):

    shape_list = arcade.ShapeElementList()

    layer_1 = midpoint_displacement([0, 100], [SCREEN_WIDTH, 200], 1.4, 20, 16)
    print(len(layer_1))
    # print(layer_1[:1000])
    layer_1 = fix_points(layer_1)
    print(len(layer_1))
    # print(layer_1)

    color_list = [arcade.color.BLACK] * len(layer_1)
    lines = arcade.create_filled_rectangles_with_colors(layer_1, color_list)
    shape_list.append(lines)

    return shape_list



@arcade.decorator.init
def setup(window):
    """
    This, and any function with the arcade.decorator.init decorator,
    is run automatically on start-up.
    """

    window.mountains = []

    background = arcade.ShapeElementList()

    points = (0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)
    colors = (arcade.color.SKY_BLUE, arcade.color.SKY_BLUE, arcade.color.BLUE, arcade.color.BLUE)
    rect = arcade.create_filled_rectangles_with_colors(points, colors)

    background.append(rect)
    window.mountains.append(background)

    color_start = arcade.color.BLACK
    color_end = arcade.color.BLACK
    min_y = 0
    max_y = 120
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
    arcade.decorator.run(SCREEN_WIDTH, SCREEN_HEIGHT, title="Drawing With Decorators", background_color=arcade.color.WHITE)

