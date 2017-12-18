"""
Use Pymunk physics engine.

For more info on Pymunk see:
http://www.pymunk.org/en/latest/

To install pymunk:
pip install pymunk

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.pymunk_box_stacks

Click and drag with the mouse to move the boxes.
"""

import arcade
import pymunk
import timeit
import math
import os

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800


class PhysicsSprite(arcade.Sprite):
    def __init__(self, pymunk_shape, filename):
        super().__init__(filename, center_x=pymunk_shape.body.position.x, center_y=pymunk_shape.body.position.y)
        self.pymunk_shape = pymunk_shape


# class CircleSprite(PhysicsSprite):
#     def __init__(self, pymunk_shape, filename):
#         super().__init__(pymunk_shape, filename)
#         self.width = pymunk_shape.radius * 2
#         self.height = pymunk_shape.radius * 2


class BoxSprite(PhysicsSprite):
    def __init__(self, pymunk_shape, filename, width, height):
        super().__init__(pymunk_shape, filename)
        self.width = width
        self.height = height


class PymunkSprite(arcade.Sprite):

    def __init__(self,
                 filename,
                 center_x=0,
                 center_y=0,
                 scale=1,
                 mass=1,
                 moment=None,
                 friction=0.2,
                 body_type=pymunk.Body.DYNAMIC):

        super().__init__(filename, scale=scale, center_x=center_x, center_y=center_y)

        width = self.texture.width * scale
        height = self.texture.height * scale

        if moment is None:
            moment = pymunk.moment_for_box(mass, (width, height))

        self.body = pymunk.Body(mass, moment, body_type=body_type)
        self.body.position = pymunk.Vec2d(center_x, center_y)

        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.friction = friction

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        super().__init__(width, height)

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
        self.sprite_list = arcade.SpriteList()
        self.static_lines = []

        # Used for dragging shapes around with the mouse
        self.shape_being_dragged = None
        self.last_mouse_position = 0, 0

        self.draw_time = 0
        self.processing_time = 0

        self.force = (0, 0)

        # Create the floor
        floor_height = 80

        size = 64

        for x in range(-1000, 2000, size):
            y = size / 2
            sprite = PymunkSprite("images/grassMid.png", x, y, scale=0.5, body_type=pymunk.Body.STATIC)
            self.sprite_list.append(sprite)
            self.space.add(sprite.body, sprite.shape)

        for x in range(200, 600, size):
            y = size * 3
            sprite = PymunkSprite("images/grassMid.png", x, y, scale=0.5, body_type=pymunk.Body.STATIC)
            self.sprite_list.append(sprite)
            self.space.add(sprite.body, sprite.shape)


        # Create the stacks of boxes

        for column in range(6):
            for row in range(column):
                x = 600 + column * size
                y = (floor_height + size / 2) + row * size
                sprite = PymunkSprite("images/boxCrate_double.png", x, y, scale=0.5)
                self.sprite_list.append(sprite)
                self.space.add(sprite.body, sprite.shape)



        # Create player
        x = 50
        y = (floor_height + size / 2)
        self.player = PymunkSprite("images/character.png", x, y, scale=0.5, moment=pymunk.inf)
        self.sprite_list.append(self.player)
        self.space.add(self.player.body, self.player.shape)


    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

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

        # Display timings
        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 20, arcade.color.WHITE, 12)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, 20, SCREEN_HEIGHT - 40, arcade.color.WHITE, 12)

        self.draw_time = timeit.default_timer() - draw_start_time

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.last_mouse_position = x, y
            # See if we clicked on anything
            shape_list = self.space.point_query((x, y), 1, pymunk.ShapeFilter())

            # If we did, remember what we clicked on
            if len(shape_list) > 0:
                self.shape_being_dragged = shape_list[0]

        elif button == 4:
            # With right mouse button, shoot a heavy coin fast.
            mass = 60
            radius = 10
            inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
            body = pymunk.Body(mass, inertia)
            body.position = x, y
            body.velocity = 2000, 0
            shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
            shape.friction = 0
            self.space.add(body, shape)

            sprite = CircleSprite(shape, "images/coin_01.png")
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

    def update(self, delta_time):
        start_time = timeit.default_timer()

        self.player.body.apply_force_at_local_point(self.force, (0, 0))

        # Check for balls that fall off the screen
        for sprite in self.sprite_list:
            if sprite.shape.body.position.y < 0:
                # Remove balls from physics space
                self.space.remove(sprite.shape, sprite.shape.body)
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
            sprite.center_x = sprite.shape.body.position.x
            sprite.center_y = sprite.shape.body.position.y
            sprite.angle = math.degrees(sprite.shape.body.angle)


        # Save the time it took to do this.
        self.processing_time = timeit.default_timer() - start_time

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.force = (700, 0)
            self.player.shape.friction = 0
        elif symbol == arcade.key.LEFT:
            self.force = (-700, 0)
            self.player.shape.friction = 0
        elif symbol == arcade.key.UP:
            # find out if player is standing on ground

            grounding = {
                'normal': pymunk.Vec2d.zero(),
                'penetration': pymunk.Vec2d.zero(),
                'impulse': pymunk.Vec2d.zero(),
                'position': pymunk.Vec2d.zero(),
                'body': None
            }

            def f(arbiter):
                n = -arbiter.contact_point_set.normal
                if n.y > grounding['normal'].y:
                    grounding['normal'] = n
                    grounding['penetration'] = -arbiter.contact_point_set.points[0].distance
                    grounding['body'] = arbiter.shapes[1].body
                    grounding['impulse'] = arbiter.total_impulse
                    grounding['position'] = arbiter.contact_point_set.points[0].point_b

            self.player.body.each_arbiter(f)

            well_grounded = False
            if grounding['body'] != None and abs(grounding['normal'].x / grounding['normal'].y) < self.player.shape.friction:
                well_grounded = True
                remaining_jumps = 2

            if well_grounded:
                self.player.body.apply_impulse_at_local_point((0, 600))

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RIGHT:
            self.force = (0, 0)
            self.player.shape.friction = 5
        elif symbol == arcade.key.LEFT:
            self.force = (0, 0)
            self.player.shape.friction = 5


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)

    arcade.run()


if __name__ == "__main__":
    main()
