"""
Blending two Backgrounds.

This program loads two infinite scrolling backgrounds.

It then blends between the two when the player reaches a certain x pos.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_blending
"""

import arcade
import arcade.background as background

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Blending Backgrounds Example"

PLAYER_SPEED = 300


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.camera = arcade.SimpleCamera()

        # Load the first background from file. Sized to match the screen
        self.background_1 = background.Background.from_file(
            ":resources:/images/tiles/sandCenter.png",
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        # Load the second background from file. Sized to match the screen
        self.background_2 = background.Background.from_file(
            ":resources:/images/tiles/dirtCenter.png",
            size=(SCREEN_WIDTH, SCREEN_HEIGHT),
        )

        # start with the second background being hidden
        self.background_2.blend = 0.0

        # Create the player sprite.
        self.player_sprite = arcade.SpriteSolidColor(20, 30, arcade.color.PURPLE)
        self.player_sprite.center_y = self.camera.viewport_height // 2
        self.player_sprite.center_x = self.camera.viewport_width // 2

        # Track Player Motion
        self.x_direction = 0
        self.y_direction = 0

    def pan_camera_to_player(self):
        # This will center the camera on the player.
        target_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        target_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # This limits where the player can see. Ensuring they never go too far from the transition.
        if -self.camera.viewport_width / 2 > target_x:
            target_x = -self.camera.viewport_width / 2
        elif target_x > self.background_1.size[0] * 2 - self.camera.viewport_width / 2:
            target_x = self.background_1.size[0] * 2 - self.camera.viewport_width / 2

        if -self.camera.viewport_height / 2 > target_y:
            target_y = -self.camera.viewport_height / 2
        elif target_y > self.background_1.size[1] - self.camera.viewport_height / 2:
            target_y = self.background_1.size[1] - self.camera.viewport_height / 2

        self.camera.move_to((target_x, target_y), 0.1)

    def on_update(self, delta_time: float):
        new_position = (
            self.player_sprite.center_x + self.x_direction * delta_time,
            self.player_sprite.center_y + self.y_direction * delta_time,
        )
        self.player_sprite.position = new_position

        # When the player is near x = SCREEN_WIDTH we transition between the two backgrounds.
        if SCREEN_WIDTH - 100 < self.player_sprite.center_x < SCREEN_WIDTH + 100:
            percent = (self.player_sprite.center_x - (SCREEN_WIDTH - 50)) / 200
            self.background_1.blend_layer(self.background_2, percent)

        self.pan_camera_to_player()

    def on_draw(self):
        self.clear()

        self.camera.use()

        # Ensure the background aligns with the camera
        self.background_1.pos = self.camera.position
        self.background_2.pos = self.camera.position

        # Offset the background texture.
        self.background_1.texture.offset = self.camera.position
        self.background_2.texture.offset = self.camera.position

        self.background_1.draw()
        self.background_2.draw()
        self.player_sprite.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_direction -= PLAYER_SPEED
        elif symbol == arcade.key.RIGHT:
            self.x_direction += PLAYER_SPEED
        elif symbol == arcade.key.DOWN:
            self.y_direction -= PLAYER_SPEED
        elif symbol == arcade.key.UP:
            self.y_direction += PLAYER_SPEED

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_direction += PLAYER_SPEED
        elif symbol == arcade.key.RIGHT:
            self.x_direction -= PLAYER_SPEED
        elif symbol == arcade.key.DOWN:
            self.y_direction += PLAYER_SPEED
        elif symbol == arcade.key.UP:
            self.y_direction -= PLAYER_SPEED

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.camera.resize(width, height)

        # This is to ensure the background covers the entire screen.
        self.background_1.size = (width, height)
        self.background_2.size = (width, height)


def main():
    app = MyGame()
    app.run()


if __name__ == "__main__":
    main()
