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
    play_sound = _play_sound_win
    load_sound = _load_sound_win
elif system == 'Darwin':
    play_sound = _playsound_osx
    load_sound = _loadsound_osx
else:
    play_sound = _playsound_unix
    load_sound = _load_sound_other

del system



