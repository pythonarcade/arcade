from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

from PIL import Image
from PIL.Image import Transpose

from arcade.resources import resolve

# from arcade import Texture
from arcade.texture import Texture
from arcade.types.rect import Rect

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

    Args:
        path (optional) Path to the image to load.
        image (optional): PIL image to use.
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
    def from_image(cls, image: Image.Image) -> SpriteSheet:
        """
        Create a sprite sheet from a PIL image.

        Args:
            image: PIL image to use.
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
        The path to the sprite sheet if it was loaded from disk.
        """
        return self._path

    @property
    def flip_flags(self) -> tuple[bool, bool]:
        """
        Query the orientation of the sprite sheet.
        This can be used to determine if the sprite sheet needs to be flipped.

        Default values are ``(False, False)``. Will be modified when
        :py:meth:`flip_left_right` or :py:meth:`flip_top_bottom` is called.

        Tuple of booleans ``(flip_left_right, flip_top_bottom)``.
        """
        return self._flip_flags

    def flip_left_right(self) -> None:
        """
        Flips the internal image left to right.
        """
        self._image = self._image.transpose(Transpose.FLIP_LEFT_RIGHT)
        self._flip_flags = (not self._flip_flags[0], self._flip_flags[1])

    def flip_top_bottom(self) -> None:
        """
        Flip the internal image top to bottom.
        """
        self._image = self._image.transpose(Transpose.FLIP_TOP_BOTTOM)
        self._flip_flags = (self._flip_flags[0], not self._flip_flags[1])

    def get_image(self, rect: Rect, y_up=False) -> Image.Image:
        """
        Slice out an image from the sprite sheet.

        Args:
            rect:
                The rectangle to crop out.
            y_up:
                Sets the coordinate space of the image to assert (0, 0)
                in the bottom left.
        """
        # PIL box is a 4-tuple: left, upper, right, and lower
        if y_up:
            return self.image.crop(
                (
                    rect.left,
                    self.image.height - rect.bottom - rect.height,
                    rect.right,
                    self.image.height - rect.bottom,
                )
            )
        else:
            return self.image.crop(
                (
                    rect.left,
                    rect.bottom,
                    rect.right,
                    rect.top,
                )
            )

    # slice an image out of the sprite sheet
    def get_texture(
        self, rect: Rect, hit_box_algorithm: HitBoxAlgorithm | None = None, y_up=False
    ) -> Texture:
        """
        Slice out texture from the sprite sheet.

        Args:
            rect:
                The rectangle to crop out.
            hit_box_algorithm:
                Hit box algorithm to use for the texture.
                If not provided, the default hit box algorithm will be used.
        """
        im = self.get_image(rect, y_up)
        texture = Texture(im, hit_box_algorithm=hit_box_algorithm)
        texture.file_path = self._path
        texture.crop_values = rect.lbwh_int
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

        Args:
            size:
                Size of each texture ``(width, height)``
            columns:
                Number of columns in the grid
            count:
                Number of textures to crop
            margin:
                The margin around each texture ``(left, right, bottom, top)``
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

        Args:
            size:
                Size of each texture ``(width, height)``
            columns:
                Number of columns in the grid
            count:
                Number of textures to crop
            margin:
                The margin around each texture ``(left, right, bottom, top)``
            hit_box_algorithm:
                Hit box algorithm to use for the textures.
                If not provided, the default hit box algorithm will be used.
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
