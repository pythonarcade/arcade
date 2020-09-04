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

        assert round(self.laser_wav.get_length(), 2) == 0.16
        assert round(self.laser_wav_stream.get_length(), 2) == 0.16

        assert round(self.laser_mp3.get_length(), 2) == 1.61
        assert round(self.laser_mp3_stream.get_length(), 2) == 1.62

        assert round(self.laser_ogg.get_length(), 2) == 1.63
        assert round(self.laser_ogg_stream.get_length(), 2) == 1.61

        self.frame_count = 0

    def update(self, dt):
        self.frame_count += 1

        if self.frame_count == 1:
            self.laser_wav.play(volume=0.5)
            assert self.laser_wav.get_volume() == 0.5
            self.laser_wav.set_volume(1.0)
            assert self.laser_wav.get_volume() == 1.0

            self.laser_wav_stream.play(volume=0.5)
            assert self.laser_wav_stream.get_volume() == 0.5
            self.laser_wav_stream.set_volume(1.0)
            assert self.laser_wav_stream.get_volume() == 1.0

        if self.frame_count == 10:
            self.laser_wav.stop()
            assert self.laser_wav.is_playing() == False

            self.laser_wav_stream.stop()
            assert self.laser_wav.is_playing() == False

        if self.frame_count == 20:
            self.laser_wav.play()
            assert self.laser_wav.is_playing() == True

            self.laser_wav_stream.play()
            assert self.laser_wav_stream.is_playing() == True

        if self.frame_count == 80:
            self.laser_ogg.play(volume=0.5)
            assert self.laser_ogg.get_volume() == 0.5
            self.laser_ogg.set_volume(1.0)
            assert self.laser_ogg.get_volume() == 1.0

            self.laser_ogg_stream.play(volume=0.5)
            assert self.laser_ogg_stream.get_volume() == 0.5
            self.laser_ogg_stream.set_volume(1.0)
            assert self.laser_ogg_stream.get_volume() == 1.0

        if self.frame_count == 90:
            self.laser_ogg.stop()
            assert self.laser_ogg.is_playing() == False

            self.laser_ogg_stream.stop()
            assert self.laser_ogg_stream.is_playing() == False

        if self.frame_count == 100:
            self.laser_ogg.play()
            assert self.laser_ogg.is_playing() == True

            self.laser_ogg_stream.play()
            assert self.laser_ogg_stream.is_playing() == True

        if self.frame_count == 200:
            arcade.play_sound(self.laser_mp3, volume=0.5)
            assert self.laser_mp3.get_volume() == 0.5
            self.laser_mp3.set_volume(1.0)
            assert self.laser_mp3.get_volume() == 1.0

            arcade.play_sound(self.laser_mp3_stream, volume=0.5)
            assert self.laser_mp3_stream.get_volume() == 0.5
            self.laser_mp3_stream.set_volume(1.0)
            assert self.laser_mp3_stream.get_volume() == 1.0

        if self.frame_count == 210:
            arcade.stop_sound(self.laser_mp3)
            assert self.laser_mp3.is_playing() == False

            arcade.stop_sound(self.laser_mp3_stream)
            assert self.laser_mp3_stream.is_playing() == False

        if self.frame_count == 220:
            self.laser_mp3.play()
            assert self.laser_mp3.is_playing() == True

            self.laser_mp3_stream.play()
            assert self.laser_mp3_stream.is_playing() == True

        if self.frame_count == 210:
            self.laser_mp3.stop()
            self.laser_mp3_stream.stop()
            
    def on_draw(self):
        """
        Render the screen.
        """

        # Start the render process. This must be done before any drawing commands.
        arcade.start_render()


def test_main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.test(240)
    window.close()
