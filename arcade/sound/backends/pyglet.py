import math
import os
import sys
from pathlib import Path
from typing import Union

if sys.platform == "darwin" or sys.platform.startswith("linux"):
    if "LD_LIBRARY_PATH" in os.environ:
        os.environ["LD_LIBRARY_PATH"] += ":" + "../../libs/ffmpeg/"
    else:
        os.environ["LD_LIBRARY_PATH"] = "../../libs/ffmpeg/"
else:
    os.environ["PATH"] += "../../libs/ffmpeg/"

import pyglet
import pyglet.media as media
from arcade.sound.backends.backend import SoundBackend


class PygletBackend(SoundBackend):
    def __init__(self, file_name: Union[str, Path], streaming: bool = False):
        super(PygletBackend, self).__init__("pyglet", file_name)
        self.source: Union[media.StaticSource, media.StreamingSource] = None
        self.player: media.Player = media.Player()
        self.player.min_distance = 100000000

        self.source = media.load(self.file_name, streaming=streaming)

    def play(self, volume=1.0, pan=0.0, loop=False) -> None:
        """
        Play the sound.

        :param float volume: Volume, from 0=quiet to 1=loud
        :param float pan: Pan, from -1=left to 0=centered to 1=right
        :param bool loop: Loop, false to play once, true to loop continously
        """
        self.player.volume = volume
        self.player.position = (pan, 0.0, math.sqrt(1 - math.pow(pan, 2)))
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
