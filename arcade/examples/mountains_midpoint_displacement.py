"""
Mountains Midpoint Displacement

Create a random mountain range.
Original idea and some code from:
https://bitesofcode.wordpress.com/2016/12/23/landscape-generation-using-midpoint-displacement/

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.mountains_midpoint_displacement
"""

# Library imports
import arcade
import random
import bisect

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Mountains Midpoint Displacement Example"


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

    x1 = last_x
    x2 = SCREEN_WIDTH
    y1 = last_y
    y2 = last_y

    new_list.append((x1, 0))
    new_list.append((x1, y1))
    new_list.append((x2, y2))
    new_list.append((x2, 0))

    return new_list


def create_mountain_range(start, end, roughness, vertical_displacement, num_of_iterations, color_start):

    shape_list = arcade.ShapeElementList()

    layer_1 = midpoint_displacement(start, end, roughness, vertical_displacement, num_of_iterations)
    layer_1 = fix_points(layer_1)

    color_list = [color_start] * len(layer_1)
    lines = arcade.create_rectangles_filled_with_colors(layer_1, color_list)
    shape_list.append(lines)

    return shape_list


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.mountains = None

        arcade.set_background_color(arcade.color.WHITE)

    def setup(self):
        """
        This, and any function with the arcade.decorator.init decorator,
        is run automatically on start-up.
        """
        self.mountains = []

        background = arcade.ShapeElementList()

        color1 = (195, 157, 224)
        color2 = (240, 203, 163)
        points = (0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)
        colors = (color1, color1, color2, color2)
        rect = arcade.create_rectangle_filled_with_colors(points, colors)

        background.append(rect)
        self.mountains.append(background)

        layer_4 = create_mountain_range([0, 350], [SCREEN_WIDTH, 320], 1.1, 250, 8, (158, 98, 204))
        self.mountains.append(layer_4)

        layer_3 = create_mountain_range([0, 270], [SCREEN_WIDTH, 190], 1.1, 120, 9, (130, 79, 138))
        self.mountains.append(layer_3)

        layer_2 = create_mountain_range([0, 180], [SCREEN_WIDTH, 80], 1.2, 30, 12, (68, 28, 99))
        self.mountains.append(layer_2)

        layer_1 = create_mountain_range([250, 0], [SCREEN_WIDTH, 200], 1.4, 20, 12, (49, 7, 82))
        self.mountains.append(layer_1)

    def on_draw(self):
        """
        Render the screen.
        """

        arcade.start_render()
        """
        This is called every time we need to update our screen. About 60
        times per second.
        
        Just draw things in this function, don't update where they are.
        """
        # Call our drawing functions.

        for mountain_range in self.mountains:
            mountain_range.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        pass


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
