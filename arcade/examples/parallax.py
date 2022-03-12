"""
Parallax Example
python -m arcade.examples.parallax
"""
import arcade

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
SCREEN_TITLE = "Parallax Example"
MOVEMENT_SPEED = 5
SPRITE_SCALING = 3
BACKGROUND_RISE_AMOUNT = 40


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.BLACK)

        self.backgrounds = arcade.SpriteList()

        self.player_sprite = arcade.SpriteSolidColor(20, 30, arcade.color.PURPLE)
        self.player_sprite.bottom = 0
        self.player_sprite.center_x = self.width / 2
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False

        self.camera = arcade.Camera(width, height)

    def setup(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here
        images = (":resources:images/cybercity_background/far-buildings.png",
                  ":resources:images/cybercity_background/back-buildings.png",
                  ":resources:images/cybercity_background/foreground.png")

        rise = BACKGROUND_RISE_AMOUNT * SPRITE_SCALING

        for count, image in enumerate(images):
            bottom = rise * (len(images) - count - 1)

            sprite = arcade.Sprite(image, scale=SPRITE_SCALING)
            sprite.bottom = bottom
            sprite.left = 0
            self.backgrounds.append(sprite)

            sprite = arcade.Sprite(image, scale=SPRITE_SCALING)
            sprite.bottom = bottom
            sprite.left = sprite.width
            self.backgrounds.append(sprite)

    def pan_camera_to_user(self, panning_fraction: float = 1.0):
        # This spot would center on the user
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (
            self.camera.viewport_height / 2
        )

        if screen_center_y < 0:
            screen_center_y = 0
        user_centered = screen_center_x, screen_center_y

        self.camera.move_to(user_centered, panning_fraction)

    def on_draw(self):
        self.clear()

        self.camera.use()

        # Call draw() on all your sprite lists below
        self.backgrounds.draw(pixelated=True)
        self.player_list.draw(pixelated=True)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.player_sprite.center_x += self.player_sprite.change_x
        self.player_sprite.center_y += self.player_sprite.change_y
        self.pan_camera_to_user(0.1)

        camera_x = self.camera.position[0]

        for count, sprite in enumerate(self.backgrounds):
            layer = count // 2
            frame = count % 2
            offset = camera_x / (2 ** (layer + 1))
            jump = (camera_x - offset) // sprite.width
            final_offset = offset + (jump + frame) * sprite.width
            sprite.left = final_offset

    def update_player_speed(self):
        """ Calculate speed based on the keys pressed """

        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.LEFT:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            self.update_player_speed()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
            self.update_player_speed()


def main():
    """ Main function """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
