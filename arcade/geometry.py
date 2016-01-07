import math


def are_polygons_intersecting(poly_a, poly_b):
    """
    Return True if two polygons intersect.

    Args:
        :poly_a (tuple): List of points that define the first polygon.
        :poly_b (tuple): List of points that define the secpmd polygon.
    Returns:
        bool
    Raises:
        None

    :Example:

    >>> import arcade
    >>> poly1 = ((0.1, 0.1), (0.2, 0.1), (0.2, 0.2), (0.1, 0.2))
    >>> poly2 = ((0.15, 0.1), (0.25, 0.1), (0.25, 0.25), (0.15, 0.25))
    >>> poly3 = ((0.3, 0.1), (0.4, 0.1), (0.4, 0.2), (0.3, 0.2))
    >>> test1 = arcade.are_polygons_intersecting(poly1, poly2)
    >>> test2 = arcade.are_polygons_intersecting(poly2, poly3)
    >>> test3 = arcade.are_polygons_intersecting(poly1, poly3)
    >>> print(test1, test2, test3)
    True False False

    """
    for polygon in (poly_a, poly_b):

        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            projection_1 = polygon[i1]
            projection_2 = polygon[i2]

            normal = (projection_2[1] - projection_1[1],
                      projection_1[0] - projection_2[0])

            minA, maxA, minB, maxB = (None,) * 4

            for p in poly_a:
                projected = normal[0] * p[0] + normal[1] * p[1]

                if not minA or projected < minA:
                    minA = projected
                if not maxA or projected > maxA:
                    maxA = projected

            for p in poly_b:
                projected = normal[0] * p[0] + normal[1] * p[1]

                if not minB or projected < minB:
                    minB = projected
                if not maxB or projected > maxB:
                    maxB = projected

            if maxA <= minB or maxB <= minA:
                return False

    return True


def rotate(x, y, cx, cy, angle):
    """ Rotate a point around a center. """
    tempX = x - cx
    tempY = y - cy

    # now apply rotation
    rotatedX = tempX * math.cos(math.radians(angle)) - \
        tempY * math.sin(math.radians(angle))
    rotatedY = tempX * math.sin(math.radians(angle)) + \
        tempY * math.cos(math.radians(angle))

    # translate back
    x = rotatedX + cx
    y = rotatedY + cy

    return x, y


def check_for_collision(sprite1, sprite2):
    """ Check for a collision between two sprites. """
    return are_polygons_intersecting(sprite1.points, sprite2.points)


def check_for_collision_with_list(sprite1, sprite_list):
    """ Check for a collision between a sprite, and a list of sprites. """
    collision_list = []
    for sprite2 in sprite_list:
        if not sprite1 is sprite2:
            if check_for_collision(sprite1, sprite2):
                collision_list.append(sprite2)
    return collision_list
