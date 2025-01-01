"""
A background group.

Background groups allow for many backgrounds to be drawn with a single draw call.
It also allows their texture scrolling together.
The position of the group is added to the position of each background.
This allows the backgrounds in the group to move together but not
necessarily positioned together.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_groups
"""

import arcade
import arcade.future.background as background

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

WINDOW_TITLE = "Background Group Example"

PLAYER_SPEED = 300
CAMERA_SPEED = 0.5


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        # Set the background color to equal to that of the first background.
        self.background_color = (5, 44, 70)

        self.camera = arcade.camera.Camera2D()

        # create a background group which will hold all the backgrounds.
        self.backgrounds = background.BackgroundGroup()

        # Add each background from a file.
        # It is important to note that the scale only impacts the texture
        # and not the background. This means we need to ensure the background
        # size is also scaled correctly.
        self.backgrounds.add_from_file(
            ":resources:/images/cybercity_background/far-buildings.png",
            (0.0, 240.0),
            (WINDOW_WIDTH, 576),
            scale=3,
        )
        self.backgrounds.add_from_file(
            ":resources:/images/cybercity_background/back-buildings.png",
            (0.0, 120.0),
            (WINDOW_WIDTH, 576),
            scale=3,
        )
        self.backgrounds.add_from_file(
            ":resources:/images/cybercity_background/foreground.png",
            (0.0, 0.0),
            (WINDOW_WIDTH, 576),
            scale=3,
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

        # This ensures the background is almost always at least partially visible.
        if 0.0 > target_x:
            target_x = 0.0
        elif target_x > 2.0 * self.camera.viewport_width:
            target_x = 2.0 * self.camera.viewport_width

        if 0.0 > target_y:
            target_y = 0.0
        elif target_y > 2.0 * self.camera.viewport_height:
            target_y = 2.0 * self.camera.viewport_height

        self.camera.position = arcade.math.lerp_2d(
            self.camera.position, (target_x, target_y), CAMERA_SPEED,
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
            with self.window.ctx.enabled(self.window.ctx.BLEND):
                self.backgrounds.draw()

            arcade.draw_sprite(self.player_sprite)

    def on_key_press(self, symbol: int, modifiers: int):
        # Support arrow keys and ASWD
        if symbol in (arcade.key.LEFT, arcade.key.A):
            self.x_direction -= PLAYER_SPEED
        elif symbol in (arcade.key.RIGHT, arcade.key.D):
            self.x_direction += PLAYER_SPEED
        elif symbol in (arcade.key.DOWN, arcade.key.S):
            self.y_direction -= PLAYER_SPEED
        elif symbol in (arcade.key.UP, arcade.key.W):
            self.y_direction += PLAYER_SPEED
        # Close the window if the user presses escape
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
