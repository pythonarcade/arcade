"""
A scrolling Background.

This program loads a texture from a file,
and create a screen sized background.
The background is constantly aligned to the screen, and the
texture offset changed. This creates an illusion of moving.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_scrolling
"""
import arcade
import arcade.future.background as background

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

WINDOW_TITLE = "Scrolling Background Example"

PLAYER_SPEED = 300
CAMERA_SPEED = 0.5


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.camera = arcade.Camera2D()

        # Load the background from file. Sized to match the screen
        self.background = background.Background.from_file(
            ":resources:/images/tiles/sandCenter.png",
            size=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

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

        self.pan_camera_to_player()

    def on_draw(self):
        self.clear()

        with self.camera.activate():
            # Ensure the background aligns with the camera
            self.background.pos = self.camera.bottom_left

            # Offset the background texture.
            self.background.texture.offset = self.camera.bottom_left

            self.background.draw()
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
        # Close the window if the user presses the escape key
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
        self.background.size = (width, height)


def main():
    """ Main function """
    # Create a window class. This is what actually shows up on screen
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

    # Create the GameView
    game = GameView()

    # Show GameView on screen
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


if __name__ == "__main__":
    main()
