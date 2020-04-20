import traceback
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

        self.light_layer = LightLayer((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.light_layer.extend([
            Light((200, 400), radius=50),
            Light((400, 400), radius=50),
            Light((600, 400), radius=50),
        ])

    def on_draw(self):
        try:
            with self.light_layer:
                # Draw stuff here!

            # Draw the contents with lighting
            self.light_layer.draw(ambient_color=(64, 64, 64))

        except Exception:
            traceback.print_exc()
            exit(1)

    def on_update(self, dt):
        self.time += dt


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
