"""
Move, manipulate, and abuse large numbers of sprites to test performance.
Checks position, scale, and collisions at volume.

.. warning:: May be extremely laggy on lower end pc's

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_properties_stress.py
"""
import arcade
import random

# -- CONSTANTS
WINDOW_TITLE = 'Sprite Stress Test'
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
SPRITE_COUNT = 2000
COIN_SCALE = 0.1
COIN_SPEED = 100.0

# Don't let more than 10 fixed updates occur in a single update cycle
# Helps protect against death spirals after lag spikes
# It means the fixed time will lag behind the update time for awhile,
# but as long as the lag decreases it will catch up.
FIXED_FRAME_CAP = 10

COLLISION_BOX_SIZE = arcade.Vec2(100, 100)
COLLISION_BOX_MAX_SCALE = arcade.Vec2(WINDOW_WIDTH / 200.0, WINDOW_HEIGHT / 200.0)
COLLISION_BOX_GROWTH_SPEED = COLLISION_BOX_MAX_SCALE / 2000  # needs 2000 collisions to reach max size

# -- TEMP FOR TESTING --
import cProfile
import time


FIXED_UPDATE_PROFILER = cProfile.Profile()

class VelocitySprite(arcade.Sprite):

    def __init__(self, texture: arcade.Texture, scale: float, position: arcade.Vec2, velocity: arcade.Vec2):
        super().__init__(texture, scale, position.x, position.y)
        self.velocity: arcade.Vec2 = velocity


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, title=WINDOW_TITLE, fixed_frame_cap=FIXED_FRAME_CAP)
        self.coin_sprites: arcade.SpriteList[VelocitySprite] = arcade.SpriteList()
        # preload the texture since all the coins will use it
        coin_texture: arcade.Texture = arcade.load_texture(":resources:images/items/coinGold.png")
        self.coin_sprites.extend([
            VelocitySprite(
                coin_texture, COIN_SCALE,
                arcade.Vec2(random.uniform(20, self.width-20), random.uniform(20, self.height-20)),
                arcade.Vec2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * COIN_SPEED
            )
            for _ in range(SPRITE_COUNT)
        ])
        self.collision_box = arcade.SpriteSolidColor(
            COLLISION_BOX_SIZE.x, COLLISION_BOX_SIZE.y,
            self.center_x, self.center_y
        )

    def on_update(self, delta_time: float) -> bool | None:
        pass

    def on_fixed_update(self, delta_time: float):
        start = time.perf_counter_ns()
        with FIXED_UPDATE_PROFILER:
            # We will be moving and colliding the sprites in the fixed update
            # as we don't want the lag to cause tunneling, may cause death spiraling.

            # calculate collisions and resulting new velocities
            # - Check for collisions with the outer wall

            for sprite in self.coin_sprites:
                if sprite.center_x <= sprite.width / 2.0 and sprite.velocity.x < 0.0:
                    sprite.center_x = sprite.width / 2.0
                    sprite.velocity = arcade.Vec2(-sprite.velocity.x, sprite.velocity.y)
                elif WINDOW_WIDTH - sprite.width / 2.0 <= sprite.center_x and sprite.velocity.x > 0.0:
                    sprite.center_x = WINDOW_WIDTH - sprite.width / 2.0
                    sprite.velocity = arcade.Vec2(-sprite.velocity.x, sprite.velocity.y)

                if sprite.center_y <= sprite.height / 2.0 and sprite.velocity.y < 0.0:
                    sprite.center_y = sprite.height / 2.0
                    sprite.velocity = arcade.Vec2(sprite.velocity.x, -sprite.velocity.y)
                elif WINDOW_HEIGHT - sprite.height / 2.0 <= sprite.center_y and sprite.velocity.y > 0.0:
                    sprite.center_y = WINDOW_HEIGHT - sprite.height / 2.
                    sprite.velocity = arcade.Vec2(sprite.velocity.x, -sprite.velocity.y)

            collides_with_box = arcade.check_for_collision_with_list(self.collision_box, self.coin_sprites, 3)
            if collides_with_box:
                c_box = self.collision_box

                c_box.scale += COLLISION_BOX_GROWTH_SPEED
                if c_box.scale_x > COLLISION_BOX_MAX_SCALE.x:
                    c_box.scale_x = COLLISION_BOX_MAX_SCALE.x
                if c_box.scale_y > COLLISION_BOX_MAX_SCALE.y:
                    c_box.scale_y = COLLISION_BOX_MAX_SCALE.y


                for collision in collides_with_box:
                    collision_point = collision.position
                    collision_rel = arcade.Vec2(collision_point[0] - c_box.center_x, collision_point[1] - c_box.center_y)

                    if abs(collision_rel[0]) > abs(collision_rel[1]):
                        if collision_rel[0] < 0:
                            collision.velocity = arcade.Vec2(-abs(collision.velocity.x), collision.velocity.y)
                        else:
                            collision.velocity = arcade.Vec2(abs(collision.velocity.x), collision.velocity.y)
                    else:
                        if collision_rel[1] < 0:
                            collision.velocity = arcade.Vec2(collision.velocity.x, -abs(collision.velocity.y))
                        else:
                            collision.velocity = arcade.Vec2(collision.velocity.x, abs(collision.velocity.y))

            # apply velocities
            for sprite in self.coin_sprites:
                old_pos = sprite.position
                frame_vel = sprite.velocity * delta_time
                sprite.position =old_pos[0] + frame_vel[0], old_pos[1] + frame_vel[1]
        print(f'update speed: {time.perf_counter_ns() - start} ns')

    def on_draw(self) -> bool | None:
        self.clear()
        self.coin_sprites.draw()
        arcade.draw_sprite(self.collision_box)


def main():
    win = MyGame()
    win.run()

if __name__ == '__main__':
    main()
    FIXED_UPDATE_PROFILER.print_stats('time')
