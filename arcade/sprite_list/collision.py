import struct
from typing import (
    Iterable,
    List,
    Optional,
    Tuple,
)

from arcade import (
    get_window,
)
from arcade.geometry import (
    are_polygons_intersecting,
    is_point_in_polygon,
)
from arcade.math import get_distance
from arcade.sprite import BasicSprite, SpriteType
from arcade.types import Point, Rect

from .sprite_list import SpriteList


def get_distance_between_sprites(sprite1: SpriteType, sprite2: SpriteType) -> float:
    """
    Returns the distance between the center of two given sprites

    :param Sprite sprite1: Sprite one
    :param Sprite sprite2: Sprite two
    :return: Distance
    :rtype: float
    """
    return get_distance(*sprite1._position, *sprite2._position)


def get_closest_sprite(
    sprite: SpriteType,
    sprite_list: SpriteList
) -> Optional[Tuple[SpriteType, float]]:
    """
    Given a Sprite and SpriteList, returns the closest sprite, and its distance.

    :param Sprite sprite: Target sprite
    :param SpriteList sprite_list: List to search for closest sprite.

    :return: A tuple containing the closest sprite and the minimum distance.
             If the spritelist is empty we return ``None``.
    :rtype: Optional[Tuple[Sprite, float]]
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


def check_for_collision(sprite1: SpriteType, sprite2: SpriteType) -> bool:
    """
    Check for a collision between two sprites.

    :param sprite1: First sprite
    :param sprite2: Second sprite

    :Returns: True or False depending if the sprites intersect.
    :rtype: bool
    """
    if __debug__:
        if not isinstance(sprite1, BasicSprite):
            raise TypeError("Parameter 1 is not an instance of a Sprite class.")
        if isinstance(sprite2, SpriteList):
            raise TypeError(
                "Parameter 2 is a instance of the SpriteList instead of a required Sprite. See if you meant to "
                "call check_for_collision_with_list instead of check_for_collision."
            )
        elif not isinstance(sprite2, BasicSprite):
            raise TypeError("Parameter 2 is not an instance of a Sprite class.")

    return _check_for_collision(sprite1, sprite2)


def _check_for_collision(sprite1: BasicSprite, sprite2: BasicSprite) -> bool:
    """
    Check for collision between two sprites.

    :param Sprite sprite1: Sprite 1
    :param Sprite sprite2: Sprite 2

    :returns: True if sprites overlap.
    :rtype: bool
    """

    #NOTE: for speed becuase attribute look ups are slow.
    sprite1_position = sprite1._position
    sprite1_width = sprite1._width
    sprite1_height = sprite1._height
    sprite2_position = sprite2._position
    sprite2_width = sprite2._width
    sprite2_height = sprite2._height

    radius_sum = (
        (sprite1_width if sprite1_width > sprite1_height else sprite1_height)
        + (sprite2_width if sprite2_width > sprite2_height else sprite2_height)
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


def _get_nearby_sprites(sprite: BasicSprite, sprite_list: SpriteList[SpriteType]) -> List[SpriteType]:
    sprite_count = len(sprite_list)
    if sprite_count == 0:
        return []

    # Update the position and size to check
    ctx = get_window().ctx
    sprite_list._write_sprite_buffers_to_gpu()

    ctx.collision_detection_program["check_pos"] = sprite.position
    ctx.collision_detection_program["check_size"] = sprite.width, sprite.height

    # Ensure the result buffer can fit all the sprites (worst case)
    buffer = ctx.collision_buffer
    if buffer.size < sprite_count * 4:
        buffer.orphan(size=sprite_count * 4)

    # Run the transform shader emitting sprites close to the configured position and size.
    # This runs in a query so we can measure the number of sprites emitted.
    with ctx.collision_query:
        sprite_list._geometry.transform(  # type: ignore
            ctx.collision_detection_program,
            buffer,
            vertices=sprite_count,
        )

    # Store the number of sprites emitted
    emit_count = ctx.collision_query.primitives_generated
    # print(emit_count, ctx.collision_query.time_elapsed, ctx.collision_query.time_elapsed / 1_000_000_000)

    # If no sprites emitted we can just return an empty list
    if emit_count == 0:
        return []

    # # Debug block for transform data to keep around
    # print("emit_count", emit_count)
    # data = buffer.read(size=emit_count * 4)
    # print("bytes", data)
    # print("data", struct.unpack(f'{emit_count}i', data))

    # .. otherwise build and return a list of the sprites selected by the transform
    return [
        sprite_list[i]
        for i in struct.unpack(f'{emit_count}i', buffer.read(size=emit_count * 4))
    ]


def check_for_collision_with_list(
    sprite: SpriteType,
    sprite_list: SpriteList,
    method: int = 0,
) -> List[SpriteType]:
    """
    Check for a collision between a sprite, and a list of sprites.

    :param Sprite sprite: Sprite to check
    :param SpriteList sprite_list: SpriteList to check against
    :param int method: Collision check method.
        0 is auto-select. (spatial if available, GPU if 1500+ sprites, else simple)
        1 is Spatial Hashing if available,
        2 is GPU based, 3 is simple check-everything. Defaults to 0.

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the Sprite class, it is an instance of {type(sprite)}."
            )
        if not isinstance(sprite_list, SpriteList):
            raise TypeError(
                f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList."
            )

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
    sprite_lists: Iterable[SpriteList[SpriteType]],
    method=1,
) -> List[SpriteType]:
    """
    Check for a collision between a Sprite, and a list of SpriteLists.

    :param Sprite sprite: Sprite to check
    :param Iterable[SpriteList] sprite_lists: SpriteLists to check against
    :param int method: Collision check method. 1 is Spatial Hashing if available,
        2 is GPU based, 3 is slow CPU-bound check-everything. Defaults to 1.

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the BasicSprite class, it is an instance of {type(sprite)}."
            )

    sprites: List[SpriteType] = []
    sprites_to_check: Iterable[SpriteType]

    for sprite_list in sprite_lists:
        if sprite_list.spatial_hash is not None and method == 1:
            sprites_to_check = sprite_list.spatial_hash.get_sprites_near_sprite(sprite)
        elif method == 3:
            sprites_to_check = sprite_list
        else:
            # GPU transform
            sprites_to_check = _get_nearby_sprites(sprite, sprite_list)

        for sprite2 in sprites_to_check:
            if sprite is not sprite2 and _check_for_collision(sprite, sprite2):
                sprites.append(sprite2)

    return sprites


def get_sprites_at_point(point: Point, sprite_list: SpriteList[SpriteType]) -> List[SpriteType]:
    """
    Get a list of sprites at a particular point. This function sees if any sprite overlaps
    the specified point. If a sprite has a different center_x/center_y but touches the point,
    this will return that sprite.

    :param Point point: Point to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if __debug__:
        if not isinstance(sprite_list, SpriteList):
            raise TypeError(
                f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList."
            )

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


def get_sprites_at_exact_point(point: Point, sprite_list: SpriteList[SpriteType]) -> List[SpriteType]:
    """
    Get a list of sprites whose center_x, center_y match the given point.
    This does NOT return sprites that overlap the point, the center has to be an exact match.

    :param Point point: Point to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if __debug__:
        if not isinstance(sprite_list, SpriteList):
            raise TypeError(
                f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList."
            )

    sprites_to_check: Iterable[SpriteType]

    if sprite_list.spatial_hash is not None:
        sprites_to_check = sprite_list.spatial_hash.get_sprites_near_point(point)
        # checks_saved = len(sprite_list) - len(sprite_list_to_check)
        # print("Checks saved: ", checks_saved)
    else:
        sprites_to_check = sprite_list

    return [s for s in sprites_to_check if s.position == point]


def get_sprites_in_rect(rect: Rect, sprite_list: SpriteList[SpriteType]) -> List[SpriteType]:
    """
    Get a list of sprites in a particular rectangle. This function sees if any sprite overlaps
    the specified rectangle. If a sprite has a different center_x/center_y but touches the rectangle,
    this will return that sprite.

    The rectangle is specified as a tuple of (left, right, bottom, top).

    :param Rect rect: Rectangle to check
    :param SpriteList sprite_list: SpriteList to check against

    :returns: List of sprites colliding, or an empty list.
    :rtype: list
    """
    if __debug__:
        if not isinstance(sprite_list, SpriteList):
            raise TypeError(
                f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList."
            )

    rect_points = (
        (rect[0], rect[3]),
        (rect[1], rect[3]),
        (rect[1], rect[2]),
        (rect[0], rect[2]),
    )
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
