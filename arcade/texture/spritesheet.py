from PIL import Image
from pathlib import Path
from typing import Union, Tuple

import arcade
from arcade.types import Rect


class SpriteSheet:
    """
    Class to hold a sprite sheet. A sprite sheet is a single image that contains
    multiple textures. Textures can be created from the sprite sheet by cropping
    out sections of the image.

    This is only a utility class. It does not have any special functionality

    :param path: Path to the file to load.
    """
    def __init__(self, path: Union[str, Path]):
        self._path = path
        path = arcade.resources.resolve_resource_path(path)
        self._image = Image.open(path).convert("RGBA")
        self._flip_flags = (False, False)

    @property
    def flip_flags(self) -> Tuple[bool, bool]:
        """
        Query the orientation of the sprite sheet.
        This can be used to determine if the sprite sheet needs to be flipped.

        Default values are ``(False, False)``. Will be modified when
        :py:meth:`flip_left_right` or :py:meth:`flip_top_bottom` is called.

        :return: Tuple of booleans ``(flip_left_right, flip_top_bottom)``.
        """
        return self._flip_flags

    def flip_left_right(self) -> None:
        """
        Flip the sprite sheet left/right.
        """
        self._image = self._image.transpose(Image.FLIP_LEFT_RIGHT)
        self._flip_flags = (not self._flip_flags[0], self._flip_flags[1])

    def flip_top_bottom(self):
        """
        Flip the sprite sheet up/down.
        """
        self._image = self._image.transpose(Image.FLIP_TOP_BOTTOM)
        self._flip_flags = (self._flip_flags[0], not self._flip_flags[1])

    def crop(self, area: Rect):
        """
        Crop a texture from the sprite sheet.

        :param area: Area to crop ``(x, y, width, height)``
        """
        pass

    def crop_grid(self, width: int, height: int, count: int, column_count: int, spacing: int = 0):
        """
        Crop a grid of textures from the sprite sheet.

        :param width: Width of the crop.
        :param height: Height of the crop.
        :param count: Number of textures to crop.
        :param column_count: Number of columns in the grid.
        :param spacing: Spacing between the textures.
        """
        pass
