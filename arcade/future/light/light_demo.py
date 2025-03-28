import math

import arcade
from arcade.future.light import Light, LightLayer

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Lighting Demo (Experimental)"


class MyGame(arcade.Window):
    """
    Set up the application.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.background = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")

        self.torch_list = arcade.SpriteList()
        self.torch_list.extend(
            [
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=100, center_y=150
                ),
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=300, center_y=150
                ),
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=500, center_y=150
                ),
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=700, center_y=150
                ),
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=100, center_y=450
                ),
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=300, center_y=450
                ),
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=500, center_y=450
                ),
                arcade.Sprite(
                    ":resources:images/tiles/torch1.png", scale=0.4, center_x=700, center_y=450
                ),
            ]
        )

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        # Add lights to the location of the torches. We're just using hacky tweak value list here
        params = (
            (100, "hard"),
            (100, "hard"),
            (100, "hard"),
            (100, "hard"),
            (120, "soft"),
            (120, "soft"),
            (120, "soft"),
            (120, "soft"),
        )
        for sprite, p in zip(self.torch_list, params):
            self.light_layer.add(
                Light(sprite.center_x, sprite.center_y, radius=p[0], mode=p[1]),
            )
        self.moving_light = Light(400, 300, radius=300, mode="soft")
        self.light_layer.add(self.moving_light)

    def on_draw(self):
        self.clear()

        # Everything that should be affected by lights in here
        with self.light_layer:
            arcade.draw_texture_rect(
                self.background, arcade.LBWH(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            self.torch_list.draw()

        # Draw the contents with lighting
        self.light_layer.draw()
        # draw with ambient
        # self.light_layer.draw(ambient_color=(127, 127, 127))

    def on_update(self, dt):
        # Keep track of elapsed time
        self.moving_light.position = (
            400 + math.sin(self.time) * 300,
            300 + math.cos(self.time) * 50,
        )
        self.moving_light.radius = 300 + math.sin(self.time * 2.34) * 150

    def on_resize(self, width, height):
        self.default_camera.use()
        self.light_layer.resize(width, height)


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
