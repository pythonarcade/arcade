"""
Perspective Parallax

Using a perspective projector and sprites at different depths you can cheaply get a parallax effect.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.perspective_parallax
"""

import math

import arcade

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
LAYERS = (
    ":assets:/images/cybercity_background/far-buildings.png",
    ":assets:/images/cybercity_background/back-buildings.png",
    ":assets:/images/cybercity_background/foreground.png",
)


class PerspectiveParallax(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Perspective Parallax")
        self.t = 0.0
        self.camera = arcade.camera.PerspectiveProjector()

        self.camera_data = self.camera.view
        self.camera_data.zoom = 2.0

        self.camera.projection.far = 1000

        self.background_sprites = arcade.SpriteList()
        for index, layer_src in enumerate(LAYERS):
            layer = arcade.Sprite(layer_src)
            layer.depth = -500 + index * 100.0
            self.background_sprites.append(layer)

    def on_draw(self):
        self.clear()
        with self.camera.activate():
            self.background_sprites.draw(pixelated=True)

    def on_update(self, delta_time: float):
        self.t += delta_time

        self.camera_data.position = (math.cos(self.t) * 200.0, math.sin(self.t) * 200.0, 0.0)


def main():
    window = PerspectiveParallax()
    window.run()


if __name__ == "__main__":
    main()
