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


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Sprite Depth with Cosine Modulation")

        texture = arcade.load_texture(":resources:images/test_textures/xy_square.png")

        self.sprite_list = arcade.SpriteList()
        self.time = 0.0

        for i in range(10):
            sprite = arcade.Sprite(texture, center_x=150 + 50 * i, center_y=300)
            self.sprite_list.append(sprite)

    def on_draw(self):
        self.clear()

        # This context manager temporarily enables depth testing
        with self.ctx.enabled(self.ctx.DEPTH_TEST):
            self.sprite_list.draw()

        # Draw wave visualization markers over each sprite
        for i, sprite in enumerate(self.sprite_list):
            arcade.draw_point(150 + 50 * i, 300 + sprite.depth, arcade.color.WHITE, 10)

    def on_update(self, delta_time):
        self.time += delta_time

        for i, sprite in enumerate(self.sprite_list):
            sprite.depth = math.cos(self.time + i) * 50


if __name__ == "__main__":
    MyGame().run()
