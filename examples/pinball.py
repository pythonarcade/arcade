"""
Array Backed Grid

Show how to use a two-dimensional list/array to back the display of a
grid on-screen.
"""
import arcade
import pymunk
import math

# Do the math to figure out oiur screen dimensions
SCREEN_WIDTH = 390
SCREEN_HEIGHT = 732
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

    def __init__(self, width, height):
        """
        Set up the application.
        """
        super().__init__(width, height, resizable=True)
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


        vertices = [(2, -2), (-12, 0), (2, 2)]
        #vertices = [(3, 3), (5, 3), (5, 5)]

        mass = 100
        moment = pymunk.moment_for_poly(mass, vertices)

        # right flipper
        left_flipper = Poly(5, 0, 0, vertices)
        self.left_flipper.append(left_flipper.graphic_shape)
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
        # j = pymunk.PinJoint(r_flipper_body, r_flipper_joint_body, (0, 0), (0, 0))
        # s = pymunk.DampedRotarySpring(r_flipper_body, r_flipper_joint_body, 0.15, 20000000, 900000)
        # self.space.add(j, s)


    def on_resize(self, width, height):
        super().on_resize(width, height)
        prefered_height = 55 * width // 29
        if height != prefered_height:
            self.set_size(width, prefered_height)
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
        self.left_flipper.draw()

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
            mass = 0.2
            radius = BALL_RADIUS
            moment = pymunk.moment_for_circle(mass, 0, radius)
            body = pymunk.Body(mass, moment)
            body.position = pymunk.Vec2d(27, 3)

            shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
            shape.friction = 0.05
            shape.elasticity = 0.9

            self.space.add(body, shape)
            self.balls.append(body)

            body.apply_impulse_at_local_point((0, 9))

window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT)

arcade.run()
