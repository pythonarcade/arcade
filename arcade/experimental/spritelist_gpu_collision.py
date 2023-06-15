import arcade
from pyglet import gl

coin_path = ":resources:images/items/coinGold.png"

class Test(arcade.Window):
    def __init__(self):
        super().__init__(800, 600)
        self.time = 0
        self.texture = arcade.load_texture(coin_path)
        print(self.ctx.limits.POINT_SIZE_RANGE)
        self.spritelist = arcade.SpriteList()
        for y in range(0, 600, 100):
            for x in range(0, 800, 100):
                sprite = arcade.Sprite(self.texture)
                sprite.center_x = 50 + x
                sprite.center_y = 50 + y
                self.spritelist.append(sprite)
                self.spritelist._update_points(sprite)

        # print(self.spritelist._hit_points_data[0:8 * 400])
        self.pos = 0, 0

    def on_draw(self):
        self.clear()
        self.spritelist.draw()
        self.ctx.point_size = 4.0
        gl.glLineWidth(2.0)
        # self.spritelist.collision_program.set_uniform_safe("pos", self.pos)
        self.spritelist.collision_program["point"] = self.pos
        self.spritelist.draw_gpu_collision()
        # self.spritelist.draw_hit_boxes(color=arcade.color.RED, line_thickness=2.0)
        arcade.draw_rectangle_outline(*self.pos, 100, 100, arcade.color.WHITE, 2.0)

    def on_update(self, delta_time):
        self.time += delta_time
        for i, sprite in enumerate(self.spritelist):
            sprite.angle = i * 50 + self.time * 100

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.pos = x, y


if __name__ == "__main__":
    Test().run()
