"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command
line with:

python -m arcade.examples.sound_demo

The top button is to play a music track.
The 3 rows of buttons are arranged such that the audio is panned in the
direction of the button, and the volume increases as you go down the column.

Left click a button to play a sound. 
If a sound is playing right click to increase volume, middle click to decrease.
"""

import typing

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Starting Template"
BUTTON_SIZE = 30


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

    def draw(self):
        super().draw(self)


class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        self.button_sprites = None

    def setup(self):
        self.button_sprites = arcade.SpriteList()

        upgrade_sound = ":resources:sounds/gameover3.wav"

        # fmt: off
        button_params = [
        #    sound        , speed, vol   , x                          , y
            [upgrade_sound, 0.1 , 0.1   , BUTTON_SIZE                , SCREEN_HEIGHT / 2 + 50 ],
            [upgrade_sound, 0.5 , 0.1   , SCREEN_WIDTH / 4           , SCREEN_HEIGHT / 2 + 50 ],
            [upgrade_sound, 1.0 , 0.1   , SCREEN_WIDTH / 2           , SCREEN_HEIGHT / 2 + 50 ],
            [upgrade_sound, 2.0 , 0.1   , SCREEN_WIDTH / 4 * 3       , SCREEN_HEIGHT / 2 + 50 ],
            [upgrade_sound, 4.0 , 0.1   , SCREEN_WIDTH - BUTTON_SIZE , SCREEN_HEIGHT / 2 + 50 ],
            
            [upgrade_sound, 0.1 , 0.5   , BUTTON_SIZE                , SCREEN_HEIGHT / 2      ],
            [upgrade_sound, 0.5 , 0.5   , SCREEN_WIDTH / 4           , SCREEN_HEIGHT / 2      ],
            [upgrade_sound, 1.0 , 0.5   , SCREEN_WIDTH / 2           , SCREEN_HEIGHT / 2      ],
            [upgrade_sound, 2.0 , 0.5   , SCREEN_WIDTH / 4 * 3       , SCREEN_HEIGHT / 2      ],
            [upgrade_sound, 4.0 , 0.5   , SCREEN_WIDTH - BUTTON_SIZE , SCREEN_HEIGHT / 2      ],
            
            [upgrade_sound, 0.1 , 1     , BUTTON_SIZE                , SCREEN_HEIGHT / 2 - 50 ],
            [upgrade_sound, 0.5 , 1     , SCREEN_WIDTH / 4           , SCREEN_HEIGHT / 2 - 50 ],
            [upgrade_sound, 1.0 , 1     , SCREEN_WIDTH / 2           , SCREEN_HEIGHT / 2 - 50 ],
            [upgrade_sound, 2.0 , 1     , SCREEN_WIDTH / 4 * 3       , SCREEN_HEIGHT / 2 - 50 ],
            [upgrade_sound, 4.0 , 1     , SCREEN_WIDTH - BUTTON_SIZE , SCREEN_HEIGHT / 2 - 50 ],
        ]
        # fmt: on

        self.button_sprites.extend([SoundButton(*param) for param in button_params])

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        self.clear()

        # Call draw() on all your sprite lists below
        self.button_sprites.draw()

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """
        self.button_sprites.update()

    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        https://api.arcade.academy/en/latest/arcade.key.html
        """
        pass

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        pass

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """
        Called whenever the mouse moves.
        """
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        hit_sprites = arcade.get_sprites_at_point((x, y), self.button_sprites)
        for sprite in hit_sprites:
            button_sprite = typing.cast(SoundButton, sprite)
            if button == arcade.MOUSE_BUTTON_LEFT:
                button_sprite.play()
            elif (
                button == arcade.MOUSE_BUTTON_RIGHT
            ):  # right click to increase volume on currently playing sound
                if not button_sprite.sound.is_complete():
                    button_sprite.volume_up()
                    button_sprite.stream_position()
            elif button == arcade.MOUSE_BUTTON_MIDDLE:
                if not button_sprite.sound.is_complete():
                    button_sprite.volume_down()
                    button_sprite.stream_position()

    def on_mouse_release(self, x, y, button, key_modifiers):
        """
        Called when a user releases a mouse button.
        """
        pass


def main():
    """Main function"""
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
