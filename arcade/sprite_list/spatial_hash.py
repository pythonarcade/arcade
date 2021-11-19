import logging

from typing import (
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
)

from arcade import Sprite
from arcade import Point
from arcade import rotate_point
from arcade import are_polygons_intersecting
from arcade import get_distance_between_sprites
from arcade import is_point_in_polygon
from .sprite_list import SpriteList

LOG = logging.getLogger(__name__)


class _SpatialHash:
    """
    Structure for fast collision checking.

    See: https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/
    """

    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.contents = {}
        self.buckets_for_sprite = {}

    def _hash(self, point):
        return int(point[0] / self.cell_size), int(point[1] / self.cell_size)

    def reset(self):
        """
        Clear the spatial hash
        """
        self.contents = {}

    def insert_object_for_box(self, new_object: Sprite):
        """
        Insert a sprite.
        """
        # Get the corners
        min_x = new_object.left
        max_x = new_object.right
        min_y = new_object.bottom
        max_y = new_object.top

        # print(f"New - Center: ({new_object.center_x}, {new_object.center_y}), Angle: {new_object.angle}, "
        #       f"Left: {new_object.left}, Right {new_object.right}")

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # print(f"Add 1: {min_point} {max_point}")

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print(f"Add 2: {min_point} {max_point}")
        # print("Add: ", min_point, max_point)

        buckets = []

        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # append to each intersecting cell
                bucket = self.contents.setdefault((i, j), [])
                buckets.append(bucket)
                bucket.append(new_object)

        self.buckets_for_sprite[new_object] = buckets

    def remove_object(self, sprite_to_delete: Sprite):
        """
        Remove a Sprite.

        :param Sprite sprite_to_delete: Pointer to sprite to be removed.
        """

        for bucket in self.buckets_for_sprite[sprite_to_delete]:
            bucket.remove(sprite_to_delete)

    def get_objects_for_box(self, check_object: Sprite) -> Set[Sprite]:
        """
        Returns colliding Sprites.

        :param Sprite check_object: Sprite we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List
        """
        # Get the corners
        min_x = check_object.left
        max_x = check_object.right
        min_y = check_object.bottom
        max_y = check_object.top

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        close_by_sprites: List[Sprite] = []
        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # print(f"Checking {i}, {j}")
                # append to each intersecting cell
                new_items = self.contents.setdefault((i, j), [])
                # for item in new_items:
                #     print(f"Found {item.guid} in {i}, {j}")
                close_by_sprites.extend(new_items)

        return set(close_by_sprites)

    def get_objects_for_point(self, check_point: Point) -> List[Sprite]:
        """
        Returns Sprites at or close to a point.

        :param Point check_point: Point we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List


        """

        hash_point = self._hash(check_point)

        close_by_sprites: List[Sprite] = []
        new_items = self.contents.setdefault(hash_point, [])
        close_by_sprites.extend(new_items)

        return close_by_sprites


def _create_rects(rect_list: Iterable[Sprite]) -> List[float]:
    """
    Create a vertex buffer for a set of rectangles.
    """

    v2f = []
    for shape in rect_list:
        x1 = -shape.width / 2 + shape.center_x
        x2 = shape.width / 2 + shape.center_x
        y1 = -shape.height / 2 + shape.center_y
        y2 = shape.height / 2 + shape.center_y

        p1 = [x1, y1]
        p2 = [x2, y1]
        p3 = [x2, y2]
        p4 = [x1, y2]

        if shape.angle:
            p1 = rotate_point(p1[0], p1[1], shape.center_x, shape.center_y, shape.angle)
            p2 = rotate_point(p2[0], p2[1], shape.center_x, shape.center_y, shape.angle)
            p3 = rotate_point(p3[0], p3[1], shape.center_x, shape.center_y, shape.angle)
            p4 = rotate_point(p4[0], p4[1], shape.center_x, shape.center_y, shape.angle)

        v2f.extend([p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], p4[0], p4[1]])

    return v2f


def get_closest_sprite(
    sprite: Sprite, sprite_list: "SpriteList"
) -> Optional[Tuple[Sprite, float]]:
    """
    Given a Sprite and SpriteList, returns the closest sprite, and its distance.

    :param Sprite sprite: Target sprite
    :param SpriteList sprite_list: List to search for closest sprite.

    :return: Closest sprite.
    :rtype: Sprite
    """
    if len(sprite_list) == 0:
        return None

    min_pos = 0
    min_distance = get_distance_between_sprites(sprite, sprite_list[min_pos])
    for i in range(1, len(sprite_list)):
        distance = get_distance_between_sprites(sprite, sprite_list[i])
        if distance < min_distance:
            min_pos = i
            min_distance = distance
    return sprite_list[min_pos], min_distance


def check_for_collision(sprite1: Sprite, sprite2: Sprite) -> bool:
    """
    Check for a collision between two sprites.

    :param sprite1: First sprite
    :param sprite2: Second sprite

    :Returns: True or False depending if the sprites intersect.
    :rtype: bool
    """
    if not isinstance(sprite1, Sprite):
        raise TypeError("Parameter 1 is not an instance of the Sprite class.")
    if isinstance(sprite2, SpriteList):
        raise TypeError(
            "Parameter 2 is a instance of the SpriteList instead of a required Sprite. See if you meant to "
            "call check_for_collision_with_list instead of check_for_collision."
        )
    elif not isinstance(sprite2, Sprite):
        raise TypeError("Parameter 2 is not an instance of the Sprite class.")

    return _check_for_collision(sprite1, sprite2)


def _check_for_collision(sprite1: Sprite, sprite2: Sprite) -> bool:
    """
    Check for collision between two sprites.

    :param Sprite sprite1: Sprite 1
    :param Sprite sprite2: Sprite 2

    :returns: True if sprites overlap.
    :rtype: bool
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

    return are_polygons_intersecting(
        sprite1.get_adjusted_hit_box(), sprite2.get_adjusted_hit_box()
    )


def check_for_collision_with_list(
    sprite: Sprite, sprite_list: SpriteList
) -> List[Sprite]:
    """
    Check for a collision between a sprite, and a list of sprites.

    :param Sprite sprite: Sprite to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if not isinstance(sprite, Sprite):
        raise TypeError(
            f"Parameter 1 is not an instance of the Sprite class, it is an instance of {type(sprite)}."
        )
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(
            f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList."
        )

    if (
        sprite_list.use_spatial_hash is None
        and len(sprite_list) > 30
        and sprite_list.percent_sprites_moved < 10
    ):
        LOG.debug(
            f"Enabling spatial hash - Spatial hash is none, sprite list "
            f"is {len(sprite_list)} elements. Percent moved "
            f"{sprite_list._percent_sprites_moved * 100}."
        )
        sprite_list.enable_spatial_hashing()

    if sprite_list.spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_box(sprite)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
    else:
        sprite_list_to_check = sprite_list  # type: ignore

    # print(len(sprite_list_to_check.sprite_list))
    return [
        sprite2
        for sprite2 in sprite_list_to_check
        if sprite is not sprite2 and _check_for_collision(sprite, sprite2)
    ]

    # collision_list = []
    # for sprite2 in sprite_list_to_check:
    #     if sprite1 is not sprite2 and sprite2 not in collision_list:
    #         if _check_for_collision(sprite1, sprite2):
    #             collision_list.append(sprite2)


def check_for_collision_with_lists(sprite: Sprite,
                                   sprite_lists: Iterable[SpriteList]) -> List[Sprite]:
    """
    Check for a collision between a Sprite, and a list of SpriteLists.
    :param Sprite sprite: Sprite to check
    :param List[SpriteList] sprite_list: SpriteLists to check against
    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if not isinstance(sprite, Sprite):
        raise TypeError(f"Parameter 1 is not an instance of the Sprite class, it is an instance of {type(sprite)}.")

    sprites = []

    for sprite_list in sprite_lists:  
        if sprite_list.use_spatial_hash is None and len(sprite_list) > 30 and sprite_list.percent_sprites_moved < 10:
            LOG.debug(f"Enabling spatial hash - Spatial hash is none, sprite list "
                      f"is {len(sprite_list)} elements. Percent moved "
                      f"{sprite_list._percent_sprites_moved * 100}.")
            sprite_list.enable_spatial_hashing()

        if sprite_list.use_spatial_hash:
            sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_box(sprite)  # type: ignore
            # checks_saved = len(sprite_list) - len(sprite_list_to_check)
        else:
            sprite_list_to_check = sprite_list  # type: ignore

        for sprite2 in sprite_list_to_check:
            if sprite is not sprite2 and _check_for_collision(sprite, sprite2):
                sprites.append(sprite2)

    return sprites


def get_sprites_at_point(point: Point, sprite_list: SpriteList) -> List[Sprite]:
    """
    Get a list of sprites at a particular point. This function sees if any sprite overlaps
    the specified point. If a sprite has a different center_x/center_y but touches the point,
    this will return that sprite.

    :param Point point: Point to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(
            f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList."
        )

    if sprite_list.spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_point(point)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
        # print("Checks saved: ", checks_saved)
    else:
        sprite_list_to_check = sprite_list  # type: ignore

    return [
        s
        for s in sprite_list_to_check
        if is_point_in_polygon(point[0], point[1], s.get_adjusted_hit_box())
    ]


def get_sprites_at_exact_point(point: Point, sprite_list: SpriteList) -> List[Sprite]:
    """
    Get a list of sprites whose center_x, center_y match the given point.
    This does NOT return sprites that overlap the point, the center has to be an exact match.

    :param Point point: Point to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if not isinstance(sprite_list, SpriteList):
        raise TypeError(
            f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList."
        )

    if sprite_list.spatial_hash:
        sprite_list_to_check = sprite_list.spatial_hash.get_objects_for_point(point)  # type: ignore
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
        # print("Checks saved: ", checks_saved)
    else:
        sprite_list_to_check = sprite_list  # type: ignore

    return [s for s in sprite_list_to_check if s.position == point]
