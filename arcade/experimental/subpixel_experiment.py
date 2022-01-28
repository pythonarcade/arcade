import logging
from itertools import cycle
import arcade
from arcade import gl

# Do the math to figure out our screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Subpixel Experiment"

arcade.configure_logging(logging.DEBUG)


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        """
        Set up the application.
        """
        super().__init__(width, height, title, resizable=True)
        self.time = 0
        self.sprites = arcade.SpriteList()

        # Just grab all the image resources we can find
        resources = [
            getattr(arcade.resources, resource)
            for resource in dir(arcade.resources) if resource.startswith('image_')]
        resource_cycle = cycle(resources)
        # We only care about sprites of this size
        sprite_size = 128

        for y in range(0, SCREEN_HEIGHT, sprite_size):
            for x in range(0, SCREEN_WIDTH, sprite_size):
                # Just cycle until we get a sprite of the right size. This is terrible, but works!
                while True:
                    resource = next(resource_cycle)
                    print('sprite', resource)
                    sprite = arcade.Sprite(
                        resource,
                        center_x=x + sprite_size // 2,
                        center_y=y + sprite_size // 2,
                        hit_box_algorithm='None',
                    )
                    # Add sprite if correct size and get to the next sprite in the grid
                    if sprite.width == 128 and sprite.height == 128:
                        self.sprites.append(sprite)
                        break

    def on_draw(self):
        self.clear()
        # self.sprites.draw(filter=gl.NEAREST)
        self.sprites.draw(filter=gl.LINEAR)

    def on_update(self, dt):
        pass

    def on_resize(self, width, height):
        print("Resize", width, height)
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        # arcade.set_viewport(100, 200, 100, 200)


if __name__ == "__main__":
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
