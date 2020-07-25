"""
Sound library.
"""


from pathlib import Path
from typing import Union
from arcade.resources import resolve_resource_path

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
    def __init__(self, file_name: Union[str, Path], streaming: bool = False):
        """ Create and load the sound. """
        self.file_name: str = ""
        self.wav_file:Union[soloud.WavStream, soloud.Wav]

        self.voice_handle = None # needed for volume control

        if not _audiolib:
            return

        # If we should pull from local resources, replace with proper path
        file_name = resolve_resource_path(file_name)

        if not Path(file_name).is_file():
            raise FileNotFoundError(f"The sound file '{file_name}' is not a file or can't be read")
        self.file_name = str(file_name)

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

    def is_complete(self):
        """ Return true if the sound is done playing. """
        if not _audiolib:
            return False
        return not bool(_audiolib.is_valid_voice_handle(self.voice_handle))

    # --- These functions should work, but instead just return zero or otherwise
    # don't appear functional.

    def get_volume(self):
        """ Get the current volume """
        if not _audiolib:
            return 0
        return _audiolib.get_volume(self.voice_handle)

    def set_volume(self, volume):
        """
        Set the current volume.

        This can only be done after the sound has started
        playing. Setting the sound volume when there is no sound playing generates
        a TypeError. If you want to set the volume before playing, use the ``volume``
        parameter in the ``play`` method.
        """
        if not _audiolib:
            return
        _audiolib.set_volume(self.voice_handle, volume)

    def set_left_right_volume(self, left_volume, right_volume):
        """
        Set absolute left/right volume

        This can only be done after the sound has started
        playing. Setting the sound volume when there is no sound playing generates
        a TypeError. If you want to set the volume before playing, use the ``volume``
        parameter in the ``play`` method.

        """
        if not _audiolib:
            return
        _audiolib.set_pan_absolute(self.voice_handle, left_volume, right_volume)

    def get_stream_position(self):
        """
        Return where we are in the stream. This will reset back to
        zero when it is done playing.
        """
        return _audiolib.get_stream_position(self.voice_handle)


def load_sound(path: Union[str, Path]):
    """
    Load a sound.

    :param str path: Name of the sound file to load.

    :returns: Sound object
    :rtype: Sound
    """

    try:
        file_name = str(path)
        sound = Sound(file_name)
        return sound
    except Exception as ex:
        print(f"Unable to load sound file: \"{file_name}\". Exception: {ex}")
        return None


def play_sound(sound: Sound, volume: float=1.0, pan: float=0.0):
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
        msg = "Error, passed in a string as a sound. " +\
              "Make sure to use load_sound first, and use that result in play_sound."
        raise Exception(msg)
    try:
        sound.play(volume, pan)
    except Exception as ex:
        print("Error playing sound.", ex)


def stop_sound(sound: Sound):
    """
    Stop a sound that is currently playing.

    :param sound:
    """
    # noinspection PyUnresolvedReferences
    sound.wav_file.stop()
