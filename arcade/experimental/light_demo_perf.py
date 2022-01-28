import math
import random
import arcade
from arcade.experimental.lights import Light, LightLayer

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Lighting Demo (Experimental)"


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title)
        self.time = 0
        self.frame = 0
        self.background = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.light_layer.set_background_color(arcade.color.WHITE)
        # Add some random lights
        for _ in range(500):
            self.light_layer.add(
                Light(
                    random.randrange(0, SCREEN_WIDTH),
                    random.randrange(0, SCREEN_HEIGHT),
                    radius=50,
                    mode='soft',
                    color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                ),
            )

    def on_draw(self):
        self.clear()

        # Everything that should be affected by lights in here
        with self.light_layer:
            # The light layer is just cleared using the background color here (white)
            pass

        # Draw the contents with lighting
        self.light_layer.draw()

        # image = arcade.get_image()
        # image.save(f'screenshots/frame{str(self.frame).zfill(3)}.png', 'png')

    def on_update(self, dt):
        # dt = 0.1
        self.frame += 1
        try:
            self.time += dt
            for i, light in enumerate(self.light_layer):
                light.radius = 20 + math.sin(self.time + i) * 40
        except Exception as e:
            print(e)

    def on_resize(self, width, height):
        arcade.set_viewport(0, width, 0, height)
        self.light_layer.resize(width, height)


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
