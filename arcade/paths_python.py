from arcade import Point
from arcade import SpriteList
from arcade import get_distance
from arcade import lerp_vec
from arcade import get_sprites_at_point


def has_line_of_sight(point_1: Point,
                      point_2: Point,
                      walls: SpriteList,
                      max_distance: int = -1,
                      check_resolution: int = 2):
    """
    Determine if we have line of sight between two points. Try to make sure
    that spatial hashing is enabled on the wall SpriteList or this will be
    very slow.

    :param Point point_1: Start position
    :param Point point_2: End position position
    :param SpriteList walls: List of all blocking sprites
    :param int max_distance: Max distance point 1 can see
    :param int check_resolution: Check every x pixels for a sprite. Trade-off
                                 between accuracy and speed.
    """
    distance = get_distance(point_1[0], point_1[1],
                            point_2[0], point_2[1])
    steps = int(distance // check_resolution)
    for step in range(steps + 1):
        step_distance = step * check_resolution
        u = step_distance / distance
        midpoint = lerp_vec(point_1, point_2, u)
        if max_distance != -1 and step_distance > max_distance:
            return False
        # print(point_1, point_2, step, u, step_distance, midpoint)
        sprite_list = get_sprites_at_point(midpoint, walls)
        if len(sprite_list) > 0:
            return False
    return True
