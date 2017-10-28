"""
City Scape Generator
"""
import random
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def make_star_field(star_count):
    """ Make a bunch of circles for stars. """

    shape_list = arcade.ShapeElementList()

    for star_no in range(star_count):
        x = random.randrange(SCREEN_WIDTH)
        y = random.randrange(SCREEN_HEIGHT)
        radius = random.randrange(1, 4)
        brightness = random.randrange(127, 256)
        color = (brightness, brightness, brightness)
        shape = arcade.create_ellipse_filled(x, y, radius, radius, color)
        shape_list.append(shape)

    return shape_list


def make_skyline(width, skyline_height, skyline_color):
    """ Make a skyline """

    shape_list = arcade.ShapeElementList()

    gap_chance = 0.70
    window_chance = 0.30
    light_on_chance = 0.5
    window_color = (255, 255, 200)
    window_margin = 3
    window_gap = 2

    # Add the "base" that we build the buildings on
    shape = arcade.create_rectangle_filled(width / 2, skyline_height / 2, width, skyline_height, skyline_color)
    shape_list.append(shape)

    building_center_x = 0
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

        # Add building to the list
        shape = arcade.create_rectangle_filled(building_center_x, building_center_y,
                                               building_width, building_height, skyline_color)
        shape_list.append(shape)

        # See if we should have some windows
        if random.random() < window_chance:
            # Yes windows! How many windows?
            window_rows = random.randrange(10, 15)
            window_columns = random.randrange(1, 7)

            # Based on that, how big should they be?
            window_height = (building_height - window_margin * 2) / window_rows
            window_width = (building_width - window_margin * 2 - window_gap * (window_columns - 1)) / window_columns

            # Find the bottom left of the building so we can start adding widows
            building_base_y = building_center_y - building_height / 2
            building_left_x = building_center_x - building_width / 2

            # Loop through each window
            for row in range(window_rows):
                for column in range(window_columns):
                    if random.random() < light_on_chance:
                        window_y = building_base_y + row * window_height + window_height / 2
                        window_x = building_left_x + column * (window_width + window_gap) + window_width / 2 + window_margin
                        shape = arcade.create_rectangle_filled(window_x, window_y,
                                                               window_width, window_height * 0.8, window_color)
                        shape_list.append(shape)

        building_center_x += (building_width / 2)

    return shape_list


class MyWindow(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Shape Demo")

        self.stars = make_star_field(150)
        self.skyline1 = make_skyline(SCREEN_WIDTH, 250, (80, 80, 80))
        self.skyline2 = make_skyline(SCREEN_WIDTH, 150, (50, 50, 50))

        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        """ Set up the game and initialize the variables. """

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.stars.draw()
        self.skyline1.draw()
        self.skyline2.draw()

    def update(self, delta_time):
        """ Movement and game logic """
        pass



def main():
    window = MyWindow()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
