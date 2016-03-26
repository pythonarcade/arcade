import random
import arcade

import math
import numpy

# Adapted from this tutorial:
# http://gamedevelopment.tutsplus.com/tutorials/how-to-create-a-custom-2d-physics-engine-the-basics-and-impulse-resolution--gamedev-6331
# The tutorial has a lot of mistakes in the code, which is kind of annoying.

# Don't use this type of engine on a platformer
# http://higherorderfun.com/blog/2012/05/20/the-guide-to-implementing-2d-platformers/


class PhysicsObject:
    def __init__(self, position, velocity, restitution, mass):
        self.velocity = velocity
        self.restitution = restitution
        self.mass = mass
        self.position = position  # Vector

    def _get_x(self):
        return self.position[0]

    x = property(_get_x)

    def _get_y(self):
        return self.position[1]

    y = property(_get_y)


class Circle(PhysicsObject):
    def __init__(self, position, velocity, restitution, mass, radius, color):
        super().__init__(position, velocity, restitution, mass)
        self.radius = radius
        self.color = color

    def draw(self):
        arcade.draw_circle_filled(self.position[0], self.position[1],
                                  self.radius, self.color)


class AABB(PhysicsObject):
    def __init__(self, rect, velocity, restitution, mass, color):
        super().__init__([rect[0], rect[1]], velocity, restitution, mass)
        self.color = color
        self.width = rect[2]
        self.height = rect[3]

    def draw(self):
        arcade.draw_rect_filled(self.position[0], self.position[1], self.width,
                                self.height, self.color)

    def _get_min(self):
        return Vector(self.position.x, self.position.y)

    min = property(_get_min)

    def _get_max(self):
        return Vector(self.position.x + self.width,
                      self.position.y + self.height)

    max = property(_get_max)


def distanceA(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


class Manifold:
    def __init__(self, a, b, penetration, normal):
        self.a = a
        self.b = b
        self.penetration = penetration
        self.normal = normal

    def __str__(self):
        return "Penetration: {}, Normal: {}".format(self.penetration,
                                                    self.normal)


def circle_vs_circle(m):
    n = numpy.subtract(m.b.position.data, m.a.position.data)
    r = m.a.radius + m.b.radius
    r *= r

    if r < (m.a.x - m.b.x) ** 2 + (m.a.y - m.b.y) ** 2:
        return False

    d = distanceA(m.a.position.data, m.b.position.data)

    if d != 0:
        # Distance is difference between radius and distance
        m.penetration = r - d

        # Utilize our d since we performed sqrt on it already within Length( )
        # Points from A to B, and is a unit vector
        m.normal = n / d
        return True
    else:
        # Choose random (but consistent) values
        m.penetration = m.a.radius
        m.normal = [1, 0]
        return True


def resolve_collision(m):
    # Calculate relative velocity
    rv = numpy.subtract(m.b.velocity, m.a.velocity)

    # Calculate relative velocity in terms of the normal direction
    velocity_along_normal = numpy.dot(rv, m.normal)

    # Do not resolve if velocities are separating
    if velocity_along_normal > 0:
        # print("Separating:", velocity_along_normal)
        # print("  Normal:  ", m.normal)
        # print("  Vel:     ", m.b.velocity, m.a.velocity)
        return False

    # Calculate restitution
    e = min(m.a.restitution, m.a.restitution)

    # Calculate impulse scalar
    j = -(1 + e) * velocity_along_normal
    j /= 1 / m.a.mass + 1 / m.b.mass

    # Apply impulse
    impulse = numpy.multiply(j, m.normal)

    # print("Before: ", m.a.velocity, m.b.velocity)
    m.a.velocity = numpy.subtract(m.a.velocity,
                                  numpy.multiply(1 / m.a.mass, impulse))
    m.b.velocity = numpy.add(m.b.velocity,
                             numpy.multiply(1 / m.b.mass, impulse))
    # print("After:  ", m.a.velocity, m.b.velocity)
    # print("  Normal:  ", m.normal)

    return True


def aabb_vs_aabb(m):
    n = numpy.subtract(m.b.position, m.a.position)

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
                if n[0] < 0:  # n.x
                    m.normal = [-1, 0]
                else:
                    m.normal = [1, 0]
                m.penetration = x_overlap
                return True

            else:
                # Point toward B knowing that n points from A to B
                if n[1] < 0:  # n.y
                    m.normal = [0, -1]
                else:
                    m.normal = [0, 1]
                m.penetration = y_overlap
                return True

    return False


def clamp(a, min_value, max_value):
    return max(min(a, max_value), min_value)


def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))


def add(u, v):
    return [u[i]+v[i] for i in range(len(u))]


def sub(u, v):
    return [u[i]-v[i] for i in range(len(u))]


def neg(u):
    return [-u[i] for i in range(len(u))]


def dot(u, v):
    return sum(u[i]*v[i] for i in range(len(u)))


def normalize(v):
    vmag = magnitude(v)
    return [v[i]/vmag for i in range(len(v))]


def aabb_vs_circle(m):
    x_extent = m.a.width / 2
    y_extent = m.a.height / 2

    a_center = [m.a.x + x_extent, m.a.y - y_extent]
    b_center = m.b.position

    closestX = clamp(b_center[0],
                     m.a.position[0], m.a.position[0] + m.a.width)
    closestY = clamp(b_center[1],
                     m.a.position[1] - m.a.height, m.a.position[1])

    # Calculate the distance between the circle's center and this closest point
    distanceX = b_center[0] - closestX
    distanceY = b_center[1] - closestY

    # If the distance is less than the circle's radius, an intersection occurs
    distanceSquared = (distanceX * distanceX) + (distanceY * distanceY)
    collision = distanceSquared < (m.b.radius * m.b.radius)
    if not collision:
        return False

    # print("Bang")
    d = distanceA(a_center, b_center)
    # print(d)

    if d == 0:
        # Choose random (but consistent) values
        m.penetration = m.b.radius
        m.normal = [1, 0]
        return True
    else:
        m.normal = neg(normalize(sub(a_center, b_center)))

        return collision
