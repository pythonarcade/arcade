"""
Sound library.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

from pathlib import Path
import soloud.soloud as soloud


_audiolib = None
try:
    _audiolib = soloud.Soloud()
    _audiolib.init()
    _audiolib.set_global_volume(10)
except Exception as e:
    print(f"Warning, can't initialize soloud {e}. Sound support will be limited.")


class Sound:

    def __init__(self, file_name: str):
        # If we should pull from local resources, replace with proper path
        if file_name.startswith(":resources:"):
            import os
            path = os.path.dirname(os.path.abspath(__file__))
            file_name = f"{path}/resources/{file_name[11:]}"

        if not Path(file_name).is_file():
            raise FileNotFoundError(f"The sound file '{file_name}' is not a file or can't be read")
        self.file_name = file_name
        self.wav_file = soloud.Wav()
        self.wav_file.load(self.file_name)

    def play(self, volume=1.0, pan=0.0):

        _audiolib.play(self.wav_file,
                       aVolume = volume,
                       aPan = pan,
                       aPaused = 0,
                       aBus = 0)

class AudioStream:

    def __init__(self, file_name: str):
        # If we should pull from local resources, replace with proper path
        if file_name.startswith(":resources:"):
            import os
            path = os.path.dirname(os.path.abspath(__file__))
            file_name = f"{path}/resources/{file_name[11:]}"

        if not Path(file_name).is_file():
            raise FileNotFoundError(f"The sound file '{file_name}' is not a file or can't be read")
        self.file_name = file_name
        self.wav_file = soloud.WavStream()
        self.wav_file.load(self.file_name)
        print(self.wav_file.get_length())
        self.handle = None

    def play(self, volume=1.0, pan=0.0):
        self.wav_file.stop()
        self.handle = _audiolib.play(self.wav_file,
                                     aVolume = volume,
                                     aPan = pan,
                                     aPaused = 0,
                                     aBus = 0)

    def stop(self):
        # _audiolib.stop(self.wav_file)
        self.wav_file.stop()

    def get_length(self):
        # if self.handle:
        #     return _audiolib.get_stream_time(self.wav_file.objhandle)
        return self.wav_file.get_length()

class PlaysoundException(Exception):
    pass

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


def stop_sound(sound: Sound):
    """
    Stop a sound that is currently playing.

    :param sound:
    """
    # noinspection PyUnresolvedReferences
    sound.pause()
