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
    if system == 'Windows':

        import sys
        is64bit = sys.maxsize > 2**32

        import site
        if hasattr(site, 'getsitepackages'):
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
            if is64bit:
                path = "Win64/avbin"
            else:
                path = "Win32/avbin"


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

class _Player:
    """
    Creates a media player from which a user can play audio. This audio can be played on a loop, paused, queued up,
    skipped and the volume changed.

        TODO: Need better music to play for testing

    Use:

        >>> import arcade
        >>> player = arcade.Player()
        >>> player.load_dir("arcade/examples/sounds/")
        >>> m = player.music
        >>> player.add(m[0])
        >>> player.play()

    Or:
    
        >>> import arcade
        >>> player = arcade.Player()
        >>> player.load_file("arcade/examples/sounds/rockHit2.wav")
        >>> m = player.music
        >>> player.add(m[0])
        >>> player.play()
    """

    def __init__(self):
        self._player = pyglet.media.Player()
        self._loop = True
        self._player.EOS_LOOP = self._loop

        self._current = None

        self._music = dict()

    @property
    def player(self) -> typing.Type[pyglet.media.Player]:
        """
        Get the player object from the class so it can be worked on directly.
        :return: pyglet.media.Player object
        """
        return self._player

    @property
    def playing(self) -> bool:
        """
        Checks if the player is currently playing music.
        :return: True/False to indicate if playing
        """
        return self._player.playing

    @property
    def loop(self) -> bool:
        """
        Checks the looping status of the player.
        :return: True/False to indicate if looping
        """
        return self._loop

    @property
    def music(self) -> typing.List:
        """
        Gives the user a list of all available loaded media files by name so they can be immediatly used
        by the player to add a music file to the queue.
        """
        return list(self._music.keys())

    def play(self) -> typing.NoReturn:
        """
        Starts to play the music in the queue, will not go to the next song if looping is enabled.
        """
        self._player.play()

    def stop(self) -> typing.NoReturn:
        """
        Stops the player from playing music.
        """
        self._player.pause()

    def next(self) -> typing.NoReturn:
        """
        Plays the next song in the queue even if looping is enabled.
        """
        if self.playing:
            self._player.next_source()
        else:
            raise UserWarning("Failed to play as current state is not playing music.")

    def add(self, music: str) -> typing.NoReturn:
        """
        Add a music file to the queue to be played by the player.
        As it is a queue it is first in first out, so the first song in will be played then the secon
        """
        if music in self._music:
            self._player.queue(self._music[music])
        else:
            raise UserWarning("Failed to load music, does not {} exist in loaded music.".format(music))

    def volume(self, volume: int) -> typing.NoReturn:
        """
        Allows for the volume to be changed on the music played.

        :param volume: Int from 0-100 to adjust the volume
        """
        self._player.volume = volume / 100

    def clear(self) -> typing.NoReturn:
        """
        Resets the player.
        """
        self._player = pyglet.media.Player()

    def looping(self, loop: bool) -> typing.NoReturn:
        """
        Changes if looping is enabled.
        :param loop: True/False
        """
        self._loop = loop
        self._player.EOS_LOOP = pyglet.media.SourceGroup.loop if self._loop else self._loop
        return list(self._music.keys())

    def load_dir(self, dir: str) -> typing.NoReturn:
        """
        Given a directory path loads all media files from the directory. Assumes all files are acceptable by
        pyglet media.
        :param dir: Directory path
        """
        if not os.path.exists(dir):
            raise FileExistsError("Directory does not exist.")
        if not self._music:
            self._music = {".".join(name.split(".")[0:-1]): pyglet.media.load(os.path.join(dir, name))
                           for name in os.listdir(dir)}
        else:
            for name in os.listdir(location):
                n_ = ".".join(name.split(".")[0:-1])
                self._music[n_] = pyglet.media.load(os.path.join(dir, name))

    def load_file(self, file: str) -> typing.NoReturn:
        """
        Loads a file to be used by the player.

        :param file: Location of file to be loaded
        """
        name = ".".join(file.split(".")[0:-1])
        if not self._music:
            self._music = {"{}".format(name): pyglet.media.load(file=file)}
        else:
            self._music["{}".format(name): pyglet.media.load(file=file)]


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
    
Player = _Player

del system



