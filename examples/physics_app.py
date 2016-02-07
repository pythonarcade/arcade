import timeit

import random
import arcade

import math
import numpy

# Adapted from this tutorial:
# http://gamedevelopment.tutsplus.com/tutorials/how-to-create-a-custom-2d-physics-engine-the-basics-and-impulse-resolution--gamedev-6331
# The tutorial has a lot of mistakes in the code, which is kind of annoying.

class Vector:

    def __init__(self, x, y):
        self.data = [x, y]

    def _get_x(self):
        return self.data[0]

    x = property(_get_x)

    def _get_y(self):
        return self.data[1]

    y = property(_get_y)

    def __iter__(self):
        for elem in self._data:
            yield elem

class PhysicsObject:
    def __init__(self, position, velocity, restitution, mass):
        self.velocity = velocity
        self.restitution = restitution
        self.mass = mass
        self.position = position # Vector

    def _get_x(self):
        return self.position.x

    x = property(_get_x)

    def _get_y(self):
        return self.position.y

    y = property(_get_y)

class Rect():
    def __init__(self, rect):
        self.rect = rect

    def _get_x(self):
        return self.rect[0]

    x = property(_get_x)

    def _get_y(self):
        return self.rect[1]

    y = property(_get_y)

    def _get_width(self):
        return self.rect[2]

    width = property(_get_width)

    def _get_height(self):
        return self.rect[3]

    height = property(_get_height)

    def _get_min(self):
        return Vector(self.rect[0], self.rect[1])

    min = property(_get_min)

    def _get_max(self):
        return Vector(self.rect[0] + self.rect[2], self.rect[1] + self.rect[3])

    max = property(_get_max)

class Circle(PhysicsObject):
    def __init__(self, position, velocity, restitution, mass, radius, color):
        super().__init__(position, velocity, restitution, mass)
        self.radius = radius
        self.color = color

    def draw(self):
        arcade.draw_circle_filled(self.position.x, self.position.y, self.radius, self.color)


class AABB(PhysicsObject):
    def __init__(self, rect, velocity, restitution, mass, color):
        super().__init__(Vector(rect[0], rect[1]), velocity, restitution, mass)
        self.color = color
        self.width = rect[2]
        self.height = rect[3]

    def draw(self):
        arcade.draw_rect_filled(self.position.x, self.position.y, self.width, self.height, self.color)

    def _get_min(self):
        return Vector(self.position.x, self.position.y)

    min = property(_get_min)

    def _get_max(self):
        return Vector(self.position.x + self.width, self.position.y + self.height)

    max = property(_get_max)

def AABBvsAABB( a, b ):
    # Exit with no intersection if found separated along an axis
    if(a.max.x < b.min.x or a.min.x > b.max.x):
        return False
    if(a.max.y < b.min.y or a.min.y > b.max.y):
        return False

    # No separating axis found, therefor there is at least one overlapping axis
    return True


def distance(a, b):
    """
    Return the distance between two vectors

    Example:

    >>> a = Vector(0, 0)
    >>> b = Vector(1, 0)
    >>> c = Vector(1, 1)
    >>> print(distance(a, b), distance(a, c))
    1.0 1.4142135623730951
    """
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


class Manifold:
    def __init__(self, a, b, penetration, normal):
        self.a = a
        self.b = b
        self.penetration = penetration
        self.normal = normal

    def __str__(self):
        return "Penetration: {}, Normal: {}".format(self.penetration, self.normal)

def circle_vs_circle(m):
    n = numpy.subtract(m.b.position.data, m.a.position.data)
    r = m.a.radius + m.b.radius
    r *= r

    if r < (m.a.x - m.b.x) ** 2 + (m.a.y - m.b.y) ** 2:
        return False

    d = distance(m.a, m.b)

    if d != 0:
        # Distance is difference between radius and distance
        m.penetration = r - d

        # Utilize our d since we performed sqrt on it already within Length( )
        # Points from A to B, and is a unit vector
        m.normal = n / d
        return True
    else:
        # Choose random (but consistent) values
        m.penetration = a.radius
        m.normal = [1, 0]
        return True




def resolve_collision(m):
    # Calculate relative velocity
    rv = numpy.subtract(m.b.velocity.data, m.a.velocity.data)

    # Calculate relative velocity in terms of the normal direction
    velocity_along_normal = numpy.dot(rv, m.normal)

    # Do not resolve if velocities are separating
    if velocity_along_normal > 0:
        return False

    # Calculate restitution
    e = min(m.a.restitution, m.a.restitution)

    # Calculate impulse scalar
    j = -(1 + e) * velocity_along_normal
    j /= 1 / m.a.mass + 1 / m.b.mass

    # Apply impulse
    impulse = numpy.multiply(j, m.normal)

    m.a.velocity.data = numpy.subtract(m.a.velocity.data, numpy.multiply(1 / m.a.mass, impulse))
    m.b.velocity.data = numpy.add(m.b.velocity.data, numpy.multiply(1 / m.b.mass, impulse))

    return True

def aabb_vs_aabb(m):
    n = numpy.subtract(m.b.position.data, m.a.position.data)

    abox = m.a
    bbox = m.b

    a_extent = (abox.width) / 2
    b_extent = (bbox.width) / 2

    x_overlap = a_extent + b_extent - abs(n[0])

    if x_overlap > 0:
        # Calculate half extents along x axis for each object
        a_extent = (abox.height) / 2
        b_extent = (bbox.height) / 2

        # Calculate overlap on y axis
        y_overlap = a_extent + b_extent - abs(n[1])

        # SAT test on y axis
        if y_overlap > 0:
            # Find out which axis is axis of least penetration
            if x_overlap < y_overlap:

                # Point towards B knowing that n points from A to B
                if n[0] < 0: # n.x
                    m.normal = [-1, 0]
                else:
                    m.normal = [1, 0]
                m.penetration = x_overlap
                return True

            else:
                # Point toward B knowing that n points from A to B
                if n[1] < 0: # n.y
                    m.normal = [0, -1]
                else:
                    m.normal = [0, 1]
                m.penetration = y_overlap
                return True

    return False




class MyApplication(arcade.Window):
    """ Main application class. """

    def setup(self):
        self.hit_sound = arcade.load_sound("rockHit2.ogg")
        self.object_list = []
        a = Circle(Vector(390, 400), Vector(0.5, -2), .5, 3, 15, arcade.color.RED)
        self.object_list.append(a)

        for x in range(300, 500, 25):
            for y in range(250, 320, 25):
                a = Circle(Vector(x, y), Vector(0, 0), .5, .5, 10, arcade.color.AZURE)
                self.object_list.append(a)

        a = Circle(Vector(400, 150), Vector(0, 0), .5, 2, 20, arcade.color.BANGLADESH_GREEN)
        self.object_list.append(a)
        a = Circle(Vector(370, 120), Vector(0, 0), .5, 2, 20, arcade.color.BANGLADESH_GREEN)
        self.object_list.append(a)
        a = Circle(Vector(430, 120), Vector(0, 0), .5, 2, 20, arcade.color.BANGLADESH_GREEN)
        self.object_list.append(a)
        a = Circle(Vector(400, 90), Vector(0, 0), .5, 2, 20, arcade.color.BANGLADESH_GREEN)
        self.object_list.append(a)

        a = AABB([0, 400, 15, 15], Vector(1, -2), .5, 3, arcade.color.ALABAMA_CRIMSON)
        self.object_list.append(a)

        for x in range(50, 200, 20):
            for y in range(150, 200, 20):
                a = AABB([x, y, 15, 15], Vector(0, 0), .5, 1, arcade.color.MELLOW_APRICOT)
                self.object_list.append(a)



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
            a.position.data = numpy.add(a.position.data, a.velocity.data)

        for a in self.object_list:
            for b in self.object_list:
                if a is not b:
                    m = Manifold(a, b, 0, 0)

                    if isinstance(a, Circle) and isinstance(b, Circle):
                        collided = circle_vs_circle(m)
                    elif isinstance(a, AABB) and isinstance(b, AABB):
                        collided = aabb_vs_aabb(m)
                    else:
                        collided = False

                    if collided:
                        really_collided = resolve_collision(m)
                        if really_collided:
                            arcade.play_sound(self.hit_sound)

        elapsed = timeit.default_timer() - start_time
        print("Time: {}".format(elapsed))

window = MyApplication(800, 500)
window.setup()

arcade.run()
