from PIL import Image
from pathlib import Path
from typing import Union, Tuple, Optional

from arcade.types import Rect


class SpriteSheet:
    """
    Class to hold a sprite sheet. A sprite sheet is a single image that contains
    multiple textures. Textures can be created from the sprite sheet by cropping
    out sections of the image.

    This is only a utility class. It does not have any special functionality

    :param path: Path to the file to load.
    """
    def __init__(
            self,
            path: Optional[Union[str, Path]] = None,
            image: Optional[Image.Image] = None,
        ):
        from arcade.resources import resolve_resource_path
        self._path = None
        if path:
            self._path = resolve_resource_path(path)
            self._image = Image.open(self._path).convert("RGBA")
        elif image:
            self._image = image
        else:
            raise ValueError("Must provide either path or image")

        self._flip_flags = (False, False)

    @classmethod
    def from_image(cls, image: Image.Image):
        return cls(image=image)

    @property
    def image(self) -> Image.Image:
        """
        The image of the sprite sheet.

        :return: The image.
        """
        return self._image

    @property
    def path(self) -> Optional[Path]:
        """
        The path to the sprite sheet.

        :return: The path.
        """
        return self._path

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
