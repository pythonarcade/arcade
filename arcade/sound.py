"""
Sound library.

From https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
"""

import typing


class PlaysoundException(Exception):
    pass


def _shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


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
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if errorCode:
            errorBuffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254)
            exceptionMessage = ('\n    Error ' + str(errorCode) + ' for command:'
                                '\n        ' + command.decode() +
                                '\n    ' + errorBuffer.value.decode())
            raise PlaysoundException(exceptionMessage)
        return buf.value

    alias = str(uuid.uuid4())
    win_command(f'open "{sound}" alias {alias}')
    win_command(f'set {alias} time format milliseconds')
    durationInMS = win_command(f'status {alias} length')
    return f'play {alias} from 0 to {durationInMS.decode()}'


def _play_sound_win(sound):
    """
    Play a sound on Windows
    """

    from ctypes import c_buffer, windll
    from sys import getfilesystemencoding

    def win_command(*command):
        buf = c_buffer(255)
        command = ' '.join(command).encode(getfilesystemencoding())
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if errorCode:
            errorBuffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254)
            exceptionMessage = ('\n    Error ' + str(errorCode) + ' for command:'
                                '\n        ' + command.decode() +
                                '\n    ' + errorBuffer.value.decode())
            raise PlaysoundException(exceptionMessage)
        return buf.value

    win_command(sound)

def _loadsound_osx(filename):
    import Cocoa
    if '://' in filename:
        url = Cocoa.NSURL.URLWithString_(filename)  # don't think this works
    else:
        if not filename.startswith('/'):
            from os import getcwd
            sound = getcwd() + '/' + filename
        url = Cocoa.NSURL.fileURLWithPath_(sound)  # this seems to work

    nssound = Cocoa.NSSound.alloc().initWithContentsOfURL_byReference_(url, True)
    return nssound


def _playsound_osx(nssound):
    if not nssound.isPlaying():
        nssound.play()
    else:
        # Already playing. Make a copy and play that.
        nssound.copy().play()


def _playsound_unix(sound):
    import threading
    import subprocess
    import os

    def popen_and_call(popen_args, on_exit=None):
        def run_in_thread(popen_args, onExit):
            dev_null = open(os.devnull, 'wb')
            proc = subprocess.Popen(popen_args, stdout=dev_null, stderr=dev_null)
            proc.wait()
            if on_exit is not None:
                on_exit()
            return

        thread = threading.Thread(target=run_in_thread, args=(popen_args, on_exit))
        thread.start()
        # returns immediately after the thread starts
        return thread

    my_command = ("ffplay", "-nodisp", "-autoexit", sound)
    popen_and_call(my_command)


def _load_sound_other(filename: str) -> typing.Any:
    """
    Ok, this doesn't do anything yet.

    >>> import arcade
    >>> my_sound = arcade.load_sound("arcade/examples/sounds/rockHit2.wav")
    >>> arcade.play_sound(my_sound)
    """
    return filename


from platform import system
system = system()

if system == 'Windows':
    play_sound = _play_sound_win
    load_sound = _load_sound_win
elif system == 'Darwin':
    play_sound = _playsound_osx
    load_sound = _loadsound_osx
else:
    play_sound = _playsound_unix
    load_sound = _load_sound_other

del system



