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
SPRITE_COUNT = 3000
COIN_START_SCALE = 0.1
COIN_END_SCALE = 10.0

COLLISION_BOX_SIZE = arcade.Vec2(100, 100)
COLLISION_BOX_MAX_SCALE = arcade.Vec2(WINDOW_WIDTH / 200.0, WINDOW_HEIGHT / 200.0)

# -- TEMP FOR TESTING --
import cProfile


FIXED_UPDATE_PROFILER = cProfile.Profile()

class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, title=WINDOW_TITLE)
        self.coin_sprites: arcade.SpriteList = arcade.SpriteList()
        # preload the texture since all the coins will use it
        coin_texture: arcade.Texture = arcade.load_texture(":resources:images/items/coinGold.png")
        self.coin_sprites.extend([
            arcade.Sprite(
                coin_texture, COIN_START_SCALE,
                random.uniform(20, self.width-20), random.uniform(20, self.height-20)
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
        with FIXED_UPDATE_PROFILER:
            # We will be moving and colliding the sprites in the fixed update
            # as we don't want the lag to cause tunneling, may cause death spiraling.
            pass

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
