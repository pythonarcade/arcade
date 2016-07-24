"""
Attempt at a 2D physics engine.

This part needs a lot of work.
"""
# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods
import math
import numpy
import arcade

from numbers import Number
from typing import List
from arcade.arcade_types import Point
from arcade import Sprite

# Adapted from this tutorial:
# http://gamedevelopment.tutsplus.com/tutorials/how-to-create-a-custom-2d-physics-engine-the-basics-and-impulse-resolution--gamedev-6331
# The tutorial has a lot of mistakes in the code, which is kind of annoying.

# Don't use this type of engine on a platformer
# http://higherorderfun.com/blog/2012/05/20/the-guide-to-implementing-2d-platformers/


class PhysicsObject(Sprite):
    """
    Base object to represent something we apply physics on.
    """

    def __init__(self,
                 filename: str,
                 position: [float, float],
                 size: [float, float],
                 velocity: [float, float],
                 restitution: float,
                 mass: float,
                 drag: float):

        super().__init__(filename)
        self.velocity = velocity
        self.restitution = restitution
        self.mass = mass
        self.position = position
        self.width = size[0]
        self.height = size[1]
        self.frozen = True
        self.drag = drag
        self.static = False
        self.freeze_check()

    def freeze_check(self):
        if abs(self.velocity[0]) < 0.1 and abs(self.velocity[1]) < 0.1:
            self.frozen = True
        else:
            self.frozen = False


class PhysicsCircle(PhysicsObject):

    """
    A physics object, which is a circle.
    """
    def __init__(self,
                 filename,
                 position: List[float],
                 radius: float,
                 velocity: List[float],
                 restitution: float,
                 mass: float,
                 drag: float):
        super().__init__(filename, position, [radius * 2, radius * 2], velocity, restitution, mass, drag)
        self.radius = radius


class PhysicsAABB(PhysicsObject):

    """
    Axis-aligned bounding box. In English, a non-rotating rectangle.
    """
    def __init__(self,
                 filename: str,
                 position: List[float],
                 size: [float, float],
                 velocity: List[float],
                 restitution: float,
                 mass: float,
                 drag: float):
        super().__init__(filename, position, size, velocity, restitution, mass, drag)



def distance_a(a: Point, b: Point) -> float:  # pylint: disable=invalid-name
    """ Use square root to calc distance """
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

class Manifold:
    def __init__(self,
                 a: PhysicsObject,
                 b: PhysicsObject,
                 penetration: float,  # pylint: disable=invalid-name
                 normal: float):
        self.a = a
        self.b = b
        self.penetration = penetration
        self.normal = normal


def circle_vs_circle(m: Manifold) -> bool:
    """
    Process two circles that collide.
    """
    n = numpy.subtract(m.b.position, m.a.position)
    r = m.a.radius + m.b.radius
    r *= r

    x_diff = m.a.center_x - m.b.center_x
    y_diff = m.a.center_y - m.b.center_y
    if r < x_diff * x_diff + y_diff * y_diff:
        return False

    d = distance_a(m.a.position, m.b.position)

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


def resolve_collision(m: Manifold) -> bool:
    """
    Process two colliding objects.
    """
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
    if not m.a.static:
        m.a.velocity = numpy.subtract(m.a.velocity,
                                      numpy.multiply(1 / m.a.mass, impulse))
    if not m.b.static:
        m.b.velocity = numpy.add(m.b.velocity,
                                 numpy.multiply(1 / m.b.mass, impulse))
    # print("After:  ", m.a.velocity, m.b.velocity)
    # print("  Normal:  ", m.normal)

    return True


def aabb_vs_aabb(m: Manifold) -> bool:
    """
    Process two AABB objects that collide
    """
    # Fast check
    if m.a.position[0] + m.a.width / 2 < m.b.position[0] - m.b.width / 2:
        return False
    if m.a.position[0] - m.a.width / 2 > m.b.position[0] + m.b.width / 2:
        return False
    if m.a.position[1] + m.a.height / 2 < m.b.position[1] - m.b.height / 2:
        return False
    if m.a.position[1] - m.a.height / 2 > m.b.position[1] + m.b.height / 2:
        return False

    n = numpy.subtract(m.b.position, m.a.position)

    abox = m.a
    bbox = m.b

    a_extent = abox.width / 2
    b_extent = bbox.width / 2

    x_overlap = a_extent + b_extent - abs(n[0])

    if x_overlap > 0:
        # Calculate half extents along x axis for each object
        a_extent = abox.height / 2
        b_extent = bbox.height / 2

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


def clamp(a: float, min_value: float, max_value: float) -> float:
    """
    Clamp a between two values.
    """
    return max(min(a, max_value), min_value)


def magnitude(v: List[float]) -> float:
    """
    Get the magnitude of a vector.
    """
    return math.sqrt(sum(v[i] * v[i] for i in range(len(v))))


def add(u: List[float], v: List[float]) -> List[float]:
    return [u[i] + v[i] for i in range(len(u))]


def sub(u: List[float], v: List[float]) ->List[float]:
    return [u[i] - v[i] for i in range(len(u))]


def neg(u: List[float]) -> List[Number]:
    return [-u[i] for i in range(len(u))]


def dot(u: List[float], v: List[float]) -> Number:
    return sum(u[i] * v[i] for i in range(len(u)))


def normalize(v: List[float]) -> List[float]:
    vmag = magnitude(v)
    return [v[i] / vmag for i in range(len(v))]


def aabb_vs_circle(m: Manifold) -> bool:

    if m.a.center_x + m.a.width < m.b.center_x - m.b.width:
        return False
    if m.a.center_x - m.a.width > m.b.center_x + m.b.width:
        return False
    if m.a.center_y + m.a.height < m.b.center_y - m.b.height:
        return False
    if m.a.center_y - m.a.height > m.b.center_y + m.b.height:
        return False

    a_center = m.a.position
    b_center = m.b.position

    closest_x = clamp(b_center[0],
                      m.a.position[0] - m.a.width / 2,
                      m.a.position[0] + m.a.width / 2)
    closest_y = clamp(b_center[1],
                      m.a.position[1] - m.a.height / 2,
                      m.a.position[1] + m.a.height / 2)

    # Calculate the distance between the circle's center and this closest point
    distance_x = b_center[0] - closest_x
    distance_y = b_center[1] - closest_y

    # If the distance is less than the circle's radius, an intersection occurs
    distance_squared = (distance_x * distance_x) + (distance_y * distance_y)
    collision = distance_squared < (m.b.radius * m.b.radius)
    if not collision:
        return False

    # print("Bang")
    d = distance_a(a_center, b_center)
    # print(d)

    if d == 0:
        # Choose random (but consistent) values
        m.penetration = m.b.radius
        m.normal = [1, 0]
        return True
    else:
        m.normal = neg(normalize(sub(a_center, b_center)))
        return collision


def process_2d_physics_movement(object_list, gravity=0):
    for a in object_list:
        if not a.frozen:
            if not a.static:
                a.velocity[1] -= gravity
            a.center_x += a.velocity[0]
            a.center_y += a.velocity[1]
            if not a.static:
                if a.velocity[0] > 0:
                    a.velocity[0] -= a.drag * a.velocity[0] * a.velocity[0]
                elif a.velocity[0] < 0:
                    a.velocity[0] += a.drag * a.velocity[0] * a.velocity[0]
                if a.velocity[1] > 0:
                    a.velocity[1] -= a.drag * a.velocity[1] * a.velocity[1]
                elif a.velocity[1] < 0:
                    a.velocity[1] += a.drag * a.velocity[1] * a.velocity[1]

        if not a.static:
            a.velocity[0] += a.force[0]
            a.velocity[1] += a.force[1]

        a.freeze_check()


def process_2d_physics_collisions(object_list):
    count = 0
    for i in range(len(object_list)):
        for j in range(i + 1, len(object_list)):
            a = object_list[i]
            b = object_list[j]
            if not a.frozen or not b.frozen:
                count += 1
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
                    if really_collided:
                        b.frozen = False
    # print(count)
