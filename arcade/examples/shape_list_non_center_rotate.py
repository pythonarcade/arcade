import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


def make_shape():

    shape_list = arcade.ShapeElementList()

    # Shape center around which we will rotate
    center_x = 20
    center_y = 30

    width = 30
    height = 40

    shape = arcade.create_ellipse_filled(center_x, center_y, width, height, arcade.color.WHITE)
    shape_list.append(shape)

    return shape_list


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Shape Demo")

        self.shape_list = make_shape()

        # This specifies where on the screen the center of the shape will go
        self.shape_list.center_x = SCREEN_WIDTH / 2
        self.shape_list.center_y = SCREEN_HEIGHT / 2

        arcade.set_background_color(arcade.color.AMAZON)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.shape_list.draw()

    def update(self, delta_time):
        """ Movement and game logic """
        self.shape_list.angle += 1


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
