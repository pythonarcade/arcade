"""
Array Backed Grid

Show how to use a two-dimensional list/array to back the display of a
grid on-screen.
"""
import arcade

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height):
        """
        Set up the application.
        """
        super().__init__(width, height)

        self.shape_list = arcade.ShapeList()
        my_line = arcade.create_line(-100, 0, 100, 0, arcade.color.PURPLE, 10)
        self.shape_list.append(my_line)
        my_line = arcade.create_line(0, -100, 0, 100, arcade.color.PURPLE_MOUNTAIN_MAJESTY, 10)
        self.shape_list.append(my_line)
        self.shape_list.center_x = 100
        self.shape_list.center_y = 100

        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.shape_list.draw()

    def update(self, delta_time):
        self.shape_list.angle += 1
        self.shape_list.center_x += 1
        self.shape_list.center_y += 1
        #print(self.shape_list.angle)

window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)

arcade.run()
