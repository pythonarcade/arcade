"""
Sound library.

From https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
"""

from platform import system
import typing
import pyglet


def _load_sound_library():
    """
    Special code for Windows so we grab the proper avbin from our directory.
    Otherwise hope the correct package is installed.
    """

    # lazy loading
    if not _load_sound_library._sound_library_loaded:
        _load_sound_library._sound_library_loaded = True
    else:
        return

    import os
    appveyor = not os.environ.get('APPVEYOR') is None

    import platform
    system = platform.system()
    if system == 'Windows':

        import sys
        is64bit = sys.maxsize > 2**32

        import site
        packages = site.getsitepackages()

        if appveyor:
            if is64bit:
                path = "Win64/avbin"
            else:
                path = "Win32/avbin"

        else:
            if is64bit:
                path = packages[0] + "/lib/site-packages/arcade/Win64/avbin"
            else:
                path = packages[0] + "/lib/site-packages/arcade/Win32/avbin"
    elif system == 'Darwin':
        from distutils.sysconfig import get_python_lib
        path = get_python_lib() + '/lib/site-packages/arcade/lib/libavbin.10.dylib'
        pyglet.options['audio'] = ('openal', 'pulse', 'silent')

    else:
        path = "avbin"
        pyglet.options['audio'] = ('openal', 'pulse', 'silent')

    pyglet.lib.load_library(path)
    pyglet.have_avbin = True

# Initialize static function variable
_load_sound_library._sound_library_loaded = False


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


def _loadsound_osx(sound):
    return sound


def _playsound_osx(sound):
    player = pyglet.media.load(sound)
    player.play()


def _playsound_unix(sound):
    player = pyglet.media.load(sound)
    player.play()


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
    _load_sound_library()
    play_sound = _play_sound_win
    load_sound = _load_sound_win
elif system == 'Darwin':
    play_sound = _playsound_osx
    load_sound = _loadsound_osx
else:
    play_sound = _playsound_unix
    load_sound = _load_sound_other

del system



