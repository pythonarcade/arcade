"""
Pyglet Sound Backend

This uses Pyglet for all Sound functions, using built-in decoders
on Windows and Linux. On Mac, ffmpeg is shipped with Arcade and loaded
in to provide support for more file formats.

If you need ffmpeg support for Windows or Linux, the binaries simply
need placed in the "lib" folder of Arcade and they will be automatically loaded
"""
import math
from pathlib import Path
from typing import Union

import pyglet
import pyglet.media as media
from arcade.sound.backends.backend import SoundBackend


class PygletBackend(SoundBackend):
    def __init__(self, file_name: Union[str, Path], streaming: bool = False):
        super(PygletBackend, self).__init__("pyglet", file_name)
        self.source: Union[media.StaticSource, media.StreamingSource] = None
        self.player: media.Player = media.Player()
        self.player.min_distance = 100000000 #setting this allows for 2D panning with 3D audio

        self.source = media.load(self.file_name, streaming=streaming)

    def play(self, volume=1.0, pan=0.0, loop=False) -> None:
        """
        Play the sound.

        :param float volume: Volume, from 0=quiet to 1=loud
        :param float pan: Pan, from -1=left to 0=centered to 1=right
        :param bool loop: Loop, false to play once, true to loop continously
        """
        self.player.volume = volume
        self.player.position = (pan, 0.0, math.sqrt(1 - math.pow(pan, 2))) #used to mimic panning with 3D audio
        self.player.loop = loop
        self.player.queue(self.source)
        self.player.play()

    def stop(self) -> None:
        """
        Stop a currently playing sound.
        """
        self.player.pause()
        self.player.delete()

    def get_length(self) -> float:
        """ Get length of audio in seconds """
        return self.source.duration

    def get_volume(self) -> float:
        """ Get the current volume """
        return self.player.volume

    def set_volume(self, volume: float) -> None:
        """ Set the current volume """
        self.player.volume = volume

    def get_stream_position(self) -> float:
        """
        Return where we are in the stream. This will reset back to
        zero when it is done playing.
        """
        return self.player.time

    def is_complete(self) -> bool:
        """ Return true if the sound is done playing. """
        if self.player.time >= self.source.duration:
            return True
        else:
            return False

    def is_playing(self) -> bool:
        """ Return true if the sound is playing. """
        return self.player.playing