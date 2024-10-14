"""
City Scape Generator

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shape_list_demo_skylines
"""
import random
import arcade
from arcade.shape_list import (
    ShapeElementList,
    create_rectangle_filled,
    create_polygon,
    create_rectangles_filled_with_colors,
)

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Skyline Using Buffered Shapes"


def make_star_field(star_count):
    """Make a bunch of circles for stars"""
    shape_list = ShapeElementList()

    for _ in range(star_count):
        x = random.randrange(WINDOW_WIDTH)
        y = random.randrange(WINDOW_HEIGHT)
        radius = random.randrange(1, 4)
        brightness = random.randrange(127, 256)
        color = (brightness, brightness, brightness)
        shape = create_rectangle_filled(x, y, radius, radius, color)
        shape_list.append(shape)

    return shape_list


def make_skyline(width, skyline_height, skyline_color,
                 gap_chance=0.70, window_chance=0.30, light_on_chance=0.5,
                 window_color=(255, 255, 200), window_margin=3, window_gap=2,
                 cap_chance=0.20):
    """Make a skyline of buildings"""
    shape_list = ShapeElementList()

    # Add the "base" that we build the buildings on
    shape = create_rectangle_filled(
        center_x=width / 2,
        center_y=skyline_height / 2,
        width=width,
        height=skyline_height,
        color=skyline_color,
    )
    shape_list.append(shape)

    building_center_x = 0

    skyline_point_list = []
    color_list = []

    while building_center_x < width:

        # Is there a gap between the buildings?
        if random.random() < gap_chance:
            gap_width = random.randrange(10, 50)
        else:
            gap_width = 0

        # Figure out location and size of building
        building_width = random.randrange(20, 70)
        building_height = random.randrange(40, 150)
        building_center_x += gap_width + (building_width / 2)
        building_center_y = skyline_height + (building_height / 2)

        x1 = building_center_x - building_width / 2
        x2 = building_center_x + building_width / 2
        y1 = skyline_height
        y2 = skyline_height + building_height

        skyline_point_list.append([x1, y1])
        skyline_point_list.append([x1, y2])
        skyline_point_list.append([x2, y2])
        skyline_point_list.append([x2, y1])

        for i in range(4):
            color_list.append([skyline_color[0], skyline_color[1], skyline_color[2]])

        if random.random() < cap_chance:
            x1 = building_center_x - building_width / 2
            x2 = building_center_x + building_width / 2
            x3 = building_center_x

            y1 = y2 = building_center_y + building_height / 2
            y3 = y1 + building_width / 2

            # Roof
            shape = create_polygon([[x1, y1], [x2, y2], [x3, y3]], skyline_color)
            shape_list.append(shape)

        # See if we should have some windows
        if random.random() < window_chance:
            # Yes windows! How many windows?
            window_rows = random.randrange(10, 15)
            window_columns = random.randrange(1, 7)

            # Based on that, how big should they be?
            window_height = (building_height - window_margin * 2) / window_rows
            window_width = (
                (building_width - window_margin * 2 - window_gap * (window_columns - 1))
                / window_columns
            )

            # Find the bottom left of the building so we can start adding widows
            building_base_y = building_center_y - building_height / 2
            building_left_x = building_center_x - building_width / 2

            # Loop through each window
            for row in range(window_rows):
                for column in range(window_columns):
                    if random.random() > light_on_chance:
                        continue

                    x1 = (
                        building_left_x
                        + column * (window_width + window_gap)
                        + window_margin
                    )
                    x2 = (
                        building_left_x
                        + column * (window_width + window_gap)
                        + window_width
                        + window_margin
                    )
                    y1 = building_base_y + row * window_height
                    y2 = building_base_y + row * window_height + window_height * .8

                    skyline_point_list.append([x1, y1])
                    skyline_point_list.append([x1, y2])
                    skyline_point_list.append([x2, y2])
                    skyline_point_list.append([x2, y1])

                    for i in range(4):
                        color_list.append((
                            window_color[0],
                            window_color[1],
                            window_color[2],
                        ))

        building_center_x += (building_width / 2)

    shape = create_rectangles_filled_with_colors(skyline_point_list, color_list)
    shape_list.append(shape)

    return shape_list


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()
        # Enable vertical sync to make scrolling smoother
        self.window.set_vsync(True)

        self.stars = make_star_field(150)
        self.skyline1 = make_skyline(WINDOW_WIDTH * 5, 250, (80, 80, 80))
        self.skyline2 = make_skyline(WINDOW_WIDTH * 5, 150, (50, 50, 50))

        self.background_color = arcade.color.BLACK

    def on_draw(self):
        """Draw to screen"""
        self.clear()

        self.stars.draw()
        self.skyline1.draw()
        self.skyline2.draw()

    def on_update(self, delta_time):
        """Per frame update logic"""
        # Scroll each shape list with a slight offset to give a parallax effect
        self.skyline1.center_x -= 0.5 * 60 * delta_time
        self.skyline2.center_x -= 1 * 60 * delta_time

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        """Make it possible scroll the scene around by dragging the mouse"""
        self.skyline1.center_x += dx
        self.skyline1.center_y += dy

        self.skyline2.center_x += dx
        self.skyline2.center_y += dy


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
