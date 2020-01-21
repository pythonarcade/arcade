"""
Physics engines for top-down or platformers.
"""
# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods

from arcade import check_for_collision_with_list
from arcade import check_for_collision
from arcade import Sprite
from arcade import SpriteList


class PhysicsEngineSimple:
    """
    Simplistic physics engine for use in games without gravity, such as top-down
    games. It is easier to get
    started with this engine than more sophisticated engines like PyMunk. Note, it
    does not currently handle rotation.
    """

    def __init__(self, player_sprite: Sprite, walls: SpriteList):
        """
        Create a simple physics engine.

        :param Sprite player_sprite: The moving sprite
        :param SpriteList walls: The sprites it can't move through
        """
        assert(isinstance(player_sprite, Sprite))
        assert(isinstance(walls, SpriteList))
        self.player_sprite = player_sprite
        self.walls = walls

    def update(self):
        """
        Move everything and resolve collisions.

        :Returns: SpriteList with all sprites contacted. Empty list if no sprites.
        """

        # --- Move in the x direction
        self.player_sprite.center_x += self.player_sprite.change_x

        # Check for wall hit
        hit_list_x = \
            check_for_collision_with_list(self.player_sprite,
                                          self.walls)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list_x) > 0:
            if self.player_sprite.change_x > 0:
                for item in hit_list_x:
                    self.player_sprite.right = min(item.left,
                                                   self.player_sprite.right)
            elif self.player_sprite.change_x < 0:
                for item in hit_list_x:
                    self.player_sprite.left = max(item.right,
                                                  self.player_sprite.left)
            else:
                print("Error, collision while player wasn't moving.")

        # --- Move in the y direction
        self.player_sprite.center_y += self.player_sprite.change_y

        # Check for wall hit
        hit_list_y = \
            check_for_collision_with_list(self.player_sprite,
                                          self.walls)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list_y) > 0:
            if self.player_sprite.change_y > 0:
                for item in hit_list_y:
                    self.player_sprite.top = min(item.bottom,
                                                 self.player_sprite.top)
            elif self.player_sprite.change_y < 0:
                for item in hit_list_y:
                    self.player_sprite.bottom = max(item.top,
                                                    self.player_sprite.bottom)
            else:
                print("Error, collision while player wasn't moving.")

        # Return list of encountered sprites
        complete_hit_list = hit_list_x
        for sprite in hit_list_y:
            complete_hit_list.append(sprite)
        return complete_hit_list


class PhysicsEnginePlatformer:
    """
    Simplistic physics engine for use in a platformer. It is easier to get
    started with this engine than more sophisticated engines like PyMunk. Note, it
    does not currently handle rotation.
    """

    def __init__(self,
                 player_sprite: Sprite,
                 platforms: SpriteList,
                 gravity_constant: float = 0.5,
                 ladders: SpriteList = None,
                 ):
        """
        Create a physics engine for a platformer.

        :param Sprite player_sprite: The moving sprite
        :param SpriteList walls: The sprites it can't move through
        :param float gravity_constant: Downward acceleration per frame
        :param SpriteList ladders: Ladders the user can climb on
        """
        if ladders is not None and not isinstance(ladders, SpriteList):
            raise TypeError("Fourth parameter should be a SpriteList of ladders")

        self.player_sprite = player_sprite
        self.platforms = platforms
        self.gravity_constant = gravity_constant
        self.jumps_since_ground = 0
        self.allowed_jumps = 1
        self.allow_multi_jump = False
        self.ladders = ladders

    def is_on_ladder(self):
        # Check for touching a ladder
        if self.ladders:
            hit_list = check_for_collision_with_list(self.player_sprite, self.ladders)
            if len(hit_list) > 0:
                return True
        return False

    def can_jump(self, y_distance=5) -> bool:
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
        hit_list = check_for_collision_with_list(self.player_sprite, self.platforms)

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
        # print(f"Spot A ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

        # --- Add gravity if we aren't on a ladder
        if not self.is_on_ladder():
            self.player_sprite.change_y -= self.gravity_constant

        # --- Move in the y direction
        self.player_sprite.center_y += self.player_sprite.change_y

        # Check for wall hit
        hit_list_x = check_for_collision_with_list(self.player_sprite, self.platforms)
        complete_hit_list = hit_list_x

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list_x) > 0:
            if self.player_sprite.change_y > 0:
                while len(check_for_collision_with_list(self.player_sprite, self.platforms)) > 0:
                    self.player_sprite.center_y -= 1
                # print(f"Spot X ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
            elif self.player_sprite.change_y < 0:
                # Reset number of jumps
                for item in hit_list_x:
                    while check_for_collision(self.player_sprite, item):
                        # self.player_sprite.bottom = item.top <- Doesn't work for ramps
                        self.player_sprite.bottom += 0.25

                    if item.change_x != 0:
                        self.player_sprite.center_x += item.change_x

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
            self.player_sprite.change_y = min(0.0, hit_list_x[0].change_y)

        # print(f"Spot B ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
        self.player_sprite.center_y = round(self.player_sprite.center_y, 2)
        # print(f"Spot Q ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

        # --- Move in the x direction
        self.player_sprite.center_x += self.player_sprite.change_x

        check_again = True
        while check_again:
            check_again = False
            # Check for wall hit
            hit_list_y = check_for_collision_with_list(self.player_sprite, self.platforms)
            complete_hit_list = hit_list_x
            for sprite in hit_list_y:
                if sprite not in complete_hit_list:
                    complete_hit_list.append(sprite)

            # If we hit a wall, move so the edges are at the same point
            if len(hit_list_y) > 0:
                change_x = self.player_sprite.change_x
                if change_x > 0:
                    for _ in hit_list_y:
                        # print(f"Spot 1 ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
                        # See if we can "run up" a ramp
                        self.player_sprite.center_y += change_x
                        if len(check_for_collision_with_list(self.player_sprite, self.platforms)) > 0:
                            # No, ramp run-up doesn't work.
                            self.player_sprite.center_y -= change_x
                            self.player_sprite.center_x -= 1
                            # print(f"Spot R ({self.player_sprite.center_x}, {self.player_sprite.center_y})")
                            check_again = True
                            break
                        # else:
                            # print("Run up ok 1")
                        # print(f"Spot 2 ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

                elif change_x < 0:
                    for item in hit_list_y:
                        # See if we can "run up" a ramp
                        self.player_sprite.center_y -= change_x
                        if len(check_for_collision_with_list(self.player_sprite, self.platforms)) > 0:
                            # Can't run up the ramp, reverse
                            self.player_sprite.center_y += change_x
                            self.player_sprite.left = max(item.right, self.player_sprite.left)
                            # print(f"Reverse 1 {item.right}, {self.player_sprite.left}")
                            # Ok, if we were shoved back to the right, we need to check this whole thing again.
                            check_again = True
                            break
                        # print(f"Spot 4 ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

                else:
                    print("Error, x collision while player wasn't moving.\n"
                          "Make sure you aren't calling multiple updates, like "
                          "a physics engine update and an all sprites list update.")

            # print(f"Spot E ({self.player_sprite.center_x}, {self.player_sprite.center_y})")

        for platform in self.platforms:
            if platform.change_x != 0 or platform.change_y != 0:
                platform.center_x += platform.change_x

                if platform.boundary_left is not None \
                        and platform.left <= platform.boundary_left:
                    platform.left = platform.boundary_left
                    if platform.change_x < 0:
                        platform.change_x *= -1

                if platform.boundary_right is not None \
                        and platform.right >= platform.boundary_right:
                    platform.right = platform.boundary_right
                    if platform.change_x > 0:
                        platform.change_x *= -1

                if check_for_collision(self.player_sprite, platform):
                    if platform.change_x < 0:
                        self.player_sprite.right = platform.left
                    if platform.change_x > 0:
                        self.player_sprite.left = platform.right

                platform.center_y += platform.change_y

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

        # Return list of encountered sprites
        return complete_hit_list

