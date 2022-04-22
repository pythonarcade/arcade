"""

"""

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

SCREEN_TITLE = "Stationary Background Example"

PLAYER_SPEED = 300


class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, enable_polling=True)
        # Load the background from file. It defaults to the size of the texture with the bottom left corner at (0, 0).
        self.background = arcade.Background.from_file(":resources:/images/backgrounds/abstract_1.jpg")

        # Create the player sprite.
        self.player_sprite = arcade.SpriteSolidColor(20, 30, arcade.color.PURPLE)
        self.player_sprite.center_y = SCREEN_HEIGHT // 2
        self.player_sprite.center_x = SCREEN_WIDTH // 2

        # Track Player Motion
        self.x_direction = 0
        self.y_direction = 0

        self.camera = arcade.Camera()

    def pan_camera_to_player(self):
        # This will center the camera on the player.
        target_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        target_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        # This ensures the background is always at least partially visible.
        if -SCREEN_WIDTH / 2 > target_x:
            target_x = -SCREEN_WIDTH / 2
        elif target_x > self.background.size[0] - SCREEN_WIDTH / 2:
            target_x = self.background.size[0] - SCREEN_WIDTH / 2

        if -SCREEN_HEIGHT / 2 > target_y:
            target_y = -SCREEN_HEIGHT / 2
        elif target_y > self.background.size[1] - SCREEN_HEIGHT / 2:
            target_y = self.background.size[1] - SCREEN_HEIGHT / 2

        self.camera.move_to((target_x, target_y), 0.1)

    def on_update(self, delta_time: float):
        new_position = (self.player_sprite.center_x + self.x_direction * delta_time,
                        self.player_sprite.center_y + self.y_direction * delta_time)
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


def main():
    app = MyGame()
    app.run()


if __name__ == '__main__':
    main()
