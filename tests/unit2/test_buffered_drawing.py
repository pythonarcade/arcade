import arcade
import os
import pyglet.gl as gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def make_objects():
    shape_list = arcade.ShapeElementList()

    center_x = 0
    center_y = 0
    width = 20
    height = 20
    shape = arcade.create_ellipse_filled(center_x, center_y, width, height, arcade.color.WHITE)
    shape_list.append(shape)

    center_x += 40
    shape = arcade.create_ellipse_outline(center_x, center_y, width, height, arcade.color.RED, border_width=1)
    shape_list.append(shape)

    center_x += 40
    shape = arcade.create_ellipse_outline(center_x, center_y, width, height, arcade.color.DARK_RED, border_width=1)
    shape_list.append(shape)

    shape = arcade.create_line(0, 0, 80, 0, arcade.color.BLUE, line_width=1)
    shape_list.append(shape)

    shape = arcade.create_line(0, 0, 80, 0, arcade.color.LIGHT_BLUE, line_width=1)
    shape_list.append(shape)

    center_x = 0
    center_y = 50
    width = 20
    height = 20
    outside_color = arcade.color.AERO_BLUE
    inside_color = arcade.color.AFRICAN_VIOLET
    tilt_angle = 45
    shape = arcade.create_ellipse_filled_with_colors(center_x, center_y,
                                                     width, height,
                                                     outside_color, inside_color,
                                                     tilt_angle)
    shape_list.append(shape)

    center_x = 0
    center_y = -50
    width = 20
    height = 20
    shape = arcade.create_rectangle_filled(center_x, center_y, width, height,
                                           arcade.color.WHITE)
    shape_list.append(shape)
    shape = arcade.create_rectangle_outline(center_x, center_y, width, height,
                                            arcade.color.BLACK, border_width=1)
    shape_list.append(shape)
    shape = arcade.create_rectangle_outline(center_x, center_y, width, height,
                                            arcade.color.AMERICAN_ROSE, border_width=1)
    shape_list.append(shape)

    color1 = (215, 214, 165)
    color2 = (219, 166, 123)
    points = (70, 70), (150, 70), (150, 150), (70, 150)
    colors = (color1, color1, color2, color2)
    shape = arcade.create_rectangle_filled_with_colors(points, colors)
    shape_list.append(shape)

    points = (0, 0), (150, 150), (0, 150), (0, 250)
    shape = arcade.create_line_strip(points, arcade.color.AFRICAN_VIOLET)
    shape_list.append(shape)

    points = (0, 0), (75, 90), (60, 150), (90, 250)
    shape = arcade.create_line_generic(points, arcade.color.ALIZARIN_CRIMSON, gl.GL_TRIANGLE_FAN)
    shape_list.append(shape)

    return shape_list


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """
        Initializer
        """
        super().__init__(width, height)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        new_path = os.path.join(file_path, '..', '..', 'arcade', 'examples')
        os.chdir(new_path)

        arcade.set_background_color(arcade.color.AMAZON)

        self.shape_list = make_objects()

        self.shape_list.center_x = 200
        self.shape_list.center_y = 200

    def on_draw(self):
        """
        Render the screen.
        """

        # Start the render process. This must be done before any drawing commands.
        arcade.start_render()

        self.shape_list.draw()

    def update(self, delta_time):
        """ Movement and game logic """
        self.shape_list.move(1, 1)
        self.shape_list.angle += .1


def test_main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.test()
    window.close()
