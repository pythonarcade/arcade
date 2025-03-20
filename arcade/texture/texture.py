from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import PIL.Image
import PIL.ImageDraw
import PIL.ImageOps

from arcade import hitbox
from arcade.color import TRANSPARENT_BLACK
from arcade.hitbox.base import HitBoxAlgorithm
from arcade.texture.transforms import (
    ORIENTATIONS,
    FlipLeftRightTransform,
    FlipTopBottomTransform,
    Rotate90Transform,
    Rotate180Transform,
    Rotate270Transform,
    Transform,
    TransposeTransform,
    TransverseTransform,
)
from arcade.types import RGBA255, Point2List

# from arcade.types.rect import Rect

__all__ = ["ImageData", "Texture"]


class ImageData:
    """
    A class holding the image for a texture with other metadata such as the hash.
    This information is used internally by the texture atlas to identify unique textures.

    If a hash is not provided, it will be calculated.
    By default, the hash is calculated using the sha256 algorithm.

    The ability to provide a hash directly is mainly there
    for ensuring we can load and save texture atlases to disk
    and for users to be able to allocate named regions in
    texture atlases.

    Args:
        image:
            The image for this texture
        hash:
            The hash of the image
    """

    __slots__ = ("image", "hash", "__weakref__")
    hash_func = "sha256"

    def __init__(self, image: PIL.Image.Image, hash: str | None = None, **kwargs):
        self.image = image
        """The pillow image"""
        self.hash = hash or self.calculate_hash(image)
        """The hash of the image"""

    @classmethod
    def calculate_hash(cls, image: PIL.Image.Image) -> str:
        """
        Calculates the hash of an image.

        The algorithm used is defined by the ``hash_func`` class variable.

        Args:
            image: The Pillow image to calculate the hash for
        """
        hash = hashlib.new(cls.hash_func)
        hash.update(image.tobytes())
        return hash.hexdigest()

    @property
    def width(self) -> int:
        """Width of the image in pixels."""
        return self.image.width

    @property
    def height(self) -> int:
        """Height of the image in pixels."""
        return self.image.height

    @property
    def size(self) -> tuple[int, int]:
        """The size of the image in pixels."""
        return self.image.size

    # ImageData uniqueness is based on the hash
    # -----------------------------------------
    def __hash__(self) -> int:
        return hash(self.hash)

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        return self.hash == other.hash

    def __ne__(self, other) -> bool:
        if other is None:
            return True
        if not isinstance(other, self.__class__):
            return True
        return self.hash != other.hash

    # -----------------------------------------

    def __repr__(self):
        return f"<ImageData width={self.width}, height={self.height}, hash={self.hash}>"


class Texture:
    """
    A Texture is wrapper for image data as a Pillow image,
    hit box data for this image used in collision detection
    and transformations like rotation and flipping if applied.

    Textures are by definition immutable. If you want to change
    the image data, you should create a new texture with the
    desired changes. There are some exceptions to this rule
    if you know the inner workings of the library.

    Args:
        image:
            The image or ImageData for this texture
        hit_box_algorithm:
            The algorithm to use for calculating the hit box.
        hit_box_points:
            A list of hitbox points for the texture to use (Optional).
            Completely overrides the hit box algorithm.
        hash:
            Optional unique name for the texture. Can be used to make this texture
            globally unique. By default the hash of the pixel data is used.
    """

    __slots__ = (
        "_image_data",
        "_size",
        "_vertex_order",
        "_transforms",
        "_hit_box_algorithm",
        "_hit_box_points",
        "_hash",
        "_cache_name",
        "_atlas_name",
        "_file_path",
        "_crop_values",
        "_properties",
        "__weakref__",
    )

    def __init__(
        self,
        image: PIL.Image.Image | ImageData,
        *,
        hit_box_algorithm: HitBoxAlgorithm | None = None,
        hit_box_points: Point2List | None = None,
        hash: str | None = None,
        **kwargs,
    ):
        # Overrides the hash
        self._hash = hash

        if isinstance(image, PIL.Image.Image):
            self._image_data = ImageData(image, hash=hash)
        elif isinstance(image, ImageData):
            self._image_data = image
        else:
            raise TypeError(
                f"image must be an instance of PIL.Image.Image or ImageData, not {type(image)}"
            )

        # Set the size of the texture since this is immutable
        self._size = image.width, image.height
        # The order of the texture coordinates when mapping
        # to a sprite/quad. This order is changed when the
        # texture is flipped or rotated.
        self._vertex_order = 0, 1, 2, 3

        self._hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
        if not isinstance(self._hit_box_algorithm, HitBoxAlgorithm):
            raise TypeError(
                f"hit_box_algorithm must be an instance of HitBoxAlgorithm, "
                f"not {type(self._hit_box_algorithm)}"
            )

        # Internal names
        self._cache_name: str = ""
        self._atlas_name: str = ""
        self._update_cache_names()
        self._hit_box_points: Point2List = hit_box_points or self._calculate_hit_box_points()

        # Optional filename for debugging
        self._file_path: Path | None = None
        self._crop_values: tuple[int, int, int, int] | None = None
        self._properties: dict[str, Any] = {}

    @property
    def properties(self) -> dict[str, Any]:
        """
        A dictionary of properties for this texture.
        This can be used to store any data you want.
        """
        return self._properties

    @property
    def cache_name(self) -> str:
        """
        The name of the texture used for caching (read only).
        """
        return self._cache_name

    @property
    def image_cache_name(self) -> str | None:
        """
        Get the image cache name for this texture.
        Returns ``None`` if not loaded from a file.
        """
        if self.file_path is None:
            return None

        return self.create_image_cache_name(
            self.file_path,
            self.crop_values or (0, 0, 0, 0),
        )

    @classmethod
    def create_cache_name(
        cls,
        *,
        hash: str,
        hit_box_algorithm: HitBoxAlgorithm,
        vertex_order: tuple[int, int, int, int] = (0, 1, 2, 3),
    ) -> str:
        """
        Create a cache name for the texture.

        Args:
            hash:
                The hash of the image data
            hit_box_algorithm:
                The hit box algorithm for this texture
            vertex_order:
                The current vertex order of the texture
        """
        if not isinstance(hash, str):
            raise TypeError(f"Expected str, got {type(hash)}")
        if not isinstance(hit_box_algorithm, HitBoxAlgorithm):
            raise TypeError(f"Expected HitBoxAlgorithm, got {type(hit_box_algorithm)}")

        return f"{hash}|{vertex_order}|{hit_box_algorithm.cache_name}|"

    @classmethod
    def create_atlas_name(cls, hash: str, vertex_order: tuple[int, int, int, int] = (0, 1, 2, 3)):
        """
        Create a name for the texture in a texture atlas.

        Args:
            hash:
                The hash of the image data
            vertex_order:
                The current vertex order of the texture
        """
        return f"{hash}|{vertex_order}"

    def _update_cache_names(self):
        """Update the internal cache names."""
        self._cache_name = self.create_cache_name(
            hash=self._hash or self._image_data.hash,
            hit_box_algorithm=self._hit_box_algorithm,
            vertex_order=self._vertex_order,
        )
        self._atlas_name = self.create_atlas_name(
            hash=self._hash or self._image_data.hash,
            vertex_order=self._vertex_order,
        )

    @classmethod
    def create_image_cache_name(
        cls, path: str | Path, crop: tuple[int, int, int, int] = (0, 0, 0, 0)
    ):
        """
        Create a cache name for an image.

        Args:
            path:
                The path to the image file
            crop:
                The crop values used to create the texture
        """
        return f"{str(path)}|{crop}"

    @property
    def atlas_name(self) -> str:
        """
        The name of the texture used for the texture atlas (read only).
        """
        return self._atlas_name

    @property
    def file_path(self) -> Path | None:
        """
        A Path to the file this texture was loaded from
        """
        return self._file_path

    @file_path.setter
    def file_path(self, path: Path | None):
        self._file_path = path

    @property
    def crop_values(self) -> tuple[int, int, int, int] | None:
        """
        The crop values used to create this texture,
        This is used to track the real origin of the pixel data.
        """
        return self._crop_values

    @crop_values.setter
    def crop_values(self, crop: tuple[int, int, int, int] | None):
        self._crop_values = crop

    @property
    def image(self) -> PIL.Image.Image:
        """
        Get or set the image of the texture.

        .. warning::

            This is an advanced function. Be absolutely sure
            you know the consequences of changing the image.
            It can cause problems with the texture atlas and
            hit box points.
        """
        return self._image_data.image

    @image.setter
    def image(self, image: PIL.Image.Image):
        if image.size != self._image_data.image.size:
            raise ValueError("New image must be the same size as the old image")

        self._image_data.image = image

    @property
    def image_data(self) -> ImageData:
        """
        The image data of the texture (read only).

        This is a simple wrapper around the image containing metadata like hash
        and is used to determine the uniqueness of the image in texture atlases.
        """
        return self._image_data

    @property
    def width(self) -> int:
        """
        The virtual width of the texture in pixels.

        This can be different from the actual width of the image
        if set manually. It can be used to trick sprites into
        believing the texture us much larger than it is.
        """
        return self._size[0]

    @width.setter
    def width(self, value: int):
        self._size = (value, self._size[1])

    @property
    def height(self) -> int:
        """
        The virtual width of the texture in pixels.

        This can be different from the actual height of the image
        if set manually. It can be used to trick sprites into
        believing the texture us much larger than it is.
        """
        return self._size[1]

    @height.setter
    def height(self, value: int):
        self._size = (self._size[0], value)

    @property
    def size(self) -> tuple[int, int]:
        """
        The virtual size of the texture in pixels.

        This can be different from the actual size of the image
        if set manually. It can be used to trick sprites into
        believing the texture us much larger than it is.
        """
        return self._size

    @size.setter
    def size(self, value: tuple[int, int]):
        self._size = value

    @property
    def hit_box_points(self) -> Point2List:
        """
        Get the hit box points for this texture (read only).

        Custom hit box points must be supplied during texture creation
        and should ideally not be changed after creation.
        """
        return self._hit_box_points

    @property
    def hit_box_algorithm(self) -> HitBoxAlgorithm:
        """
        (read only) The algorithm used to calculate the hit box for this texture.
        """
        return self._hit_box_algorithm

    @classmethod
    def create_empty(
        cls,
        name: str,
        size: tuple[int, int],
        color: RGBA255 = TRANSPARENT_BLACK,
        hit_box_points: Point2List | None = None,
    ) -> Texture:
        """
        Create a texture with all pixels set to the given color.

        The hit box of the returned Texture will be set to a rectangle
        with the dimensions in ``size`` unless hit_box_points are provided.

        Args:
            name:
                The unique name for this texture. This is used for caching
                and uniqueness in texture atlases.
            size:
                The xy size of the internal image
            color:
                The color to fill the texture with
            hit_box_points:
                A list of hitbox points for the texture
        """
        return Texture(
            image=PIL.Image.new("RGBA", size, color),
            hash=name,
            hit_box_algorithm=hitbox.algo_bounding_box,
            hit_box_points=hit_box_points,
        )

    # ----- Transformations -----

    def flip_left_right(self) -> Texture:
        """
        Create a new texture that is flipped left to right from this texture.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.transform(FlipLeftRightTransform)

    def flip_top_bottom(self) -> Texture:
        """
        Create a new texture that is flipped top to bottom from this texture.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.transform(FlipTopBottomTransform)

    def flip_horizontally(self) -> Texture:
        """
        Create a new texture that is flipped horizontally from this texture.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.flip_left_right()

    def flip_vertically(self) -> Texture:
        """
        Create a new texture that is flipped vertically from this texture.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.flip_top_bottom()

    def flip_diagonally(self) -> Texture:
        """
        Creates a new texture that is flipped diagonally from this texture.
        This is an alias for :func:`transpose`.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.transpose()

    def transpose(self) -> Texture:
        """
        Creates a new texture that is transposed from this texture.
        This flips the texture diagonally from lower right to upper left.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.transform(TransposeTransform)

    def transverse(self) -> Texture:
        """
        Creates a new texture that is transverse from this texture.
        This flips the texture diagonally from lower left to upper right.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.transform(TransverseTransform)

    def rotate_90(self, count: int = 1) -> Texture:
        """
        Create a new texture that is rotated 90 degrees from this texture.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        Args:
            count: Number of 90 degree steps to rotate.
        """
        angles = [None, Rotate90Transform, Rotate180Transform, Rotate270Transform]
        count = count % 4
        transform = angles[count]
        if transform is None:
            return self
        return self.transform(transform)

    def rotate_180(self) -> Texture:
        """
        Create a new texture that is rotated 180 degrees from this texture.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.transform(Rotate180Transform)

    def rotate_270(self) -> Texture:
        """
        Create a new texture that is rotated 270 degrees from this texture.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).
        """
        return self.transform(Rotate270Transform)

    def transform(
        self,
        transform: type[Transform],
    ) -> Texture:
        """
        Create a new texture with the given transform applied.

        Args:
            transform: Transform to apply
        """
        new_hit_box_points = transform.transform_hit_box_points(self._hit_box_points)
        texture = Texture(
            self.image_data,
            hit_box_algorithm=self._hit_box_algorithm,
            hit_box_points=new_hit_box_points,
            hash=self._hash,
        )
        texture.width = self.width
        texture.height = self.height
        texture._vertex_order = transform.transform_vertex_order(self._vertex_order)
        texture.file_path = self.file_path
        texture.crop_values = self.crop_values

        # Swap width and height of the texture if needed
        old_rotation = ORIENTATIONS[self._vertex_order][0]
        new_rotation = ORIENTATIONS[texture._vertex_order][0]
        old_swapped = abs(old_rotation) % 180 != 0
        new_swapped = abs(new_rotation) % 180 != 0
        if old_swapped != new_swapped:
            texture.width, texture.height = self.height, self.width

        texture._update_cache_names()
        return texture

    def crop(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> Texture:
        """
        Create a new texture from a sub-section of this texture.

        If the crop is the same size as the original texture or
        the crop is 0 width or height, the original texture is
        returned.

        Args:
            x:
                X position to start crop
            y:
                Y position to start crop
            width:
                Width of crop
            height:
                Height of crop
        """
        # Return self if the crop is the same size as the original image
        if width == self.image.width and height == self.image.height and x == 0 and y == 0:
            return self

        # Return self width and height is 0
        if width == 0 and height == 0:
            return self

        self.validate_crop(self.image, x, y, width, height)

        area = (x, y, x + width, y + height)
        image = self.image.crop(area)
        image_data = ImageData(image)
        texture = Texture(
            image_data,
            hit_box_algorithm=self._hit_box_algorithm,
        )
        texture.crop_values = (x, y, width, height)
        return texture

    # ----- Utility functions -----

    @staticmethod
    def validate_crop(image: PIL.Image.Image, x: int, y: int, width: int, height: int) -> None:
        """
        Validate the crop values for a given image.

        Args:
            image:
                The image to crop
            x:
                X position to start crop
            y:
                Y position to start crop
            width:
                Width of crop
            height:
                Height of crop
        """
        if x < 0 or y < 0 or width < 0 or height < 0:
            raise ValueError(f"crop values must be positive: {x}, {y}, {width}, {height}")
        if x >= image.width:
            raise ValueError(f"x position is outside of texture: {x}")
        if y >= image.height:
            raise ValueError(f"y position is outside of texture: {y}")
        if x + width - 1 >= image.width:
            raise ValueError(f"width is outside of texture: {width + x}")
        if y + height - 1 >= image.height:
            raise ValueError(f"height is outside of texture: {height + y}")

    def _calculate_hit_box_points(self) -> Point2List:
        """
        Calculate the hit box points for this texture based on the configured
        hit box algorithm. This is usually done on texture creation
        or when the hit box points are requested the first time.
        """
        return self._hit_box_algorithm.calculate(self.image)
