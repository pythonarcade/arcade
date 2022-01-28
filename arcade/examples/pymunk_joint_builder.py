"""
Pymunk 2

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.pymunk_joint_builder
"""
import arcade
import pymunk
import timeit
import math
import os

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Pymunk 2 Example"

"""
Key bindings:

1 - Drag mode
2 - Make box mode
3 - Make PinJoint mode
4 - Make DampedSpring mode

S - No gravity or friction
L - Layout, no gravity, lots of friction
G - Gravity, little bit of friction

Right-click, fire coin

"""


class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape


class CircleSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(pymunk_shape, filename)
        self.width = pymunk_shape.radius * 2
        self.height = pymunk_shape.radius * 2


class BoxSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename, width, height):
        super().__init__(pymunk_shape, filename)
        self.width = width
        self.height = height


class MyApplication(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        # -- Pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        # Lists of sprites or lines
        self.sprite_list: arcade.SpriteList[PhysicsSprite] = arcade.SpriteList()
        self.static_lines = []

        # Used for dragging shapes around with the mouse
        self.shape_being_dragged = None
        self.last_mouse_position = 0, 0

        self.processing_time_text = None
        self.draw_time_text = None
        self.draw_mode_text = None
        self.shape_1 = None
        self.shape_2 = None
        self.draw_time = 0
        self.processing_time = 0
        self.joints = []

        self.physics = "Normal"
        self.mode = "Make Box"

        # Create the floor
        self.floor_height = 80
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shape = pymunk.Segment(body, [0, self.floor_height], [SCREEN_WIDTH, self.floor_height], 0.0)
        shape.friction = 10
        self.space.add(shape, body)
        self.static_lines.append(shape)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        self.clear()

        # Start timing how long this takes
        draw_start_time = timeit.default_timer()

        # Draw all the sprites
        self.sprite_list.draw()

        # Draw the lines that aren't sprites
        for line in self.static_lines:
            body = line.body

            pv1 = body.position + line.a.rotated(body.angle)
            pv2 = body.position + line.b.rotated(body.angle)
            arcade.draw_line(pv1.x, pv1.y, pv2.x, pv2.y, arcade.color.WHITE, 2)

        for joint in self.joints:
            color = arcade.color.WHITE
            if isinstance(joint, pymunk.DampedSpring):
                color = arcade.color.DARK_GREEN
            arcade.draw_line(joint.a.position.x,
                             joint.a.position.y,
                             joint.b.position.x,
                             joint.b.position.y,
                             color, 3)

        # arcade.draw_text(output, 10, 20, arcade.color.WHITE, 14)
        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE)

        self.draw_time = timeit.default_timer() - draw_start_time

        output = f"Mode: {self.mode}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 60, arcade.color.WHITE)

        output = f"Physics: {self.physics}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 80, arcade.color.WHITE)

    def make_box(self, x, y):
        size = 45
        mass = 12.0
        moment = pymunk.moment_for_box(mass, (size, size))
        body = pymunk.Body(mass, moment)
        body.position = pymunk.Vec2d(x, y)
        shape = pymunk.Poly.create_box(body, (size, size))
        shape.friction = 0.3
        self.space.add(body, shape)

        sprite = BoxSprite(shape, ":resources:images/tiles/boxCrate_double.png", width=size, height=size)
        self.sprite_list.append(sprite)

    def make_circle(self, x, y):
        size = 20
        mass = 12.0
        moment = pymunk.moment_for_circle(mass, 0, size, (0, 0))
        body = pymunk.Body(mass, moment)
        body.position = pymunk.Vec2d(x, y)
        shape = pymunk.Circle(body, size, pymunk.Vec2d(0, 0))
        shape.friction = 0.3
        self.space.add(body, shape)

        sprite = CircleSprite(shape, ":resources:images/items/coinGold.png")
        self.sprite_list.append(sprite)

    def make_pin_joint(self, x, y):
        shape_selected = self.get_shape(x, y)
        if shape_selected is None:
            return

        if self.shape_1 is None:
            print("Shape 1 Selected")
            self.shape_1 = shape_selected
        elif self.shape_2 is None:
            print("Shape 2 Selected")
            self.shape_2 = shape_selected
            joint = pymunk.PinJoint(self.shape_1.shape.body, self.shape_2.shape.body)
            self.space.add(joint)
            self.joints.append(joint)
            self.shape_1 = None
            self.shape_2 = None
            print("Joint Made")

    def make_damped_spring(self, x, y):
        shape_selected = self.get_shape(x, y)
        if shape_selected is None:
            return

        if self.shape_1 is None:
            print("Shape 1 Selected")
            self.shape_1 = shape_selected
        elif self.shape_2 is None:
            print("Shape 2 Selected")
            self.shape_2 = shape_selected
            joint = pymunk.DampedSpring(self.shape_1.shape.body, self.shape_2.shape.body, (0, 0), (0, 0), 45, 300, 30)
            self.space.add(joint)
            self.joints.append(joint)
            self.shape_1 = None
            self.shape_2 = None
            print("Joint Made")

    def get_shape(self, x, y):
        # See if we clicked on anything
        shape_list = self.space.point_query((x, y), 1, pymunk.ShapeFilter())

        # If we did, remember what we clicked on
        if len(shape_list) > 0:
            shape = shape_list[0]
        else:
            shape = None

        return shape

    def on_mouse_press(self, x, y, button, modifiers):

        if button == 1 and self.mode == "Drag":
            self.last_mouse_position = x, y
            self.shape_being_dragged = self.get_shape(x, y)

        elif button == 1 and self.mode == "Make Box":
            self.make_box(x, y)

        elif button == 1 and self.mode == "Make Circle":
            self.make_circle(x, y)

        elif button == 1 and self.mode == "Make PinJoint":
            self.make_pin_joint(x, y)

        elif button == 1 and self.mode == "Make DampedSpring":
            self.make_damped_spring(x, y)

        elif button == 4:
            # With right mouse button, shoot a heavy coin fast.
            mass = 60
            radius = 10
            inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
            body = pymunk.Body(mass, inertia)
            body.position = x, y
            body.velocity = 2000, 0
            shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
            shape.friction = 0.3
            self.space.add(body, shape)

            sprite = CircleSprite(shape, ":resources:images/items/coinGold.png")
            self.sprite_list.append(sprite)

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1:
            # Release the item we are holding (if any)
            self.shape_being_dragged = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.shape_being_dragged is not None:
            # If we are holding an object, move it with the mouse
            self.last_mouse_position = x, y
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = dx * 20, dy * 20

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.KEY_1:
            self.mode = "Drag"
        elif symbol == arcade.key.KEY_2:
            self.mode = "Make Box"
        elif symbol == arcade.key.KEY_3:
            self.mode = "Make Circle"

        elif symbol == arcade.key.KEY_4:
            self.mode = "Make PinJoint"
        elif symbol == arcade.key.KEY_5:
            self.mode = "Make DampedSpring"

        elif symbol == arcade.key.S:
            self.space.gravity = (0.0, 0.0)
            self.space.damping = 1
            self.physics = "Outer Space"
        elif symbol == arcade.key.L:
            self.space.gravity = (0.0, 0.0)
            self.space.damping = 0
            self.physics = "Layout"
        elif symbol == arcade.key.G:
            self.space.damping = 0.95
            self.space.gravity = (0.0, -900.0)
            self.physics = "Normal"

    def on_update(self, delta_time):
        start_time = timeit.default_timer()

        # Check for balls that fall off the screen
        for sprite in self.sprite_list:
            if sprite.pymunk_shape.body.position.y < 0:
                # Remove balls from physics space
                self.space.remove(sprite.pymunk_shape, sprite.pymunk_shape.body)
                # Remove balls from physics list
                sprite.kill()

        # Update physics
        self.space.step(1 / 80.0)

        # If we are dragging an object, make sure it stays with the mouse. Otherwise
        # gravity will drag it down.
        if self.shape_being_dragged is not None:
            self.shape_being_dragged.shape.body.position = self.last_mouse_position
            self.shape_being_dragged.shape.body.velocity = 0, 0

        # Move sprites to where physics objects are
        for sprite in self.sprite_list:
            sprite.center_x = sprite.pymunk_shape.body.position.x
            sprite.center_y = sprite.pymunk_shape.body.position.y
            sprite.angle = math.degrees(sprite.pymunk_shape.body.angle)

        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time


window = MyApplication(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

arcade.run()
