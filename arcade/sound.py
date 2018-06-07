"""
Sound library.

From https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
"""

import os
import typing
from platform import system

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
        is64bit = sys.maxsize > 2 ** 32

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
    s = pyglet.media.load(sound)
    s.file = sound
    return s


def _play_sound_win(sound: typing.Type[pyglet.media.Source]):
    """
    Play a sound on Windows
    """
    sound.play()


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


class _Player:
    """
    Creates a media player from which a user can play audio. The player can handle multiple background tracks at once,
    and because of this

        TODO: Need better music to play for testing

    Use:
        >>> import arcade
        >>> player = arcade.Player()
        >>> player.load_dir("arcade/examples/sounds/")
        >>> m = player.music
        >>> player.play(m[0])

    Or:
        >>> import arcade
        >>> player = arcade.Player()
        >>> player.load_file("arcade/examples/sounds/rockHit2.wav")
        >>> m = player.music
        >>> player.play(m[0])

    Looping can be disabled as follows
        >>> import arcade
        >>> player = arcade.Player()
        >>> player.load_file("arcade/examples/sounds/rockHit2.wav")
        >>> player.looping(False)  # Bool val passed to tell it to loop or not
        >>> m = player.music
        >>> player.play(m[0])
    """

    def __init__(self):
        self._loop = True
        self._current = None
        self._reset_on_resume = False
        self._pause_others_on_play = True

        self._music = dict()

    @property
    def player(self) -> typing.Type[pyglet.media.Player]:
        """
        Get the player object from the class so it can be worked on directly.
        :return: pyglet.media.Player object
        """
        return self._current

    @property
    def playing(self) -> bool:
        """
        Checks if the player is currently playing music.
        :return: True/False to indicate if playing
        """
        return any(player.playing for player in self._music.items())

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

    @property
    def resume_on_play(self) -> bool:
        """
        Indicates the status of resume on play. This means the track will resume from where it was stopped last.
        :return: True/False of resume on play
        """
        return self._reset_on_resume

    @resume_on_play.setter
    def resume_on_play(self, val: bool) -> typing.NoReturn:
        """
        Set the resume on play, True will acause the player to resume at the last point in the track, False will
        reset the track from the beginning.
        :param val: True/False to set resume on play
        """
        self._reset_on_resume = val

    @property
    def pause_others(self) -> bool:
        """
        Returns the value of pause others, if True it will pause the other players to allow a single player to play.
        :return: True/False of pause others when playing a new song
        """
        return self._pause_others_on_play

    @pause_others.setter
    def pause_others(self, val: bool) -> typing.NoReturn:
        """
        Sets the pause others to True or False to indicate if the other players will be paused when a new track is
        played.
        :param val: True/False of pause others when playing a new song
        """
        self._pause_others_on_play = val

    def play(self, music: str) -> typing.NoReturn:
        """
        Starts to play the music in the queue, will not go to the next song if looping is not enabled.
        """
        if music in self._music:
            if self._pause_others_on_play:
                self.stop()
            if type(self._music[music]) is not pyglet.media.Player:
                m = pyglet.media.StaticSource(self._music[music])
                self._music[music] = pyglet.media.Player()
                self._music[music].queue(m)
                self._music[music].play()
            else:
                self._music[music].play()
            self._current = self._music[music]
            if self._reset_on_resume:
                self._current.seek(0)
            self.looping(self.loop)
        else:
            raise UserWarning("Failed to load music, does not {} exist in loaded music.".format(music))

    def stop(self) -> typing.NoReturn:
        """
        Stops the player from playing music.
        """
        if self._current is not None:
            self._current.pause()

    def stop_single(self, music: str) -> typing.NoReturn:
        """
        Stops a specific track from playing.
        :param music: str name of track
        """
        if music in self._music:
            if type(self._music[music]) is not pyglet.media.Player:
                self._music[music].pause()
        else:
            raise UserWarning("Failed to load music, does not {} exist in loaded music.".format(music))

    def volume(self, volume: int, music: str="") -> typing.NoReturn:
        """
        Allows for the volume to be changed on the music played.

        :param volume: Int from 0-100 to adjust the volume
        """
        if not music:
            for player in self._music:
                if type(player) is not pyglet.media.Player:
                    player.volume = volume
        elif music not in self._music.keys():
            raise UserWarning("Music file indicated does not exisit in the player.")
        else:
            if type(self._music[music]) is pyglet.media.Player:
                self._music[music].volume = volume

    def clear(self) -> typing.NoReturn:
        """
        Resets the player.
        """
        self.stop()
        self._current = None

    def looping(self, loop: bool) -> typing.NoReturn:
        """
        Changes if looping is enabled.
        :param loop: True/False

            TODO: FIx
        """
        self._loop = loop
        for player in self._music:
            if type(player) is pyglet.media.Player:
                player.EOS_LOOP = pyglet.media.SourceGroup.loop if self._loop else pyglet.media.SourceGroup.next

    def load_dir(self, dir_: str) -> typing.NoReturn:
        """
        Given a directory path loads all media files from the directory. Assumes all files are acceptable by
        pyglet media.
        :param dir: Directory path
        """
        if not os.path.exists(dir_):
            raise FileExistsError("Directory does not exist.")
        if not self._music:
            self._music = {".".join(name.split(".")[0:-1]): load_sound(os.path.join(dir_, name))
                           for name in os.listdir(dir_)}
        else:
            for name in os.listdir(location):
                n_ = ".".join(name.split(".")[0:-1])
                self._music[n_] = load_sound(os.path.join(dir_, name))

    def load_file(self, file: str) -> typing.NoReturn:
        """
        Loads a file to be used by the player.

        :param file: Location of file to be loaded
        """
        name = ".".join(file.split(".")[0:-1])
        if not self._music:
            self._music = {"{}".format(name): load_sound(os.path.join(name))}
        else:
            self._music["{}".format(name): load_sound(os.path.join(name))]



Player = _Player

