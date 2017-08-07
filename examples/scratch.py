"""
Array Backed Grid

Show how to use a two-dimensional list/array to back the display of a
grid on-screen.
"""
import arcade
import math

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400




class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Set up the application.
        """
        super().__init__(width, height, resizable=True)
        self.set_location(20, 20)
        arcade.set_background_color(arcade.color.BLACK)

        self.my_shape_1 = arcade.ShapeElementList()

        box = arcade.create_rectangle_filled(0, 0, 50, 50, arcade.color.WHITE)
        self.my_shape_1.append(box)
        box = arcade.create_rectangle_filled(60, 60, 5, 5, arcade.color.GREEN)
        self.my_shape_1.append(box)
        # box = arcade.create_rectangle_filled(-60, -60, 5, 5, arcade.color.RED)
        # self.my_shape_1.append(box)
        # box = arcade.create_rectangle_filled(60, -60, 5, 5, arcade.color.BLUE)
        # self.my_shape_1.append(box)



    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()
        self.my_shape_1.draw()


    def update(self, delta_time):
        self.my_shape_1.center_x += 1
        self.my_shape_1.center_y += 1


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)

arcade.run()
