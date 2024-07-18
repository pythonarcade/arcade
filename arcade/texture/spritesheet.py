from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from PIL import Image

from arcade.resources import resolve

# from arcade import Texture
from arcade.texture import Texture

if TYPE_CHECKING:
    from arcade.hitbox import HitBoxAlgorithm

OriginChoices = Literal["upper_left", "lower_left"]


class SpriteSheet:
    """
    A sprite sheet is a single image containing multiple smaller images, or
    frames. The class is used to load the image providing methods to slice out
    parts of the image as separate images or textures.

    Note that the default coordinate system used for slicing is using image coordinates
    (0, 0) in the upper left corner. This matches the coordinate system used by PIL.

    :param path: Path to the file to load.
    :param image: PIL image to use.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        image: Image.Image | None = None,
    ):
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
    def from_image(cls, image: Image.Image) -> "SpriteSheet":
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
    def path(self) -> Path | None:
        """
        The path to the sprite sheet.

        :return: The path.
        """
        return self._path

    @property
    def flip_flags(self) -> tuple[bool, bool]:
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
        Flips the internal image left to right.
        """
        self._image = self._image.transpose(Image.FLIP_LEFT_RIGHT)
        self._flip_flags = (not self._flip_flags[0], self._flip_flags[1])

    def flip_top_bottom(self) -> None:
        """
        Flip the internal image top to bottom.
        """
        self._image = self._image.transpose(Image.FLIP_TOP_BOTTOM)
        self._flip_flags = (self._flip_flags[0], not self._flip_flags[1])

    def get_image(
        self, x: int, y: int, width: int, height: int, origin: OriginChoices = "upper_left"
    ) -> Image.Image:
        """
        Slice out an image from the sprite sheet.

        :param x: X position of the image (lower left corner)
        :param y: Y position of the image (lower left corner)
        :param width: Width of the image.
        :param height: Height of the image.
        :param origin: Origin of the image. Default is "upper_left".
                       Options are "upper_left" or "lower_left".
        """
        # PIL box is a 4-tuple: left, upper, right, and lower
        if origin == "upper_left":
            return self.image.crop((x, y, x + width, y + height))
        elif origin == "lower_left":
            return self.image.crop(
                (x, self.image.height - y - height, x + width, self.image.height - y)
            )
        else:
            raise ValueError("Invalid value for origin. Must be 'upper_left' or 'lower_left'.")

    # slice an image out of the sprite sheet
    def get_texture(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        hit_box_algorithm: HitBoxAlgorithm | None = None,
        origin: OriginChoices = "upper_left",
    ) -> Texture:
        """
        Slice out texture from the sprite sheet.

        :param x: X position of the texture (lower left corner).
        :param y: Y position of the texture (lower left corner).
        :param width: Width of the texture.
        :param height: Height of the texture.
        """
        im = self.get_image(x, y, width, height, origin=origin)
        texture = Texture(im, hit_box_algorithm=hit_box_algorithm)
        texture.file_path = self._path
        texture.crop_values = x, y, width, height
        return texture

    def get_image_grid(
        self,
        size: tuple[int, int],
        columns: int,
        count: int,
        margin: tuple[int, int, int, int] = (0, 0, 0, 0),
    ) -> list[Image.Image]:
        """
        Slice a grid of textures from the sprite sheet.

        :param size: Size of each texture ``(width, height)``
        :param columns: Number of columns in the grid
        :param count: Number of textures to crop
        :param margin: The margin around each texture ``(left, right, bottom, top)``
        """
        images = []
        width, height = size
        left, right, bottom, top = margin

        for sprite_no in range(count):
            row = sprite_no // columns
            column = sprite_no % columns

            x = (width + left + right) * column
            y = (height + top + bottom) * row
            im = self.image.crop((x, y, x + width, y + height))
            images.append(im)

        return images

    def get_texture_grid(
        self,
        size: tuple[int, int],
        columns: int,
        count: int,
        margin: tuple[int, int, int, int] = (0, 0, 0, 0),
        hit_box_algorithm: HitBoxAlgorithm | None = None,
    ) -> list[Texture]:
        """
        Slice a grid of textures from the sprite sheet.

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
