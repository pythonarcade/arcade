from .sprite import *
from .geometry import *


class PhysicsEngineSimple():
    """
    This class will move everything, and take care of collisions.
    """
    def __init__(self, player_sprite, walls):
        """
        Constructor.
        """
        self.player_sprite = player_sprite
        self.walls = walls

    def update(self):
        """
        Move everything and resolve collisions.
        """
        # --- Move in the x direction
        self.player_sprite.center_x += self.player_sprite.change_x

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.walls)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list) > 0:
            if self.player_sprite.change_x > 0:
                for item in hit_list:
                    self.player_sprite.right = min(item.left,
                                                   self.player_sprite.right)
            elif self.player_sprite.change_x < 0:
                for item in hit_list:
                    self.player_sprite.left = max(item.right,
                                                  self.player_sprite.left)
            else:
                print("Error, collision while player wasn't moving.")

        # --- Move in the y direction
        self.player_sprite.center_y += self.player_sprite.change_y

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.walls)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list) > 0:
            if self.player_sprite.change_y > 0:
                for item in hit_list:
                    self.player_sprite.top = min(item.bottom,
                                                 self.player_sprite.top)
            elif self.player_sprite.change_y < 0:
                for item in hit_list:
                    self.player_sprite.bottom = max(item.top,
                                                    self.player_sprite.bottom)
            else:
                print("Error, collision while player wasn't moving.")


class PhysicsEnginePlatformer():
    """
    This class will move everything, and take care of collisions.
    """
    def __init__(self, player_sprite, platforms, gravity_constant=0.5):
        """
        Constructor.
        """
        self.player_sprite = player_sprite
        self.platforms = platforms
        self.gravity_constant = gravity_constant

    def can_jump(self):

        # --- Move in the y direction
        self.player_sprite.center_y -= 2

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.platforms)

        result = False

        if len(hit_list) > 0:
            result = True

        self.player_sprite.center_y += 2
        return result

    def update(self):
        """
        Move everything and resolve collisions.
        """

        # Add gravity
        self.player_sprite.change_y -= self.gravity_constant

        # --- Move in the x direction
        self.player_sprite.center_x += self.player_sprite.change_x

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.platforms)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list) > 0:
            change_x = self.player_sprite.change_x
            if change_x > 0:
                for item in hit_list:
                    # See if we can "run up" a ramp
                    self.player_sprite.center_y += change_x
                    if arcade.check_for_collision(self.player_sprite, item):
                        self.player_sprite.center_y -= change_x
                        self.player_sprite.right = \
                            min(item.left, self.player_sprite.right)
            elif change_x < 0:
                for item in hit_list:
                    # See if we can "run up" a ramp
                    self.player_sprite.center_y += change_x
                    if arcade.check_for_collision(self.player_sprite, item):
                        self.player_sprite.center_y -= change_x
                        self.player_sprite.left = min(item.right,
                                                      self.player_sprite.left)
            else:
                print("Error, collision while player wasn't moving.")

        # --- Move in the y direction
        self.player_sprite.center_y += self.player_sprite.change_y

        # Check for wall hit
        hit_list = \
            arcade.check_for_collision_with_list(self.player_sprite,
                                                 self.platforms)

        # If we hit a wall, move so the edges are at the same point
        if len(hit_list) > 0:
            if self.player_sprite.change_y > 0:
                for item in hit_list:
                    self.player_sprite.top = min(item.bottom,
                                                 self.player_sprite.top)
            elif self.player_sprite.change_y < 0:
                for item in hit_list:
                    while arcade.check_for_collision(self.player_sprite, item):
                        self.player_sprite.bottom += 0.5
            else:
                print("Error, collision while player wasn't moving.")
            self.player_sprite.change_y = 0