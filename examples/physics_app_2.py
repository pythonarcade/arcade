import numpy
import arcade
import timeit
from arcade.color import *


MOVEMENT_SPEED = 0.08
DRAG = 0.04

def create_boxes(object_list, start_x, start_y, width, height):
    spacing = 20
    for x in range(start_x, start_x + width * spacing, spacing):
        for y in range(start_y, start_y + height * spacing, spacing):
            a = arcade.PhysicsAABB("images/boxCrate_double.png", [x, y], 15, 15, [0, 0], .5, 1)
            object_list.append(a)

def create_circles(object_list, start_x, start_y, width, height):
    spacing = 20
    for x in range(start_x, start_x + width * spacing, spacing):
        for y in range(start_y, start_y + height * spacing, spacing):
            a = arcade.PhysicsCircle("images/coin_01.png", [x, y], [0, 0], .5, 1, 9)
            object_list.append(a)

class MyApplication(arcade.Window):
    """ Main application class. """

    def setup_b(self, object_list):

        self.player = arcade.PhysicsAABB("images/character.png", [390, 400], 79 / 2, 125 / 2, [0, 0], .5, 3)
        object_list.append(self.player)

        create_circles(object_list, 300, 300, 5, 2)

        a = arcade.PhysicsCircle("images/meteorGrey_med1.png", [400, 150], [0, 0], .5, 2, 20)
        object_list.append(a)
        a = arcade.PhysicsCircle("images/meteorGrey_med2.png", [370, 120], [0, 0], .5, 2, 20)
        object_list.append(a)
        a = arcade.PhysicsCircle("images/meteorGrey_med1.png", [430, 120], [0, 0], .5, 2, 20)
        object_list.append(a)
        a = arcade.PhysicsCircle("images/meteorGrey_med1.png", [400, 90], [0, 0], .5, 2, 20)
        object_list.append(a)

        create_boxes(object_list, 150, 250, 2, 20)
        create_boxes(object_list, 450, 250, 2, 20)
        create_boxes(object_list, 190, 250, 13, 2)
        create_boxes(object_list, 190, 450, 13, 2)
        create_boxes(object_list, 190, 610, 13, 2)

    def setup(self):
        self.hit_sound = arcade.load_sound("sounds/rockHit2.ogg")
        self.object_list = arcade.SpriteList()
        self.setup_b(self.object_list)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()
        self.object_list.draw()

    def animate(self, x):
        """ Move everything """

        start_time = timeit.default_timer()

        arcade.process_2d_physics_movement(self.object_list, DRAG)
        arcade.process_2d_physics_collisions(self.object_list, DRAG)

        elapsed = timeit.default_timer() - start_time
        print("Time: {}".format(elapsed))


    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.UP:
            self.player.force[1] = MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player.force[1] = -MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player.force[0] = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player.force[0] = MOVEMENT_SPEED


    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player.force[1] = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.force[0] = 0

window = MyApplication(1024, 800)
window.setup()

arcade.run()
