"""
Sound library.

From https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
"""

from platform import system
import typing
import pyglet


class PlaysoundException(Exception):
    pass


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
    path_user = None

    if system == 'Windows':

        import sys
        is64bit = sys.maxsize > 2 ** 32

        import site
        if hasattr(site, 'getsitepackages'):
            packages = site.getsitepackages()
            user_packages = site.getuserbase()

            if appveyor:
                if is64bit:
                    path_global = "Win64/avbin"
                else:
                    path_global = "Win32/avbin"

            else:
                if is64bit:
                    path_global = packages[0] + "/lib/site-packages/arcade/Win64/avbin"
                    path_user = user_packages + "/lib/site-packages/arcade/Win64/avbin"
                else:
                    path_global = packages[0] + "/lib/site-packages/arcade/Win32/avbin"
                    path_user = user_packages + "/lib/site-packages/arcade/Win32/avbin"

        else:
            if is64bit:
                path_global = "Win64/avbin"
            else:
                path_global = "Win32/avbin"


    elif system == 'Darwin':
        from distutils.sysconfig import get_python_lib
        path_global = get_python_lib() + '/lib/site-packages/arcade/lib/libavbin.10.dylib'
        pyglet.options['audio'] = ('openal', 'pulse', 'silent')

    else:
        path_global = "avbin"
        pyglet.options['audio'] = ('openal', 'pulse', 'silent')

    pyglet.have_avbin = False
    try:
        if path_user is not None:
            pyglet.lib.load_library(path_user)
            pyglet.have_avbin = True
    except ImportError:
        pass

    if not pyglet.have_avbin:
        try:
            pyglet.lib.load_library(path_global)
            pyglet.have_avbin = True
        except ImportError:
            pass

    if not pyglet.have_avbin:
        # Try loading like its never been installed, from current directory.
        try:
            import platform
            mysys = platform.architecture()
            post = "avbin"
            if mysys[0] == '32bit':
                post = "/../Win32/avbin"
            elif mysys[1] == '64bit':
                post = "/../Win64/avbin"

            import os
            dir_path = os.path.dirname(os.path.realpath(__file__)) + post
            pyglet.lib.load_library(dir_path)
            pyglet.have_avbin = True
        except ImportError:
            pass

    if not pyglet.have_avbin:
        print("Warning - Unable to load sound library.")

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


def _loadsound_osx(filename):
    try:
        import Cocoa
    except ImportError:
        print("Unable to import Cocoa. Try running 'pip3 install PyObjC' from the terminal.")
        return

    if filename.endswith(".ogg"):
        print("Warning: .ogg (Ogg Vorbis) files are not compatible with the Mac on the Arcade library.")
        return None

    if '://' in filename:
        url = Cocoa.NSURL.URLWithString_(filename)  # don't think this works
    else:
        if not filename.startswith('/'):
            from os import getcwd
            filename = getcwd() + '/' + filename
        url = Cocoa.NSURL.fileURLWithPath_(filename)  # this seems to work

    nssound = Cocoa.NSSound.alloc().initWithContentsOfURL_byReference_(url, True)
    return nssound


def _playsound_osx(nssound):
    if nssound is None:
        print("Unable to play sound, sound passed in is 'None'.")
        return
    if not nssound.isPlaying():
        nssound.play()
    else:
        # Already playing. Make a copy and play that.
        nssound.copy().play()


def _playsound_unix(sound):
    """Play a sound using GStreamer.
    Inspired by this:
    https://gstreamer.freedesktop.org/documentation/tutorials/playback/playbin-usage.html
    """
    # pathname2url escapes non-URL-safe characters
    if isinstance(sound, pyglet.media.sources.riff.WaveSource):
        sound.play()
        return

    import os
    from urllib.request import pathname2url

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


def _load_sound_unix(filename: str) -> typing.Any:
    if filename.endswith(".wav"):
        my_sound = pyglet.media.load(filename)
        return my_sound
    else:
        return filename


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
    load_sound = _load_sound_unix

del system



