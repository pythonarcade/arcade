"""
Sound Library.
"""

from pathlib import Path
from typing import Union

import arcade.sound.backends.pyglet as pyglet
from arcade.sound.backends.backend import SoundBackend

AUDIO_BACKENDS = ["pyglet"]
SELECTED_BACKEND = "pyglet"

if SELECTED_BACKEND not in AUDIO_BACKENDS:
    raise NotImplementedError(
        "unsupported Audio Backend Selected. Please use one of the following: "
        + AUDIO_BACKENDS
    )


class Sound:
    """ This class represents a sound you can play."""

    def __init__(self, file_name: Union[str, Path], streaming: bool = False):
        self.backend: SoundBackend = None

        if SELECTED_BACKEND == "pyglet":
            self.backend = pyglet.PygletBackend(str(file_name), streaming)
        else:
            raise NotImplementedError(
                "unsupported Audio Backend Selected. Please use one of the following: "
                + AUDIO_BACKENDS
            )

    def play(self, volume: float = 1.0, pan: float = 0.0, loop: bool = False) -> None:
        """
        Play the sound.

        :param float volume: Volume, from 0=quiet to 1=loud
        :param float pan: Pan, from -1=left to 0=centered to 1=right
        """
        self.backend.play(volume, pan, loop)

    def stop(self) -> None:
        """
        Stop a currently playing sound.
        """
        self.backend.stop()

    def get_length(self) -> float:
        """ Get length of audio in seconds """
        return self.backend.get_length()

    def is_complete(self) -> bool:
        """ Return true if the sound is done playing. """
        return self.backend.is_complete()

    def is_playing(self) -> bool:
        """ Return if the sound is currently playing or not """
        return self.backend.is_playing()

    def get_volume(self) -> float:
        """ Get the current volume """
        return self.backend.get_volume()

    def set_volume(self, volume) -> None:
        """
        Set the current volume.

        In the soloud backend this can only be done after the sound has started
        playing. Setting the sound volume when there is no sound playing generates
        a TypeError. If you want to set the volume before playing, use the ``volume``
        parameter in the ``play`` method.

        With pyglet backend you can set this at any time.
        """
        self.backend.set_volume(volume)

    def get_stream_position(self) -> float:
        """
        Return where we are in the stream. This will reset back to
        zero when it is done playing.
        """
        return self.backend.get_stream_position()


def load_sound(path: Union[str, Path], streaming=False) -> Sound:
    """
    Load a sound.

    :param str path: Name of the sound file to load.

    :returns: Sound object
    :rtype: Sound
    """

    try:
        file_name = str(path)
        sound = Sound(file_name, streaming)
        return sound
    except Exception as ex:
        print(f'Unable to load sound file: "{file_name}". Exception: {ex}')
        return None


def play_sound(
    sound: Sound, volume: float = 1.0, pan: float = 0.0, looping: bool = False
):
    """
    Play a sound.

    :param Sound sound: Sound loaded by load_sound. Do NOT use a string here for the filename.
    :param float volume: Volume, from 0=quiet to 1=loud
    :param float pan: Pan, from -1=left to 0=centered to 1=right
    """
    if sound is None:
        print("Unable to play sound, no data passed in.")
        return
    elif isinstance(sound, str):
        msg = (
            "Error, passed in a string as a sound. "
            + "Make sure to use load_sound first, and use that result in play_sound."
        )
        raise Exception(msg)
    try:
        sound.play(volume, pan, looping)
    except Exception as ex:
        print("Error playing sound.", ex)


def stop_sound(sound: Sound):
    """
    Stop a sound that is currently playing.

    :param sound:
    """
    sound.stop()
