"""
A parallax background group.

Parallax background groups allow easy implementation of parallax.
each background is assigned a depth value.
This impacts how much the offset is applied to the background texture.
greater depth means less impact. making them seem further away.

This is a common technique used in platformers and side scrollers.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.background_parallax
"""

import arcade
import arcade.background as background

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Background Group Example"

PLAYER_SPEED = 300


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
        # Set the background color to equal to that of the first background.
        self.background_color = (5, 44, 70)

        self.camera = arcade.SimpleCamera()

        # create a background group which will hold all the backgrounds.
        self.backgrounds = background.ParallaxGroup()

        # Add each background from a file.
        # It is important to note that the scale only impacts the texture and not the background.
        # This means we need to ensure the background size is also scaled correctly.
        self.backgrounds.add_from_file(
            ":resources:/images/cybercity_background/far-buildings.png",
            (0.0, 240.0),
            (SCREEN_WIDTH, 576),
            4,
            scale=3,
        )
        self.backgrounds.add_from_file(
            ":resources:/images/cybercity_background/back-buildings.png",
            (0.0, 120.0),
            (SCREEN_WIDTH, 576),
            2,
            scale=3,
        )
        self.backgrounds.add_from_file(
            ":resources:/images/cybercity_background/foreground.png",
            (0.0, 0.0),
            (SCREEN_WIDTH, 576),
            1,
            scale=3,
        )

        # Create the player sprite.
        self.player_sprite = arcade.SpriteSolidColor(20, 30, arcade.color.PURPLE)
        self.player_sprite.center_y = self.camera.viewport_height // 2
        self.player_sprite.bottom = 0

        # Track Player Motion
        self.x_direction = 0

    def pan_camera_to_player(self):
        # This will center the camera on the player.
        target_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)

        # This ensures the background is almost always at least partially visible.
        if -self.camera.viewport_width / 2 > target_x:
            target_x = -self.camera.viewport_width / 2
        elif target_x > 1.5 * self.camera.viewport_width:
            target_x = 1.5 * self.camera.viewport_width

        self.camera.move_to((target_x, 0.0), 0.1)

    def on_update(self, delta_time: float):
        self.player_sprite.center_x += self.x_direction * delta_time

        self.pan_camera_to_player()

    def on_draw(self):
        self.clear()

        self.camera.use()

        # Ensure the backgrounds aligns with the camera
        self.backgrounds.pos = self.camera.position

        # Offset the backgrounds texture.
        self.backgrounds.offset = self.camera.position

        self.backgrounds.draw()
        self.player_sprite.draw()

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_direction -= PLAYER_SPEED
        elif symbol == arcade.key.RIGHT:
            self.x_direction += PLAYER_SPEED

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self.x_direction += PLAYER_SPEED
        elif symbol == arcade.key.RIGHT:
            self.x_direction -= PLAYER_SPEED

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.camera.resize(width, height)

        # We can iterate through a background group,
        # but in the case of a parallax group the iter returns
        # both the Backgrounds and the depths. (tuple[Background, float])
        for backgrounds, depth in self.backgrounds:
            backgrounds.size = (width, 576)


def main():
    app = MyGame()
    app.run()


if __name__ == "__main__":
    main()
