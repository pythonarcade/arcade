"""
Starting Template

Once you have learned how to use classes, you can begin your program with this
template.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sound_demo

The top button is to play a music track.
The 3 rows of buttons are arranged such that the audio is panned in the direction of the button,
and the volume increases as you go down the column.

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
    """ Button, click-for-sound """

    def __init__(self, sound_file, pan, volume):
        super().__init__(BUTTON_SIZE, BUTTON_SIZE, arcade.color.WHITE)
        self.sound = arcade.Sound(sound_file)
        self.pan = pan
        self.volume = volume

    def play(self):
        """ Play """
        self.sound.play(pan=self.pan, volume=self.volume)


class AudioStreamButton(arcade.SpriteSolidColor):
    """ Button, click-for-streaming-sound """

    def __init__(self, sound_file, pan, volume):
        super().__init__(BUTTON_SIZE, BUTTON_SIZE, arcade.color.WHITE)
        self.sound = arcade.Sound(sound_file, streaming=True)
        self.pan = pan
        self.volume = volume

    def play(self):
        """ Play """
        self.sound.play(volume=self.volume, pan=self.pan)

    def volume_up(self):
        vol = self.sound.get_volume()
        self.sound.set_volume(vol + 0.1)
        print(f"Volume: {self.sound.get_volume()}")

    def volume_down(self):
        vol = self.sound.get_volume()
        self.sound.set_volume(vol - 0.1)
        print(f"Volume: {self.sound.get_volume()}")

    def stream_position(self):
        print(f"Current position: {self.sound.get_stream_position()}")


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

        y = SCREEN_HEIGHT / 2 + 150
        volume = 0.1
        button = AudioStreamButton(
            ":resources:music/funkyrobot.mp3", pan=-1.0, volume=volume
        )
        button.center_x = BUTTON_SIZE
        button.center_y = y
        self.button_sprites.append(button)

        y = SCREEN_HEIGHT / 2 + 50
        volume = 0.1
        button = SoundButton(":resources:sounds/upgrade4.wav", pan=-1.0, volume=volume)
        button.center_x = BUTTON_SIZE
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=-0.5, volume=volume)
        button.center_x = SCREEN_WIDTH / 4
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=0, volume=volume)
        button.center_x = SCREEN_WIDTH / 2
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=0.5, volume=volume)
        button.center_x = SCREEN_WIDTH / 4 * 3
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=1, volume=volume)
        button.center_x = SCREEN_WIDTH - BUTTON_SIZE
        button.center_y = y
        self.button_sprites.append(button)

        y = SCREEN_HEIGHT / 2
        volume = 0.5
        button = SoundButton(":resources:sounds/upgrade4.wav", pan=-1.0, volume=volume)
        button.center_x = BUTTON_SIZE
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=-0.5, volume=volume)
        button.center_x = SCREEN_WIDTH / 4
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=0, volume=volume)
        button.center_x = SCREEN_WIDTH / 2
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=0.5, volume=volume)
        button.center_x = SCREEN_WIDTH / 4 * 3
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=1, volume=volume)
        button.center_x = SCREEN_WIDTH - BUTTON_SIZE
        button.center_y = y
        self.button_sprites.append(button)

        y = SCREEN_HEIGHT / 2 - 50
        volume = 1
        button = SoundButton(":resources:sounds/upgrade4.wav", pan=-1.0, volume=volume)
        button.center_x = BUTTON_SIZE
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=-0.5, volume=volume)
        button.center_x = SCREEN_WIDTH / 4
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=0, volume=volume)
        button.center_x = SCREEN_WIDTH / 2
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=0.5, volume=volume)
        button.center_x = SCREEN_WIDTH / 4 * 3
        button.center_y = y
        self.button_sprites.append(button)

        button = SoundButton(":resources:sounds/upgrade4.wav", pan=1, volume=volume)
        button.center_x = SCREEN_WIDTH - BUTTON_SIZE
        button.center_y = y
        self.button_sprites.append(button)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

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
        http://arcade.academy/arcade.key.html
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
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
