from pathlib import Path
from typing import Union

from arcade.resources import resolve_resource_path


class SoundBackend:
    """ This class is an abstraction for audio backends."""

    def __init__(self, name: str, file_name: Union[str, Path]):
        self.name = name
        self.file_name: str = ""
        
        file_name = resolve_resource_path(file_name)

        if not Path(file_name).is_file():
            raise FileNotFoundError(
                f"The sound file '{file_name}' is not a file or can't be read."
            )
        self.file_name = str(file_name)

    def play(self, volume=1.0, pan=0.0, loop=False) -> None:
        """
        Play the sound.

        :param float volume: Volume, from 0=quiet to 1=loud
        :param float pan: Pan, from -1=left to 0=centered to 1=right
        :param bool loop: Loop, false to play once, true to loop continously
        """
        raise NotImplementedError(
            "The sound backend you've selected has not implemented the 'play' method."
        )

    def stop(self) -> None:
        """
        Stop a currently playing sound.
        """
        raise NotImplementedError(
            "The sound backend you've selected has not implemented the 'stop' method."
        )

    def get_length(self) -> float:
        """ Get length of audio in seconds """
        raise NotImplementedError(
            "The sound backend you've selected has not implemented the 'get_length' method."
        )

    def get_volume(self) -> float:
        """ Get the current volume """
        raise NotImplementedError(
            "The sound backend you've selected has not implemented the 'get_volume' method."
        )

    def set_volume(self) -> None:
        """ Set the current volume """
        raise NotImplementedError(
            "The sound backend you've selected has not implemented the 'set_volume' method."
        )

    def get_stream_position(self) -> float:
        """ Return where we are in the stream. Should reset to 0 if it is done playing """
        raise NotImplementedError(
            "The sound backend you've selected has not implemented the 'get_stream_position' method."
        )

    def is_complete(self) -> bool:
        """ Return true if the sound is done playing """
        raise NotImplementedError(
            "The sound backend you've selected has not implemented the 'is_complete' method."
        )
