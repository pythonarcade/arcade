""" This simple animation example shows how to bounce a rectangle
on the screen. """

import arcade
import random
import time

# Set up the constants
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

RECT_WIDTH = 50
RECT_HEIGHT = 50


class Shape():

    def __init__(self, x, y, width, height, angle, delta_x, delta_y, delta_angle, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.delta_angle = delta_angle
        self.color = color

    def move(self):
        self.x += self.delta_x
        self.y += self.delta_y
        self.angle += self.delta_angle

class Ellipse(Shape):
    def __init__(self, x, y, width, height, angle, delta_x, delta_y, delta_angle, color):
        super().__init__(x, y, width, height, angle, delta_x, delta_y, delta_angle, color)
        self.vbo = arcade.create_ellipse(self.width, self.height, self.color)

    def draw(self):
        # arcade.draw_ellipse_filled(self.x, self.y, self.width, self.height, self.color, self.angle)
        arcade.render_ellipse_filled(self.vbo, self.x, self.y, self.color, self.angle)

class Rectangle(Shape):
    def __init__(self, x, y, width, height, angle, delta_x, delta_y, delta_angle, color):
        super().__init__(x, y, width, height, angle, delta_x, delta_y, delta_angle, color)
        self.vbo = arcade.create_rect(self.width, self.height, self.color)


    def draw(self):
        # arcade.draw_rect_filled(self.x, self.y, self.width, self.height, self.color, self.angle)
        arcade.render_rect_filled(self.vbo, self.x, self.y, self.color, self.angle)


class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        """ Set up the game and initialize the variables. """

        arcade.set_background_color(arcade.color.WHITE)

        self.shape_list = []

        for i in range(2000):
            x = random.randrange(0, SCREEN_WIDTH)
            y = random.randrange(0, SCREEN_HEIGHT)
            width = random.randrange(20, 71)
            height = random.randrange(20, 71)
            angle = random.randrange(0, 360)
            angle = 0

            d_x = random.randrange(-3, 4)
            d_y = random.randrange(-3, 4)
            # d_x = 0
            # d_y = 0
            d_angle = random.randrange(-3, 4)
            d_angle = 0

            red = random.randrange(256)
            green = random.randrange(256)
            blue = random.randrange(256)
            alpha = random.randrange(256)
            shape_type = random.randrange(2)
            #shape_type = 0

            if shape_type == 0:
                shape = Rectangle(x, y, width, height, angle, d_x, d_y, d_angle, (red, green, blue))
            else:
                shape = Ellipse(x, y, width, height, angle, d_x, d_y, d_angle, (red, green, blue))
            self.shape_list.append(shape)


    def animate(self, dt):
        """ Move everything """

        for shape in self.shape_list:
            shape.move()

    def on_draw(self):
        """
        Render the screen.
        """
        start = time.time()

        arcade.start_render()

        for shape in self.shape_list:
            shape.draw()

        elapsed = time.time() - start
        print(elapsed)

window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)
window.setup()

arcade.run()