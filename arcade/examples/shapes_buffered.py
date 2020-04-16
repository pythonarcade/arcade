"""
This simple animation example shows how to use classes to animate
multiple objects on the screen at the same time.

Because this is redraws the shapes from scratch each frame, this is SLOW
and inefficient.

Using buffered drawing commands (Vertex Buffer Objects) is a bit more complex,
but faster.

See http://arcade.academy/examples/index.html#shape-lists for some examples.

Also, any Sprite class put in a SpriteList and drawn with the SpriteList will
be drawn using Vertex Buffer Objects for better performance.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shapes

"""

import arcade
import random
import timeit

# Set up the constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Shapes! Buffered"

RECT_WIDTH = 50
RECT_HEIGHT = 50

NUMBER_OF_SHAPES = 500


class Shape:
    """ Generic base shape class """
    def __init__(self, x, y, width, height, angle, delta_x, delta_y,
                 delta_angle, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.delta_angle = delta_angle
        self.color = color
        self.shape_list = None

    def move(self):
        self.x += self.delta_x
        self.y += self.delta_y
        self.angle += self.delta_angle
        if self.x < 0 and self.delta_x < 0:
            self.delta_x *= -1
        if self.y < 0 and self.delta_y < 0:
            self.delta_y *= -1
        if self.x > SCREEN_WIDTH and self.delta_x > 0:
            self.delta_x *= -1
        if self.y > SCREEN_HEIGHT and self.delta_y > 0:
            self.delta_y *= -1

    def draw(self):
        self.shape_list.center_x = self.x
        self.shape_list.center_y = self.y
        # self.shape_list.angle = self.angle
        self.shape_list.draw()

class Ellipse(Shape):

    def __init__(self, x, y, width, height, angle, delta_x, delta_y,
                 delta_angle, color):

        super().__init__(x, y, width, height, angle, delta_x, delta_y,
                         delta_angle, color)

        shape = arcade.create_ellipse_filled(0, 0,
                                             self.width, self.height,
                                             self.color, self.angle)
        self.shape_list = arcade.ShapeElementList()
        self.shape_list.append(shape)


class Rectangle(Shape):

    def __init__(self, x, y, width, height, angle, delta_x, delta_y,
                 delta_angle, color):

        super().__init__(x, y, width, height, angle, delta_x, delta_y,
                         delta_angle, color)

        shape = arcade.create_rectangle_filled(0, 0,
                                               self.width, self.height,
                                               self.color, self.angle)
        self.shape_list = arcade.ShapeElementList()
        self.shape_list.append(shape)

class Line(Shape):

    def __init__(self, x, y, width, height, angle, delta_x, delta_y,
                 delta_angle, color):

        super().__init__(x, y, width, height, angle, delta_x, delta_y,
                         delta_angle, color)

        shape = arcade.create_line(0, 0,
                                   self.width, self.height,
                                   self.color, 2)
        self.shape_list = arcade.ShapeElementList()
        self.shape_list.append(shape)

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.shape_list = None

        self.processing_time = 0
        self.draw_time = 0
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None

    def setup(self):
        """ Set up the game and initialize the variables. """
        self.shape_list = []

        for i in range(NUMBER_OF_SHAPES):
            x = random.randrange(0, SCREEN_WIDTH)
            y = random.randrange(0, SCREEN_HEIGHT)
            width = random.randrange(10, 30)
            height = random.randrange(10, 30)
            angle = random.randrange(0, 360)

            d_x = random.randrange(-3, 4)
            d_y = random.randrange(-3, 4)
            d_angle = random.randrange(-3, 4)

            red = random.randrange(256)
            green = random.randrange(256)
            blue = random.randrange(256)
            alpha = random.randrange(256)

            shape_type = random.randrange(3)
            # shape_type = 2

            if shape_type == 0:
                shape = Rectangle(x, y, width, height, angle, d_x, d_y,
                                  d_angle, (red, green, blue, alpha))
            elif shape_type == 1:
                shape = Ellipse(x, y, width, height, angle, d_x, d_y,
                            d_angle, (red, green, blue, alpha))
            elif shape_type == 2:
                shape = Line(x, y, width, height, angle, d_x, d_y,
                             d_angle, (red, green, blue, alpha))

            self.shape_list.append(shape)

    def on_update(self, dt):
        """ Move everything """
        start_time = timeit.default_timer()

        for shape in self.shape_list:
            shape.move()

        self.processing_time = timeit.default_timer() - start_time

    def on_draw(self):
        """
        Render the screen.
        """
        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        if self.frame_count % 60 == 0:
            if self.fps_start_timer is not None:
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = 60 / total_time
            self.fps_start_timer = timeit.default_timer()
        self.frame_count += 1

        arcade.start_render()

        for shape in self.shape_list:
            shape.draw()

        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 16)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 16)

        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.WHITE, 16)

        self.draw_time = timeit.default_timer() - draw_start_time


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
