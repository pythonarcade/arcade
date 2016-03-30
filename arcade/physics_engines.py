from .sprite import *
from .geometry import *


class PlatformerPhysicsEngine(SpriteList):
    def __init__(self):
        super().__init__()
        self.gravity_constant = 0.25

    def update(self):
        """
        Call the update() method on each sprite in the list.
        """
        super().update()

        for sprite in self.sprite_list:

            # Gravity
            if sprite.apply_gravity:
                sprite.change_y -= self.gravity_constant

            # y direction
            if sprite.change_y != 0:
                sprite.center_y += sprite.change_y

                check = True
                collision = False
                check_count = 0
                while check and check_count < 10:
                    check_count += 1
                    colliding_sprites = check_for_collision_with_list(sprite, self.sprite_list)
                    if(len(colliding_sprites)) == 0:
                        check = False
                    else:
                        colliding_sprite = colliding_sprites.pop()
                        collision = True
                        if sprite.change_y < 0:
                            sprite.bottom = colliding_sprite.top
                        else:
                            sprite.top = colliding_sprite.bottom

                if collision:
                    sprite.change_y = 0

            # x direction
            if sprite.change_x != 0:
                sprite.center_x += sprite.change_x

                check = True
                collision = False
                check_count = 0
                while check and check_count < 10:
                    check_count += 1
                    colliding_sprites = check_for_collision_with_list(sprite, self.sprite_list)
                    if(len(colliding_sprites)) == 0:
                        check = False
                    else:
                        colliding_sprite = colliding_sprites.pop()
                        collision = True
                        if sprite.change_x < 0:
                            sprite.left = colliding_sprite.right
                        else:
                            sprite.right = colliding_sprite.left

                if collision:
                    sprite.change_x = 0
