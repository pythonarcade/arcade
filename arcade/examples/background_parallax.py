"""
Parallax scrolling layers move slower the "farther" away they are.

Use the right and left arrow keys to move the car.

Arcade's ParallaxGroup allows you to implement this technique quickly
to create more satisfying backgrounds to your games. The example below
demonstrates how to fake an endless world by adjusting ParallaxGroup's
position & offset values. For limited worlds or backgrounds, limit the
repositioning to only occur within certain bounds, or delete it.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_parallax
"""

import arcade
import arcade.background as background


SCREEN_TITLE = "Background Group Example"
SCREEN_WIDTH = 800

# How much we'll scale up our pixel art
PIXEL_SCALE = 3

# The original & scaled heights of our background layer image data in pixels.
ORIGINAL_BG_LAYER_HEIGHT_PX = 240
SCALED_BG_LAYER_HEIGHT_PX = ORIGINAL_BG_LAYER_HEIGHT_PX * PIXEL_SCALE


PLAYER_SPEED = 300  # The player's speed in pixels / second


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCALED_BG_LAYER_HEIGHT_PX, SCREEN_TITLE, resizable=True)

        # Set the background color to match the sky in the background images
        self.background_color = (162, 84, 162, 255)

        self.camera = arcade.SimpleCamera()

        # Create a background group to hold all the landscape's layers
        self.backgrounds = background.ParallaxGroup()

        # Calculate the current size of each background fill layer in pixels
        bg_layer_size_px = (SCREEN_WIDTH, SCALED_BG_LAYER_HEIGHT_PX)

        # Import the image data for each background layer.
        # Unlike sprites, the scale argument doesn't resize the layer
        # itself. Instead, it changes the zoom level, while depth
        # controls how fast each layer scrolls. This means you have to
        # pass a correct size value when adding a layer. We calculated
        # this above.
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/layers/back.png",
            size=bg_layer_size_px,
            depth=10.0,
            scale=PIXEL_SCALE
        )
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/layers/buildings.png",
            size=bg_layer_size_px,
            depth=5.0,
            scale=PIXEL_SCALE
        )
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/layers/palms.png",
            size=bg_layer_size_px,
            depth=3.0,
            scale=PIXEL_SCALE
        )
        self.backgrounds.add_from_file(
            ":resources:/images/miami_synth_parallax/layers/highway.png",
            size=bg_layer_size_px,
            depth=1.0,
            scale=PIXEL_SCALE
        )

        # Create & position the player sprite in the center of the camera's view
        self.player_sprite = arcade.Sprite(
            ":resources:/images/miami_synth_parallax/car/car-idle.png",
            center_x=self.camera.viewport_width // 2, scale=PIXEL_SCALE
        )
        self.player_sprite.bottom = 0

        # Track the player's x velocity
        self.x_velocity = 0

    def pan_camera_to_player(self):
        # Move the camera toward the center of the player's sprite
        target_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        self.camera.move_to((target_x, 0.0), 0.1)

    def on_update(self, delta_time: float):
        # Move the player in our infinite world
        self.player_sprite.center_x += self.x_velocity * delta_time
        self.pan_camera_to_player()

    def on_draw(self):

        # Set up our drawing
        self.clear()
        self.camera.use()

        # Store a reference to the background layers as shorthand
        bg = self.backgrounds

        # Fake an endless world with scrolling terrain
        # Try experimenting with commenting out 1 or both of the 2 lines
        # below to get an intuitive understanding of what each does!
        bg.offset = self.camera.position  # Fake depth by moving layers
        bg.pos = self.camera.position  # Follow the car to fake infinity

        # Draw the background & the player's car
        bg.draw()
        self.player_sprite.draw(pixelated=True)

    def update_car_direction(self):
        """
        Don't use the trick below in a real game!

        It will cause problems! Instead, use different textures, either
        from different files or by using Texture.flop_left_to_right().
        """
        if self.x_velocity < 0:
            self.player_sprite.scale_xy = (-PIXEL_SCALE, PIXEL_SCALE)
            print(self.player_sprite.width)
        elif self.x_velocity > 0:
            self.player_sprite.scale_xy = (PIXEL_SCALE, PIXEL_SCALE)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_velocity -= PLAYER_SPEED
            self.update_car_direction()
        elif symbol == arcade.key.RIGHT:
            self.x_velocity += PLAYER_SPEED
            self.update_car_direction()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_velocity += PLAYER_SPEED
            self.update_car_direction()
        elif symbol == arcade.key.RIGHT:
            self.x_velocity -= PLAYER_SPEED
            self.update_car_direction()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.camera.resize(width, height)
        full_width_size = (width, SCALED_BG_LAYER_HEIGHT_PX)

        # We can iterate through a background group,
        # but in the case of a parallax group the iter returns
        # both the Backgrounds and the depths. (tuple[Background, float])
        for layer, depth in self.backgrounds:
            layer.size = full_width_size


def main():
    app = MyGame()
    app.run()


if __name__ == "__main__":
    main()
