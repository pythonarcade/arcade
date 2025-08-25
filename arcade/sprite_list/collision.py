from collections.abc import Iterable

from arcade.geometry import (
    are_polygons_intersecting,
    is_point_in_polygon,
)
from arcade.math import get_distance
from arcade.sprite import BasicSprite, SpriteType
from arcade.types import Point
from arcade.types.rect import Rect

from .sprite_list import SpriteSequence


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
    sprite1_width = sprite1._width
    sprite1_height = sprite1._height
    sprite2_position = sprite2._position
    sprite2_width = sprite2._width
    sprite2_height = sprite2._height

    radius_sum = (sprite1_width if sprite1_width > sprite1_height else sprite1_height) + (
        sprite2_width if sprite2_width > sprite2_height else sprite2_height
    )

    # Multiply by half of the theoretical max diagonal length for an estimation of distance
    radius_sum *= 0.71  # 1.42 / 2
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

    return are_polygons_intersecting(
        sprite1.hit_box.get_adjusted_points(), sprite2.hit_box.get_adjusted_points()
    )


def _get_nearby_sprites(
    sprite: BasicSprite, sprite_list: SpriteSequence[SpriteType]
) -> list[SpriteType]:
    sprite_count = len(sprite_list)
    if sprite_count == 0:
        return []
    return sprite_list.get_nearby_sprites_gpu(sprite.position, sprite.size)


def check_for_collision_with_list(
    sprite: BasicSprite,
    sprite_list: SpriteSequence[SpriteType],
    method: int = 0,
) -> list[SpriteType]:
    """
    Check for a collision between a sprite, and a list of sprites.

    Args:
        sprite:
            Sprite to check
        sprite_list:
            SpriteList to check against
        method:
            Collision check method. Defaults to 0.

            - 0: auto-select. (spatial if available, GPU if 1500+ sprites, else simple)
            - 1: Spatial Hashing if available,
            - 2: GPU based
            - 3: Simple check-everything.

            Note that while the GPU method is very fast when you cannot use spatial hashing,
            it's also very slow if you are calling this function many times per frame.
            What method is the most appropriate depends entirely on your use case.

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

    sprites_to_check: Iterable[SpriteType]
    # Spatial
    if sprite_list.spatial_hash is not None and (method == 1 or method == 0):
        sprites_to_check = sprite_list.spatial_hash.get_sprites_near_sprite(sprite)
    elif method == 3 or (method == 0 and len(sprite_list) <= 1500):
        sprites_to_check = sprite_list
    else:
        # GPU transform
        sprites_to_check = _get_nearby_sprites(sprite, sprite_list)

    return [
        sprite2
        for sprite2 in sprites_to_check
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
    method=0,
) -> list[SpriteType]:
    """
    Check for a collision between a Sprite, and a list of SpriteLists.

    Args:
        sprite:
            Sprite to check
        sprite_lists:
            SpriteLists to check against
        method:
            Collision check method. Defaults to 0.

            - 0: auto-select. (spatial if available, GPU if 1500+ sprites, else simple)
            - 1: Spatial Hashing if available,
            - 2: GPU based
            - 3: Simple check-everything.

            Note that while the GPU method is very fast when you cannot use spatial hashing,
            it's also very slow if you are calling this function many times per frame.
            What method is the most appropriate depends entirely on your use case.

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
    sprites_to_check: Iterable[SpriteType]

    for sprite_list in sprite_lists:
        # Spatial
        if sprite_list.spatial_hash is not None and (method == 1 or method == 0):
            sprites_to_check = sprite_list.spatial_hash.get_sprites_near_sprite(sprite)
        elif method == 3 or (method == 0 and len(sprite_list) <= 1500):
            sprites_to_check = sprite_list
        else:
            # GPU transform
            sprites_to_check = _get_nearby_sprites(sprite, sprite_list)

        for sprite2 in sprites_to_check:
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
