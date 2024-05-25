"""
Physics engines for top-down or platformers.
"""
from __future__ import annotations

# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods
import math
from typing import Iterable, List, Optional, Union

from arcade import (
    Sprite,
    SpriteList,
    SpriteType,
    check_for_collision,
    check_for_collision_with_lists
)
from arcade.math import get_distance

__all__ = [
    "PhysicsEngineSimple",
    "PhysicsEnginePlatformer"
]

from arcade.utils import copy_dunders_unimplemented


def _circular_check(player: Sprite, walls: List[SpriteList]):
    """
    This is a horrible kludge to 'guess' our way out of a collision
    Returns:

    """
    original_x = player.center_x
    original_y = player.center_y

    vary = 1
    while True:
        try_list = [[original_x, original_y + vary],
                    [original_x, original_y - vary],
                    [original_x + vary, original_y],
                    [original_x - vary, original_y],
                    [original_x + vary, original_y + vary],
                    [original_x + vary, original_y - vary],
                    [original_x - vary, original_y + vary],
                    [original_x - vary, original_y - vary]
                    ]

        for my_item in try_list:
            x, y = my_item
            player.center_x = x
            player.center_y = y
            check_hit_list = check_for_collision_with_lists(player, walls)
            # print(f"Vary {vary} ({self.player_sprite.center_x} {self.player_sprite.center_y}) "
            #       f"= {len(check_hit_list)}")
            if len(check_hit_list) == 0:
                return
        vary *= 2


def _move_sprite(moving_sprite: Sprite, walls: List[SpriteList[SpriteType]], ramp_up: bool) -> List[SpriteType]:

    # See if we are starting this turn with a sprite already colliding with us.
    if len(check_for_collision_with_lists(moving_sprite, walls)) > 0:
        _circular_check(moving_sprite, walls)

    original_x = moving_sprite.center_x
    original_y = moving_sprite.center_y
    original_angle = moving_sprite.angle

    # --- Rotate
    rotating_hit_list = []
    if moving_sprite.change_angle:

        # Rotate
        moving_sprite.angle += moving_sprite.change_angle

        # Resolve collisions caused by rotating
        rotating_hit_list = check_for_collision_with_lists(moving_sprite, walls)

        if len(rotating_hit_list) > 0:

            max_distance = (moving_sprite.width + moving_sprite.height) / 2

            # Resolve any collisions by this weird kludge
            _circular_check(moving_sprite, walls)
            if get_distance(original_x, original_y, moving_sprite.center_x, moving_sprite.center_y) > max_distance:
                # Ok, glitched trying to rotate. Reset.
                moving_sprite.center_x = original_x
                moving_sprite.center_y = original_y
                moving_sprite.angle = original_angle

    # --- Move in the y direction
    moving_sprite.center_y += moving_sprite.change_y

    # Check for wall hit
    hit_list_x = check_for_collision_with_lists(moving_sprite, walls)
    # print(f"Post-y move {hit_list_x}")
    complete_hit_list = hit_list_x

    # If we hit a wall, move so the edges are at the same point
    if len(hit_list_x) > 0:
        if moving_sprite.change_y > 0:
            while len(check_for_collision_with_lists(moving_sprite, walls)) > 0:
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
        moving_sprite.change_y = min(0.0, getattr(hit_list_x[0], 'change_y', 0.0))

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
            collision_check = check_for_collision_with_lists(moving_sprite, walls)

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

                    collision_check = check_for_collision_with_lists(moving_sprite, walls)
                    if len(collision_check) > 0:
                        cur_y_change -= cur_x_change
                    else:
                        while (len(collision_check) == 0) and cur_y_change > 0:
                            # print("Ramp up check")
                            cur_y_change -= 1
                            moving_sprite.center_y = almost_original_y + cur_y_change
                            collision_check = check_for_collision_with_lists(moving_sprite, walls)
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
                    cur_x_change = (upper_bound + lower_bound) // 2 + (upper_bound + lower_bound) % 2

        # print(cur_x_change * direction, cur_y_change)
        moving_sprite.center_x = original_x + cur_x_change * direction
        moving_sprite.center_y = almost_original_y + cur_y_change
        # print(f"({moving_sprite.center_x}, {moving_sprite.center_y}) {cur_x_change * direction}, {cur_y_change}")

    # Add in rotating hit list
    for sprite in rotating_hit_list:
        if sprite not in complete_hit_list:
            complete_hit_list.append(sprite)

    # end_time = time.time()
    # print(f"Move 2 - {end_time - start_time:7.4f} {loop_count}")

    return complete_hit_list


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

    def __init__(self, player_sprite: Sprite, walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None):
        self.player_sprite: Sprite = player_sprite
        self._walls: List[SpriteList]

        if walls:
            self._walls = [walls] if isinstance(walls, SpriteList) else list(walls)
        else:
            self._walls = []

    @property
    def walls(self):
        return self._walls

    @walls.setter
    def walls(self, walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None):
        if walls:
            self._walls = [walls] if isinstance(walls, SpriteList) else list(walls)
        else:
            self._walls = []

    @walls.deleter
    def walls(self):
        self._walls = []

    def update(self):
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

    def __init__(self,
                 player_sprite: Sprite,
                 platforms: Optional[Union[SpriteList, Iterable[SpriteList]]] = None,
                 gravity_constant: float = 0.5,
                 ladders: Optional[Union[SpriteList, Iterable[SpriteList]]] = None,
                 walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None,
                 ):
        self._ladders: Optional[List[SpriteList]]
        self._platforms: List[SpriteList]
        self._walls: List[SpriteList]

        if ladders:
            self._ladders = [ladders] if isinstance(ladders, SpriteList) else list(ladders)
        else:
            self._ladders = []

        if platforms:
            self._platforms = [platforms] if isinstance(platforms, SpriteList) else list(platforms)
        else:
            self._platforms = []

        if walls:
            self._walls = [walls] if isinstance(walls, SpriteList) else list(walls)
        else:
            self._walls = []

        self.player_sprite: Sprite = player_sprite
        self.gravity_constant: float = gravity_constant
        self.jumps_since_ground: int = 0
        self.allowed_jumps: int = 1
        self.jump_delay: int = 0
        self.jump_ticks: int = 0
        self.allow_multi_jump: bool = False

    # The property object for ladders. This allows us setter/getter/deleter capabilities in safe manner
    @property
    def ladders(self):
        """ The ladder list registered with the physics engine."""
        return self._ladders

    @ladders.setter
    def ladders(self, ladders: Optional[Union[SpriteList, Iterable[SpriteList]]] = None):
        if ladders:
            self._ladders = [ladders] if isinstance(ladders, SpriteList) else list(ladders)
        else:
            self._ladders = []

    @ladders.deleter
    def ladders(self):
        self._ladders = []

    @property
    def platforms(self):
        """ The moving platform list registered with the physics engine."""
        return self._platforms

    @platforms.setter
    def platforms(self, platforms: Optional[Union[SpriteList, Iterable[SpriteList]]] = None):
        if platforms:
            self._platforms = [platforms] if isinstance(platforms, SpriteList) else list(platforms)
        else:
            self._platforms = []

    @platforms.deleter
    def platforms(self):
        self._platforms = []

    @property
    def walls(self):
        """ The wall list registered with the physics engine."""
        return self._walls

    @walls.setter
    def walls(self, walls: Optional[Union[SpriteList, Iterable[SpriteList]]] = None):
        if walls:
            self._walls = [walls] if isinstance(walls, SpriteList) else list(walls)
        else:
            self._walls = []

    @walls.deleter
    def walls(self):
        self._walls = []

    def is_on_ladder(self):
        """ Return 'true' if the player is in contact with a sprite in the ladder list. """
        # Check for touching a ladder
        if self.ladders:
            hit_list = check_for_collision_with_lists(self.player_sprite, self.ladders)
            if len(hit_list) > 0 and self.jump_ticks >= self.jump_delay:
                self.jumps_since_ground = 0
                return True
        return False

    def is_on_ground(self, y_distance: float = 5) -> bool:
        """
        Method that looks to see if there is a floor under
        the player_sprite. If there is a floor, we return a True.

        :returns: True if there is a platform below us.
        """

        # Move down to see if we are on a platform
        self.player_sprite.center_y -= y_distance

        # Check for wall hit
        hit_list = check_for_collision_with_lists(self.player_sprite, self.walls + self.platforms)

        self.player_sprite.center_y += y_distance

        if len(hit_list) > 0:
            self.jumps_since_ground = 0
            return True
        else:
            return False

    def can_jump(self, y_distance: float = 5) -> bool:
        """
        Method that looks to see if there is a floor under
        the player_sprite. If there is a floor, the player can jump
        and we return a True.

        :returns: True if there is a platform below us
        """

        if (self.is_on_ground(y_distance) or self.allow_multi_jump and self.jumps_since_ground < self.allowed_jumps and
                self.jump_ticks >= self.jump_delay):
            return True
        else:
            return False

    def enable_multi_jump(self, allowed_jumps: int, jump_delay: int = 0):
        """
        Enables multi-jump.
        allowed_jumps should include the initial jump.
        (1 allows only a single jump, 2 enables double-jump, etc)

        If you enable multi-jump, you MUST call increment_jump_counter()
        every time the player jumps. Otherwise, they can jump infinitely.

        :param allowed_jumps: Maximum number of jumps allowed
        :param jump_delay: Number of ticks before another jump is allowed
        """
        self.allowed_jumps = allowed_jumps
        self.jump_delay = jump_delay
        self.jump_ticks = jump_delay
        self.allow_multi_jump = True

    def disable_multi_jump(self):
        """
        Disables multi-jump.

        Calling this function also removes the requirement to
        call increment_jump_counter() every time the player jumps.
        """
        self.allow_multi_jump = False
        self.allowed_jumps = 1
        self.jumps_since_ground = 0

    def jump(self, velocity: int,
             air_jump_velocity: Optional[int] = None,
             air_jump_style: Optional[str] = "set",
             jump_velocity_limit: Optional[int] = None):
        """ Have the character jump. Multijump can be set with a separate in-air velocity and air jumps can be
        set to be additive, limited, or a set value. Additive only adds to the player's change_y velocity. Limited
        will add to the players' change_y until the jump_velocity limit. Set always sets the players velocity
        to their air jump speed. """
        if self.can_jump():
            # Air Jump logic
            if self.jumps_since_ground > 0:
                # This checks if air_jump_velocity is set. If not it will default to the velocity for all air jumps.
                if air_jump_velocity:
                    air_jump = air_jump_velocity
                else:
                    air_jump = velocity
                if air_jump_style == "additive":
                    self.player_sprite.change_y += air_jump
                elif air_jump_style == "limited":
                    if not jump_velocity_limit:
                        jump_velocity_limit = air_jump
                    if self.player_sprite.change_y < 0:
                        self.player_sprite.change_y = air_jump
                    elif self.player_sprite.change_y + air_jump < jump_velocity_limit:
                        self.player_sprite.change_y += air_jump
                    else:
                        self.player_sprite.change_y = jump_velocity_limit
                elif air_jump_style == "set":
                    self.player_sprite.change_y = air_jump
                else:
                    raise ValueError("Air jump style set is not valid. Use additive, limited, or set.")

            # Ground Jump Logic
            else:
                self.player_sprite.change_y = velocity

            self.increment_jump_counter()

    def increment_jump_counter(self):
        """
        Updates the jump counter for multi-jump tracking
        """
        if self.allow_multi_jump:
            self.jumps_since_ground += 1
            self.jump_ticks = 0

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
        if self.allow_multi_jump:
            if self.jump_ticks < self.jump_delay:
                self.jump_ticks += 1

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
                    if platform.boundary_top is not None \
                            and platform.top >= platform.boundary_top:
                        platform.top = platform.boundary_top
                        if platform.change_y > 0:
                            platform.change_y *= -1

                    if platform.boundary_bottom is not None \
                            and platform.bottom <= platform.boundary_bottom:
                        platform.bottom = platform.boundary_bottom
                        if platform.change_y < 0:
                            platform.change_y *= -1

                    platform.center_y += platform.change_y

        complete_hit_list = _move_sprite(self.player_sprite, self.walls + self.platforms, ramp_up=True)

        # print(f"Spot Z ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
        # Return list of encountered sprites
        # end_time = time.time()
        # print(f"Update - {end_time - start_time:7.4f}\n")

        return complete_hit_list
