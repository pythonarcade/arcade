"""
Sound library.
"""


from pathlib import Path
from typing import Union

_audiolib = None
try:
    import arcade.soloud.soloud as soloud

    _audiolib = soloud.Soloud()
    _audiolib.init()
    _audiolib.set_global_volume(10)
except Exception as e:
    print(f"Warning, can't initialize soloud {e}. Sound support will be limited.")


class Sound:
    """ This class represents a sound you can play."""
    def __init__(self, file_name: str, streaming: bool = False):
        """ Create and load the sound. """
        self.file_name: str = ""
        self.wav_file:Union[soloud.WavStream, soloud.Wav]

        self.voice_handle = None # needed for volume control

        if not _audiolib:
            return

        # If we should pull from local resources, replace with proper path
        if isinstance(file_name, str) and str(file_name).startswith(":resources:"):
            import os
            path = os.path.dirname(os.path.abspath(__file__))
            file_name = f"{path}/resources/{file_name[11:]}"

        if not Path(file_name).is_file():
            raise FileNotFoundError(f"The sound file '{file_name}' is not a file or can't be read")
        self.file_name = file_name
        if streaming:
            self.wav_file = soloud.WavStream()
        else:
            self.wav_file = soloud.Wav()
        self.wav_file.load(self.file_name)

    def play(self, volume=1.0, pan=0.0):
        """
        Play the sound.

        :param float volume: Volume, from 0=quiet to 1=loud
        :param float pan: Pan, from -1=left to 0=centered to 1=right
        """
        if not _audiolib:
            return

        self.voice_handle = _audiolib.play(self.wav_file,
                                           aVolume=volume,
                                           aPan=pan,
                                           aPaused=0,
                                           aBus=0)

    def stop(self):
        """
        Stop a currently playing sound.
        """
        if not soloud:
            return
        self.wav_file.stop()

    def get_length(self):
        """ Get length of audio in seconds """
        if not soloud:
            return 0
        return self.wav_file.get_length()

    # --- These functions should work, but instead just return zero or otherwise
    # don't appear functional.

    def get_volume(self):
        """ Get the current volume """
        if not _audiolib:
            return 0
        return _audiolib.get_volume(self.voice_handle)

    def set_volume(self, volume):
        """ Set the current volume. """
        if not _audiolib:
            return
        _audiolib.set_volume(self.voice_handle, volume)

    def set_left_right_volume(self, left_volume, right_volume):
        """ Set absolute left/right volume """
        if not _audiolib:
            return
        _audiolib.set_pan_absolute(self.voice_handle, left_volume, right_volume)

    def get_stream_position(self):
        """ This always returns zero for some unknown reason. """
        return _audiolib.get_stream_position(self.voice_handle)


def load_sound(file_name: str):
    """
    Load a sound.

    :param str file_name: Name of the sound file to load.

    :returns: Sound object
    :rtype: Sound
    """

    try:
        sound = Sound(file_name)
        return sound
    except Exception as ex:
        print(f"Unable to load sound file: \"{file_name}\". Exception: {ex}")
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
    except Exception as ex:
        print("Error playing sound.", ex)


def stop_sound(sound: Sound):
    """
    Stop a sound that is currently playing.

    :param sound:
    """
    # noinspection PyUnresolvedReferences
    sound.wav_file.stop()
