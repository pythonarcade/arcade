import math
import arcade


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(800, 600, "Sprite Depth")
        self.sprite_list = arcade.SpriteList()
        texture = arcade.load_texture(":resources:images/test_textures/xy_square.png")
        self.time = 0.0

        for i in range(10):
            sprite = arcade.Sprite(texture, center_x=150 + 50 * i, center_y=300)
            self.sprite_list.append(sprite)

    def on_draw(self):
        self.clear()
        with self.ctx.enabled(self.ctx.DEPTH_TEST):
            self.sprite_list.draw()

        for i, sprite in enumerate(self.sprite_list):
            arcade.draw_point(150 + 50 * i, 300 + sprite.depth, arcade.color.WHITE, 10)

    def on_update(self, delta_time):
        self.time += delta_time
        for i, sprite in enumerate(self.sprite_list):
            sprite.depth = math.cos(self.time + i) * 50


MyGame().run()
