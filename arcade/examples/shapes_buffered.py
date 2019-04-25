"""
Shapes buffered in ShapeElementList

Show how to use a ShapeElementList to display multiple shapes on-screen.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.shapes_buffered
"""
import arcade
import random

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Buffered Shapes"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title)

        self.shape_list = arcade.ShapeElementList()
        self.shape_list.center_x = SCREEN_WIDTH // 2
        self.shape_list.center_y = SCREEN_HEIGHT // 2
        self.shape_list.angle = 0
        point_list = ((0, 50),
                      (10, 10),
                      (50, 0),
                      (10, -10),
                      (0, -50),
                      (-10, -10),
                      (-50, 0),
                      (-10, 10),
                      (0, 50))
        colors = [
            getattr(arcade.color, color)
            for color in dir(arcade.color)
            if not color.startswith("__")
        ]
        for i in range(5):
            x = SCREEN_WIDTH // 2 - random.randrange(SCREEN_WIDTH - 50)
            y = SCREEN_HEIGHT // 2 - random.randrange(SCREEN_HEIGHT - 50)
            color = random.choice(colors)
            points = [(px + x, py + y) for px, py in point_list]

            my_line_strip = arcade.create_line_strip(points, color, 5)
            self.shape_list.append(my_line_strip)

        point_list = ((-50, -50),
                      (0, 40),
                      (50, -50))
        for i in range(5):
            x = SCREEN_WIDTH // 2 - random.randrange(SCREEN_WIDTH - 50)
            y = SCREEN_HEIGHT // 2 - random.randrange(SCREEN_HEIGHT - 50)
            points = [(px + x, py + y) for px, py in point_list]
            triangle_filled = arcade.create_triangles_filled_with_colors(
                points,
                random.sample(colors, 3)
            )
            self.shape_list.append(triangle_filled)

        point_list = ((-50, -70),
                      (-50, 70),
                      (50, 70),
                      (50, -70))
        for i in range(5):
            x = SCREEN_WIDTH // 2 - random.randrange(SCREEN_WIDTH - 50)
            y = SCREEN_HEIGHT // 2 - random.randrange(SCREEN_HEIGHT - 50)
            points = [(px + x, py + y) for px, py in point_list]
            rect_filled = arcade.create_rectangle_filled_with_colors(
                points,
                random.sample(colors, 4)
            )
            self.shape_list.append(rect_filled)

        point_list = ((100, 100),
                      (50, 150),
                      (100, 200),
                      (200, 200),
                      (250, 150),
                      (200, 100))
        poly = arcade.create_polygon(point_list, (255, 10, 10))
        self.shape_list.append(poly)

        ellipse = arcade.create_ellipse(20, 30, 50, 20, (230, 230, 0))
        self.shape_list.append(ellipse)

        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        self.shape_list.draw()

    def update(self, delta_time):
        self.shape_list.angle += 0.2
        self.shape_list.center_x += 0.1
        self.shape_list.center_y += 0.1


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()
