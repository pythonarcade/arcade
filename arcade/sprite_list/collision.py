from collections.abc import Iterable
from enum import IntEnum
from math import hypot
from typing import NamedTuple, TypeVar

from pyglet.math import Vec2

from arcade.geometry import (
    _are_polygons_overlapping_on_axes,
    are_polygons_intersecting,
    is_point_in_polygon,
)
from arcade.math import get_distance
from arcade.sprite import BasicSprite, SpriteType
from arcade.types import Point
from arcade.types.rect import LRBT, Rect
from arcade.window_commands import get_window

from .sprite_list import SpriteSequence

# The sprite type of the second list in check_for_collision_between_lists
_SpriteType2 = TypeVar("_SpriteType2", bound=BasicSprite)


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
    Use the sprite list's spatial hash. If it doesn't have one, choose the
    same way as :py:attr:`AUTO`.
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


class CollisionInfo(NamedTuple):
    """
    How two colliding sprites overlap. Returned by :py:func:`get_collision_info`.

    Moving the first sprite by ``normal * depth`` is the smallest move that
    separates the two sprites, leaving their hit boxes just touching::

        info = arcade.get_collision_info(player, wall)
        if info:
            player.position += info.normal * info.depth
    """

    normal: Vec2
    """
    A unit vector pointing the way to move the first sprite to separate it
    from the second. Swapping the sprites flips its direction.
    """

    depth: float
    """
    How far, in pixels, to move the first sprite along :py:attr:`normal` to
    separate the sprites. Always greater than zero.
    """


class SweepInfo(NamedTuple):
    """
    The first sprite hit by a moving sprite. Returned by :py:func:`sweep_sprite`.

    To move the sprite up to the point where it hits::

        hit = arcade.sweep_sprite(bullet, dx, dy, walls)
        if hit:
            bullet.position += Vec2(dx, dy) * hit.fraction
    """

    sprite: BasicSprite
    """The sprite that was hit."""

    fraction: float
    """
    How far along the move the hit happens, from 0.0 (at the start) to just
    under 1.0. It's 0.0 if the moving sprite already overlaps :py:attr:`sprite`.
    """

    distance: float
    """How far the moving sprite travels before the hit, in pixels."""

    normal: Vec2
    """
    A unit vector pointing out of the hit sprite's surface, back toward the
    moving sprite. Useful for bouncing. If the moving sprite started inside
    the hit sprite, this is the way to push it out, as from
    :py:func:`get_collision_info`.
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

    Sprites whose hit boxes only touch, sharing an edge or a corner, don't
    count as colliding. This lets the physics engines rest a sprite against
    a wall or on the ground.

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


def get_collision_info(sprite1: BasicSprite, sprite2: BasicSprite) -> CollisionInfo | None:
    """
    Check for a collision between two sprites, and find how to separate them.

    This works like :py:func:`check_for_collision`, but instead of ``True``
    it returns a :py:class:`CollisionInfo` with the smallest move that
    separates the sprites: the direction to move ``sprite1`` and how far.
    This is useful for pushing a sprite out of a wall, or bouncing::

        info = arcade.get_collision_info(player, wall)
        if info:
            player.position += info.normal * info.depth

    As with :py:func:`check_for_collision`, sprites that only touch don't
    count as colliding.

    .. note:: After moving by exactly ``normal * depth`` the hit boxes touch,
              but floating point rounding can leave them overlapping by a
              tiny amount. Add a small extra distance if they must not
              overlap at all.

    .. warning:: The result is only correct for convex hit boxes. The
                 detailed hit box algorithm can create concave ones.

    When more than one move is equally small, the y axis is preferred, then
    the x axis, then other directions, and moving up or right over moving
    down or left. So two identical sprites in the same place are separated
    by moving ``sprite1`` up.

    Args:
        sprite1: The sprite to separate
        sprite2: The sprite to separate it from

    Returns:
        A :py:class:`CollisionInfo` if the sprites collide, otherwise ``None``.
    """
    if __debug__:
        if not isinstance(sprite1, BasicSprite):
            raise TypeError("Parameter 1 is not an instance of a Sprite class.")
        if isinstance(sprite2, SpriteSequence):
            raise TypeError(
                "Parameter 2 is a instance of the SpriteList instead of a required "
                "Sprite. A list isn't supported here; check each sprite in it instead."
            )
        elif not isinstance(sprite2, BasicSprite):
            raise TypeError("Parameter 2 is not an instance of a Sprite class.")

    return _get_collision_info(sprite1, sprite2)


def _get_collision_info(sprite1: BasicSprite, sprite2: BasicSprite) -> CollisionInfo | None:
    """:py:func:`get_collision_info` without the argument type checks."""
    hit_box1 = sprite1._hit_box
    hit_box2 = sprite2._hit_box

    # Quick check with circles around each hit box, as in _check_for_collision
    radius1 = hit_box1._radius
    if radius1 is None:
        radius1 = hit_box1._get_radius()
    radius2 = hit_box2._radius
    if radius2 is None:
        radius2 = hit_box2._get_radius()
    radius_sum = radius1 + radius2
    diff_x = sprite1._position[0] - sprite2._position[0]
    diff_y = sprite1._position[1] - sprite2._position[1]
    if diff_x * diff_x + diff_y * diff_y > radius_sum * radius_sum:
        return None

    points1 = hit_box1.get_adjusted_points()
    points2 = hit_box2.get_adjusted_points()
    if not points1 or not points2:
        return None

    left1, right1, bottom1, top1 = hit_box1.get_adjusted_bounds()
    left2, right2, bottom2, top2 = hit_box2.get_adjusted_bounds()
    if right1 <= left2 or right2 <= left1 or top1 <= bottom2 or top2 <= bottom1:
        return None

    # Find the smallest overlap. The y and x axes come from the bounds, then
    # the hit boxes' other edge directions. For each axis there are two
    # ways to move: in the positive direction (sprite1 past the top of
    # sprite2's range) or the negative one. Ties keep the earlier choice.
    up = top2 - bottom1
    down = top1 - bottom2
    if up <= down:
        best_depth, best_x, best_y = up, 0.0, 1.0
    else:
        best_depth, best_x, best_y = down, 0.0, -1.0

    right = right2 - left1
    left = right1 - left2
    if right < best_depth and right <= left:
        best_depth, best_x, best_y = right, 1.0, 0.0
    elif left < best_depth and left < right:
        best_depth, best_x, best_y = left, -1.0, 0.0

    axes = hit_box1._get_axes() | hit_box2._get_axes()
    for normal_x, normal_y in axes.values():
        projected_1 = [normal_x * px + normal_y * py for px, py in points1]
        projected_2 = [normal_x * px + normal_y * py for px, py in points2]
        min_1 = min(projected_1)
        max_1 = max(projected_1)
        min_2 = min(projected_2)
        max_2 = max(projected_2)
        if max_1 <= min_2 or max_2 <= min_1:
            return None

        # The normals aren't unit length, so convert the overlaps to pixels
        length = hypot(normal_x, normal_y)
        positive = (max_2 - min_1) / length
        negative = (max_1 - min_2) / length
        if positive < best_depth and positive <= negative:
            best_depth, best_x, best_y = positive, normal_x / length, normal_y / length
        elif negative < best_depth and negative < positive:
            best_depth, best_x, best_y = negative, -normal_x / length, -normal_y / length

    return CollisionInfo(Vec2(best_x, best_y), best_depth)


def _get_separation_distance(
    sprite1: BasicSprite, sprite2: BasicSprite, direction_x: float, direction_y: float
) -> float:
    """
    How far ``sprite1`` must move along a direction to stop colliding with ``sprite2``.

    Unlike :py:func:`get_collision_info`, the direction is fixed, for
    example straight up to land on a slope. Returns ``0.0`` if the sprites
    don't collide. Like the other separating axis functions, this is only
    exact for convex hit boxes; callers should check the result.

    Args:
        sprite1: The sprite to move
        sprite2: The sprite to move it away from
        direction_x: X component of the unit direction to move ``sprite1``
        direction_y: Y component of the unit direction to move ``sprite1``
    """
    hit_box1 = sprite1._hit_box
    hit_box2 = sprite2._hit_box
    points1 = hit_box1.get_adjusted_points()
    points2 = hit_box2.get_adjusted_points()
    if not points1 or not points2:
        return 0.0

    left1, right1, bottom1, top1 = hit_box1.get_adjusted_bounds()
    left2, right2, bottom2, top2 = hit_box2.get_adjusted_bounds()
    if right1 <= left2 or right2 <= left1 or top1 <= bottom2 or top2 <= bottom1:
        return 0.0

    # Moving a distance t along the direction shifts sprite1's projection on
    # an axis by t * (direction . axis). The sprites are separated once they
    # are on any one axis, so the answer is the smallest distance that
    # separates them on some axis.
    best = float("inf")
    if direction_x > 0:
        best = min(best, (right2 - left1) / direction_x)
    elif direction_x < 0:
        best = min(best, (right1 - left2) / -direction_x)
    if direction_y > 0:
        best = min(best, (top2 - bottom1) / direction_y)
    elif direction_y < 0:
        best = min(best, (top1 - bottom2) / -direction_y)

    axes = hit_box1._get_axes() | hit_box2._get_axes()
    for normal_x, normal_y in axes.values():
        projected_1 = [normal_x * px + normal_y * py for px, py in points1]
        projected_2 = [normal_x * px + normal_y * py for px, py in points2]
        min_1 = min(projected_1)
        max_1 = max(projected_1)
        min_2 = min(projected_2)
        max_2 = max(projected_2)
        if max_1 <= min_2 or max_2 <= min_1:
            return 0.0
        speed = direction_x * normal_x + direction_y * normal_y
        if speed > 0:
            best = min(best, (max_2 - min_1) / speed)
        elif speed < 0:
            best = min(best, (max_1 - min_2) / -speed)

    return best


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
    if method == _AUTO or method == _SPATIAL:
        if sprite_list.spatial_hash is not None:
            return sprite_list.spatial_hash.get_sprites_near_sprite(sprite)
        if len(sprite_list) <= 1500:
            return sprite_list
    if method == _SIMPLE or get_window().ctx._gl_api == "webgl":
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


def has_collision_with_list(
    sprite: BasicSprite,
    sprite_list: SpriteSequence[BasicSprite],
    method: CollisionMethod | int = CollisionMethod.AUTO,
) -> bool:
    """
    Check if a sprite collides with any sprite in a list.

    This is faster than checking whether :py:func:`check_for_collision_with_list`
    returns an empty list, since it stops at the first collision it finds.

    Args:
        sprite:
            Sprite to check
        sprite_list:
            SpriteList to check against
        method:
            How to find the sprites to check. See :py:class:`CollisionMethod`.
            Defaults to :py:attr:`CollisionMethod.AUTO`.

    Returns:
        ``True`` if the sprite collides with at least one sprite in the list.
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the Sprite class, "
                f"it is an instance of {type(sprite)}."
            )
        if not isinstance(sprite_list, SpriteSequence):
            raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    for sprite2 in _get_sprites_to_check(sprite, sprite_list, method):
        if sprite is not sprite2 and _check_for_collision(sprite, sprite2):
            return True
    return False


def has_collision_with_lists(
    sprite: BasicSprite,
    sprite_lists: Iterable[SpriteSequence[BasicSprite]],
    method: CollisionMethod | int = CollisionMethod.AUTO,
) -> bool:
    """
    Check if a sprite collides with any sprite in any of several lists.

    This is faster than checking whether :py:func:`check_for_collision_with_lists`
    returns an empty list, since it stops at the first collision it finds.

    Args:
        sprite:
            Sprite to check
        sprite_lists:
            SpriteLists to check against
        method:
            How to find the sprites to check. See :py:class:`CollisionMethod`.
            Defaults to :py:attr:`CollisionMethod.AUTO`.

    Returns:
        ``True`` if the sprite collides with at least one sprite in the lists.
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the BasicSprite class, "
                f"it is an instance of {type(sprite)}."
            )

    for sprite_list in sprite_lists:
        for sprite2 in _get_sprites_to_check(sprite, sprite_list, method):
            if sprite is not sprite2 and _check_for_collision(sprite, sprite2):
                return True
    return False


def check_for_collision_between_lists(
    sprite_list_a: SpriteSequence[SpriteType],
    sprite_list_b: SpriteSequence[_SpriteType2],
    method: CollisionMethod | int = CollisionMethod.AUTO,
) -> list[tuple[SpriteType, _SpriteType2]]:
    """
    Find every pair of colliding sprites between two lists.

    For example, to remove bullets and the enemies they hit::

        for bullet, enemy in arcade.check_for_collision_between_lists(bullets, enemies):
            bullet.remove_from_sprite_lists()
            enemy.remove_from_sprite_lists()

    A sprite can be in more than one pair, such as a bullet hitting two
    enemies at once.

    For each sprite in ``sprite_list_a``, ``method`` chooses how to find the
    sprites in ``sprite_list_b`` to check, the same way as in
    :py:func:`check_for_collision_with_list`. For the best speed, enable
    spatial hashing on ``sprite_list_b``, and make it the list whose sprites
    move less.

    If both arguments are the same list, each colliding pair is returned
    once, and sprites are never paired with themselves.

    Args:
        sprite_list_a:
            The first list of sprites
        sprite_list_b:
            The second list of sprites
        method:
            How to find the sprites in ``sprite_list_b`` to check. See
            :py:class:`CollisionMethod`. Defaults to :py:attr:`CollisionMethod.AUTO`.

    Returns:
        A list of ``(sprite_a, sprite_b)`` tuples, or an empty list.
    """
    if __debug__:
        if not isinstance(sprite_list_a, SpriteSequence):
            raise TypeError(
                f"Parameter 1 is a {type(sprite_list_a)} instead of expected SpriteList."
            )
        if not isinstance(sprite_list_b, SpriteSequence):
            raise TypeError(
                f"Parameter 2 is a {type(sprite_list_b)} instead of expected SpriteList."
            )

    pairs: list[tuple[SpriteType, _SpriteType2]] = []
    if not sprite_list_a or not sprite_list_b:
        return pairs

    if sprite_list_a is sprite_list_b:
        # Only report each pair once, by skipping sprites already checked
        checked: set[BasicSprite] = set()
        for sprite_a in sprite_list_a:
            checked.add(sprite_a)
            for sprite_b in _get_sprites_to_check(sprite_a, sprite_list_b, method):
                if sprite_b not in checked and _check_for_collision(sprite_a, sprite_b):
                    pairs.append((sprite_a, sprite_b))
        return pairs

    for sprite_a in sprite_list_a:
        for sprite_b in _get_sprites_to_check(sprite_a, sprite_list_b, method):
            if sprite_a is not sprite_b and _check_for_collision(sprite_a, sprite_b):
                pairs.append((sprite_a, sprite_b))
    return pairs


def get_collision_info_with_list(
    sprite: BasicSprite,
    sprite_list: SpriteSequence[SpriteType],
    method: CollisionMethod | int = CollisionMethod.AUTO,
) -> list[tuple[SpriteType, CollisionInfo]]:
    """
    Find the sprites in a list that a sprite collides with, and how to separate them.

    This works like :py:func:`check_for_collision_with_list`, but also
    returns a :py:class:`CollisionInfo` for each colliding sprite, as from
    :py:func:`get_collision_info`. The results are sorted deepest overlap
    first, which is usually the one to resolve first::

        for wall, info in arcade.get_collision_info_with_list(player, walls):
            # Each move changes the remaining overlaps, so check again
            info = arcade.get_collision_info(player, wall)
            if info:
                player.position += info.normal * info.depth

    Each :py:class:`CollisionInfo` is how to separate ``sprite`` from that
    one sprite. Moving ``sprite`` to resolve one overlap changes the others,
    so they don't add up to a move that resolves them all.

    Args:
        sprite:
            The sprite to separate
        sprite_list:
            SpriteList to check against
        method:
            How to find the sprites to check. See :py:class:`CollisionMethod`.
            Defaults to :py:attr:`CollisionMethod.AUTO`.

    Returns:
        A list of ``(colliding_sprite, CollisionInfo)`` tuples, deepest first,
        or an empty list.
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the Sprite class, "
                f"it is an instance of {type(sprite)}."
            )
        if not isinstance(sprite_list, SpriteSequence):
            raise TypeError(f"Parameter 2 is a {type(sprite_list)} instead of expected SpriteList.")

    results: list[tuple[SpriteType, CollisionInfo]] = []
    for sprite2 in _get_sprites_to_check(sprite, sprite_list, method):
        if sprite is not sprite2:
            info = _get_collision_info(sprite, sprite2)
            if info is not None:
                results.append((sprite2, info))

    # Deepest first. The sort is stable, so equal depths keep the order found.
    if len(results) > 1:
        results.sort(key=lambda result: result[1].depth, reverse=True)
    return results


def _sweep_axis(
    min_1: float, max_1: float, min_2: float, max_2: float, speed: float
) -> tuple[float, float] | None:
    """
    When two projections on an axis overlap, if one moves at ``speed``.

    Returns the ``(start, end)`` of the overlap as fractions of the move.
    Touching doesn't count as overlapping. If ``speed`` is 0, returns
    ``(-inf, inf)`` if they overlap, otherwise ``None``.
    """
    if speed == 0:
        if max_1 <= min_2 or max_2 <= min_1:
            return None
        return float("-inf"), float("inf")
    t1 = (min_2 - max_1) / speed
    t2 = (max_2 - min_1) / speed
    if t1 > t2:
        return t2, t1
    return t1, t2


def _sweep_against(
    sprite: BasicSprite, other: BasicSprite, dx: float, dy: float, best_fraction: float
) -> tuple[float, float, float] | None:
    """
    When ``sprite``, moving by ``(dx, dy)``, first overlaps ``other``.

    Returns ``(fraction, normal_x, normal_y)`` if they overlap at some point
    during the move, strictly before ``best_fraction``. A negative fraction means
    they already overlap at the start. The normal is a unit vector out of
    ``other``. Exact for convex hit boxes that don't rotate during the move.
    """
    hit_box1 = sprite._hit_box
    hit_box2 = other._hit_box
    points1 = hit_box1.get_adjusted_points()
    points2 = hit_box2.get_adjusted_points()
    if not points1 or not points2:
        return None

    # For each axis, find when the projections overlap during the move. The
    # sprites overlap while they overlap on every axis, so they first
    # overlap at the latest of the start times, if that's before the
    # earliest of the end times.
    enter = float("-inf")
    leave = float("inf")
    normal_x = 0.0
    normal_y = 0.0

    # The y axis first, then x, then the other edges, so ties prefer them
    left1, right1, bottom1, top1 = hit_box1.get_adjusted_bounds()
    left2, right2, bottom2, top2 = hit_box2.get_adjusted_bounds()
    for min_1, max_1, min_2, max_2, speed, axis_x, axis_y in (
        (bottom1, top1, bottom2, top2, dy, 0.0, 1.0),
        (left1, right1, left2, right2, dx, 1.0, 0.0),
    ):
        overlap = _sweep_axis(min_1, max_1, min_2, max_2, speed)
        if overlap is None:
            return None
        start, end = overlap
        if start > enter:
            enter = start
            if speed > 0:
                # 0.0 - x avoids -0.0 for the zero component
                normal_x, normal_y = 0.0 - axis_x, 0.0 - axis_y
            else:
                normal_x, normal_y = axis_x, axis_y
        leave = min(leave, end)
        if enter >= leave or enter >= best_fraction or leave <= 0:
            return None

    axes = hit_box1._get_axes() | hit_box2._get_axes()
    for axis_x, axis_y in axes.values():
        projected_1 = [axis_x * px + axis_y * py for px, py in points1]
        projected_2 = [axis_x * px + axis_y * py for px, py in points2]
        speed = dx * axis_x + dy * axis_y
        overlap = _sweep_axis(
            min(projected_1), max(projected_1), min(projected_2), max(projected_2), speed
        )
        if overlap is None:
            return None
        start, end = overlap
        if start > enter:
            enter = start
            length = hypot(axis_x, axis_y)
            if speed > 0:
                normal_x, normal_y = -axis_x / length, -axis_y / length
            else:
                normal_x, normal_y = axis_x / length, axis_y / length
        leave = min(leave, end)
        if enter >= leave or enter >= best_fraction or leave <= 0:
            return None

    return enter, normal_x, normal_y


def sweep_sprite(
    sprite: BasicSprite,
    dx: float,
    dy: float,
    sprite_list: SpriteSequence[SpriteType],
) -> SweepInfo | None:
    """
    Find the first sprite in a list that a sprite would hit while moving.

    :py:func:`check_for_collision` only checks where a sprite is, so a fast
    sprite can move past a thin wall between two frames without ever
    overlapping it. This checks the whole path instead: it imagines
    ``sprite`` moving in a straight line by ``(dx, dy)`` and returns the
    first sprite it would hit, and where. It doesn't move ``sprite``::

        hit = arcade.sweep_sprite(bullet, bullet.change_x, bullet.change_y, walls)
        if hit:
            # Move up to the wall, then remove the bullet
            bullet.position += Vec2(bullet.change_x, bullet.change_y) * hit.fraction
            bullet.remove_from_sprite_lists()
        else:
            bullet.position += Vec2(bullet.change_x, bullet.change_y)

    If ``sprite`` already overlaps a sprite in the list, that is an immediate
    hit, with a :py:attr:`~SweepInfo.fraction` of 0.0. If it overlaps
    several, the deepest overlap is returned.

    As with :py:func:`check_for_collision`, sprites that only touch don't
    count: a sprite can slide along a wall, or move away from one it's
    touching, without hitting it. A move that ends exactly touching a
    sprite doesn't hit it either.

    .. note:: ``sprite`` is assumed to keep the same angle during the move.
              The result is only exact for convex hit boxes.

    If the list has a spatial hash, only sprites near the path are checked.
    Otherwise every sprite in the list is. If two sprites are hit at the
    same moment, either may be returned.

    Args:
        sprite:
            The moving sprite
        dx:
            How far it moves along x
        dy:
            How far it moves along y
        sprite_list:
            The sprites it may hit

    Returns:
        A :py:class:`SweepInfo` for the first sprite hit, or ``None``.
    """
    if __debug__:
        if not isinstance(sprite, BasicSprite):
            raise TypeError(
                f"Parameter 1 is not an instance of the Sprite class, "
                f"it is an instance of {type(sprite)}."
            )
        if not isinstance(sprite_list, SpriteSequence):
            raise TypeError(f"Parameter 4 is a {type(sprite_list)} instead of expected SpriteList.")

    # Everything the sprite passes over is inside this box
    left, right, bottom, top = sprite._hit_box.get_adjusted_bounds()
    path_left = left + min(dx, 0.0)
    path_right = right + max(dx, 0.0)
    path_bottom = bottom + min(dy, 0.0)
    path_top = top + max(dy, 0.0)

    candidates: Iterable[SpriteType]
    if sprite_list.spatial_hash is not None:
        candidates = sprite_list.spatial_hash.get_sprites_near_rect(
            LRBT(path_left, path_right, path_bottom, path_top)
        )
    else:
        candidates = sprite_list

    # Hits must be strictly before this, so a move that ends exactly
    # touching a sprite doesn't hit it
    best_fraction = 1.0
    best: tuple[SpriteType, float, float, float] | None = None
    deepest_start: tuple[SpriteType, CollisionInfo] | None = None
    for other in candidates:
        if other is sprite:
            continue
        # Quick check with a circle around the other sprite's hit box, then
        # its bounding box. The radius is cached until its scale changes.
        other_hit_box = other._hit_box
        radius = other_hit_box._radius
        if radius is None:
            radius = other_hit_box._get_radius()
        other_x, other_y = other._position
        if (
            other_x + radius <= path_left
            or other_x - radius >= path_right
            or other_y + radius <= path_bottom
            or other_y - radius >= path_top
        ):
            continue
        other_left, other_right, other_bottom, other_top = other_hit_box.get_adjusted_bounds()
        if (
            path_right <= other_left
            or other_right <= path_left
            or path_top <= other_bottom
            or other_top <= path_bottom
        ):
            continue

        # Once something overlaps at the start, only other overlaps matter
        limit = 0.0 if deepest_start is not None else best_fraction
        result = _sweep_against(sprite, other, dx, dy, limit)
        if result is None:
            continue
        fraction, normal_x, normal_y = result
        if fraction < 0:
            # Already overlapping at the start. Keep the deepest.
            info = _get_collision_info(sprite, other)
            if info is not None and (deepest_start is None or info.depth > deepest_start[1].depth):
                deepest_start = (other, info)
        elif deepest_start is None:
            best_fraction = fraction
            best = (other, fraction, normal_x, normal_y)

    if deepest_start is not None:
        return SweepInfo(deepest_start[0], 0.0, 0.0, deepest_start[1].normal)
    if best is None:
        return None
    hit_sprite, fraction, normal_x, normal_y = best
    return SweepInfo(hit_sprite, fraction, fraction * hypot(dx, dy), Vec2(normal_x, normal_y))


def check_for_collision_with_lists(
    sprite: BasicSprite,
    sprite_lists: Iterable[SpriteSequence[SpriteType]],
    method: CollisionMethod | int = CollisionMethod.AUTO,
) -> list[SpriteType]:
    """
    Check for a collision between a Sprite, and a list of SpriteLists.

    Each colliding sprite is returned once, even if it's in more than one of
    the lists.

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
    list_count = 0

    for sprite_list in sprite_lists:
        list_count += 1
        for sprite2 in _get_sprites_to_check(sprite, sprite_list, method):
            if sprite is not sprite2 and _check_for_collision(sprite, sprite2):
                sprites.append(sprite2)

    # A sprite can be in more than one of the lists, but is only returned once
    if list_count > 1 and len(sprites) > 1:
        return list(dict.fromkeys(sprites))
    return sprites


def get_sprites_at_point(point: Point, sprite_list: SpriteSequence[SpriteType]) -> list[SpriteType]:
    """
    Get a list of sprites at a particular point. This function sees if any sprite overlaps
    the specified point. If a sprite has a different center_x/center_y but touches the point,
    this will return that sprite.

    A point exactly on the edge of a sprite's hit box counts. Note this is
    different from :py:func:`check_for_collision`, where sprites that only
    touch don't count as colliding.

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
    center_x/center_y but overlaps the rectangle, this will return that sprite.

    As with :py:func:`check_for_collision`, a sprite whose hit box only
    touches the rectangle, sharing an edge or a corner, isn't included.

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
