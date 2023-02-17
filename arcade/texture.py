"""
Code related to working with textures.
"""
import logging
import hashlib
from typing import Optional, Tuple, List, Type, Union, TYPE_CHECKING
from pathlib import Path

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

from arcade.types import RectList, Color
from arcade.math import lerp

from arcade.texture_transforms import (
    Transform,
    FlipLeftToRightTransform,
    FlipTopToBottomTransform,
    Rotate90Transform,
    Rotate180Transform,
    Rotate270Transform,
    TransposeTransform,
    TransverseTransform,
    get_shortest_transform,
)
from arcade.types import PointList
from arcade.color import TRANSPARENT_BLACK
from arcade.resources import resolve_resource_path
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
    :param str name: Optional unique name for the texture. Can be used to make this texture
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
        self._hit_box_points: PointList = hit_box_points or self._calculate_hit_box_points()

        # Optional filename for debugging
        self._origin: Optional[str] = None

    @property
    def cache_name(self) -> str:
        """
        The name of the texture used for caching (read only).

        :return: str 
        """
        return Texture.create_cache_name(
            hash=self._hash or self._image_data.hash,
            hit_box_algorithm=self._hit_box_algorithm,
            vertex_order=self._vertex_order,
        )

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
        return f"{self._hash or self._image_data.hash}|{self._vertex_order}"

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
        """Width of the texture in pixels."""
        return self._size[0]

    @property
    def height(self) -> int:
        """Height of the texture in pixels."""
        return self._size[1]

    @property
    def size(self) -> Tuple[int, int]:
        """Width and height as a tuple"""
        return self._size

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
        return self._new_texture_transformed(TransposeTransform)

    def transverse(self) -> "Texture":
        """
        Returns a new texture that is transverse from this texture.
        This flips the texture diagonally from lower left to upper right.

        This returns a new texture with the same image data, but
        has updated hit box data and a transform that will be
        applied to the image when it's drawn (GPU side).

        :return: Texture 
        """
        return self._new_texture_transformed(TransverseTransform)

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
        return self._new_texture_transformed(transform)

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
        return self._new_texture_transformed(Rotate270Transform)

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

    def _new_texture_transformed(self, transform: Type[Transform]) -> "Texture":
        """
        Create a new texture with the given transform applied.

        :param Transform transform: Transform to apply
        :return: New texture
        """
        points = transform.transform_hit_box_points(self._hit_box_points)
        texture = Texture(
            self.image_data,
            # Not relevant, but copy over the value
            hit_box_algorithm=self._hit_box_algorithm,
            hit_box_points=points,
        )
        texture.origin = self.origin
        texture._vertex_order = transform.transform_vertex_order(self._vertex_order)
        texture._transforms = get_shortest_transform(texture._vertex_order)
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


class SolidColorTexture(Texture):
    """
    Used internally in Arcade to make colored textures.
    This is not indented to be used by the end user.

    This texture variant is mainly here it override the
    width and height property to fake texture size for
    sprites. The internal texture is always a fixed sized
    white texture that is colored by the sprite's color property.

    :param str name: Name of the texture
    :param int width: Width of the texture
    :param int height: Height of the texture
    :param img: The pillow image
    :param hit_box_points: The hit box points
    """

    def __init__(self, name, width, height, image):
        # We hardcode hit box points based on the fake width and height
        hit_box_points = (
            (-width / 2, -height / 2),
            (width / 2, -height / 2),
            (width / 2, height / 2),
            (-width / 2, height / 2)
        )
        super().__init__(
            image=image,
            hit_box_algorithm=None,
            hit_box_points=hit_box_points,
            name=name,
        )
        # Override the width and height
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


def load_textures(
    file_name: Union[str, Path],
    image_location_list: RectList,
    mirrored: bool = False,
    flipped: bool = False,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
) -> List[Texture]:
    """
    Load a set of textures from a single image file.

    Note: If the code is to load only part of the image, the given `x`, `y`
    coordinates will start with the origin `(0, 0)` in the upper left of the
    image. When drawing, Arcade uses `(0, 0)` in the lower left corner.
    Be careful with this reversal.

    For a longer explanation of why computers sometimes start in the upper
    left, see:
    http://programarcadegames.com/index.php?chapter=introduction_to_graphics&lang=en#section_5

    :param str file_name: Name of the file.
    :param List image_location_list: List of image sub-locations. Each rectangle should be
           a `List` of four floats: `[x, y, width, height]`.
    :param bool mirrored: If set to `True`, the image is mirrored left to right.
    :param bool flipped: If set to `True`, the image is flipped upside down.
    :param str hit_box_algorithm: One of None, 'None', 'Simple' (default) or 'Detailed'.
    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
    :returns: List of :class:`Texture`'s.

    :raises: ValueError
    """
    LOG.info("load_textures: %s ", file_name)
    file_name = resolve_resource_path(file_name)
    file_name_str = str(file_name)
    hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
    image_cache_name = Texture.create_image_cache_name(file_name_str)

    # Do we have the image in the cache?
    image_data = cache.image_data_cache.get(image_cache_name)
    if not image_data:
        image_data = ImageData(PIL.Image.open(resolve_resource_path(file_name)))
        cache.image_data_cache.put(image_cache_name, image_data)
    image = image_data.image

    texture_sections = []
    for image_location in image_location_list:
        x, y, width, height = image_location

        # Check if we have already created this sub-image
        image_cache_name = Texture.create_image_cache_name(file_name_str, (x, y, width, height))
        sub_image = cache.image_data_cache.get(image_cache_name)
        if not sub_image:
            Texture.validate_crop(image, x, y, width, height)
            sub_image = ImageData(image.crop((x, y, x + width, y + height)))
            cache.image_data_cache.put(image_cache_name, sub_image)            

        # Do we have a texture for this sub-image?
        texture_cache_name = Texture.create_cache_name(hash=sub_image.hash, hit_box_algorithm=hit_box_algorithm)
        sub_texture = cache.texture_cache.get(texture_cache_name)
        if not sub_texture:
            sub_texture = Texture(sub_image, hit_box_algorithm=hit_box_algorithm)
            cache.texture_cache.put(sub_texture)

        if mirrored:
            sub_texture = sub_texture.flip_left_to_right()
        if flipped:
            sub_texture = sub_texture.flip_top_to_bottom()

        sub_texture.origin = image_cache_name
        texture_sections.append(sub_texture)

    return texture_sections


def load_texture(
    file_path: Union[str, Path],
    *,
    x: int = 0,
    y: int = 0,
    width: int = 0,
    height: int = 0,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
) -> Texture:
    """
    Load an image from disk and create a texture.

    The ``x``, ``y``, ``width``, and ``height`` parameters are used to
    specify a sub-rectangle of the image to load. If not specified, the
    entire image is loaded.

    :param str file_name: Name of the file to that holds the texture.
    :param int x: X coordinate of the texture in the image.
    :param int y: Y coordinate of the texture in the image.
    :param int width: Width of the texture in the image.
    :param int height: Height of the texture in the image.
    :param str hit_box_algorithm: 
    :returns: New :class:`Texture` object.
    :raises: ValueError
    """
    LOG.info("load_texture: %s ", file_path)
    file_path = resolve_resource_path(file_path)
    file_path_str = str(file_path)
    hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
    image_cache_name = Texture.create_image_cache_name(file_path_str, (x, y, width, height))

    # Check if ths file was already loaded and in cache
    image_data = cache.image_data_cache.get(image_cache_name)
    if not image_data:
        image_data = ImageData(PIL.Image.open(file_path).convert("RGBA"))
        cache.image_data_cache.put(image_cache_name, image_data)

    # Attempt to find a texture with the same configuration
    texture = cache.texture_cache.get_with_config(image_data.hash, hit_box_algorithm)
    if not texture:
        texture = Texture(image_data, hit_box_algorithm=hit_box_algorithm)
        texture.origin = file_path_str
        cache.texture_cache.put(texture, file_path=file_path_str)

    # If the crop values give us a different texture, return that instead
    texture_cropped = texture.crop(x, y, width, height)
    if texture_cropped != texture:
        texture = texture_cropped

    return texture


def cleanup_texture_cache():
    """
    This cleans up the cache of textures. Useful when running unit tests so that
    the next test starts clean.
    """
    cache.texture_cache.clear()
    cache.image_data_cache.clear()


def load_texture_pair(
    file_name: str,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None
) -> Tuple[Texture, Texture]:
    """
    Load a texture pair, with the second being a mirror image of the first.
    Useful when doing animations and the character can face left/right.

    :param str file_name: Path to texture
    :param str hit_box_algorithm: The hit box algorithm
    """
    LOG.info("load_texture_pair: %s ", file_name)
    texture = load_texture(file_name, hit_box_algorithm=hit_box_algorithm)
    return texture, texture.flip_left_to_right()


def load_spritesheet(
    file_name: Union[str, Path],
    sprite_width: int,
    sprite_height: int,
    columns: int,
    count: int,
    margin: int = 0,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
) -> List[Texture]:
    """
    :param str file_name: Name of the file to that holds the texture.
    :param int sprite_width: Width of the sprites in pixels
    :param int sprite_height: Height of the sprites in pixels
    :param int columns: Number of tiles wide the image is.
    :param int count: Number of tiles in the image.
    :param int margin: Margin between images
    :param str hit_box_algorithm: The hit box algorithm
    :returns List: List of :class:`Texture` objects.
    """
    LOG.info("load_spritesheet: %s ", file_name)
    texture_list = []

    # TODO: Support caching?
    file_name = resolve_resource_path(file_name)
    source_image = PIL.Image.open(file_name).convert("RGBA")

    for sprite_no in range(count):
        row = sprite_no // columns
        column = sprite_no % columns
        start_x = (sprite_width + margin) * column
        start_y = (sprite_height + margin) * row
        image = source_image.crop(
            (start_x, start_y, start_x + sprite_width, start_y + sprite_height)
        )
        texture = Texture(
            image,
            hit_box_algorithm=hit_box_algorithm,
        )
        texture.origin = f"{file_name}|{sprite_no}"
        texture_list.append(texture)

    return texture_list


def make_circle_texture(
    diameter: int,
    color: Color,
    name: Optional[str] = None,
    hitbox_algorithm: Optional[HitBoxAlgorithm] = None,
) -> Texture:
    """
    Return a Texture of a circle with the given diameter and color.

    :param int diameter: Diameter of the circle and dimensions of the square :class:`Texture` returned.
    :param Color color: Color of the circle.
    :param str name: Custom or pre-chosen name for this texture

    :returns: New :class:`Texture` object.
    """
    name = name or cache.crate_str_from_values(
        "circle_texture", diameter, color[0], color[1], color[2]
    )
    bg_color = TRANSPARENT_BLACK  # fully transparent
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=color)
    return Texture(ImageData(img, hash=name), hit_box_algorithm=hitbox_algorithm)


def make_soft_circle_texture(
    diameter: int,
    color: Color,
    center_alpha: int = 255,
    outer_alpha: int = 0,
    name: Optional[str] = None,
    hit_box_algorithm: Optional[HitBoxAlgorithm] = None,
) -> Texture:
    """
    Return a :class:`Texture` of a circle with the given diameter and color, fading out at its edges.

    :param int diameter: Diameter of the circle and dimensions of the square :class:`Texture` returned.
    :param Color color: Color of the circle.
    :param int center_alpha: Alpha value of the circle at its center.
    :param int outer_alpha: Alpha value of the circle at its edges.
    :param str name: Custom or pre-chosen name for this texture
    :param str hit_box_algorithm: The hit box algorithm

    :returns: New :class:`Texture` object.
    :rtype: arcade.Texture
    """
    # Name must be unique for caching
    name = cache.crate_str_from_values(
        "soft_circle_texture",
        diameter,
        color[0],
        color[1],
        color[2],
        center_alpha,
        outer_alpha,
    )

    bg_color = TRANSPARENT_BLACK
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    max_radius = int(diameter // 2)
    center = max_radius

    for radius in range(max_radius, 0, -1):
        alpha = int(lerp(center_alpha, outer_alpha, radius / max_radius))
        clr = (color[0], color[1], color[2], alpha)
        draw.ellipse(
            (
                center - radius,
                center - radius,
                center + radius - 1,
                center + radius - 1,
            ),
            fill=clr,
        )

    return Texture(ImageData(img, name), hit_box_algorithm=hit_box_algorithm)


def make_soft_square_texture(
    size: int,
    color: Color,
    center_alpha: int = 255,
    outer_alpha: int = 0,
    name: Optional[str] = None,
) -> Texture:
    """
    Return a :class:`Texture` of a square with the given diameter and color, fading out at its edges.

    :param int size: Diameter of the square and dimensions of the square Texture returned.
    :param Color color: Color of the square.
    :param int center_alpha: Alpha value of the square at its center.
    :param int outer_alpha: Alpha value of the square at its edges.
    :param str name: Custom or pre-chosen name for this texture

    :returns: New :class:`Texture` object.
    """
    # Build name used for caching
    name = name or cache.crate_str_from_values(
        "gradient-square", size, color, center_alpha, outer_alpha
    )

    # Generate the soft square image
    bg_color = TRANSPARENT_BLACK
    img = PIL.Image.new("RGBA", (size, size), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    half_size = int(size // 2)

    for cur_size in range(0, half_size):
        alpha = int(lerp(outer_alpha, center_alpha, cur_size / half_size))
        clr = (color[0], color[1], color[2], alpha)
        draw.rectangle(
            (cur_size, cur_size, size - cur_size, size - cur_size), clr, None
        )

    return Texture(img, name=name)
