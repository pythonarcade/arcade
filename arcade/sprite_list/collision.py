from collections.abc import Iterable
from enum import IntEnum

from arcade.geometry import (
    _are_polygons_overlapping_on_axes,
    are_polygons_intersecting,
    is_point_in_polygon,
)
from arcade.math import get_distance
from arcade.sprite import BasicSprite, SpriteType
from arcade.types import Point
from arcade.types.rect import Rect
from arcade.window_commands import get_window

from .sprite_list import SpriteSequence


class CollisionMethod(IntEnum):
    """
    How :py:func:`check_for_collision_with_list` and
    :py:func:`check_for_collision_with_lists` find the sprites to check.

    This is an :py:class:`~enum.IntEnum`, so the numbers ``0`` to ``3``
    used before it was added still work.

    While the GPU method is very fast when you can't use spatial hashing,
    it's also very slow if you call it many times per frame. Which method
    is best depends entirely on your use case.

    The GPU isn't used on WebGL: wherever a method would use it, every
    sprite is checked instead.
    """

    AUTO = 0
    """
    Use the sprite list's spatial hash if it has one. Otherwise check every
    sprite if there are 1500 or fewer, or use the GPU if there are more.
    """

    SPATIAL = 1
    """
    Use the sprite list's spatial hash. If it doesn't have one, use the GPU.
    """

    GPU = 2
    """
    Use the GPU to find sprites near the sprite being checked, then check
    those.
    """

    SIMPLE = 3
    """
    Check every sprite in the list.
    """


# Module-level aliases, so the hot path doesn't look up enum members every call
_AUTO = CollisionMethod.AUTO
_SPATIAL = CollisionMethod.SPATIAL
_SIMPLE = CollisionMethod.SIMPLE


def get_distance_between_sprites(sprite1: SpriteType, sprite2: SpriteType) -> float:
    """
    Returns the distance between the center of two given sprites

    Args:
        sprite1: Sprite one
        sprite2: Sprite two
    """
    return get_distance(*sprite1._position, *sprite2._position)


def get_closest_sprite(
    sprite: BasicSprite, sprite_list: SpriteSequence[SpriteType]
) -> tuple[SpriteType, float] | None:
    """
    Given a Sprite and SpriteList, returns the closest sprite, and its distance.

    Args:
        sprite:
            Target sprite
        sprite_list:
            List to search for closest sprite.

    Returns:
        A tuple containing the closest sprite and the minimum distance.
        If the spritelist is empty we return ``None``.
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


def check_for_collision(sprite1: BasicSprite, sprite2: BasicSprite) -> bool:
    """
    Check for a collision between two sprites.

    Args:
        sprite1: First sprite
        sprite2: Second sprite

    Returns:
        ``True`` or ``False`` depending if the sprites intersect.
    """
    if __debug__:
        if not isinstance(sprite1, BasicSprite):
            raise TypeError("Parameter 1 is not an instance of a Sprite class.")
        if isinstance(sprite2, SpriteSequence):
            raise TypeError(
                "Parameter 2 is a instance of the SpriteList instead of a required "
                "Sprite. See if you meant to call check_for_collision_with_list instead "
                "of check_for_collision."
            )
        elif not isinstance(sprite2, BasicSprite):
            raise TypeError("Parameter 2 is not an instance of a Sprite class.")

    return _check_for_collision(sprite1, sprite2)


def _check_for_collision(sprite1: BasicSprite, sprite2: BasicSprite) -> bool:
    """
    Check for collision between two sprites.

    Args:
        sprite1: Sprite 1
        sprite2: Sprite 2
    Returns:
        ``True`` if sprites overlap.
    """

    # NOTE: for speed because attribute look ups are slow.
    sprite1_position = sprite1._position
    sprite2_position = sprite2._position
    hit_box1 = sprite1._hit_box
    hit_box2 = sprite2._hit_box

    # Quick check with circles around each hit box. The radius is cached on
    # the hit box until its scale changes.
    radius1 = hit_box1._radius
    if radius1 is None:
        radius1 = hit_box1._get_radius()
    radius2 = hit_box2._radius
    if radius2 is None:
        radius2 = hit_box2._get_radius()
    radius_sum = radius1 + radius2
    radius_sum_sq = radius_sum * radius_sum

    diff_x = sprite1_position[0] - sprite2_position[0]
    diff_x_sq = diff_x * diff_x
    if diff_x_sq > radius_sum_sq:
        return False

    diff_y = sprite1_position[1] - sprite2_position[1]
    diff_y_sq = diff_y * diff_y
    if diff_y_sq > radius_sum_sq:
        return False

    distance = diff_x_sq + diff_y_sq
    if distance > radius_sum_sq:
        return False

    points1 = hit_box1.get_adjusted_points()
    points2 = hit_box2.get_adjusted_points()
    if not points1 or not points2:
        return False

    # Bounding box check with cached bounds. It's much cheaper than the
    # polygon test and covers the x and y axes, which the cached
    # separating axes leave out.
    left1, right1, bottom1, top1 = hit_box1.get_adjusted_bounds()
    left2, right2, bottom2, top2 = hit_box2.get_adjusted_bounds()
    if right1 <= left2 or right2 <= left1 or top1 <= bottom2 or top2 <= bottom1:
        return False

    # Merging the dicts drops directions both hit boxes share
    axes = hit_box1._get_axes() | hit_box2._get_axes()
    return _are_polygons_overlapping_on_axes(points1, points2, axes.values())


def _get_nearby_sprites(
    sprite: BasicSprite, sprite_list: SpriteSequence[SpriteType]
) -> list[SpriteType]:
    sprite_count = len(sprite_list)
    if sprite_count == 0:
        return []
    return sprite_list.get_nearby_sprites_gpu(sprite.position, sprite.size)


def _get_sprites_to_check(
    sprite: BasicSprite,
    sprite_list: SpriteSequence[SpriteType],
    method: CollisionMethod | int,
) -> Iterable[SpriteType]:
    """Get the sprites in a list to check for collisions, using ``method``."""
    if sprite_list.spatial_hash is not None and (method == _AUTO or method == _SPATIAL):
        return sprite_list.spatial_hash.get_sprites_near_sprite(sprite)
    if (
        method == _SIMPLE
        or (method == _AUTO and len(sprite_list) <= 1500)
        or get_window().ctx._gl_api == "webgl"
    ):
        return sprite_list
    # GPU transform - Not on WebGL
    return _get_nearby_sprites(sprite, sprite_list)


def check_for_collision_with_list(
    sprite: BasicSprite,
    sprite_list: SpriteSequence[SpriteType],
    method: CollisionMethod | int = CollisionMethod.AUTO,
) -> list[SpriteType]:
    """
    Check for a collision between a sprite, and a list of sprites.

    Args:
        sprite:
            Sprite to check
        sprite_list:
            SpriteList to check against
        method:
            How to find the sprites to check. See :py:class:`CollisionMethod`.
            Defaults to :py:attr:`CollisionMethod.AUTO`.

    Returns:
        List of sprites colliding, or an empty list.
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the Sprite class, "
                f"it is an instance of {type(sprite)}."
            )
        if not isinstance(sprite_list, SpriteSequence):
            raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    return [
        sprite2
        for sprite2 in _get_sprites_to_check(sprite, sprite_list, method)
        if sprite is not sprite2 and _check_for_collision(sprite, sprite2)
    ]

    # collision_list = []
    # for sprite2 in sprite_list_to_check:
    #     if sprite1 is not sprite2 and sprite2 not in collision_list:
    #         if _check_for_collision(sprite1, sprite2):
    #             collision_list.append(sprite2)


def check_for_collision_with_lists(
    sprite: BasicSprite,
    sprite_lists: Iterable[SpriteSequence[SpriteType]],
    method: CollisionMethod | int = CollisionMethod.AUTO,
) -> list[SpriteType]:
    """
    Check for a collision between a Sprite, and a list of SpriteLists.

    Args:
        sprite:
            Sprite to check
        sprite_lists:
            SpriteLists to check against
        method:
            How to find the sprites to check. See :py:class:`CollisionMethod`.
            Defaults to :py:attr:`CollisionMethod.AUTO`.

    Returns:
        List of sprites colliding, or an empty list.
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the BasicSprite class, "
                f"it is an instance of {type(sprite)}."
            )

    sprites: list[SpriteType] = []

    for sprite_list in sprite_lists:
        for sprite2 in _get_sprites_to_check(sprite, sprite_list, method):
            if sprite is not sprite2 and _check_for_collision(sprite, sprite2):
                sprites.append(sprite2)

    return sprites


def get_sprites_at_point(point: Point, sprite_list: SpriteSequence[SpriteType]) -> list[SpriteType]:
    """
    Get a list of sprites at a particular point. This function sees if any sprite overlaps
    the specified point. If a sprite has a different center_x/center_y but touches the point,
    this will return that sprite.

    Args:
        point: Point to check
        sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    """
    if __debug__:
        if not isinstance(sprite_list, SpriteSequence):
            raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    sprites_to_check: Iterable[SpriteType]

    if sprite_list.spatial_hash is not None:
        sprites_to_check = sprite_list.spatial_hash.get_sprites_near_point(point)
    else:
        sprites_to_check = sprite_list

    return [
        s
        for s in sprites_to_check
        if is_point_in_polygon(point[0], point[1], s.hit_box.get_adjusted_points())
    ]


def get_sprites_at_exact_point(
    point: Point, sprite_list: SpriteSequence[SpriteType]
) -> list[SpriteType]:
    """
    Get a list of sprites whose center_x, center_y match the given point.
    This does NOT return sprites that overlap the point, the center has to be an exact match.

    Args:
        point: Point to check
        sprite_list: SpriteList to check against
    Returns:
        List of sprites colliding, or an empty list.
    """
    if __debug__:
        if not isinstance(sprite_list, SpriteSequence):
            raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    sprites_to_check: Iterable[SpriteType]

    if sprite_list.spatial_hash is not None:
        sprites_to_check = sprite_list.spatial_hash.get_sprites_near_point(point)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
        # print("Checks saved: ", checks_saved)
    else:
        sprites_to_check = sprite_list

    return [s for s in sprites_to_check if s.position == point]


def get_sprites_in_rect(rect: Rect, sprite_list: SpriteSequence[SpriteType]) -> list[SpriteType]:
    """
    Get a list of sprites in a particular rectangle. This function sees if any
    sprite overlaps the specified rectangle. If a sprite has a different
    center_x/center_y but touches the rectangle, this will return that sprite.

    The rectangle is specified as a tuple of (left, right, bottom, top).

    Args:
        rect: Rectangle to check
        sprite_list: SpriteList to check against

    Returns:
        List of sprites colliding, or an empty list.
    """
    if __debug__:
        if not isinstance(sprite_list, SpriteSequence):
            raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    rect_points = rect.to_points()
    sprites_to_check: Iterable[SpriteType]

    if sprite_list.spatial_hash is not None:
        sprites_to_check = sprite_list.spatial_hash.get_sprites_near_rect(rect)
    else:
        sprites_to_check = sprite_list

    return [
        s
        for s in sprites_to_check
        if are_polygons_intersecting(rect_points, s.hit_box.get_adjusted_points())
    ]
