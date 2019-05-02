"""
Functions for calculating geometry.
"""

from arcade.sprite import Sprite
from arcade.sprite_list import SpriteList
from typing import List
from arcade.arcade_types import PointList

PRECISION = 2


def are_polygons_intersecting(poly_a: PointList,
                              poly_b: PointList) -> bool:
    """
    Return True if two polygons intersect.

    :param PointList poly_a: List of points that define the first polygon.
    :param PointList poly_b: List of points that define the second polygon.
    :Returns: True or false depending if polygons intersect

    :rtype bool:
    """

    for polygon in (poly_a, poly_b):

        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)
            projection_1 = polygon[i1]
            projection_2 = polygon[i2]

            normal = (projection_2[1] - projection_1[1],
                      projection_1[0] - projection_2[0])

            min_a, max_a, min_b, max_b = (None,) * 4

            for poly in poly_a:
                projected = normal[0] * poly[0] + normal[1] * poly[1]

                if min_a is None or projected < min_a:
                    min_a = projected
                if max_a is None or projected > max_a:
                    max_a = projected

            for poly in poly_b:
                projected = normal[0] * poly[0] + normal[1] * poly[1]

                if min_b is None or projected < min_b:
                    min_b = projected
                if max_b is None or projected > max_b:
                    max_b = projected

            if max_a <= min_b or max_b <= min_a:
                return False

    return True


def check_for_collision(sprite1: Sprite, sprite2: Sprite) -> bool:
    """
    Check for a collision between two sprites.

    :param sprite1: First sprite
    :param sprite2: Second sprite

    :Returns: True or False depending if the sprites intersect.
    """
    if not isinstance(sprite1, Sprite):
        raise TypeError("Parameter 1 is not an instance of the Sprite class.")
    if isinstance(sprite2, SpriteList):
        raise TypeError("Parameter 2 is a instance of the SpriteList instead of a required Sprite. See if you meant to "
                        "call check_for_collision_with_list instead of check_for_collision.")
    elif not isinstance(sprite2, Sprite):
        raise TypeError("Parameter 2 is not an instance of the Sprite class.")

    return _check_for_collision(sprite1, sprite2)


def _check_for_collision(sprite1: Sprite, sprite2: Sprite) -> bool:
    """
    Check for collision between two sprites.

    :param Sprite sprite1: Sprite 1
    :param Sprite sprite2: Sprite 2

    :returns: Boolean
    """
    collision_radius_sum = sprite1.collision_radius + sprite2.collision_radius

    diff_x = sprite1.position[0] - sprite2.position[0]
    diff_x2 = diff_x * diff_x

    if diff_x2 > collision_radius_sum * collision_radius_sum:
        return False

    diff_y = sprite1.position[1] - sprite2.position[1]
    diff_y2 = diff_y * diff_y
    if diff_y2 > collision_radius_sum * collision_radius_sum:
        return False

    distance = diff_x2 + diff_y2
    if distance > collision_radius_sum * collision_radius_sum:
        return False

    return are_polygons_intersecting(sprite1.points, sprite2.points)


def check_for_collision_with_list(sprite: Sprite,
                                  sprite_list: SpriteList) -> List[Sprite]:
    """
    Check for a collision between a sprite, and a list of sprites.

    :param Sprite sprite: Sprite to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    """
    if not isinstance(sprite, Sprite):
        raise TypeError("Parameter 1 is not an instance of the Sprite class.")
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    if sprite_list.use_spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_box(sprite)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
    else:
        sprite_list_to_check = sprite_list

    collision_list = [sprite2
                      for sprite2 in sprite_list_to_check
                      if sprite is not sprite2 and _check_for_collision(sprite, sprite2)]

    # collision_list = []
    # for sprite2 in sprite_list_to_check:
    #     if sprite1 is not sprite2 and sprite2 not in collision_list:
    #         if _check_for_collision(sprite1, sprite2):
    #             collision_list.append(sprite2)
    return collision_list
