import math
import time

import arcade
from arcade.experimental.camera import Camera2D


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title=title, resizable=True)
        self.set_vsync(True)
        self.map = arcade.tilemap.read_tmx(':resources:tmx_maps/map.tmx')
        self.background = arcade.tilemap.process_layer(self.map, 'Platforms', hit_box_algorithm='None')
        self.camera = Camera2D(
            viewport=(0, 0, self.width, self.height),
            projection=(0, self.width, 0, self.height),
        )
        self.background_color = self.map.background_color
        self.mouse_pos = 0, 0
        self.time = 0

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.background.draw()

        world_pos = self.camera.mouse_coordinates_to_world(*self.mouse_pos)
        arcade.draw_circle_filled(*world_pos, 10, arcade.color.BLUE)

    def on_update(self, dt):
        self.time += dt
        self.camera.scroll = (
            2800 + math.sin(self.time / 3) * 2900,
            -20 + math.cos(self.time / 3) * 100,
        )

    def on_resize(self, width, height):
        self.camera.viewport = 0, 0, width, height
        # self.camera.projection = 0, width, 0, height

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = x, y

if __name__ == "__main__":
    MyGame(800, 600, "Camera Test")
    arcade.run()
