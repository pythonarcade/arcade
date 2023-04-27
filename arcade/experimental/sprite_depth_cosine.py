"""
Depth-sort sprites using a depth buffer in the GL context.

During each update, the depth of each sprite is updated to follow a
cosine wave. Afterward, the following is drawn:

 * All sprites in depth-sorted order
 * A white square for every sprite moving with the wave along the y axis

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.experimental.sprite_depth_cosine
"""
import math
import arcade


# All constants are in pixels
WIDTH, HEIGHT = 800, 600

NUM_SPRITES = 10

SPRITE_X_START = 150
SPRITE_X_STEP = 50
SPRITE_Y = HEIGHT // 2

DOT_SIZE = 10


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(WIDTH, HEIGHT, "Sprite Depth Testing Example")

        texture = arcade.load_texture(":resources:images/test_textures/xy_square.png")

        self.sprite_list = arcade.SpriteList()
        self.time = 0.0

        for i in range(NUM_SPRITES):
            sprite = arcade.Sprite(
                texture,
                center_x=SPRITE_X_START + SPRITE_X_STEP * i,
                center_y=SPRITE_Y
            )
            self.sprite_list.append(sprite)

    def on_draw(self):
        self.clear()

        # This context manager temporarily enables depth testing
        with self.ctx.enabled(self.ctx.DEPTH_TEST):
            self.sprite_list.draw()

        # Draw wave visualization markers over each sprite
        for i, sprite in enumerate(self.sprite_list):
            arcade.draw_point(
                SPRITE_X_START + SPRITE_X_STEP * i, SPRITE_Y + sprite.depth,
                arcade.color.WHITE, DOT_SIZE
            )

    def on_update(self, delta_time):
        self.time += delta_time

        for i, sprite in enumerate(self.sprite_list):
            sprite.depth = math.cos(self.time + i) * SPRITE_X_STEP


if __name__ == "__main__":
    MyGame().run()
