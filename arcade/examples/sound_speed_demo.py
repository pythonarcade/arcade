"""
Sound Speed Demo

If Python and Arcade are installed, this example can be run from the
command line with:
python -m arcade.examples.sound_speed_demo

Left click a button to play a sound.

Each button plays the same sound sample in a slightly different way.

The middle buttons play at normal speed. The ones to the left play
slower, and the ones to the right play faster. The buttons higher on
the screen are quieter, while the ones further down are louder.
"""

import typing

import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Sound Speed Demo"
BUTTON_SIZE = 30


SPEED_VARIATION = [0.1, 0.5, 1.0, 2.0, 4.0]
MARGIN = WINDOW_WIDTH / 4
BUTTON_X_POSITIONS = [
    MARGIN,
    MARGIN + (WINDOW_WIDTH - MARGIN * 2) / 3 * 1,
    MARGIN + (WINDOW_WIDTH - MARGIN * 2) / 3 * 2,
    MARGIN + (WINDOW_WIDTH - MARGIN * 2) / 3 * 3,
    WINDOW_WIDTH - MARGIN,
]


VOLUME_VARIATION = [0.1, 0.5, 1]
Y_OFFSETS = [50, 0, -50]


class SoundButton(arcade.SpriteSolidColor):
    """
    A sprite that stores settings about how to play a sound.

    You can tell it to play a sound faster or slower, as well as adjust
    the volume of the sound.
    """
    def __init__(self, sound_file, speed, volume, center_x, center_y):
        super().__init__(BUTTON_SIZE, BUTTON_SIZE, color=arcade.color.WHITE)
        self.sound = arcade.Sound(sound_file)
        self.speed = speed
        self.volume = volume
        self.center_x = center_x
        self.center_y = center_y

    def play(self):
        self.sound.play(speed=self.speed, volume=self.volume)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.AMAZON
        self.button_sprites = arcade.SpriteList()

        # Position the grid of buttons
        # The zip function takes pieces from iterables and returns them
        # as tuples. For more information, you can see the python doc:
        # https://docs.python.org/3/library/functions.html#zip
        for vol, y_offset in zip(VOLUME_VARIATION, Y_OFFSETS):
            for speed, x_pos in zip(SPEED_VARIATION, BUTTON_X_POSITIONS):
                self.button_sprites.append(
                    SoundButton(
                        ":resources:sounds/gameover3.wav",
                        speed,
                        vol,
                        x_pos,
                        WINDOW_HEIGHT / 2 + y_offset,
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
