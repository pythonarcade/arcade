"""
This simple animation example shows how to use classes to animate
multiple objects on the screen at the same time.

Note: Sprites draw much faster than drawing primitives

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shapes
"""

import arcade
import random

# Set up the constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Shapes!"

NUMBER_OF_SHAPES = 200


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

    def move(self):
        self.x += self.delta_x
        self.y += self.delta_y
        self.angle += self.delta_angle
        if self.x < 0 and self.delta_x < 0:
            self.delta_x *= -1
        if self.y < 0 and self.delta_y < 0:
            self.delta_y *= -1
        if self.x > WINDOW_WIDTH and self.delta_x > 0:
            self.delta_x *= -1
        if self.y > WINDOW_HEIGHT and self.delta_y > 0:
            self.delta_y *= -1


class Ellipse(Shape):

    def draw(self):
        arcade.draw_ellipse_filled(self.x, self.y, self.width, self.height,
                                   self.color, self.angle)


class Rectangle(Shape):

    def draw(self):
        arcade.draw_rect_filled(arcade.rect.XYWH(self.x, self.y, self.width, self.height),
                                self.color, self.angle)


class Line(Shape):

    def draw(self):
        arcade.draw_line(self.x, self.y,
                         self.x + self.width, self.y + self.height,
                         self.color, 2)


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        # Call the parent __init__
        super().__init__()

        # Create a shape list
        self.shape_list = []

        for i in range(NUMBER_OF_SHAPES):

            # Random spot
            x = random.randrange(0, WINDOW_WIDTH)
            y = random.randrange(0, WINDOW_HEIGHT)

            # Random size
            width = random.randrange(15, 40)
            height = random.randrange(15, 40)

            # Random angle
            angle = random.randrange(0, 360)

            # Random movement
            d_x = random.randrange(-3, 4)
            d_y = random.randrange(-3, 4)
            d_angle = random.randrange(-3, 4)

            # Random color
            red = random.randrange(256)
            green = random.randrange(256)
            blue = random.randrange(256)
            alpha = random.randrange(256)

            # Random line, ellipse, or rect
            shape_type = random.randrange(3)

            if shape_type == 0:
                shape = Rectangle(x, y, width, height, angle, d_x, d_y,
                                  d_angle, (red, green, blue, alpha))
            elif shape_type == 1:
                shape = Ellipse(x, y, width, height, angle, d_x, d_y,
                                d_angle, (red, green, blue, alpha))
            else:
                shape = Line(x, y, width, height, angle, d_x, d_y,
                             d_angle, (red, green, blue, alpha))

            # Add this new shape to the list
            self.shape_list.append(shape)

    def on_update(self, dt):
        """ Move everything """
        for shape in self.shape_list:
            shape.move()

    def on_draw(self):
        """ Render the screen. """
        self.clear()

        # Draw the shapes
        for shape in self.shape_list:
            shape.draw()


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
