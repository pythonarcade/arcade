import math


def are_polygons_intersecting(poly_a, poly_b):
    """
    Return True if two polygons intersect.

    Args:
        :poly_a (tuple): List of points that define the first polygon.
        :poly_b (tuple): List of points that define the second polygon.
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
    """
    Rotate a point around a center.

    >>> x, y = rotate(1, 1, 0, 0, 90)
    >>> print(round(x), round(y))
    -1 1
    """
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
    """
    Check for a collision between two sprites.

    >>> import arcade
    >>> scale = 1
    >>> filename = "doc/source/examples/images/meteorGrey_big1.png"
    >>> sprite_1 = arcade.Sprite(filename, scale)
    >>> sprite_1.center_x = 0
    >>> sprite_1.center_y = 0
    >>> sprite_2 = arcade.Sprite(filename, scale)
    >>> sprite_2.center_x = 40
    >>> sprite_2.center_y = 40
    >>> result = check_for_collision(sprite_1, sprite_2)
    >>> sprite_3 = arcade.Sprite(filename, scale)
    >>> sprite_3.center_x = 80
    >>> sprite_3.center_y = 80
    >>> result_1 = check_for_collision(sprite_1, sprite_2)
    >>> result_2 = check_for_collision(sprite_2, sprite_3)
    >>> result_3 = check_for_collision(sprite_1, sprite_3)
    >>> print(result_1, result_2, result_3)
    True True False
    """
    return are_polygons_intersecting(sprite1.points, sprite2.points)


def check_for_collision_with_list(sprite1, sprite_list):
    """
    Check for a collision between a sprite, and a list of sprites.

    >>> import arcade
    >>> scale = 1
    >>> sprite_list = arcade.SpriteList()
    >>> filename = "doc/source/examples/images/meteorGrey_big1.png"
    >>> main_sprite = arcade.Sprite(filename, scale)
    >>> main_sprite.center_x = 0
    >>> main_sprite.center_y = 0
    >>> sprite = arcade.Sprite(filename, scale)
    >>> sprite.center_x = 40
    >>> sprite.center_y = 40
    >>> sprite_list.append(sprite)
    >>> sprite = arcade.Sprite(filename, scale)
    >>> sprite.center_x = 100
    >>> sprite.center_y = 100
    >>> sprite_list.append(sprite)
    >>> collision_list = arcade.check_for_collision_with_list(main_sprite, \
sprite_list)
    >>> print(len(collision_list))
    1
    """
    collision_list = []
    for sprite2 in sprite_list:
        if sprite1 is not sprite2:
            if check_for_collision(sprite1, sprite2):
                collision_list.append(sprite2)
    return collision_list
