import pyglet


_sound_library_loaded = False


def load_sound_library():
    """
    Special code for Windows so we grab the proper avbin from our directory.
    Otherwise hope the correct package is installed.
    """

    #lazy loading
    if not _sound_library_loaded:
        _sound_library_loaded = True
    else:
        return

    import os
    appveyor = not os.environ.get('APPVEYOR') is None
    if os.name == "nt":

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
    else:
        path = "avbin"

    pyglet.lib.load_library(path)
    pyglet.have_avbin = True


def load_sound(filename):
    """
    Load a sound and get it ready to play.
    """

    load_sound_library()
    source = pyglet.media.load(filename, streaming=False)
    return source


def play_sound(sound):
    """
    Play a previously loaded sound.
    """

    load_sound_library()
    sound.play()
