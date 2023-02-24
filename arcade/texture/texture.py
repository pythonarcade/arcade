import logging
import hashlib
from typing import Optional, Tuple, List, Type, Union, TYPE_CHECKING
from pathlib import Path

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

from arcade.types import Color
from arcade.texture.transforms import (
    Transform,
    FlipLeftToRightTransform,
    FlipTopToBottomTransform,
    Rotate90Transform,
    Rotate180Transform,
    Rotate270Transform,
    TransposeTransform,
    TransverseTransform,
    # get_shortest_transform,
)
from arcade.types import PointList
from arcade.color import TRANSPARENT_BLACK
from arcade.hitbox import HitBoxAlgorithm
from arcade import cache
from arcade import hitbox

if TYPE_CHECKING:
    from arcade.sprite import Sprite
    from arcade.sprite_list import SpriteList

LOG = logging.getLogger(__name__)


class ImageData:
    """
    A class holding the image for a texture with other metadata such as the hash.
    This information is used internally by the texture atlas to identify unique textures.

    If a hash is not provided, it will be calculated.
    It's important that all hashes are of the same type.
    By default, the hash is calculated using the sha256 algorithm.

    The ability to provide a hash directly is mainly there
    for ensuring we can load and save texture atlases to disk.

    :param PIL.Image.Image image: The image for this texture
    :param str hash: The hash of the image
    """
    hash_func = "sha256"

    def __init__(self, image: PIL.Image.Image, hash: Optional[str] = None):
        self.image = image
        self.hash = hash or self.calculate_hash(image)

    @classmethod
    def calculate_hash(cls, image: PIL.Image.Image) -> str:
        """
        Calculates the hash of an image.

        The algorithm used is defined by the ``hash_func`` class variable.
        """
        hash = hashlib.new(cls.hash_func)
        hash.update(image.tobytes())
        return hash.hexdigest()

    @property
    def width(self) -> int:
        """
        The width of the image
        """
        return self.image.width

    @property
    def height(self) -> int:
        """
        The height of the image
        """
        return self.image.height

    @property
    def size(self) -> Tuple[int, int]:
        """
        The size of the image
        """
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

    def __del__(self):
        pass
        # print("ImageData.__del__", self)


class Texture:
    """
    An arcade.Texture is simply a wrapper for image data as a Pillow image
    and the hit box data for this image used in collision detection.
    Usually created by the :class:`load_texture` or :class:`load_textures` commands.

    :param PIL.Image.Image image: The image or ImageData for this texture
    :param str hit_box_algorithm: The algorithm to use for calculating the hit box.
    :param PointList hit_box_points: List of points for the hit box (Optional).
                                     Completely overrides the hit box algorithm.
    :param str hash: Optional unique name for the texture. Can be used to make this texture
                     globally unique. By default the hash of the pixel data is used.
    """
    def __init__(
        self,
        image: Union[PIL.Image.Image, ImageData],
        *,
        hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
        hit_box_points: Optional[PointList] = None,
        hash: Optional[str] = None,
        **kwargs,
    ):
        # Overrides the hash
        self._hash = hash

        if isinstance(image, PIL.Image.Image):
            self._image_data = ImageData(image, hash=hash)
        elif isinstance(image, ImageData):
            self._image_data = image
        else:
            raise ValueError(
                "image must be an instance of PIL.Image.Image or ImageData, "
                f"not {type(image)}"
            )

        # Set the size of the texture since this is immutable
        self._size = image.width, image.height
        # The order of the texture coordinates when mapping
        # to a sprite/quad. This order is changed when the
        # texture is flipped or rotated.
        self._vertex_order = 0, 1, 2, 3
        # List of transforms applied to this texture
        self._transforms: List[Type[Transform]] = []

        # Internal sprite stuff for drawing
        self._sprite: Optional[Sprite] = None
        self._sprite_list: Optional[SpriteList] = None

        self._hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
        if not isinstance(self._hit_box_algorithm, HitBoxAlgorithm):
            raise ValueError(
                f"hit_box_algorithm must be an instance of HitBoxAlgorithm, not {type(self._hit_box_algorithm)}"
            )

        # Internal names
        self._cache_name: str = ""
        self._atlas_name: str = ""
        self._update_cache_names()
        self._hit_box_points: PointList = hit_box_points or self._calculate_hit_box_points()

        # Optional filename for debugging
        self._origin: Optional[str] = None

    @property
    def cache_name(self) -> str:
        """
        The name of the texture used for caching (read only).

        :return: str 
        """
        return self._cache_name

    @classmethod
    def create_cache_name(
        cls,
        *,
        hash: str,
        hit_box_algorithm: HitBoxAlgorithm,
        vertex_order: Tuple[int, int, int, int] = (0, 1, 2, 3),
    ) -> str:
        """
        Create a cache name for the texture.

        :param ImageData image_data: The image data
        :param hit_box_algorithm: The hit box algorithm
        :param dict hit_box_args: The hit box algorithm arguments
        :param Tuple[int, int, int, int] vertex_order: The vertex order
        :return: str
        """
        if not isinstance(hash, str):
            raise TypeError(f"Expected str, got {type(hash)}")
        if not isinstance(hit_box_algorithm, HitBoxAlgorithm):
            raise TypeError(f"Expected HitBoxAlgorithm, got {type(hit_box_algorithm)}")

        return (
            f"{hash}|{vertex_order}|{hit_box_algorithm.name}|{hit_box_algorithm.param_str}"
        )

    @classmethod
    def create_atlas_name(cls, hash: str, vertex_order: Tuple[int, int, int, int] = (0, 1, 2, 3)):
        return f"{hash}|{vertex_order}"

    def _update_cache_names(self):
        """
        Update the internal cache names.
        """
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
        cls,
        path: Union[str, Path],
        crop: Tuple[int, int, int, int] = (0, 0, 0, 0)
    ):
        return f"{str(path)}|{crop}"

    @property
    def atlas_name(self) -> str:
        """
        The name of the texture used for the texture atlas (read only).

        :return: str 
        """
        return self._atlas_name

    @property
    def origin(self) -> Optional[str]:
        """
        User defined metadata for the origin of this texture.

        This is simply metadata useful for debugging.

        :return: str
        """
        return self._origin

    @origin.setter
    def origin(self, value: str):
        self._origin = value

    @property
    def image(self) -> PIL.Image.Image:
        """
        Get or set the image of the texture.

        .. warning::

            This is an advanced function. Be absolutely sure
            you know the consequences of changing the image.
            It can cause problems with the texture atlas and
            hit box points.

        :param PIL.Image.Image image: The image to set
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

        This is a simple wrapper around the image
        containing metadata like hash and is used
        to determine the uniqueness of the image
        in texture atlases.

        :return: ImageData 
        """
        return self._image_data

    @property
    def width(self) -> int:
        """
        The virtual width of the texture in pixels.
        This can be different from the actual width
        if the texture has been transformed or the
        size have been set manually.

        :rtype: int
        """
        return self._size[0]

    @width.setter
    def width(self, value: int):
        self._size = (value, self._size[1])

    @property
    def height(self) -> int:
        """
        The virtual width of the texture in pixels.

        This can be different from the actual width
        if the texture has been transformed or the
        size have been set manually.

        :rtype: int
        """
        return self._size[1]

    @height.setter
    def height(self, value: int):
        self._size = (self._size[0], value)

    @property
    def size(self) -> Tuple[int, int]:
        """
        The virtual size of the texture in pixels.

        This can be different from the actual width
        if the texture has been transformed or the
        size have been set manually.

        :rtype: Tuple[int, int]
        """
        return self._size

    @size.setter
    def size(self, value: Tuple[int, int]):
        self._size = value

    @property
    def hit_box_points(self) -> PointList:
        """
        Get the hit box points for this texture.

        Custom hit box points must be supplied during texture creation
        and should ideally not be changed after creation.

        :return: PointList
        """
        return self._hit_box_points

    @property
    def hit_box_algorithm(self) -> HitBoxAlgorithm:
        """
        (read only) The algorithm used to calculate the hit box for this texture.
        """
        return self._hit_box_algorithm

    @classmethod
    def create_filled(cls, name: str, size: Tuple[int, int], color: Color) -> "Texture":
        """
        Create a filled texture. This is an alias for :py:meth:`create_empty`.

        :param str name: Name of the texture
        :param Tuple[int, int] size: Size of the texture
        :param Color color: Color of the texture
        :return: Texture 
        """
        return cls.create_empty(name, size, color)

    @classmethod
    def create_empty(
        cls,
        name: str,
        size: Tuple[int, int],
        color: Color = (0, 0, 0, 0),
    ) -> "Texture":
        """
        Create a texture with all pixels set to transparent black.

        The hit box of the returned Texture will be set to a rectangle
        with the dimensions in ``size`` because there is no non-blank
        pixel data to calculate a hit box.

        :param str name: The unique name for this texture
        :param Tuple[int,int] size: The xy size of the internal image

        This function has multiple uses, including:

            - Allocating space in texture atlases
            - Generating custom cached textures from component images

        The internal image can be altered with Pillow draw commands and
        then written/updated to a texture atlas. This works best for
        infrequent changes such as generating custom cached sprites.
        For frequent texture changes, you should instead render directly
        into the texture atlas.

        .. warning::

           If you plan to alter images using Pillow, read its
           documentation thoroughly! Some of the functions can have
           unexpected behavior.

           For example, if you want to draw one or more images that
           contain transparency onto a base image that also contains
           transparency, you will likely need to use
           `PIL.Image.alpha_composite`_ as part of your solution.
           Otherwise, blending may behave in unexpected ways.

           This is especially important for customizable characters.

        .. _PIL.Image.alpha_composite: https://pillow.readthedocs.io/en/stable/\
                                       reference/Image.html#PIL.Image.alpha_composite

        Be careful of your RAM usage when using this function. The
        Texture this method returns will have a new internal RGBA
        Pillow image which uses 4 bytes for every pixel in it.
        This will quickly add up if you create many large Textures.

        If you want to create more than one blank texture with the same
        dimensions, you can save CPU time and RAM by calling this
        function once, then passing the ``image`` attribute of the
        resulting Texture object to the class constructor for each
        additional blank Texture instance you would like to create.
        This can be especially helpful if you are creating multiple
        large Textures.

        """
        return Texture(
            image=PIL.Image.new("RGBA", size, TRANSPARENT_BLACK),
            hash=name,
            hit_box_algorithm=hitbox.algo_bounding_box,
        )

    def remove_from_cache(self, ignore_error: bool = True) -> None:
        """
        Remove this texture from the cache.

        :param bool ignore_error: If True, ignore errors if the texture is not in the cache
        :return: None
        """
        cache.texture_cache.delete(self)

    def flip_left_to_right(self) -> "Texture":
        """
        Flip the texture left to right / horizontally.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture 
        """
        return self._new_texture_transformed(FlipLeftToRightTransform)

    def flip_top_to_bottom(self) -> "Texture":
        """
        Flip the texture top to bottom / vertically.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture
        """
        return self._new_texture_transformed(FlipTopToBottomTransform)

    def flip_horizontally(self) -> "Texture":
        """
        Flip the texture left to right / horizontally.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture
        """
        return self.flip_left_to_right()

    def flip_vertically(self) -> "Texture":
        """
        Flip the texture top to bottom / vertically.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture
        """
        return self.flip_top_to_bottom()

    def flip_diagonally(self) -> "Texture":
        """
        Returns a new texture that is flipped diagonally from this texture.
        This is an alias for :func:`transpose`.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture 
        """
        return self.transpose()

    def transpose(self) -> "Texture":
        """
        Returns a new texture that is transposed from this texture.
        This flips the texture diagonally from lower right to upper left.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture 
        """
        return self._new_texture_transformed(TransposeTransform, swap_dims=True)

    def transverse(self) -> "Texture":
        """
        Returns a new texture that is transverse from this texture.
        This flips the texture diagonally from lower left to upper right.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture 
        """
        return self._new_texture_transformed(TransverseTransform, swap_dims=True)

    def rotate_90(self, count: int = 1) -> "Texture":
        """
        Rotate the texture by a given number of 90 degree steps.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :param int count: Number of 90 degree steps to rotate.
        :return: Texture 
        """
        angles = [None, Rotate90Transform, Rotate180Transform, Rotate270Transform]
        count = count % 4
        transform = angles[count]
        if transform is None:
            return self
        return self._new_texture_transformed(transform, swap_dims=True)

    def rotate_180(self) -> "Texture":
        """
        Rotate the texture 180 degrees.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture 
        """
        return self._new_texture_transformed(Rotate180Transform)

    def rotate_270(self) -> "Texture":
        """
        Rotate the texture 270 degrees.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture 
        """
        return self._new_texture_transformed(Rotate270Transform, swap_dims=True)

    @staticmethod
    def validate_crop(image: PIL.Image.Image, x: int, y: int, width: int, height: int) -> None:
        """
        Validate the crop values for a given image.
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

    def crop(self, x: int, y: int, width: int, height: int) -> "Texture":
        """
        Create a new texture from a sub-section of this texture.

        If the crop is the same size as the original texture or
        the crop is 0 width or height, the original texture is
        returned.

        :param int x: X position to start crop
        :param int y: Y position to start crop
        :param int width: Width of crop
        :param int height: Height of crop
        :return: Texture 
        """
        # Return self if the crop is the same size as the original image
        if (width == self.image.width and height == self.image.height and x == 0 and y == 0):
            return self

        # Return self width and height is 0
        if width == 0 and height == 0:
            return self

        self.validate_crop(self.image, x, y, width, height)

        area = (x, y, x + width, y + height)
        image = self.image.crop(area)
        image_data = ImageData(image)
        return Texture(
            image_data,
            hit_box_algorithm=self._hit_box_algorithm,
        )        

    def _new_texture_transformed(
        self,
        transform: Type[Transform],
        swap_dims: bool = False,
    ) -> "Texture":
        """
        Create a new texture with the given transform applied.

        :param Transform transform: Transform to apply
        :param bool swap_dims: If True, swap the width and height of the texture
        :return: New texture
        """
        points = transform.transform_hit_box_points(self._hit_box_points)
        texture = Texture(
            self.image_data,
            # Not relevant, but copy over the value
            hit_box_algorithm=self._hit_box_algorithm,
            hit_box_points=points,
            hash=self._hash,
        )
        if swap_dims:
            texture.width, texture.height = self.height, self.width
        texture.origin = self.origin
        texture._vertex_order = transform.transform_vertex_order(self._vertex_order)
        # texture._transforms = get_shortest_transform(texture._vertex_order)
        texture._update_cache_names()
        return texture

    # ------------------------------------------------------------
    # Comparison and hash functions so textures can work with sets
    # A texture's uniqueness is simply based on the name
    # ------------------------------------------------------------
    def __hash__(self) -> int:
        return hash(self.cache_name)

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        return self.cache_name == other.cache_name

    def __ne__(self, other) -> bool:
        if other is None:
            return True
        if not isinstance(other, self.__class__):
            return True
        return self.cache_name != other.cache_name

    def __repr__(self) -> str:
        origin = getattr(self, "origin", None)
        cache_name = getattr(self, "cache_name", None)
        return f"<Texture origin={origin} cache_name={cache_name}>"

    def __del__(self):
        pass
        # print("DELETE", self)

    # ------------------------------------------------------------

    def _calculate_hit_box_points(self) -> PointList:
        """
        Calculate the hit box points for this texture based on the configured
        hit box algorithm. This is usually done on texture creation
        or when the hit box points are requested the first time.
        """
        # Check if we have cached points
        points = cache.hit_box_cache.get(self.cache_name)
        if points:
            return points

        # Calculate points with the selected algorithm
        points = self._hit_box_algorithm.calculate(self.image)
        if self._hit_box_algorithm.cache:
            cache.hit_box_cache.put(self.cache_name, points)

        return points

    def _create_cached_sprite(self):
        from arcade.sprite import Sprite
        from arcade.sprite_list import SpriteList

        if self._sprite is None:
            self._sprite = Sprite(self)
            self._sprite.textures = [self]
            self._sprite_list = SpriteList(capacity=1)
            self._sprite_list.append(self._sprite)

    def draw_sized(
        self,
        center_x: float,
        center_y: float,
        width: float,
        height: float,
        angle: float = 0.0,
        alpha: int = 255,
    ):
        """
        Draw a texture with a specific width and height.

        .. warning:: This is a very slow method of drawing a texture,
                     and should be used sparingly. The method simply
                     creates a sprite internally and draws it.

        :param float center_x: X position to draw texture
        :param float center_y: Y position to draw texture
        :param float width: Width to draw texture
        :param float height: Height to draw texture
        :param float angle: Angle to draw texture
        :param int alpha: Alpha value to draw texture
        """
        self._create_cached_sprite()
        if self._sprite and self._sprite_list:
            self._sprite.center_x = center_x
            self._sprite.center_y = center_y
            self._sprite.height = height
            self._sprite.width = width
            self._sprite.angle = angle
            self._sprite.alpha = alpha
            self._sprite_list.draw()

    def draw_scaled(
        self,
        center_x: float,
        center_y: float,
        scale: float = 1.0,
        angle: float = 0.0,
        alpha: int = 255,
    ):
        """
        Draw the texture.

        .. warning:: This is a very slow method of drawing a texture,
                     and should be used sparingly. The method simply
                     creates a sprite internally and draws it.

        :param float center_x: X location of where to draw the texture.
        :param float center_y: Y location of where to draw the texture.
        :param float scale: Scale to draw rectangle. Defaults to 1.
        :param float angle: Angle to rotate the texture by.
        :param int alpha: The transparency of the texture `(0-255)`.
        """

        self._create_cached_sprite()
        if self._sprite and self._sprite_list:
            self._sprite.center_x = center_x
            self._sprite.center_y = center_y
            self._sprite.scale = scale
            self._sprite.angle = angle
            self._sprite.alpha = alpha
            self._sprite_list.draw()
