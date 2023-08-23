"""
Sound Library.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Optional, Union

from arcade.resources import resolve
import pyglet

if os.environ.get("ARCADE_SOUND_BACKENDS"):
    pyglet.options["audio"] = tuple(
        v.strip() for v in os.environ["ARCADE_SOUND_BACKENDS"].split(",")
    )
else:
    pyglet.options["audio"] = ("openal", "xaudio2", "directsound", "pulse", "silent")

import pyglet.media as media

__all__ = [
    "Sound",
    "load_sound",
    "play_sound",
    "stop_sound"
]


class Sound:
    """This class represents a sound you can play."""

    def __init__(self, file_name: Union[str, Path], streaming: bool = False):
        self.file_name: str = ""
        file_name = resolve(file_name)

        if not Path(file_name).is_file():
            raise FileNotFoundError(
                f"The sound file '{file_name}' is not a file or can't be read."
            )
        self.file_name = str(file_name)

        self.source: Union[media.StaticSource, media.StreamingSource] = media.load(
            self.file_name, streaming=streaming
        )

        if self.source.duration is None:
            raise ValueError("Audio duration must be known when loaded, but this audio source returned `None`")

        self.min_distance = (
            100000000  # setting the players to this allows for 2D panning with 3D audio
        )

    def play(
        self,
        volume: float = 1.0,
        pan: float = 0.0,
        loop: bool = False,
        speed: float = 1.0,
    ) -> media.Player:
        """
        Play the sound.

        :param volume: Volume, from 0=quiet to 1=loud
        :param pan: Pan, from -1=left to 0=centered to 1=right
        :param loop: Loop, false to play once, true to loop continuously
        :param speed: Change the speed of the sound which also changes pitch, default 1.0
        """
        if (
            isinstance(self.source, media.StreamingSource)
            and self.source.is_player_source
        ):
            raise RuntimeError(
                "Tried to play a streaming source more than once."
                " Streaming sources should only be played in one instance."
                " If you need more use a Static source."
            )

        player: media.Player = media.Player()
        player.volume = volume
        player.position = (
            pan,
            0.0,
            math.sqrt(1 - math.pow(pan, 2)),
        )  # used to mimic panning with 3D audio

        # Note that the underlying attribute is pitch but "speed" is used
        # because it describes the behavior better (see #1198)
        player.pitch = speed

        player.loop = loop
        player.queue(self.source)
        player.play()
        media.Source._players.append(player)

        def _on_player_eos():
            media.Source._players.remove(player)
            # There is a closure on player. To get the refcount to 0,
            # we need to delete this function.
            player.on_player_eos = None # type: ignore  # pending https://github.com/pyglet/pyglet/issues/845

        player.on_player_eos = _on_player_eos
        return player

    def stop(self, player: media.Player) -> None:
        """
        Stop a currently playing sound.
        """
        player.pause()
        player.delete()
        if player in media.Source._players:
            media.Source._players.remove(player)

    def get_length(self) -> float:
        """Get length of audio in seconds"""
        # We validate that duration is known when loading the source
        return self.source.duration # type: ignore

    def is_complete(self, player: media.Player) -> bool:
        """Return true if the sound is done playing."""
        # We validate that duration is known when loading the source
        return player.time >= self.source.duration # type: ignore

    def is_playing(self, player: media.Player) -> bool:
        """
        Return if the sound is currently playing or not

        :param player: Player returned from :func:`play_sound`.
        :returns: A boolean, ``True`` if the sound is playing.

        """
        return player.playing

    def get_volume(self, player: media.Player) -> float:
        """
        Get the current volume.

        :param player: Player returned from :func:`play_sound`.
        :returns: A float, 0 for volume off, 1 for full volume.
        """
        return player.volume # type: ignore  # pending https://github.com/pyglet/pyglet/issues/847

    def set_volume(self, volume, player: media.Player) -> None:
        """
        Set the volume of a sound as it is playing.

        :param volume: Floating point volume. 0 is silent, 1 is full.
        :param player: Player returned from :func:`play_sound`.
        """
        player.volume = volume

    def get_stream_position(self, player: media.Player) -> float:
        """
        Return where we are in the stream. This will reset back to
        zero when it is done playing.

        :param player: Player returned from :func:`play_sound`.

        """
        return player.time


def load_sound(path: Union[str, Path], streaming: bool = False) -> Optional[Sound]:
    """
    Load a sound.

    :param path: Name of the sound file to load.
    :param streaming: Boolean for determining if we stream the sound
                           or load it all into memory. Set to ``True`` for long sounds to save
                           memory, ``False`` for short sounds to speed playback.
    :returns: Sound object which can be used by the  :func:`play_sound` function.
    """
    # Initialize the audio driver if it hasn't been already.
    # This call is to avoid audio driver initialization
    # the first time a sound is played.
    # This call is inexpensive if the driver is already initialized.
    media.get_audio_driver()

    file_name = str(path)
    try:
        return Sound(file_name, streaming)
    except Exception as ex:
        raise FileNotFoundError(
            f'Unable to load sound file: "{file_name}". Exception: {ex}'
        )


def play_sound(
    sound: Sound,
    volume: float = 1.0,
    pan: float = 0.0,
    looping: bool = False,
    speed: float = 1.0,
) -> Optional[media.Player]:
    """
    Play a sound.

    :param sound: Sound loaded by :func:`load_sound`. Do NOT use a string here for the filename.
    :param volume: Volume, from 0=quiet to 1=loud
    :param pan: Pan, from -1=left to 0=centered to 1=right
    :param looping: Should we loop the sound over and over?
    :param speed: Change the speed of the sound which also changes pitch, default 1.0
    """
    if sound is None:
        print("Unable to play sound, no data passed in.")
        return None
    elif isinstance(sound, str):
        msg = (
            "Error, passed in a string as a sound. "
            "Make sure to use load_sound first, and use that result in play_sound."
        )
        raise Exception(msg)
    try:
        return sound.play(volume, pan, looping, speed)
    except Exception as ex:
        print("Error playing sound.", ex)
        return None


def stop_sound(player: media.Player):
    """
    Stop a sound that is currently playing.

    :param player: Player returned from :func:`play_sound`.
    """
    if isinstance(player, Sound):
        raise ValueError(
            "stop_sound takes the media player object returned from the play() command, "
            "not the loaded Sound object."
        )

    if not isinstance(player, media.Player):
        raise ValueError(
            "stop_sound takes a media player object returned from the play() command."
        )

    player.pause()
    player.delete()
    if player in media.Source._players:
        media.Source._players.remove(player)
