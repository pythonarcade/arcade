from PIL import Image
from pathlib import Path
from typing import Union, Tuple, Optional, List, TYPE_CHECKING

# from arcade import Texture
from arcade.types import Rect
from .texture import Texture

if TYPE_CHECKING:
    from arcade.hitbox import HitBoxAlgorithm


class SpriteSheet:
    """
    Class to hold a sprite sheet. A sprite sheet is a single image that contains
    multiple textures. Textures can be created from the sprite sheet by cropping
    out sections of the image.

    This is only a utility class. It does not have any special functionality

    :param path: Path to the file to load.
    :param image: PIL image to use.
    """
    def __init__(
        self,
        path: Optional[Union[str, Path]] = None,
        image: Optional[Image.Image] = None,
    ):
        from arcade.resources import resolve
        self._path = None
        if path:
            self._path = resolve(path)
            self._image = Image.open(self._path).convert("RGBA")
        elif image:
            self._image = image
        else:
            raise ValueError("Must provide either path or image")

        self._flip_flags = (False, False)

    @classmethod
    def from_image(cls, image: Image.Image):
        """
        Create a sprite sheet from a PIL image.

        :param image: PIL image to use.
        """
        return cls(image=image)

    @property
    def image(self) -> Image.Image:
        """
        Get or set the PIL image for this sprite sheet.
        """
        return self._image

    @image.setter
    def image(self, image: Image.Image):
        self._image = image

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

    def crop_sections(self, sections: List[Rect]):
        """
        Crop multiple textures from the sprite sheet by specifying a list of
        areas to crop.

        :param sections: List of areas to crop ``[(x, y, width, height), ...]``
        """
        pass

    def crop_grid(
        self,
        size: Tuple[int, int],
        columns: int,
        count: int,
        margin: Rect = (0, 0, 0, 0),
        hit_box_algorithm: Optional["HitBoxAlgorithm"] = None,
    ) -> List[Texture]:
        """
        Crop a grid of textures from the sprite sheet.

        :param size: Size of each texture ``(width, height)``
        :param columns: Number of columns in the grid
        :param count: Number of textures to crop
        :param margin: The margin around each texture ``(left, right, bottom, top)``
        :param hit_box_algorithm: Hit box algorithm to use for the textures.
        """
        textures = []
        width, height = size
        left, right, bottom, top = margin

        for sprite_no in range(count):
            row = sprite_no // columns
            column = sprite_no % columns

            x = (width + left + right) * column
            y = (height + top + bottom) * row
            im = self.image.crop((x, y, x + width, y + height))

            texture = Texture(im, hit_box_algorithm=hit_box_algorithm)
            texture.file_path = self._path
            texture.crop_values = x, y, width, height
            textures.append(texture)

        return textures
