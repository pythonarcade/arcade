import os
from pathlib import Path

import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """
        Initializer
        """
        super().__init__(width, height)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        arcade.set_background_color(arcade.color.WHITE)
        self.laser_wav = arcade.load_sound(":resources:sounds/laser1.wav")
        self.laser_mp3 = arcade.load_sound(":resources:sounds/laser1.mp3")
        self.laser_ogg = arcade.load_sound(":resources:sounds/laser1.ogg")

        self.laser_wav_stream = arcade.load_sound(":resources:sounds/laser1.wav", streaming=True)
        self.laser_mp3_stream = arcade.load_sound(":resources:sounds/laser1.mp3", streaming=True)
        self.laser_ogg_stream = arcade.load_sound(":resources:sounds/laser1.ogg", streaming=True)

        self.frame_count = 0

        self.player = None

    def update(self, dt):
        self.frame_count += 1

        if self.frame_count == 1:
            self.player = self.laser_wav.play(volume=0.5)
            assert self.laser_wav.get_volume(self.player) == 0.5
            self.laser_wav.set_volume(1.0, self.player)
            assert self.laser_wav.get_volume(self.player) == 1.0

        if self.frame_count == 20:
            assert self.laser_wav.is_playing(self.player) == True
            self.laser_wav.stop(self.player)
            assert self.laser_wav.is_playing(self.player) == False

            self.player = self.laser_wav_stream.play(volume=0.5)
            assert self.laser_wav_stream.get_volume(self.player) == 0.5
            self.laser_wav_stream.set_volume(1.0, self.player)
            assert self.laser_wav_stream.get_volume(self.player) == 1.0

        if self.frame_count == 40:
            assert self.laser_wav_stream.is_playing(self.player) == True
            self.laser_wav_stream.stop(self.player)
            assert self.laser_wav_stream.is_playing(self.player) == False

            self.player = self.laser_ogg.play(volume=0.5)
            assert self.laser_ogg.get_volume(self.player) == 0.5
            self.laser_ogg.set_volume(1.0, self.player)
            assert self.laser_ogg.get_volume(self.player) == 1.0

        if self.frame_count == 60:
            assert self.laser_ogg.is_playing(self.player) == True
            self.laser_ogg.stop(self.player)
            assert self.laser_ogg.is_playing(self.player) == False

            self.player = self.laser_ogg_stream.play(volume=0.5)
            assert self.laser_ogg_stream.get_volume(self.player) == 0.5
            self.laser_ogg_stream.set_volume(1.0, self.player)
            assert self.laser_ogg_stream.get_volume(self.player) == 1.0

        if self.frame_count == 80:
            assert self.laser_ogg_stream.is_playing(self.player) == True
            self.laser_ogg_stream.stop(self.player)
            assert self.laser_ogg_stream.is_playing(self.player) == False

            self.player = self.laser_mp3.play(volume=0.5)
            assert self.laser_mp3.get_volume(self.player) == 0.5
            self.laser_mp3.set_volume(1.0, self.player)
            assert self.laser_mp3.get_volume(self.player) == 1.0

        if self.frame_count == 100:
            assert self.laser_mp3.is_playing(self.player) == True
            self.laser_mp3.stop(self.player)
            assert self.laser_mp3.is_playing(self.player) == False

            self.player = self.laser_mp3_stream.play(volume=0.5)
            assert self.laser_mp3_stream.get_volume(self.player) == 0.5
            self.laser_mp3_stream.set_volume(1.0, self.player)
            assert self.laser_mp3_stream.get_volume(self.player) == 1.0

        if self.frame_count == 120:
            assert self.laser_mp3_stream.is_playing(self.player) == True
            self.laser_mp3_stream.stop(self.player)
            assert self.laser_mp3_stream.is_playing(self.player) == False



    def on_draw(self):
        """
        Render the screen.
        """

        # Start the render process. This must be done before any drawing commands.
        arcade.start_render()


def test_main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.test(140)
    window.close()
