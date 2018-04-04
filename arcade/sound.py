"""
Sound library.

From https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
"""

import typing
from platform import system


class PlaysoundException(Exception):
    pass


def _load_sound_win(sound):
    """
    Play a sound on Windows
    """

    '''
    Original comment from source
    Utilizes windll.winmm. Tested and known to work with MP3 and WAVE on
    Windows 7 with Python 2.7. Probably works with more file formats.
    Probably works on Windows XP thru Windows 10. Probably works with all
    versions of Python.
    Inspired by (but not copied from) Michael Gundlach <gundlach@gmail.com>'s mp3play:
    https://github.com/michaelgundlach/mp3play
    I never would have tried using windll.winmm without seeing his code.
    '''
    from ctypes import c_buffer, windll
    from sys import getfilesystemencoding
    import uuid

    def win_command(*command):
        buf = c_buffer(255)
        command = ' '.join(command).encode(getfilesystemencoding())
        error_code = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if error_code:
            error_buffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(error_code, error_buffer, 254)
            exception_message = ('\n    Error ' + str(error_code) + ' for command:'
                                 '\n        ' + command.decode() +
                                 '\n    ' + error_buffer.value.decode())
            raise PlaysoundException(exception_message)
        return buf.value

    alias = str(uuid.uuid4())
    win_command(f'open "{sound}" alias {alias}')
    win_command(f'set {alias} time format milliseconds')
    duration_in_ms = win_command(f'status {alias} length')
    return f'play {alias} from 0 to {duration_in_ms.decode()}'


def _play_sound_win(sound):
    """
    Play a sound on Windows
    """

    from ctypes import c_buffer, windll
    from sys import getfilesystemencoding

    def win_command(*command):
        buf = c_buffer(255)
        command = ' '.join(command).encode(getfilesystemencoding())
        error_code = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if error_code:
            error_buffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(error_code, error_buffer, 254)
            exception_message = ('\n    Error ' + str(error_code) + ' for command:'
                                 '\n        ' + command.decode() +
                                 '\n    ' + error_buffer.value.decode())
            raise PlaysoundException(exception_message)
        return buf.value

    win_command(sound)


def _playsound_osx(sound):
    import NSURL
    import NSSound
    from Foundation import *
    if '://' in sound:
        url = NSURL.URLWithString_(sound)  # don't think this works
    else:
        if not sound.startswith('/'):
            from os import getcwd
            sound = getcwd() + '/' + sound
        url = NSURL.fileURLWithPath_(sound)  # this seems to work

    nssound = NSSound.alloc().initWithContentsOfURL_byReference_(url, True)


def _playsound_unix(sound):
    """Play a sound using GStreamer.
    Inspired by this:
    https://gstreamer.freedesktop.org/documentation/tutorials/playback/playbin-usage.html
    """
    # pathname2url escapes non-URL-safe characters

    # try:
    import os
    try:
        from urllib.request import pathname2url
    except ImportError:
        # python 2
        from urllib import pathname2url

    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst

    Gst.init(None)

    playbin = Gst.ElementFactory.make('playbin', 'playbin')
    if sound.startswith(('http://', 'https://')):
        playbin.props.uri = sound
    else:
        playbin.props.uri = 'file://' + pathname2url(os.path.abspath(sound))

    set_result = playbin.set_state(Gst.State.PLAYING)
    if set_result != Gst.StateChangeReturn.ASYNC:
        raise PlaysoundException(
            "playbin.set_state returned " + repr(set_result))

    # FIXME: use some other bus method than poll() with block=False
    # https://lazka.github.io/pgi-docs/#Gst-1.0/classes/Bus.html
    bus = playbin.get_bus()
    bus.poll(Gst.MessageType.EOS, Gst.CLOCK_TIME_NONE)
    playbin.set_state(Gst.State.NULL)
    # except:
    #     print("Error playing sound.")


def _load_sound_other(filename: str) -> typing.Any:
    """
    Ok, this doesn't do anything yet.

    >>> import arcade
    >>> my_sound = arcade.load_sound("arcade/examples/sounds/rockHit2.wav")
    >>> arcade.play_sound(my_sound)
    """
    return filename


system_type = system()

if system_type == 'Windows':
    play_sound = _play_sound_win
    load_sound = _load_sound_win
elif system_type == 'Darwin':
    play_sound = _playsound_osx
    load_sound = _load_sound_other
else:
    play_sound = _playsound_unix
    load_sound = _load_sound_other

del system_type
