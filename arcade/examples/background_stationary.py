"""
A stationary Background.

This program loads a background from a file.
The texture is not added to a texture atlas or texture cache.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_stationary
"""

import arcade
import arcade.background as background

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Stationary Background Example"

PLAYER_SPEED = 300


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        self.camera = arcade.SimpleCamera()

        # Load the background from file. It defaults to the size of the texture with the bottom left corner at (0, 0).
        # Image from:
        # https://wallpaper-gallery.net/single/free-background-images/free-background-images-22.html
        self.background = background.Background.from_file(
            ":resources:/images/backgrounds/abstract_1.jpg"
        )

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

        # This ensures the background is always at least partially visible.
        if -self.camera.viewport_width / 2 > target_x:
            target_x = -self.camera.viewport_width / 2
        elif target_x > self.background.size[0] - self.camera.viewport_width / 2:
            target_x = self.background.size[0] - self.camera.viewport_width / 2

        if -self.camera.viewport_height / 2 > target_y:
            target_y = -self.camera.viewport_height / 2
        elif target_y > self.background.size[1] - self.camera.viewport_height / 2:
            target_y = self.background.size[1] - self.camera.viewport_height / 2

        self.camera.move_to((target_x, target_y), 0.1)

    def on_update(self, delta_time: float):
        new_position = (
            self.player_sprite.center_x + self.x_direction * delta_time,
            self.player_sprite.center_y + self.y_direction * delta_time,
        )
        self.player_sprite.position = new_position

        self.pan_camera_to_player()

    def on_draw(self):
        self.clear()

        self.camera.use()

        self.background.draw()
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


def main():
    app = MyGame()
    app.run()


if __name__ == "__main__":
    main()
