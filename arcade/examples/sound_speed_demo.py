"""
Sound Speed Demo

python -m arcade.examples.sound_speed_demo

The top button is to play a music track.
The 3 rows of buttons are arranged such that the audio is sped up in the
direction of the button, and the volume increases as you go down the column.

Left click a button to play a sound. 
If a sound is playing right click to increase volume, middle click to decrease.
"""

import typing

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Sound Speed Demo"
BUTTON_SIZE = 30

SPEED_VARIATION = [0.1, 0.5, 1.0, 2.0, 4.0]
assert len(SPEED_VARIATION) == 5
for speed in SPEED_VARIATION:
    assert speed > 0


class SoundButton(arcade.SpriteSolidColor):
    """Button, click-for-sound"""

    def __init__(self, sound_file, speed, volume, center_x, center_y):
        super().__init__(BUTTON_SIZE, BUTTON_SIZE, arcade.color.WHITE)
        self.sound = arcade.Sound(sound_file)
        self.speed = speed
        self.volume = volume
        self.center_x = center_x
        self.center_y = center_y

    def play(self):
        """Play"""
        self.sound.play(speed=self.speed, volume=self.volume)


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.button_sprites = None

    def setup(self):
        self.button_sprites = arcade.SpriteList()

        game_over_sound = ":resources:sounds/gameover3.wav"

        volume_variation = [0.1, 0.5, 1]
        y_offset = [50, 0, -50]
        button_x_spread = [
            BUTTON_SIZE,
            SCREEN_WIDTH / 4,
            SCREEN_WIDTH / 2,
            SCREEN_WIDTH / 4 * 3,
            SCREEN_WIDTH - BUTTON_SIZE,
        ]

        for vol, y_offset in zip(volume_variation, y_offset):
            for speed_setting, x_pos in zip(SPEED_VARIATION, button_x_spread):
                self.button_sprites.append(
                    SoundButton(
                        game_over_sound,
                        speed_setting,
                        vol,
                        x_pos,
                        SCREEN_HEIGHT / 2 + y_offset,
                    )
                )

    def on_draw(self):
        self.clear()
        self.button_sprites.draw()

    def on_update(self, delta_time):
        self.button_sprites.update()

    def on_mouse_press(self, x, y, button, key_modifiers):
        hit_sprites = arcade.get_sprites_at_point((x, y), self.button_sprites)
        for sprite in hit_sprites:
            button_sprite = typing.cast(SoundButton, sprite)
            if button == arcade.MOUSE_BUTTON_LEFT:
                button_sprite.play()
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                if not button_sprite.sound.is_complete():
                    button_sprite.volume_up()
                    button_sprite.stream_position()
            elif button == arcade.MOUSE_BUTTON_MIDDLE:
                if not button_sprite.sound.is_complete():
                    button_sprite.volume_down()
                    button_sprite.stream_position()


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
