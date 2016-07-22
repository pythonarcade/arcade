import numpy
import arcade
import timeit
from arcade.color import *


def setup_a(object_list):
    # a = arcade.PhysicsCircle("images/coin_01.png", [600, 300], [0, -0.]), .5, 3, 15, RED)
    # object_list.append(a)

    a = arcade.PhysicsAABB("images/boxCrate_double.png", [590, 200, 20, 20], [0, 0], .5, 3, ALABAMA_CRIMSON)
    object_list.append(a)

    # a = AABB([550, 200, 20, 20], [0, 0], .5, 3, ALABAMA_CRIMSON)
    # object_list.append(a)

    a = arcade.PhysicsCircle("images/coin_01.png", [600, 50], [0, 1], .5, 3, 10, RED)
    object_list.append(a)

    a = arcade.PhysicsCircle("images/coin_01.png", [600, 450], [0, -1], .5, 3, 10, RED)
    object_list.append(a)


def setup_b(object_list):

    a = arcade.PhysicsCircle("images/coin_01.png", [390, 400], [0.5, -2], .5, 3, 15, RED)
    object_list.append(a)

    for x in range(300, 500, 25):
        for y in range(250, 320, 25):
            a = arcade.PhysicsCircle("images/coin_01.png", [x, y], [0, 0], .5, .5, 10, AZURE)
            object_list.append(a)

    a = arcade.PhysicsCircle("images/coin_01.png", [400, 150], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)
    a = arcade.PhysicsCircle("images/coin_01.png", [370, 120], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)
    a = arcade.PhysicsCircle("images/coin_01.png", [430, 120], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)
    a = arcade.PhysicsCircle("images/coin_01.png", [400, 90], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)

    a = arcade.PhysicsCircle("images/coin_01.png", [0, 350], [2, -3], .5, 3, 10, ALABAMA_CRIMSON)
    object_list.append(a)

    for x in range(50, 200, 20):
        for y in range(150, 200, 20):
            a = arcade.PhysicsAABB("images/boxCrate_double.png", [x, y, 15, 15], [0, 0], .5, 1, MELLOW_APRICOT)
            object_list.append(a)


class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        self.hit_sound = arcade.load_sound("sounds/rockHit2.ogg")
        self.object_list = arcade.SpriteList()
        setup_b(self.object_list)

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

        arcade.process_2d_physics(self.object_list)

        elapsed = timeit.default_timer() - start_time
        # print("Time: {}".format(elapsed))

window = MyApplication(800, 500)
window.setup()

arcade.run()
