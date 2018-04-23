"""
Sound library.

From https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
"""

from platform import system
import typing
import pyglet


def _shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"


def _load_sound_win(sound):
    """
    Load a sound on Windows
    """

    return sound


def _play_sound_win(sound):
    """
    Play a sound on Windows
    """
    player = pyglet.media.load(sound)
    player.play()


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
        def run_in_thread(popen_args, on_exit):
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



