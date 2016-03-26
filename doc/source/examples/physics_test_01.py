import math

# http://gamedevelopment.tutsplus.com/tutorials/how-to-create-a-custom-2d-physics-engine-the-basics-and-impulse-resolution--gamedev-6331


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Circle:
    def __init__(self, position, radius):
        self.position = position
        self.radius = radius

    def _get_x(self):
        """ The lowest y coordinate. """
        return self.position.x

    x = property(_get_x)

    def _get_y(self):
        """ The lowest y coordinate. """
        return self.position.y

    y = property(_get_y)


class AABB:
    def __init__(self, min, max):
        self.min = min
        self.max = max


def AABBvsAABB(a, b):
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


def circle_vs_circle_unoptimized(a, b):
    r = a.radius + b.radius
    print(r, distance(a.position, b.position))
    return r < distance(a.position, b.position)


def circle_vs_circle_optimized(a, b):
    r = a.radius + b.radius
    r *= r
    return r < (a.x + b.x) ** 2 + (a.y + b.y) ** 2


a = Circle(Vector(0, 0), 1)
b = Circle(Vector(4, 0), 1)
print(circle_vs_circle_unoptimized(a, b))
