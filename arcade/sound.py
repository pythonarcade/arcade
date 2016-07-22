"""

Small abstraction around the sound library.

"""

import pyglet
import typing


def load_sound_library():
    """
    Special code for Windows so we grab the proper avbin from our directory.
    Otherwise hope the correct package is installed.
    """

    # lazy loading
    if not load_sound_library._sound_library_loaded:
        load_sound_library._sound_library_loaded = True
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
load_sound_library._sound_library_loaded = False


def load_sound(filename: str) -> typing.Any:
    """
    Load a sound and get it ready to play.
    """

    load_sound_library()
    source = pyglet.media.load(filename, streaming=False)
    return source


def play_sound(sound: typing.Any):
    """
    Play a previously loaded sound.
    """

    load_sound_library()
    sound.play()
