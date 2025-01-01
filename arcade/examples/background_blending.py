"""
Blending two Backgrounds.

This program loads two infinite scrolling backgrounds.

It then blends between the two when the player reaches a certain x pos.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_blending
"""

import arcade
import arcade.future.background as background

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

WINDOW_TITLE = "Blending Backgrounds Example"

PLAYER_SPEED = 300
CAMERA_SPEED = 0.1


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.camera = arcade.camera.Camera2D()

        # Load the first background from file. Sized to match the screen
        self.background_1 = background.Background.from_file(
            ":resources:/images/tiles/sandCenter.png",
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        # Load the second background from file. Sized to match the screen
        self.background_2 = background.Background.from_file(
            ":resources:/images/tiles/dirtCenter.png",
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        # start with the second background being hidden
        self.background_2.blend = 0.0

        # Create the player sprite.
        self.player_sprite = arcade.SpriteSolidColor(20, 30, color=arcade.color.PURPLE)
        self.player_sprite.center_y = self.camera.viewport_height // 2
        self.player_sprite.center_x = self.camera.viewport_width // 2

        # Track Player Motion
        self.x_direction = 0
        self.y_direction = 0

    def pan_camera_to_player(self):
        # This will center the camera on the player.
        target_x = self.player_sprite.center_x
        target_y = self.player_sprite.center_y

        # This limits where the player can see. Ensuring they never go too far
        # from the transition.
        if 0.0 > target_x:
            target_x = 0.0
        elif target_x > self.background_1.size[0] * 2:
            target_x = self.background_1.size[0] * 2

        if 0.0 > target_y:
            target_y = 0.0
        elif target_y > self.background_1.size[1]:
            target_y = self.background_1.size[1]

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position,
            (target_x, target_y),
            CAMERA_SPEED,
        )

    def on_update(self, delta_time: float):
        new_position = (
            self.player_sprite.center_x + self.x_direction * delta_time,
            self.player_sprite.center_y + self.y_direction * delta_time,
        )
        self.player_sprite.position = new_position

        # When the player is near x = WINDOW_WIDTH we transition between the two backgrounds.
        if WINDOW_WIDTH - 100 < self.player_sprite.center_x < WINDOW_WIDTH + 100:
            percent = (self.player_sprite.center_x - (WINDOW_WIDTH - 50)) / 200
            self.background_1.blend_layer(self.background_2, percent)

        self.pan_camera_to_player()

    def on_draw(self):
        self.clear()

        with self.camera.activate():
            # Ensure the background aligns with the camera
            self.background_1.pos = self.camera.bottom_left
            self.background_2.pos = self.camera.bottom_left

            # Offset the background texture.
            self.background_1.texture.offset = self.camera.position
            self.background_2.texture.offset = self.camera.position

            self.background_1.draw()
            self.background_2.draw()
            arcade.draw_sprite(self.player_sprite)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol in (arcade.key.LEFT, arcade.key.A):
            self.x_direction -= PLAYER_SPEED
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.x_direction += PLAYER_SPEED
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.y_direction -= PLAYER_SPEED
        elif symbol in (arcade.key.UP, arcade.key.W):
            self.y_direction += PLAYER_SPEED
        # Close the window
        elif symbol == arcade.key.ESCAPE:
            self.window.close()

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol in (arcade.key.LEFT, arcade.key.A):
            self.x_direction += PLAYER_SPEED
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.x_direction -= PLAYER_SPEED
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.y_direction += PLAYER_SPEED
        elif symbol in (arcade.key.UP, arcade.key.W):
            self.y_direction -= PLAYER_SPEED

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.camera.match_window()

        # This is to ensure the background covers the entire screen.
        self.background_1.size = (width, height)
        self.background_2.size = (width, height)


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=True)

    # Create and setup the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
