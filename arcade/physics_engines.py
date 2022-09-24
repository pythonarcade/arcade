"""
Physics engines for top-down or platformers.
"""
# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods

import math
from typing import Iterable, List, Optional, Union

from arcade import (Sprite, SpriteList, check_for_collision,
                    check_for_collision_with_lists, get_distance)


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


def _move_sprite(moving_sprite: Sprite, walls: List[SpriteList], ramp_up: bool) -> List[Sprite]:

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

                if item.change_x != 0:
                    moving_sprite.center_x += item.change_x

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
        moving_sprite.change_y = min(0.0, hit_list_x[0].change_y)

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
                        while len(collision_check) == 0 and cur_y_change > 0:
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


class PhysicsEngineSimple:
    """
    Simplistic physics engine for use in games without gravity, such as top-down
    games. It is easier to get
    started with this engine than more sophisticated engines like PyMunk.

    :param Sprite player_sprite: The moving sprite
    :param  Union[SpriteList, Iterable[SpriteList] walls: The sprites it can't move through.
        This can be one or multiple spritelists.
    """

    def __init__(self, player_sprite: Sprite, walls: Union[SpriteList, Iterable[SpriteList]]):
        """
        Create a simple physics engine.
        """
        assert isinstance(player_sprite, Sprite)

        if walls:
            if isinstance(walls, SpriteList):
                self.walls = [walls]
            else:
                self.walls = list(walls)
        else:
            self.walls = []

        self.player_sprite = player_sprite

    def update(self):
        """
        Move everything and resolve collisions.

        :Returns: SpriteList with all sprites contacted. Empty list if no sprites.
        """

        return _move_sprite(self.player_sprite, self.walls, ramp_up=False)


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

    :param Sprite player_sprite: The moving sprite
    :param Optional[Union[SpriteList, Iterable[SpriteList]]] platforms: Sprites the player can't move through.
        This value should only be used for moving Sprites. Static sprites should be sent to the ``walls`` parameter.
    :param float gravity_constant: Downward acceleration per frame
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
        """
        Create a physics engine for a platformer.
        """
        self.ladders: Optional[List[SpriteList]]
        self.platforms: List[SpriteList]
        self.walls: List[SpriteList]

        if ladders:
            if isinstance(ladders, SpriteList):
                self.ladders = [ladders]
            else:
                self.ladders = list(ladders)
        else:
            self.ladders = None

        if platforms:
            if isinstance(platforms, SpriteList):
                self.platforms = [platforms]
            else:
                self.platforms = list(platforms)
        else:
            self.platforms = []

        if walls:
            if isinstance(walls, SpriteList):
                self.walls = [walls]
            else:
                self.walls = list(walls)
        else:
            self.walls = []

        self.player_sprite: Sprite = player_sprite
        self.gravity_constant: float = gravity_constant
        self.jumps_since_ground: int = 0
        self.allowed_jumps: int = 1
        self.allow_multi_jump: bool = False

    def is_on_ladder(self):
        """ Return 'true' if the player is in contact with a sprite in the ladder list. """
        # Check for touching a ladder
        if self.ladders:
            hit_list = check_for_collision_with_lists(self.player_sprite, self.ladders)
            if len(hit_list) > 0:
                return True
        return False

    def can_jump(self, y_distance: float = 5) -> bool:
        """
        Method that looks to see if there is a floor under
        the player_sprite. If there is a floor, the player can jump
        and we return a True.

        :returns: True if there is a platform below us
        :rtype: bool
        """

        # Move down to see if we are on a platform
        self.player_sprite.center_y -= y_distance

        # Check for wall hit
        hit_list = check_for_collision_with_lists(self.player_sprite, self.walls + self.platforms)

        self.player_sprite.center_y += y_distance

        if len(hit_list) > 0:
            self.jumps_since_ground = 0

        if len(hit_list) > 0 or self.allow_multi_jump and self.jumps_since_ground < self.allowed_jumps:
            return True
        else:
            return False

    def enable_multi_jump(self, allowed_jumps: int):
        """
        Enables multi-jump.
        allowed_jumps should include the initial jump.
        (1 allows only a single jump, 2 enables double-jump, etc)

        If you enable multi-jump, you MUST call increment_jump_counter()
        every time the player jumps. Otherwise they can jump infinitely.

        :param int allowed_jumps:
        """
        self.allowed_jumps = allowed_jumps
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

    def jump(self, velocity: int):
        """ Have the character jump. """
        self.player_sprite.change_y = velocity
        self.increment_jump_counter()

    def increment_jump_counter(self):
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

        complete_hit_list = _move_sprite(self.player_sprite, self.walls + self.platforms, ramp_up=True)

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

        # print(f"Spot Z ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
        # Return list of encountered sprites
        # end_time = time.time()
        # print(f"Update - {end_time - start_time:7.4f}\n")

        return complete_hit_list
