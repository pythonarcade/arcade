"""
Physics engines for top-down or platformers.
"""

from __future__ import annotations

# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods
import math
from typing import Iterable, Optional, Union

from arcade import (
    Sprite,
    SpriteList,
    SpriteType,
    check_for_collision,
    check_for_collision_with_lists,
)
from arcade.math import get_distance

__all__ = ["PhysicsEngineSimple", "PhysicsEnginePlatformer"]

from arcade.utils import Chain, copy_dunders_unimplemented


def _wiggle_until_free(colliding: Sprite, walls: Iterable[SpriteList]) -> None:
    """Kludge to 'guess' a colliding sprite out of a collision.

    It works by iterating over increasing wiggle sizes of 8 points
    around the ``colliding`` sprite's original center position. Each
    time it fails to find a free position. Although the wiggle distance
    starts at 1, it grows quickly since each failed iteration multiplies
    wiggle distance by two.

    Args:
        colliding:
            A sprite to move out of the given list of SpriteLists.
        walls:
            A list of walls to guess our way out of.
    """

    # Original x & y of the moving object
    o_x, o_y = colliding.position

    # fmt: off
    try_list = [  # Allocate once so we don't recreate or gc
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
    ]

    wiggle_distance = 1
    while True:
        # Cache our variant dimensions
        o_x_plus  = o_x + wiggle_distance
        o_y_plus  = o_y + wiggle_distance
        o_x_minus = o_x - wiggle_distance
        o_y_minus = o_y - wiggle_distance

        # Burst setting of no-gc region is cheaper than nested lists
        try_list[:] = (
            o_x       , o_y_plus ,
            o_x       , o_y_minus,
            o_x_plus  , o_y      ,
            o_x_minus , o_y      ,
            o_x_plus  , o_y_plus ,
            o_x_plus  , o_y_minus,
            o_x_minus , o_y_plus ,
            o_x_minus , o_y_minus
        )
        # fmt: on

        # Iterate and slice the try_list
        for strided_index in range(0, 16, 2):
            x, y = try_list[strided_index:strided_index + 2]
            colliding.position = x, y
            check_hit_list = check_for_collision_with_lists(colliding, walls)
            # print(f"Vary {vary} ({trapped.center_x} {trapped.center_y}) "
            #       f"= {len(check_hit_list)}")
            if len(check_hit_list) == 0:
                return
        wiggle_distance *= 2


def _move_sprite(
        moving_sprite: Sprite,
        can_collide: Iterable[SpriteList[SpriteType]],
        ramp_up: bool
) -> list[SpriteType]:
    """Update a sprite's angle and position, returning a list of collisions.

    The steps covered are:

    #. Rotation
    #. Move in the y direction
    #. Move in the x direction

    Args:
        moving_sprite:
            The sprite to move.
        can_collide:
            An iterable source of SpriteList objects which can be
            collided with.
        ramp_up:
            Whether to enable platformer-like ramp support for x
            direction movement.
    Returns:
        A list of other individual sprites the ``moving_sprite``
        collided with.
    """

    # See if we are starting this turn with a sprite already colliding with us.
    if len(check_for_collision_with_lists(moving_sprite, can_collide)) > 0:
        _wiggle_until_free(moving_sprite, can_collide)

    original_x, original_y = moving_sprite.position
    original_angle = moving_sprite.angle

    # --- Rotate
    rotating_hit_list = []
    if moving_sprite.change_angle:

        # Rotate
        moving_sprite.angle += moving_sprite.change_angle

        # Resolve collisions caused by rotating
        rotating_hit_list = check_for_collision_with_lists(moving_sprite, can_collide)

        if len(rotating_hit_list) > 0:

            max_distance = (moving_sprite.width + moving_sprite.height) / 2

            # Resolve any collisions by this weird kludge
            _wiggle_until_free(moving_sprite, can_collide)
            if (
                get_distance(original_x, original_y, moving_sprite.center_x, moving_sprite.center_y)
                > max_distance
            ):
                # Ok, glitched trying to rotate. Reset.
                moving_sprite.position = original_x, original_y
                moving_sprite.angle = original_angle

    # --- Move in the y direction
    moving_sprite.center_y += moving_sprite.change_y

    # Check for wall hit
    hit_list_x = check_for_collision_with_lists(moving_sprite, can_collide)
    # print(f"Post-y move {hit_list_x}")
    complete_hit_list = hit_list_x

    # If we hit a wall, move so the edges are at the same point
    if len(hit_list_x) > 0:
        if moving_sprite.change_y > 0:
            while len(check_for_collision_with_lists(moving_sprite, can_collide)) > 0:
                moving_sprite.center_y -= 1
            # print(f"Spot X ({self.player_sprite.center_x}, {self.player_sprite.center_y})"
            #       f" {self.player_sprite.change_y}")
        elif moving_sprite.change_y < 0:
            # Reset number of jumps
            for item in hit_list_x:
                while check_for_collision(moving_sprite, item):
                    # self.player_sprite.bottom = item.top <- Doesn't work for ramps
                    moving_sprite.center_y += 0.25

                # NOTE: Not all sprites have velocity
                if getattr(item, "change_x", 0.0) != 0:
                    moving_sprite.center_x += item.change_x  # type: ignore

            # print(f"Spot Y ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
        else:
            pass
            # TODO: The code below can't execute, as "item" doesn't
            # exist. In theory, this condition should never be arrived at.
            # Collision while player wasn't moving, most likely
            # moving platform.
            # if self.player_sprite.center_y >= item.center_y:
            #     self.player_sprite.bottom = item.top
            # else:
            #     self.player_sprite.top = item.bottom
        moving_sprite.change_y = min(0.0, getattr(hit_list_x[0], "change_y", 0.0))

    # print(f"Spot D ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
    moving_sprite.center_y = round(moving_sprite.center_y, 2)
    # print(f"Spot Q ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

    # end_time = time.time()
    # print(f"Move 1 - {end_time - start_time:7.4f}")
    # start_time = time.time()

    loop_count = 0
    # --- Move in the x direction
    if moving_sprite.change_x:
        # Keep track of our current y, used in ramping up
        almost_original_y = moving_sprite.center_y

        # Strip off sign so we only have to write one version of this for
        # both directions
        direction = math.copysign(1, moving_sprite.change_x)
        cur_x_change = abs(moving_sprite.change_x)
        upper_bound = cur_x_change
        lower_bound: float = 0
        cur_y_change: float = 0

        exit_loop = False
        while not exit_loop:

            loop_count += 1
            # print(f"{cur_x_change=}, {upper_bound=}, {lower_bound=}, {loop_count=}")

            # Move sprite and check for collisions
            moving_sprite.center_x = original_x + cur_x_change * direction
            collision_check = check_for_collision_with_lists(moving_sprite, can_collide)

            # Update collision list
            for sprite in collision_check:
                if sprite not in complete_hit_list:
                    complete_hit_list.append(sprite)

            # Did we collide?
            if len(collision_check) > 0:
                # We did collide. Can we ramp up and not collide?
                if ramp_up:
                    cur_y_change = cur_x_change
                    moving_sprite.center_y = original_y + cur_y_change

                    collision_check = check_for_collision_with_lists(moving_sprite, can_collide)
                    if len(collision_check) > 0:
                        cur_y_change -= cur_x_change
                    else:
                        while (len(collision_check) == 0) and cur_y_change > 0:
                            # print("Ramp up check")
                            cur_y_change -= 1
                            moving_sprite.center_y = almost_original_y + cur_y_change
                            collision_check = check_for_collision_with_lists(moving_sprite, can_collide)
                        cur_y_change += 1
                        collision_check = []

                if len(collision_check) > 0:
                    # print(f"Yes @ {cur_x_change}")
                    upper_bound = cur_x_change - 1
                    if upper_bound - lower_bound <= 0:
                        cur_x_change = lower_bound
                        exit_loop = True
                        # print(f"Exit 2 @ {cur_x_change}")
                    else:
                        cur_x_change = (upper_bound + lower_bound) // 2
                else:
                    exit_loop = True
                    # print(f"Exit 1 @ {cur_x_change}")

            else:
                # No collision. Keep this new position and exit
                lower_bound = cur_x_change
                if upper_bound - lower_bound <= 0:
                    # print(f"Exit 3 @ {cur_x_change}")
                    exit_loop = True
                else:
                    # print(f"No @ {cur_x_change}")
                    cur_x_change = (upper_bound + lower_bound) // 2 + (
                        upper_bound + lower_bound
                    ) % 2

        # print(cur_x_change * direction, cur_y_change)
        moved_x = original_x + cur_x_change * direction
        moved_y = almost_original_y + cur_y_change
        moving_sprite.position = moved_x, moved_y
        # print(f"({moving_sprite.center_x}, {moving_sprite.center_y}) {cur_x_change * direction}, {cur_y_change}")

    # Add in rotating hit list
    for sprite in rotating_hit_list:
        if sprite not in complete_hit_list:
            complete_hit_list.append(sprite)

    # end_time = time.time()
    # print(f"Move 2 - {end_time - start_time:7.4f} {loop_count}")

    return complete_hit_list


def _add_to_list(dest: list[SpriteList], source: Optional[SpriteList | Iterable[SpriteList]]) -> None:
    if source is None:
        return
    elif isinstance(source, SpriteList):
        dest.append(source)
    else:
        dest.extend(source)


@copy_dunders_unimplemented
class PhysicsEngineSimple:
    """
    Simplistic physics engine for use in games without gravity, such as top-down
    games. It is easier to get
    started with this engine than more sophisticated engines like PyMunk.

    :param player_sprite: The moving sprite
    :param  Union[SpriteList, Iterable[SpriteList] walls: The sprites it can't move through.
        This can be one or multiple spritelists.
    """

    def __init__(
        self,
        player_sprite: Sprite,
        walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None,
    ) -> None:
        self.player_sprite: Sprite = player_sprite
        self._walls: list[SpriteList] = []

        if walls:
            _add_to_list(self._walls, walls)

    @property
    def walls(self) -> list[SpriteList]:
        return self._walls

    @walls.setter
    def walls(self, walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None) -> None:
        if walls:
            _add_to_list(self._walls, walls)
        else:
            self._walls.clear()

    @walls.deleter
    def walls(self) -> None:
        self._walls.clear()

    def update(self) -> list[SpriteType]:
        """
        Move everything and resolve collisions.

        :Returns: SpriteList with all sprites contacted. Empty list if no sprites.
        """

        return _move_sprite(self.player_sprite, self.walls, ramp_up=False)


@copy_dunders_unimplemented
class PhysicsEnginePlatformer:
    """
    Simplistic physics engine for use in a platformer. It is easier to get
    started with this engine than more sophisticated engines like PyMunk.

    **Note:** Sending static sprites to the ``walls`` parameter and moving sprites to the
    ``platforms`` parameter will have very extreme benefits to performance.

    **Note:** This engine will automatically move any Sprites sent to the ``platforms``
    parameter between a ``boundary_top`` and ``boundary_bottom`` or a ``boundary_left``
    and ``boundary_right`` attribute of the Sprite. You need only set an initial
    ``change_x`` or ``change_y`` on it.

    :param player_sprite: The moving sprite
    :param Optional[Union[SpriteList, Iterable[SpriteList]]] platforms: Sprites the player can't move through.
        This value should only be used for moving Sprites. Static sprites should be sent to the ``walls`` parameter.
    :param gravity_constant: Downward acceleration per frame
    :param Optional[Union[SpriteList, Iterable[SpriteList]]] ladders: Ladders the user can climb on
    :param Optional[Union[SpriteList, Iterable[SpriteList]]] walls: Sprites the player can't move through.
        This value should only be used for static Sprites. Moving sprites should be sent to the ``platforms`` parameter.
    """

    def __init__(
        self,
        player_sprite: Sprite,
        platforms: Optional[Union[SpriteList, Iterable[SpriteList]]] = None,
        gravity_constant: float = 0.5,
        ladders: Optional[Union[SpriteList, Iterable[SpriteList]]] = None,
        walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None,
    ) -> None:

        self._ladders: list[SpriteList] = []
        self._platforms: list[SpriteList] = []
        self._walls: list[SpriteList] = []
        self._all_obstacles = Chain(self._walls, self._platforms)

        _add_to_list(self._ladders, ladders)
        _add_to_list(self._platforms, platforms)
        _add_to_list(self._walls, walls)

        self.player_sprite: Sprite = player_sprite
        self.gravity_constant: float = gravity_constant
        self.jumps_since_ground: int = 0
        self.allowed_jumps: int = 1
        self.allow_multi_jump: bool = False

    # The property object for ladders. This allows us setter/getter/deleter capabilities in safe manner
    @property
    def ladders(self) -> list[SpriteList]:
        """The ladder list registered with the physics engine."""
        return self._ladders

    @ladders.setter
    def ladders(self, ladders: Optional[Union[SpriteList, Iterable[SpriteList]]] = None) -> None:
        if ladders:
            _add_to_list(self._ladders, ladders)
        else:
            self._ladders.clear()

    @ladders.deleter
    def ladders(self) -> None:
        self._ladders.clear()

    @property
    def platforms(self) -> list[SpriteList]:
        """Controls which sprites are used as moving platforms.

        .. tip:: For best performance, put non-moving terrain in
                 :py:attr:`.walls` instead.

        This is a :py:class:`list` of
        :py:class:`~arcade.sprite_list.sprite_list.SpriteList` instances.

        Motion is controlled by the presence of the following
        attribute pairs on a :py:class:`~arcade.sprite.sprite.Sprite`:

        * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_left` and
          :py:attr:`~arcade.sprite.sprite.Sprite.boundary_right`
        * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_bottom` and
          :py:attr:`~arcade.sprite.sprite.Sprite.boundary_top`

        * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_left` and
          :py:attr:`~arcade.sprite.sprite.Sprite.boundary_right`
        * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_bottom` and
          :py:attr:`~arcade.sprite.sprite.Sprite.boundary_top`

        """
        return self._platforms

    @platforms.setter
    def platforms(self, platforms: Optional[Union[SpriteList, Iterable[SpriteList]]] = None) -> None:
        if platforms:
            _add_to_list(self._platforms, platforms)
        else:
            self._platforms.clear()

    @platforms.deleter
    def platforms(self) -> None:
        self._platforms.clear()

    @property
    def walls(self):
        """The wall list registered with the physics engine."""
        return self._walls

    @walls.setter
    def walls(self, walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None) -> None:
        if walls:
            _add_to_list(self._walls, walls)
        else:
            self._walls.clear()

    @walls.deleter
    def walls(self) -> None:
        self._walls.clear()

    def is_on_ladder(self) -> bool:
        """Check if the :py:attr:`.player` touches any :py:attr:`.ladders`.

        .. warning:: This runs collisions **every** time it is called!

        Returns:
            ``True`` if the :py:attr:`.player` sprite overlaps any
             :py:class:`Sprite` in :py:attr:`.ladders`.
        """
        if self.ladders:
            hit_list = check_for_collision_with_lists(self.player_sprite, self.ladders)
            if len(hit_list) > 0:
                return True
        return False

    def can_jump(self, y_distance: float = 5) -> bool:
        """Update jump state and return ``True`` if the player can jump.

        .. warning:: This runs collisions **every** time it is called!

        The player can jump when at least one of the following are true:

        .. list-table::
           :header-rows: 0

           * - The player is "touching" the ground
             - :py:attr:`.player`'s :py:attr:`~arcade.BasicSprite.center_y`
               is within ``y_distance`` of any sprite in :py:attr:`.walls`
               or :py:attr:`.platforms`
           * - The player can air-jump
             - :py:attr:`.allow_multi_jump` is ``True`` and the player
               hasn't jumped more than :py:attr:`.allowed_jumps` times

        Args:
            y_distance: The distance to temporarily move the
            :py:attr:`.player` downward before checking for a collision
            with either :py:attr:`.walls` or :py:attr:`.platforms`.


        Returns:
             ``True`` if the player can jump.

        """

        # Temporarily move the player down to collide floor-like sprites
        self.player_sprite.center_y -= y_distance
        hit_list = check_for_collision_with_lists(self.player_sprite, self._all_obstacles)
        self.player_sprite.center_y += y_distance

        # Reset the number jumps if the player touched a floor-like sprite
        if len(hit_list) > 0:
            self.jumps_since_ground = 0

        if (
            len(hit_list) > 0
            or self.allow_multi_jump
            and self.jumps_since_ground < self.allowed_jumps
        ):
            return True
        else:
            return False

    def enable_multi_jump(self, allowed_jumps: int) -> None:
        """
        Enables multi-jump.
        allowed_jumps should include the initial jump.
        (1 allows only a single jump, 2 enables double-jump, etc)

        If you enable multi-jump, you MUST call increment_jump_counter()
        every time the player jumps. Otherwise they can jump infinitely.

        :param allowed_jumps:
        """
        self.allowed_jumps = allowed_jumps
        self.allow_multi_jump = True

    def disable_multi_jump(self) -> None:
        """
        Disables multi-jump.

        Calling this function also removes the requirement to
        call increment_jump_counter() every time the player jumps.
        """
        self.allow_multi_jump = False
        self.allowed_jumps = 1
        self.jumps_since_ground = 0

    def jump(self, velocity: int):
        """Have the character jump."""
        self.player_sprite.change_y = velocity
        self.increment_jump_counter()

    def increment_jump_counter(self) -> None:
        """
        Updates the jump counter for multi-jump tracking
        """
        if self.allow_multi_jump:
            self.jumps_since_ground += 1

    def update(self):
        """
        Move everything and resolve collisions.

        :Returns: SpriteList with all sprites contacted. Empty list if no sprites.
        """
        # start_time = time.time()
        # print(f"Spot A ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

        # --- Add gravity if we aren't on a ladder
        if not self.is_on_ladder():
            self.player_sprite.change_y -= self.gravity_constant

            # print(f"Spot F ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

        # print(f"Spot B ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

        for platform_list in self.platforms:
            for platform in platform_list:
                if platform.change_x != 0 or platform.change_y != 0:

                    # Check x boundaries and move the platform in x direction
                    if platform.boundary_left and platform.left <= platform.boundary_left:
                        platform.left = platform.boundary_left
                        if platform.change_x < 0:
                            platform.change_x *= -1

                    if platform.boundary_right and platform.right >= platform.boundary_right:
                        platform.right = platform.boundary_right
                        if platform.change_x > 0:
                            platform.change_x *= -1

                    platform.center_x += platform.change_x

                    # Check y boundaries and move the platform in y direction
                    if platform.boundary_top is not None and platform.top >= platform.boundary_top:
                        platform.top = platform.boundary_top
                        if platform.change_y > 0:
                            platform.change_y *= -1

                    if (
                        platform.boundary_bottom is not None
                        and platform.bottom <= platform.boundary_bottom
                    ):
                        platform.bottom = platform.boundary_bottom
                        if platform.change_y < 0:
                            platform.change_y *= -1

                    platform.center_y += platform.change_y

        complete_hit_list = _move_sprite(self.player_sprite, self._all_obstacles, ramp_up=True)

        # print(f"Spot Z ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
        # Return list of encountered sprites
        # end_time = time.time()
        # print(f"Update - {end_time - start_time:7.4f}\n")

        return complete_hit_list
