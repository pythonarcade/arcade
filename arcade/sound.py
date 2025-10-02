"""Sound Library."""

import logging
import math
import os
from pathlib import Path

import pyglet
from pyglet.media import Source

from arcade.resources import resolve

if os.environ.get("ARCADE_SOUND_BACKENDS"):
    pyglet.options.audio = tuple(v.strip() for v in os.environ["ARCADE_SOUND_BACKENDS"].split(","))
else:
    pyglet.options.audio = ("openal", "xaudio2", "directsound", "pulse", "silent")

import pyglet.media as media

__all__ = ["Sound", "load_sound", "play_sound", "stop_sound"]

logger = logging.getLogger("arcade")


class Sound:
    """Holds :ref:`playable <sound-basics-playing>` loaded audio data.

    .. important:: :ref:`Streaming <sound-loading-modes>` disables features!

    When ``streaming=True``, :py:meth:`.play` and :py:func:`play_sound`:

    * raise a :py:class:`RuntimeError` if there is already another
      active playback
    * do not support looping

    To learn about the restrictions on :ref:`streaming <sound-loading-modes>`,
    please see:

    * :ref:`sound-loading-modes-streaming`
    * The :py:class:`pyglet.media.codecs.base.StreamingSource` class used
      internally

    To learn about cross-platform loading and file format concerns,
    please see:

    * Arcade's sound documentation:

      * :ref:`sound-loading-modes`
      * :ref:`sound-compat-easy`
      * :ref:`sound-compat-loading`

    * The pyglet guide to :external+pyglet:ref:`guide-media`

    Args:
         file_name:
            The path of a file to load, optionally prefixed with a
            :ref:`resource handle <resource_handles>`.
         streaming:
            If ``True``, attempt to load data from ``file_path`` via
            via :ref:`streaming <sound-loading-modes>`.
    """

    def __init__(self, file_name: str | Path, streaming: bool = False):
        self.file_name: str = ""
        file_name = resolve(file_name)

        if not Path(file_name).is_file():
            raise FileNotFoundError(f"The sound file '{file_name}' is not a file or can't be read.")
        self.file_name = str(file_name)

        self.source: Source = media.load(self.file_name, streaming=streaming)
        """
        The :py:class:`pyglet.media.Source` object that holds the audio data.
        """

        if self.source.duration is None:
            raise ValueError(
                "Audio duration must be known when loaded, but this audio source returned `None`"
            )

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
        """Try to play this :py:class:`Sound` and return a |pyglet Player|.

        .. important:: A :py:class:`Sound` with ``streaming=True`` loses features!

                       Neither ``loop`` nor simultaneous playbacks will work. See
                       :py:class:`Sound` and :ref:`sound-loading-modes`.

        Args:
            volume: Volume (``0.0`` is silent, ``1.0`` is loudest).
            pan: Left / right channel balance (``-1`` is left,  ``0.0`` is
                center, and ``1.0`` is right).
            loop: ``True`` attempts to restart playback after finishing.
            speed: Change the speed (and pitch) of the sound. Default speed is
                ``1.0``.
        Returns:
            A |pyglet Player| for this playback.
        """
        if isinstance(self.source, media.StreamingSource) and self.source.is_player_source:
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
            # Some race condition within Pyglet can cause the player to be removed
            # from this list before we get to it, so we try and catch the ValueError
            # raised by the removal if it's already been removed.
            try:
                media.Source._players.remove(player)
            except ValueError:
                pass
            # There is a closure on player. To get the refcount to 0,
            # we need to delete this function.
            player.on_player_eos = None  # type: ignore  # pending https://github.com/pyglet/pyglet/issues/845

        player.on_player_eos = _on_player_eos  # type: ignore
        return player

    def stop(self, player: media.Player) -> None:
        """Stop and :py:meth:`~pyglet.media.player.Player.delete` ``player``.

        All references to it in the internal table for
        :py:class:`pyglet.media.Source` will be deleted.

        Args:
            player: A pyglet |pyglet Player| from :func:`play_sound`
                or :py:meth:`Sound.play`.
        """
        player.pause()
        player.delete()
        if player in media.Source._players:
            media.Source._players.remove(player)

    def get_length(self) -> float:
        """Get length of the loaded audio in seconds"""
        # We validate that duration is known when loading the source
        return self.source.duration  # type: ignore

    def is_complete(self, player: media.Player) -> bool:
        """``True`` if the sound is done playing."""
        # We validate that duration is known when loading the source
        return player.time >= self.source.duration  # type: ignore

    def is_playing(self, player: media.Player) -> bool:
        """``True`` if ``player`` is currently playing, otherwise ``False``.

        Args:
            player: A |pyglet Player| from :func:`play_sound` or
                :py:meth:`Sound.play`.

        Returns:
            ``True`` if the passed pyglet player is playing.
        """
        return player.playing

    def get_volume(self, player: media.Player) -> float:
        """Get the current volume.

        Args:
            player: A |pyglet Player| from :func:`play_sound` or
                :py:meth:`Sound.play`.
        Returns:
            A volume between ``0.0`` (silent) and ``1.0`` (full volume).
        """
        return player.volume  # type: ignore  # pending https://github.com/pyglet/pyglet/issues/847

    def set_volume(self, volume: float, player: media.Player) -> None:
        """Set the volume of a sound as it is playing.

        Args:
            volume: Floating point volume. 0 is silent, 1 is full.
            player: A |pyglet Player| from :func:`play_sound` or
                :py:meth:`Sound.play`.
        """
        player.volume = volume

    def get_stream_position(self, player: media.Player) -> float:
        """Return where we are in the stream. This will reset back to
        zero when it is done playing.

        Args:
            player: A |pyglet Player| from :func:`play_sound` or
                 :py:meth:`Sound.play`.
        """
        return player.time


def load_sound(path: str | Path, streaming: bool = False) -> Sound:
    """Load a file as a :py:class:`Sound` data object.

    .. important:: A :py:class:`Sound` with ``streaming=True`` loses features!

                   Neither ``loop`` nor simultaneous playbacks will work. See
                   :py:class:`Sound` and :ref:`sound-loading-modes`.

    Args:
        path: a path which may be prefixed with a
            :ref:`resource_handle <resource_handles>`.
        streaming: Boolean for determining if we stream the sound or
            load it all into memory. Set to ``True`` for long sounds to
            save memory, ``False`` for short sounds to speed playback.

    Returns:
        A :ref:`playable <sound-basics-playing>` instance of a
        :py:class:`Sound` object.
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
        ) from ex


def play_sound(
    sound: Sound | None,
    volume: float = 1.0,
    pan: float = 0.0,
    loop: bool = False,
    speed: float = 1.0,
) -> media.Player | None:
    """Try to play the ``sound`` and return a |pyglet Player|.

    The ``sound`` must be a loaded :py:class:`Sound` object. If you
    pass a path or :py:class:`str`, the function will raise a
    :py:class:`TypeError.`

    .. important:: A :py:class:`Sound` with ``streaming=True`` loses features!

                   Neither ``loop`` nor simultaneous playbacks will work. See
                   :py:class:`Sound` and :ref:`sound-loading-modes`.

    The output and return value depend on whether playback succeeded:
    .. # Note: substitutions don't really work inside tables, so the
    .. # pyglet player below is left as a normal class cross-reference.

    .. list-table::
       :header-rows: 1

       * - Success?
         - Console output
         - Return value

       * - No / ``sound`` is ``None``
         - Log a warning
         - ``None``

       * - Yes
         - N/A
         - A pyglet :py:class:`~pyglet.media.player.Player`

    To learn more about the ``streaming`` keyword and restrictions, please see:

    * :py:class:`Sound`
    * :ref:`sound-intermediate-playback-change-aspects-ongoing`
    * :ref:`sound-intermediate-playback-change-aspects-new`

    Args:
        sound: A :py:class:`Sound` instance or ``None``.
        volume: From ``0.0`` (silent) to ``1.0`` (max volume).
        pan: The left / right ear balance (``-1`` is left, ``0`` is center,
        and ``1`` is right)
        loop: ``True`` makes playback restart each time it reaches the end.
        speed: How fast to play. Slower than ``1.0`` deepens sound while
            values higher than ``1.0`` raise the pitch.

    Returns:
        A |pyglet Player| instance for this playback or
        ``None`` if playback failed.
    """
    if sound is None:
        logger.warning("Unable to play sound, no data passed in.")
        return None

    elif not isinstance(sound, Sound):
        raise TypeError(
            f"Error, got {sound!r} instead of an arcade.Sound."
            if not isinstance(sound, str | Path | bytes)
            else " Make sure to use load_sound first, then play the result with play_sound."
        )

    try:
        return sound.play(volume, pan, loop, speed)
    except Exception as ex:
        logger.warning("Error playing sound.", ex)
        return None


def stop_sound(player: media.Player) -> None:
    """Stop and delete a |pyglet Player| which is currently playing.

    Args:
        player: A pyglet |pyglet Player| from :py:func:`play_sound`
            or :py:meth:`Sound.play`.
    """

    if not isinstance(player, media.Player):
        raise TypeError(
            "stop_sound takes a media player object returned from the play_sound() command, not a "
            "loaded Sound object."
            if isinstance(player, Sound)
            else f"{player!r}"
        )

    player.pause()
    player.delete()
    if player in media.Source._players:
        media.Source._players.remove(player)
