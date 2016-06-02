import numpy
import arcade
import timeit
from arcade.color import *


def setup_a(object_list):
    # a = arcade.PhysicsCircle([600, 300], [0, -0.]), .5, 3, 15, RED)
    # object_list.append(a)

    a = arcade.PhysicsAABB([590, 200, 20, 20], [0, 0], .5, 3, ALABAMA_CRIMSON)
    object_list.append(a)

    # a = AABB([550, 200, 20, 20], [0, 0], .5, 3, ALABAMA_CRIMSON)
    # object_list.append(a)

    a = arcade.PhysicsCircle([600, 50], [0, 1], .5, 3, 10, RED)
    object_list.append(a)

    a = arcade.PhysicsCircle([600, 450], [0, -1], .5, 3, 10, RED)
    object_list.append(a)


def setup_b(object_list):

    a = arcade.PhysicsCircle([390, 400], [0.5, -2], .5, 3, 15, RED)
    object_list.append(a)

    for x in range(300, 500, 25):
        for y in range(250, 320, 25):
            a = arcade.PhysicsCircle([x, y], [0, 0], .5, .5, 10, AZURE)
            object_list.append(a)

    a = arcade.PhysicsCircle([400, 150], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)
    a = arcade.PhysicsCircle([370, 120], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)
    a = arcade.PhysicsCircle([430, 120], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)
    a = arcade.PhysicsCircle([400, 90], [0, 0], .5, 2, 20, BANGLADESH_GREEN)
    object_list.append(a)

    a = arcade.PhysicsCircle([0, 350], [2, -3], .5, 3, 10, ALABAMA_CRIMSON)
    object_list.append(a)

    for x in range(50, 200, 20):
        for y in range(150, 200, 20):
            a = arcade.PhysicsAABB([x, y, 15, 15], [0, 0], .5, 1, MELLOW_APRICOT)
            object_list.append(a)


class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        self.hit_sound = arcade.load_sound("sounds/rockHit2.ogg")
        self.object_list = []
        setup_b(self.object_list)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()
        for a in self.object_list:
            a.draw()

    def animate(self, x):
        """ Move everything """

        start_time = timeit.default_timer()

        for a in self.object_list:
            a.position = numpy.add(a.position, a.velocity)

        for i in range(len(self.object_list)):
            for j in range(i+1, len(self.object_list)):
                a = self.object_list[i]
                b = self.object_list[j]
                m = arcade.Manifold(a, b, 0, 0)

                if isinstance(a, arcade.PhysicsCircle) \
                        and isinstance(b, arcade.PhysicsCircle):
                    collided = arcade.circle_vs_circle(m)
                elif isinstance(a, arcade.PhysicsAABB) \
                        and isinstance(b, arcade.PhysicsAABB):
                    collided = arcade.aabb_vs_aabb(m)
                elif isinstance(a, arcade.PhysicsAABB) \
                        and isinstance(b, arcade.PhysicsCircle):
                    collided = aabb_vs_circle(m)
                elif isinstance(a, arcade.PhysicsCircle) \
                        and isinstance(b, arcade.PhysicsAABB):
                    m = arcade.Manifold(b, a, 0, 0)
                    collided = arcade.aabb_vs_circle(m)
                else:
                    collided = False

                if collided:
                    really_collided = arcade.resolve_collision(m)

        elapsed = timeit.default_timer() - start_time
        # print("Time: {}".format(elapsed))

window = MyApplication(800, 500)
window.setup()

arcade.run()
