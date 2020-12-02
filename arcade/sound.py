"""
Sound Library.
"""

import math
from pathlib import Path
from typing import Optional, Union

import pyglet
import pyglet.media as media
from arcade.resources import resolve_resource_path


class Sound:
    """ This class represents a sound you can play."""

    def __init__(self, file_name: Union[str, Path], streaming: bool = False):
        self.file_name: str = ""

        file_name = resolve_resource_path(file_name)

        if not Path(file_name).is_file():
            raise FileNotFoundError(
                f"The sound file '{file_name}' is not a file or can't be read."
            )
        self.file_name = str(file_name)

        self.source: Union[media.StaticSource, media.StreamingSource] = media.load(self.file_name, streaming=streaming)

        self.min_distance = 100000000 #setting the players to this allows for 2D panning with 3D audio

    def play(self, volume: float = 1.0, pan: float = 0.0, loop: bool = False) -> media.Player:
        """
        Play the sound.

        :param float volume: Volume, from 0=quiet to 1=loud
        :param float pan: Pan, from -1=left to 0=centered to 1=right
        :param bool loop: Loop, false to play once, true to loop continously
        """
        player: media.Player = media.Player()
        player.volume = volume
        player.position = (pan, 0.0, math.sqrt(1 - math.pow(pan, 2))) #used to mimic panning with 3D audio
        player.loop = loop
        player.queue(self.source)
        player.play()
        media.Source._players.append(player)

        def _on_player_eos():
            media.Source._players.remove(player)
            # There is a closure on player. To get the refcount to 0,
            # we need to delete this function.
            player.on_player_eos = None

        player.on_player_eos = _on_player_eos
        return player

    def stop(self, player: media.Player) -> None:
        """
        Stop a currently playing sound.
        """
        player.pause()
        player.delete()
        media.Source._players.remove(player)

    def get_length(self) -> float:
        """ Get length of audio in seconds """
        return self.source.get_length()

    def is_complete(self, player: media.Player) -> bool:
        """ Return true if the sound is done playing. """
        if player.time >= self.source.duration:
            return True
        else:
            return False

    def is_playing(self, player: media.Player) -> bool:
        """
        Return if the sound is currently playing or not

        :param pyglet.media.Player player: Player returned from :func:`play_sound`.
        :returns: A boolean, ``True`` if the sound is playing.
        :rtype: bool

        """
        return player.playing

    def get_volume(self, player: media.Player) -> float:
        """
        Get the current volume.

        :param pyglet.media.Player player: Player returned from :func:`play_sound`.
        :returns: A float, 0 for volume off, 1 for full volume.
        :rtype: float
        """
        return player.volume

    def set_volume(self, volume, player: media.Player) -> None:
        """
        Set the volume of a sound as it is playing.

        :param float volume: Floating point volume. 0 is silent, 1 is full.
        :param pyglet.media.Player player: Player returned from :func:`play_sound`.
        """
        player.volume = volume

    def get_stream_position(self, player: media.Player) -> float:
        """
        Return where we are in the stream. This will reset back to
        zero when it is done playing.

        :param pyglet.media.Player player: Player returned from :func:`play_sound`.

        """
        return player.time


def load_sound(path: Union[str, Path], streaming: bool =False) -> Optional[Sound]:
    """
    Load a sound.

    :param Path path: Name of the sound file to load.
    :param bool streaming: Boolean for determining if we stream the sound
                           or load it all into memory. Set to ``True`` for long sounds to save
                           memory, ``False`` for short sounds to speed playback.
    :returns: Sound object which can be used by the  :func:`play_sound` function.
    :rtype: Sound
    """

    try:
        file_name = str(path)
        sound = Sound(file_name, streaming)
        return sound
    except Exception as ex:
        print(f'Unable to load sound file: "{file_name}". Exception: {ex}')
        return None


def play_sound(
    sound: Sound, volume: float = 1.0, pan: float = 0.0, looping: bool = False
) -> media.Player:
    """
    Play a sound.

    :param Sound sound: Sound loaded by :func:`load_sound`. Do NOT use a string here for the filename.
    :param float volume: Volume, from 0=quiet to 1=loud
    :param float pan: Pan, from -1=left to 0=centered to 1=right
    """
    if sound is None:
        print("Unable to play sound, no data passed in.")
        return
    elif isinstance(sound, str):
        msg = (
            "Error, passed in a string as a sound. "
            + "Make sure to use load_sound first, and use that result in play_sound."
        )
        raise Exception(msg)
    try:
        return sound.play(volume, pan, looping)
    except Exception as ex:
        print("Error playing sound.", ex)


def stop_sound(player: media.Player):
    """
    Stop a sound that is currently playing.

    :param pyglet.media.Player player: Player returned from :func:`play_sound`.
    """
    player.pause()
    player.delete()
    media.Source._players.remove(player)
