"""
Pinball

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.pinball
"""
import arcade
import pymunk
import math
import random
import os

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 390
SCREEN_HEIGHT = 732
SCREEN_TITLE = "Pinball"
BALL_RADIUS = 0.53

class Shape:
    pass

class Segment(Shape):
    def __init__(self, x1, y1, x2, y2):
        self.point_list = ((x1, y2), (x2, y2))
        self.graphic_shape = arcade.create_line(x1, y1, x2, y2, arcade.color.WHITE)
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.pymunk_shape = pymunk.Segment(self.body, [x1, y1], [x2, y2], 0.0)
        self.pymunk_shape.friction = 1
        self.pymunk_shape.elasticity = 0.9

class Box(Shape):
    def __init__(self, width, height, x, y, angle = 0):
        self.point_list = ((-width / 2, -height / 2),
                           (+width / 2, -height / 2),
                           (+width / 2, +height / 2),
                           (-width / 2, +height / 2))
        self.graphic_shape = arcade.create_rectangle_filled(x, y, width, height, arcade.color.WHITE, tilt_angle=angle)
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.body.position = pymunk.Vec2d(x, y)
        self.body.angle = math.radians(angle)

        self.pymunk_shape = pymunk.Poly.create_box(self.body, (width, height))

        self.pymunk_shape.friction = 1
        self.pymunk_shape.elasticity = 0.9

class Poly(Shape):
    def __init__(self, x, y, angle, vertices):
        self.graphic_shape = arcade.create_polygon(vertices, arcade.color.WHITE, 1)
        self.graphic_shape.center_x = x
        self.graphic_shape.center_y = y
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.body.position = pymunk.Vec2d(x, y)
        self.body.angle = math.radians(angle)

        self.pymunk_shape = pymunk.Poly(self.body,vertices)

        self.pymunk_shape.friction = 1
        self.pymunk_shape.elasticity = 0.9

class MyApplication(arcade.Window):
    """
    Main application class.
    """

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title, resizable=True)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.set_location(20, 20)
        arcade.set_background_color(arcade.color.BLACK)

        self.board_shape_element_list = arcade.ShapeElementList()
        self.left_flipper = arcade.ShapeElementList()
        self.balls = []

        # -- Pymunk --

        self.space = pymunk.Space()
        self.space.gravity = (0.0, -15.0)

        my_file = open("pinball_layout.txt")

        line_number = 0
        for line in my_file:
            line_number += 1
            try:
                parameters = line.split()
                if parameters[0] == "Box":
                    x = float(parameters[1])
                    y = float(parameters[2])
                    angle = float(parameters[3])
                    width = float(parameters[4])
                    height = float(parameters[5])
                    my_shape = Box(width, height, x, y, angle=angle)
                    self.board_shape_element_list.append(my_shape.graphic_shape)
                    self.space.add(my_shape.pymunk_shape)

                if parameters[0] == "Poly":
                    x = float(parameters[1])
                    y = float(parameters[2])
                    angle = float(parameters[3])

                    count = (len(parameters) - 3) // 2
                    vertices = []

                    for i in range(count):
                        x = float(parameters[i * 2 + 1])
                        y = float(parameters[i * 2 + 2])
                        vertices.append((x, y))

                    my_shape = Poly(0, 0, 0, vertices)
                    self.board_shape_element_list.append(my_shape.graphic_shape)
                    self.space.add(my_shape.pymunk_shape)
                    print("Poly")

            except Exception as e:
                print(f"Error parsing line {line_number}: '{line}'")
                print(e)
                return


        vertices = [(-0.5, -0.5), (3, 0), (-0.5, 0.5)]

        mass = 10
        moment = pymunk.moment_for_poly(mass, vertices)

        # right flipper
        self.right_flipper_poly = arcade.create_polygon(vertices, arcade.color.WHITE, 1)
        self.right_flipper_shape_list = arcade.ShapeElementList()
        self.right_flipper_shape_list.append(self.right_flipper_poly)
        self.right_flipper_shape_list.center_x = 2
        self.right_flipper_shape_list.center_y = 2

        self.right_flipper_body = pymunk.Body(mass, moment)
        self.right_flipper_body.position = pymunk.Vec2d(self.right_flipper_shape_list.center_x, self.right_flipper_shape_list.center_y)
        self.right_flipper_pymunk_shape = pymunk.Poly(self.right_flipper_body, vertices)
        self.space.add(self.right_flipper_body, self.right_flipper_pymunk_shape)

        r_flipper_joint_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        r_flipper_joint_body.position = pymunk.Vec2d(self.right_flipper_shape_list.center_x, self.right_flipper_shape_list.center_y)

        j = pymunk.PinJoint(self.right_flipper_body, r_flipper_joint_body, (0, 0), (5,5))
        #s = pymunk.DampedRotarySpring(self.right_flipper.body, r_flipper_joint_body, 0, 500, 110)
        #self.space.add(j, s)
        self.space.add(j, r_flipper_joint_body)

        print("X1", self.right_flipper_shape_list.center_x, self.right_flipper_shape_list.center_y)
        print("X2", self.right_flipper_body.position.x, self.right_flipper_body.position.y)
        """
        vertices = [(0.5, -0.5), (-3, 0), (0.5, 0.5)]

        mass = 100
        moment = pymunk.moment_for_poly(mass, vertices)

        # right flipper
        self.left_flipper = Poly(0, 0, 0, vertices)
        self.left_flipper_shape = arcade.ShapeElementList()
        self.left_flipper_shape.append(self.left_flipper.graphic_shape)
        self.left_flipper_shape.center_x = 12
        self.left_flipper_shape.center_y = 1
        """
        #self.left_flipper.append(left_flipper.graphic_shape)
        #
        # r_flipper_body = pymunk.Body(mass, moment)
        # r_flipper_body.position = 450, 100
        # graphic_shape.
        #
        # r_flipper_shape = pymunk.Poly(r_flipper_body, vertices)
        # self.space.add(r_flipper_body, r_flipper_shape)
        # r_flipper_joint_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        # r_flipper_joint_body.position = r_flipper_body.position
        #
        # self.space.add(j, s)


    def on_resize(self, width, height):
        super().on_resize(width, height)
        preferred_height = 55 * width // 29
        if height != preferred_height:
            self.set_size(width, preferred_height)
        else:
            self.set_viewport(0, 29, 0, 55)
        print(f"Resize {width} {height}")

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        self.board_shape_element_list.draw()
        #self.left_flipper_shape.draw()

        self.right_flipper_shape_list.center_x = self.right_flipper_body.position.x
        self.right_flipper_shape_list.center_y = self.right_flipper_body.position.y
        self.right_flipper_shape_list.angle = self.right_flipper_body.angle
        print(self.right_flipper_shape_list.center_x, self.right_flipper_shape_list.center_y, self.right_flipper_shape_list.angle)
        #self.right_flipper_shape.center_y += 1
        self.right_flipper_shape_list.draw()

        for ball in self.balls:
            arcade.draw_circle_filled(ball.position.x, ball.position.y, BALL_RADIUS, arcade.color.WHITE)

    def update(self, delta_time):
        # Check for balls that fall off the screen
        # for sprite in self.sprite_list:
        #     if sprite.pymunk_shape.body.position.y < 0:
        #         # Remove balls from physics space
        #         self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
        #         # Remove balls from physics list
        #         sprite.kill()

        # Update physics
        self.space.step(delta_time)
        for ball in self.balls:
            if ball.position.y < -1:
                self.balls.remove(ball)
                self.space.remove(ball)
                print("Bye")

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.SPACE:
            mass = 1
            radius = BALL_RADIUS
            for x_position in range(0, 28, 1):
                moment = pymunk.moment_for_circle(mass, 0, radius)
                body = pymunk.Body(mass, moment)
                # x_position = random.randrange(2, 27)
                body.position = pymunk.Vec2d(x_position, 3)

                shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
                shape.friction = 0.15
                shape.elasticity = 0.9

                self.space.add(body, shape)
                self.balls.append(body)

                body.apply_impulse_at_local_point((0, 6))
        elif symbol == arcade.key.F:
            self.right_flipper.body.apply_impulse_at_local_point((0, 100), (40, 0))


def main():
    window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == "__main__":
    main()

