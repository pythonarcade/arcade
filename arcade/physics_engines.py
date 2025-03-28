"""
Physics engines for top-down or platformers.
"""

import math
from typing import Iterable

from arcade import (
    BasicSprite,
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
    moving_sprite: Sprite, can_collide: Iterable[SpriteList[SpriteType]], ramp_up: bool
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
                            collision_check = check_for_collision_with_lists(
                                moving_sprite, can_collide
                            )
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
        # print(
        #     f"({moving_sprite.center_x}, {moving_sprite.center_y}) "
        #     f"{cur_x_change * direction}, {cur_y_change}"
        # )

    # Add in rotating hit list
    for sprite in rotating_hit_list:
        if sprite not in complete_hit_list:
            complete_hit_list.append(sprite)

    # end_time = time.time()
    # print(f"Move 2 - {end_time - start_time:7.4f} {loop_count}")

    return complete_hit_list


def _add_to_list(dest: list[SpriteList], source: SpriteList | Iterable[SpriteList] | None) -> None:
    """Helper function to add a SpriteList or list of SpriteLists to a list."""
    if not source:
        return
    elif isinstance(source, SpriteList):
        dest.append(source)
    else:
        dest.extend(source)


@copy_dunders_unimplemented
class PhysicsEngineSimple:
    """A basic physics engine best for single-player top-down games.

    This is the easiest engine to get started with. It's best when:

    * You need a top-down view
    * You need to collide with non-moving terrain
    * You don't need anything else

    For side-scrolling games focused on jumping puzzles, you may want
    the :py:class:`PhysicsEnginePlatformer` instead. Experienced users
    may want to try the
    :py:class:`~arcade.pymunk_physics_engine.PymunkPhysicsEngine`.

    Args:
        player_sprite:
            A sprite which will be controlled by the player.

        walls:
            A :py:class:`.SpriteList` or :py:class:`list` of them which
            should stop player movement.
    """

    def __init__(
        self,
        player_sprite: Sprite,
        walls: SpriteList | Iterable[SpriteList] | None = None,
    ) -> None:
        self.player_sprite: Sprite = player_sprite
        """The player-controlled :py:class:`.Sprite`."""
        self._walls: list[SpriteList] = []

        if walls:
            _add_to_list(self._walls, walls)

    @property
    def walls(self) -> list[SpriteList]:
        """Which :py:class:`.SpriteList` instances block player movement.

        .. important:: Avoid moving sprites in these lists!

                       Doing so incurs performance costs.

        See :py:class:`PhysicsEnginePlatformer.walls` for further information.
        For platformer physics such as moving platforms and gravity, consider
        using the :py:class:`PhysicsEnginePlatformer`.
        """
        return self._walls

    @walls.setter
    def walls(self, walls: SpriteList | Iterable[SpriteList] | None = None) -> None:
        if walls:
            _add_to_list(self._walls, walls)
        else:
            self._walls.clear()

    @walls.deleter
    def walls(self) -> None:
        self._walls.clear()

    def update(self) -> list[BasicSprite]:
        """Move :py:attr:`player_sprite` and return any colliding sprites.

        Returns:
            A :py:class:`list` of the colliding sprites. If there were
            zero collisions, it will be empty.
        """

        return _move_sprite(self.player_sprite, self.walls, ramp_up=False)


@copy_dunders_unimplemented
class PhysicsEnginePlatformer:
    """A single-player engine with gravity and moving platform support.

    .. _Super Mario Bros.: https://en.wikipedia.org/wiki/Super_Mario_Bros.
    .. _Rayman: https://en.wikipedia.org/wiki/Rayman_(video_game)

    This engine is best for simple versions of platformer games like
    the `Super Mario Bros.`_ (the first Mario game) and `Rayman`_. It
    is more important to pay attention to the performance tips with
    this engine than with  :py:class:`PhysicsEngineSimple`.

    .. important:: For best performance, you must put your sprites
                   in the right group!

    Be sure to add each :py:class:`.Sprite` and :py:class:`.SpriteList`
    to the right group, regardless of whether you do so via arguments
    or properties:

    .. list-table::
       :header-rows: 1

       * - Creation argument
         - Purpose
         - :py:class:`list` property

       * - ``walls``
         - Non-moving sprites the player can stand on.
         - :py:attr:`walls`

       * - ``platforms``
         - Sprites the player can stand on, but which can still move.
         - :py:attr:`platforms`

       * - ``ladders``
         - Ladders which allow gravity-free movement while touched by
           the :py:attr:`player_sprite`.
         - :py:attr:`ladders`

    To learn about the automatic moving platform feature, please see
    :py:attr:`platforms`.

    Not that if you use the :py:class:`list` properties above, you can
    add or remove :py:attr:`platforms` in response to game events. It
    is also possible to add new sprites such as terrain in response to
    gameplay events, but there may be performance implications due to
    the way :py:class:`SpriteList` handles spatial hashing. To learn
    more, see :py:attr:`walls`.

    Args:
        player_sprite:
            The player character's sprite. It will be stored on the engine
            as :py:attr:`player_sprite`.
        platforms:
            The initial list of :py:attr:`platforms`, sprites which can move
            freely.
        gravity_constant:
            A constant to subtract from the :py:attr:`player_sprite`'s
            velocity (:py:attr:`.Sprite.change_y`) each :py:meth:`update`
            when in the air. See :py:attr:`gravity_constant` to learn
            more.
        ladders:
            :py:class:`.Sprite` instances the player can climb without
            being affected by gravity.
        walls:
            :py:class:`Sprite` instances which are static and never move.
            **Do not put moving sprites into this!** See :py:attr:`walls`
            to learn more.

    """

    def __init__(
        self,
        player_sprite: Sprite,
        platforms: SpriteList | Iterable[SpriteList] | None = None,
        gravity_constant: float = 0.5,
        ladders: SpriteList | Iterable[SpriteList] | None = None,
        walls: SpriteList | Iterable[SpriteList] | None = None,
    ) -> None:
        if not isinstance(player_sprite, Sprite):
            raise TypeError("player_sprite must be a Sprite, not a basic_sprite!")

        self._ladders: list[SpriteList] = []
        self._platforms: list[SpriteList] = []
        self._walls: list[SpriteList] = []
        self._all_obstacles = Chain(self._walls, self._platforms)

        _add_to_list(self._ladders, ladders)
        _add_to_list(self._platforms, platforms)
        _add_to_list(self._walls, walls)

        self.player_sprite: Sprite = player_sprite
        """ The sprite controlled by the player.

        .. important:: This **must** be a :py:class:`.Sprite` or a
                       subclass of it!

        You can't use :py:class:`.BasicSprite` since it lacks
        required :py:attr:`~.Sprite.change_y` property.
        """
        self.gravity_constant: float = gravity_constant
        """The player's default downward acceleration.

        The engine's :py:meth:`update` method subtracts this value
        from the :py:attr:`player_sprite`'s :py:attr:`~.Sprite.change_y`
        when the player is not touching a sprite in :py:attr:`ladders` or
        :py:attr:`walls`.

        You can change the value of gravity after engine creation through
        this attribute. In addition to responding to GUI events, you can
        also change gravity in response to game events such as touching
        power-ups.

        Values for ``gravity_constant`` work as follows:

        .. list-table::
           :header-rows: 1

           * - ``gravity_constant``
             - Effect
           * - Greater than zero
             - Gravity points downward as expected
           * - Less than zero
             - Player falls upward (Consider adding a ceiling)
           * - Zero
             - No gravity

        To learn more, please see the following parts of the
        :ref:`platformer_tutorial`:

        * :ref:`platformer_part_five`
        * :ref:`platformer_part_twelve`
        """
        self.jumps_since_ground: int = 0
        """How many times the player has jumped since touching a
        sprite in :py:attr:`walls`.

        This is used throughout the engine's logic, including
        the :py:meth:`jump` and :py:meth:`can_jump` methods.
        """
        self.allowed_jumps: int = 1
        """Total number of jumps the player should be capable of.

        This includes the first jump. To enable multi-jump, see
        :py:meth:`enable_multi_jump` instead.
        """

        self.allow_multi_jump: bool = False
        """Whether multi-jump is enabled.

        For ease of use in simple games, you may want to use the
        following methods instead of setting this directly:

        * :py:meth:`enable_multi_jump`
        * :py:meth:`disable_multi_jump`
        """

    # The property object for ladders. This allows us setter/getter/deleter
    # capabilities in safe manner
    # TODO: figure out what do do with 15_ladders_moving_platforms.py
    # It's no longer used by any example or tutorial file
    @property
    def ladders(self) -> list[SpriteList]:
        """Ladders turn off gravity while touched by the player.

        This means that whenever the :py:attr:`player_sprite` collides
        with any any :py:class:`.Sprite` or :py:class:`.BasicSprite` in this
        list, the following are true:

        * The :py:attr:`gravity_constant` is not subtracted from
          :py:attr:`player_sprite`\'s :py:attr:`~.Sprite.change_y`
          during :py:meth:`update` calls
        * The player may otherwise move as freely as you allow

        """
        return self._ladders

    @ladders.setter
    def ladders(self, ladders: SpriteList | Iterable[SpriteList] | None = None) -> None:
        if ladders:
            _add_to_list(self._ladders, ladders)
        else:
            self._ladders.clear()

    @ladders.deleter
    def ladders(self) -> None:
        self._ladders.clear()

    @property
    def platforms(self) -> list[SpriteList]:
        """:py:class:`~arcade.sprite_list.sprite_list.SpriteList` instances containing platforms.

        .. important:: For best performance, put non-moving terrain in
                       :py:attr:`.walls` instead.

        Platforms are intended to support automatic movement by setting
        the appropriate attributes.

        You can enable automatic motion by setting one of the following
        attribute pairs on a :py:class:`~arcade.sprite.sprite.Sprite`:

        .. list-table::
           :header-rows: 1

           * - Movement Axis
             - :py:class:`~arcade.sprite.sprite.Sprite` Attributes to Set
           * - X (side to side)
             - * :py:attr:`~arcade.sprite.sprite.Sprite.change_x`
               * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_left`
               * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_right`
           * - Y (up and down)
             - * :py:attr:`~arcade.sprite.sprite.Sprite.change_y`
               * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_bottom`
               * :py:attr:`~arcade.sprite.sprite.Sprite.boundary_top`

        For a working example, please see :ref:`sprite_moving_platforms`.
        """
        return self._platforms

    @platforms.setter
    def platforms(self, platforms: SpriteList | Iterable[SpriteList] | None = None) -> None:
        if platforms:
            _add_to_list(self._platforms, platforms)
        else:
            self._platforms.clear()

    @platforms.deleter
    def platforms(self) -> None:
        self._platforms.clear()

    @property
    def walls(self) -> list[SpriteList]:
        """Exposes the :py:class:`SpriteList` instances use as terrain.

        .. important:: For best performance, only add non-moving sprites!

        The walls lists make a tradeoff through **spatial hashing**:

        * Collision checking against sprites in the list becomes
          very fast
        * Moving sprites or adding new ones becomes very slow

        This is worth the tradeoff for non-moving terrain, but it means
        you have to be careful. If you move too many sprites in the walls
        lists every frame, your game may slow down. For moving sprites
        the player can stand and jump on, see the :py:attr:`platforms`
        feature.

        To learn more about spatial hashing, please see the following:

        * :ref:`collision_detection_performance`
        * :py:class:`~arcade.sprite_list.spatial_hash.SpatialHash`
        """
        return self._walls

    @walls.setter
    def walls(self, walls: SpriteList | Iterable[SpriteList] | None = None) -> None:
        if walls:
            _add_to_list(self._walls, walls)
        else:
            self._walls.clear()

    @walls.deleter
    def walls(self) -> None:
        self._walls.clear()

    def is_on_ladder(self) -> bool:
        """Check if the :py:attr:`player_sprite` touches any :py:attr:`ladders`.

        .. warning:: This runs collisions **every** time it is called!

        Returns:
            ``True`` if the :py:attr:`player_sprite` touches any
            :py:attr:`ladders`.
        """
        if self.ladders:
            hit_list = check_for_collision_with_lists(self.player_sprite, self.ladders)
            if len(hit_list) > 0:
                return True
        return False

    def can_jump(self, y_distance: float = 5) -> bool:
        """Update jump state and return ``True`` if the player can jump.

        .. warning:: This runs collisions **every** time it is called!

        If you are thinking of calling this repeatedly, first double-check
        whether you can store the returned value to a local variable instead.

        The player can jump when at least one of the following are true:
        after updating state:

        .. list-table::
           :header-rows: 0

           * - The player is "touching" the ground
             - :py:attr:`player_sprite`\'s :py:attr:`.BasicSprite.center_y`
               is within ``y_distance`` of any sprite in :py:attr:`walls`
               or :py:attr:`platforms`

           * - The player can air-jump
             - :py:attr:`allow_multi_jump` is ``True`` and the player
               hasn't jumped more than :py:attr:`allowed_jumps` times

        Args:
            y_distance:
                The distance to temporarily move the :py:attr:`player_sprite`
                downward before checking for a collision with either
                :py:attr:`walls` or :py:attr:`platforms`.

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
        """Enable multi-jump.

        The ``allowed_jumps`` argument is the total number of jumps
        the player should be able to make, including the first from
        solid ground in :py:attr:`walls` or any :py:attr:`platforms`.
        It will be stored as :py:attr:`allowed_jumps`.

        .. important:: If you override :py:meth:`jump`, be sure to call
                       :py:meth:`increment_jump_counter` inside it!

                       Otherwise, the player may be able to jump forever.

        Args:
            allowed_jumps:
                Total number of jumps the player should be capable of,
                including the first.

        """
        self.allowed_jumps = allowed_jumps
        self.allow_multi_jump = True

    def disable_multi_jump(self) -> None:
        """Disable multi-jump.

        Calling this function removes the requirement for :py:meth:`jump`
        to call :py:meth:`increment_jump_counter` with each jump to
        prevent infinite jumping.
        """
        self.allow_multi_jump = False
        self.allowed_jumps = 1
        self.jumps_since_ground = 0

    def jump(self, velocity: float) -> None:
        """Jump with an initial upward velocity.

        This works as follows:

        #. Set the :py:attr:`player_sprite`\'s :py:attr:`~.Sprite.change_y`
           to the passed ``velocity``
        #. Call :py:meth:`increment_jump_counter`

        Args:
            velocity:
                A positive value to set the player's y velocity to.
        """
        self.player_sprite.change_y = velocity
        self.increment_jump_counter()

    def increment_jump_counter(self) -> None:
        """Update jump tracking if multi-jump is enabled.

        If :py:attr:`allow_multi_jumps` is ``True``, calling this adds
        ``1`` to :py:attr:`jumps_since_ground`. Otherwise, it does
        nothing.
        """
        if self.allow_multi_jump:
            self.jumps_since_ground += 1

    def update(self) -> list[BasicSprite]:
        """Move the player and platforms, then return colliding sprites.

        The returned sprites will in a :py:class:`list` of individual
        sprites taken from all :py:class:`arcade.SpriteList` instances
        in the following:

        * :attr:`~platforms`
        * :attr:`~walls`

        The :py:attr:`~ladders` are not included.

        Returns:
            A list of all sprites the player collided with. If there
            were no collisions, the list will be empty.
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
