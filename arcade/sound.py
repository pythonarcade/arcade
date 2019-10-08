"""
Sound library.
"""

import pyglet
from pathlib import Path


class Sound:

    def __init__(self, file_name: str):
        if not Path(file_name).is_file():
            raise FileNotFoundError(f"The sound file '{file_name}' is not a file or can't be read")
        self.file_name = file_name
        self.player = pyglet.media.load(file_name)

    def play(self):
        if self.player.is_queued:
            player = pyglet.media.load(self.file_name)
            player.play()
        else:
            self.player.play()


class PlaysoundException(Exception):
    pass


def _load_sound_library():
    """
    Special code for Windows so we grab the proper library from our directory.
    Otherwise hope the correct package is installed.
    """

    import pyglet_ffmpeg2
    pyglet_ffmpeg2.load_ffmpeg()


# Initialize static function variable
_load_sound_library._sound_library_loaded = False  # type: ignore # dynamic attribute on function obj


def load_sound(file_name: str):
    """
    Load a sound. Support for .wav files. If ffmpeg is available, will work
    with ogg and mp3 as well.

    :param str file_name: Name of the sound file to load.

    :returns: Sound object
    :rtype: Sound
    """

    try:
        sound = Sound(file_name)
        return sound
    except Exception as e:
        print(f"Unable to load sound file: \"{file_name}\". Exception: {e}")
        return None


def play_sound(sound: Sound):
    """
    Play a sound.

    :param Sound sound: Sound loaded by load_sound. Do NOT use a string here for the filename.
    """
    if sound is None:
        print("Unable to play sound, no data passed in.")
        return
    elif isinstance(sound, str):
        msg = "Error, passed in a string as a sound. " +\
              "Make sure to use load_sound first, and use that result in play_sound."
        raise Exception(msg)
    try:
        sound.play()
    except Exception as e:
        print("Error playing sound.", e)


def stop_sound(sound: pyglet.media.Source):
    """
    Stop a sound that is currently playing.

    :param sound:
    """
    # noinspection PyUnresolvedReferences
    sound.pause()


_load_sound_library()
