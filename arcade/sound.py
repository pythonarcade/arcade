import pyglet


def load_sound_library():
    """
    Special code for Windows so we grab the proper avbin from our directory.
    Otherwise hope the correct package is installed.
    """

    #lazy loading
    if not load_sound_library._sound_library_loaded:
        load_sound_library._sound_library_loaded = True
    else:
        return

    import platform
    system = platform.system()

    import os
    appveyor = not os.environ.get('APPVEYOR') is None

    from distutils.sysconfig import get_python_lib
    python_lib = get_python_lib()

    if system == "Windows":
        if appveyor:
            path = "avbin"
        else:
            import sys
            path = python_lib + "/lib/site-packages/arcade/avbin-win32-" + \
                'x64' if sys.maxsize > 2**32 else 'x86'
    elif system == 'Darwin':
        path = python_lib + '/lib/site-packages/arcade/libavbin.10.dylib'
    else:
        path = "avbin"

    pyglet.lib.load_library(path)
    pyglet.have_avbin = True

# Initialize static function variable
load_sound_library._sound_library_loaded = False

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
