import math
import time

import arcade
from arcade.experimental.camera import Camera2D

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Camera Test"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title=title, resizable=True)
        self.set_vsync(True)
        self.map = arcade.tilemap.read_tmx(':resources:tmx_maps/map.tmx')
        self.background = arcade.tilemap.process_layer(self.map, 'Platforms', hit_box_algorithm='None')
        self.camera = Camera2D(
            viewport=(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            projection=(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT),
        )
        self.time = 0

    def on_draw(self):
        self.clear()        
        self.camera.use()
        self.background.draw()

    def on_update(self, dt):
        self.time += dt
        self.camera.scroll = (
            2800 + math.sin(self.time / 3) * 2900,
            -20 + math.cos(self.time / 3) * 100,
        )
        pass

    def on_resize(self, width, height):
        self.camera.viewport = 0, 0, width, height


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
