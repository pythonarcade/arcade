"""
Code related to working with textures.
"""
import logging
from typing import Callable, Dict, Optional, Tuple, List, Type, Union, TYPE_CHECKING
from pathlib import Path
from weakref import WeakValueDictionary

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

from arcade import (
    lerp,
    RectList,
    Color,
    get_four_byte_color,
    calculate_hit_box_points_simple,
    calculate_hit_box_points_detailed,
)
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
from arcade.arcade_types import PointList
from arcade.resources import resolve_resource_path
from arcade.cache.hit_box import HitBoxCache
from arcade.cache.image import ImageCache

if TYPE_CHECKING:
    from arcade.sprite import Sprite
    from arcade.sprite_list import SpriteList

LOG = logging.getLogger(__name__)


class Texture:
    """
    An arcade.Texture is simply a wrapper for image data as a Pillow image
    and the hit box data for this image used in collision detection.
    Usually created by the :class:`load_texture` or :class:`load_textures` commands.

    :param str name: Globally unique name for this texture.
                     This is used internally for caching and texture atlas.
    :param PIL.Image.Image image: The image for this texture
    :param str hit_box_algorithm: One of None, 'None', 'Simple' or 'Detailed'. \
    Defaults to 'Simple'. Use 'Simple' for the :data:`PhysicsEngineSimple`, \
    :data:`PhysicsEnginePlatformer` \
    and 'Detailed' for the :data:`PymunkPhysicsEngine`.

        .. figure:: ../images/hit_box_algorithm_none.png
           :width: 40%

           hit_box_algorithm = "None"

        .. figure:: ../images/hit_box_algorithm_simple.png
           :width: 55%

           hit_box_algorithm = "Simple"

        .. figure:: ../images/hit_box_algorithm_detailed.png
           :width: 75%

           hit_box_algorithm = "Detailed"

    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
    :param PointList hit_box_points: List of points for the hit box (Optional).
                                     Completely overrides the hit box algorithm.
    """
    cache: WeakValueDictionary[str, "Texture"] = WeakValueDictionary()
    image_cache = ImageCache()
    hit_box_cache = HitBoxCache()

    _hit_box_funcs: Dict[str, Optional[Callable]] = {
        "default": calculate_hit_box_points_simple,
        "simple": calculate_hit_box_points_simple,
        "detailed": calculate_hit_box_points_detailed,
        "none": None,
    }

    def __init__(
        self,
        name: str,
        image: PIL.Image.Image = None,
        hit_box_algorithm: Optional[str] = "default",
        hit_box_detail: float = 4.5,
        hit_box_points: Optional[PointList] = None,
    ):
        if not isinstance(image, PIL.Image.Image):
            raise ValueError("A texture must have an image")

        self._name = name
        self._image = image
        # The order of the texture coordinates when mapping
        # to a sprite/quad. This order is changed when the
        # texture is flipped or rotated.
        self._vertex_order = 0, 1, 2, 3
        # List of transforms applied to this texture
        self._transforms: List[Type[Transform]] = []

        # Internal sprite stuff for drawing
        self._sprite: Optional[Sprite] = None
        self._sprite_list: Optional[SpriteList] = None

        self._hit_box_func: Optional[Callable] = None
        self._hit_box_algorithm: Optional[str] = hit_box_algorithm
        if self._hit_box_algorithm is not None and hit_box_points is None:
            if not isinstance(self._hit_box_algorithm, str):
                raise ValueError(
                    f"hit_box_algorithm must be a string or None, not {hit_box_algorithm}")

            self._hit_box_algorithm = self._hit_box_algorithm.lower()
            try:
                self._hit_box_func = self._hit_box_funcs[self._hit_box_algorithm]
            except KeyError:
                raise ValueError(
                    "hit_box_algorithm must be None or one of: {}".format(
                        ", ".join(str(v) for v in self._hit_box_funcs.keys())
                    ))
        self._hit_box_detail = hit_box_detail
        self._hit_box_points: PointList = hit_box_points or self._calculate_hit_box_points()

    @property
    def name(self) -> str:
        """
        The name of the texture (read only).

        :return: str 
        """
        return self._name

    @property
    def image(self) -> PIL.Image.Image:
        """
        The image of the texture (read only).

        :return: PIL.Image.Image 
        """
        return self._image

    @image.setter
    def image(self, image: PIL.Image.Image):
        """
        Set the image of the texture.

        .. warning::

            This is an advanced function. Be absolutely sure
            you know the consequences of changing the image.
            It can cause problems with the texture atlas and
            hit box points.

        :param PIL.Image.Image image: The image to set
        """
        self._image = image

    @property
    def width(self) -> int:
        """Width of the texture in pixels."""
        return self._image.width

    @property
    def height(self) -> int:
        """Height of the texture in pixels."""
        return self._image.height

    @property
    def size(self) -> Tuple[int, int]:
        """Width and height as a tuple"""
        return self._image.size

    @property
    def hit_box_points(self) -> PointList:
        """
        Get the hit box points for this texture.

        Custom hit box points must be supplied during texture creation.

        :return: PointList
        """
        if self._hit_box_points is None:
            self.calculate_hit_box_points()

        return self._hit_box_points

    @property
    def hit_box_algorithm(self) -> Optional[str]:
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
            name,
            image=PIL.Image.new("RGBA", size, get_four_byte_color(color)),
            hit_box_algorithm=None,
        )

    @staticmethod
    def build_cache_name(name, *args) -> str:
        """
        Generate cache names from the given parameters

        This is mostly useful when generating textures with many parameters

        :param str name: Name of the texture
        :param args: params to format
        :param separator: separator character or string between params

        :return: Formatted cache string representing passed parameters
        """
        values = [str(name)] + [str(arg) for arg in args]
        return "|".join([v for v in values])

    # Texture name
    # ------------
    # name, xy, size, hit_box_algorithm, vertex_order
    # 
    # Image name
    # ----------
    # name, xy, size
    # 
    # Hit Box name
    # name, xy, size, hit_box_algorithm, vertex_order

    @classmethod
    def register_hit_box_algorithm(cls, name: str, func: Optional[Callable] = None) -> None:
        """
        Register a hit box function.

        Can also be used to change the default hit box algorithm.

        This function must be given a name such as the default
        "Simple" and "Detailed" ones. The supplied function must
        take a PIL image and an float value representing detail
        and return the hit box points.

        The names are case insensitive are stored in lowercase.

        Example::

            # A custom hit box function. Ideally it would inspect the image
            def my_hit_box_func(image: PIL.Image, detail: float):
                return ((0, 0), (0, 1), (1, 1), (1, 0))

            Texture.register_hit_box_algorithm("MyHitBoxAlgo", my_hit_box_func)

            # Change the default hit box algorithm to simple bounding box
            Texture.register_hit_box_algorithm("default", None)

        :param str name: Name of the hit box algorithm
        :param Callable func: Function to calculate hit box points
        """
        cls._hit_box_funcs[name.lower()] = func

    def flip_left_to_right(self) -> "Texture":
        """
        Flip the texture left to right / horizontally.

        :return: Texture 
        """
        return self._new_texture_transformed(FlipLeftToRightTransform)

    def flip_top_to_bottom(self) -> "Texture":
        """
        Flip the texture top to bottom / vertically.

        :return: Texture 
        """
        return self._new_texture_transformed(FlipTopToBottomTransform)

    def flip_diagonally(self) -> "Texture":
        """
        Returns a new texture that is flipped diagonally from this texture.
        This is an alias for :func:`transpose`.

        :return: Texture 
        """
        return self.transpose()

    def transpose(self) -> "Texture":
        """
        Returns a new texture that is transposed from this texture.
        This flips the texture diagonally from lower right to upper left.

        :return: Texture 
        """
        return self._new_texture_transformed(TransposeTransform)

    def transverse(self) -> "Texture":
        """
        Returns a new texture that is transverse from this texture.
        This flips the texture diagonally from lower left to upper right.

        :return: Texture 
        """
        return self._new_texture_transformed(TransverseTransform)

    def rotate(self, count: int) -> "Texture":
        """
        Rotate the texture by a given number of 90 degree steps.

        :param int count: Number of 90 degree steps to rotate.
        :return: Texture 
        """
        angles = [None, Rotate90Transform, Rotate180Transform, Rotate270Transform]
        count = count % 4
        transform = angles[count]
        if transform is None:
            return self
        return self._new_texture_transformed(transform)

    def crop(self, x: int, y: int, width: int, height: int) -> "Texture":
        """
        Create a new texture from a crop of this texture.

        :param int x: X position to start crop
        :param int y: Y position to start crop
        :param int width: Width of crop
        :param int height: Height of crop
        :return: Texture 
        """
        raise NotImplementedError()

    def _new_texture_transformed(self, transform: Type[Transform]) -> "Texture":
        """
        Create a new texture with the given transform applied.

        :param Transform transform: Transform to apply
        :return: New texture
        """
        points = transform.transform_hit_box_points(self._hit_box_points)
        texture = Texture(
            name=self._name,
            image=self._image,
            # Not relevant, but copy over the value
            hit_box_algorithm=self._hit_box_algorithm,
            hit_box_points=points,
        )
        texture._vertex_order = transform.transform_vertex_order(self._vertex_order)
        texture._transforms = get_shortest_transform(texture._vertex_order)
        return texture

    # ------------------------------------------------------------
    # Comparison and hash functions so textures can work with sets
    # A texture's uniqueness is simply based on the name
    # ------------------------------------------------------------
    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name

    def __ne__(self, other) -> bool:
        if other is None:
            return True
        if not isinstance(other, self.__class__):
            return True
        return self.name != other.name

    def _calculate_hit_box_points(self):
        """
        Calculate the hit box points for this texture
        based on the configured hit box algorithm.
        This is usually done on texture creation
        or when the hit box points are requested the first time.
        """
        if self._hit_box_func:
            return self._hit_box_func(self._image, self._hit_box_detail)

        # Fall back to simple rectangle
        return (
            (-self._image.width / 2, -self._image.height / 2),
            (self._image.width / 2, -self._image.height / 2),
            (self._image.width / 2, self._image.height / 2),
            (-self._image.width / 2, self._image.height / 2),
        )

    def _create_cached_sprite(self):
        from arcade.sprite import Sprite
        from arcade.sprite_list import SpriteList

        if self._sprite is None:
            self._sprite = Sprite()
            self._sprite.texture = self
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


def load_textures(
    file_name: Union[str, Path],
    image_location_list: RectList,
    mirrored: bool = False,
    flipped: bool = False,
    hit_box_algorithm: Optional[str] = "Simple",
    hit_box_detail: float = 4.5,
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
    image = PIL.Image.open(resolve_resource_path(file_name))

    texture_sections = []
    for image_location in image_location_list:
        x, y, width, height = image_location

        if width <= 0:
            raise ValueError("Texture has a width of {}, must be > 0.".format(width))
        if x > image.width:
            raise ValueError(
                "Can't load texture starting at an x of {} "
                "when the image is only {} across.".format(x, image.width)
            )
        if y > image.height:
            raise ValueError(
                "Can't load texture starting at an y of {} "
                "when the image is only {} high.".format(y, image.height)
            )
        if x + width > image.width:
            raise ValueError(
                "Can't load texture ending at an x of {} "
                "when the image is only {} wide.".format(x + width, image.width)
            )
        if y + height > image.height:
            raise ValueError(
                "Can't load texture ending at an y of {} "
                "when the image is only {} high.".format(
                    y + height, image.height,
                )
            )

        # See if we already loaded this texture, and we can just use a cached version.
        name = Texture.build_cache_name(
            file_name, x, y, width, height, flipped, mirrored
        )
        try:
            sub_texture = Texture.cache[name]
        except KeyError:
            sub_image = image.crop((x, y, x + width, y + height))

            if mirrored:
                sub_image = PIL.ImageOps.mirror(sub_image)

            if flipped:
                sub_image = PIL.ImageOps.flip(sub_image)

            sub_texture = Texture(
                name,
                image=sub_image,
                hit_box_algorithm=hit_box_algorithm,
                hit_box_detail=hit_box_detail,
            )
            Texture.cache[name] = sub_texture

        texture_sections.append(sub_texture)

    return texture_sections


def load_texture(
    file_name: Union[str, Path],
    x: int = 0,
    y: int = 0,
    width: int = 0,
    height: int = 0,
    flipped_horizontally: bool = False,
    flipped_vertically: bool = False,
    flipped_diagonally: bool = False,
    hit_box_algorithm: Optional[str] = "Simple",
    hit_box_detail: float = 4.5,
) -> Texture:
    """
    Load an image from disk and create a texture.

    Note: If the code is to load only part of the image, the given `x`, `y`
    coordinates will start with the origin `(0, 0)` in the upper left of the
    image. When drawing, Arcade uses `(0, 0)` in the lower left corner.
    Be careful with this reversal.

    For a longer explanation of why computers sometimes start in the upper
    left, see:
    http://programarcadegames.com/index.php?chapter=introduction_to_graphics&lang=en#section_5

    :param str file_name: Name of the file to that holds the texture.
    :param float x: X position of the crop area of the texture.
    :param float y: Y position of the crop area of the texture.
    :param float width: Width of the crop area of the texture.
    :param float height: Height of the crop area of the texture.
    :param bool flipped_horizontally: Mirror the sprite image. Flip left/right across vertical axis.
    :param bool flipped_vertically: Flip the image up/down across the horizontal axis.
    :param bool flipped_diagonally: Transpose the image, flip it across the diagonal.
    :param bool mirrored: Deprecated.
    :param str hit_box_algorithm: One of None, 'None', 'Simple' or 'Detailed'. \
    Defaults to 'Simple'. Use 'Simple' for the :data:`PhysicsEngineSimple`, \
    :data:`PhysicsEnginePlatformer` \
    and 'Detailed' for the :data:`PymunkPhysicsEngine`.

        .. figure:: ../images/hit_box_algorithm_none.png
           :width: 40%

           hit_box_algorithm = "None"

        .. figure:: ../images/hit_box_algorithm_simple.png
           :width: 55%

           hit_box_algorithm = "Simple"

        .. figure:: ../images/hit_box_algorithm_detailed.png
           :width: 75%

           hit_box_algorithm = "Detailed"

    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
    :returns: New :class:`Texture` object.
    :raises: ValueError
    """
    LOG.info("load_texture: %s ", file_name)

    # First check if we have a cached version of this texture.
    name = Texture.build_cache_name(
        file_name,
        x, y,
        width, height,
        flipped_horizontally, flipped_vertically, flipped_diagonally,
        hit_box_algorithm,
    )
    try:
        return Texture.cache[name]
    except KeyError:
        pass

    # See if we already loaded this texture file, and we can just use a cached version.
    try:
        texture = Texture.cache[str(file_name)]
    except KeyError:
        file_name = resolve_resource_path(file_name)
        texture = Texture(
            str(file_name),
            PIL.Image.open(file_name).convert("RGBA"),
            hit_box_algorithm=hit_box_algorithm,
            hit_box_detail=hit_box_detail,
        )
        Texture.cache[str(file_name)] = texture

    if x != 0 or y != 0 or width != 0 or height != 0:
        if x > texture.image.width:
            raise ValueError(
                "Can't load texture starting at an x of {} "
                "when the image is only {} across.".format(x, texture.image.width)
            )
        if y > texture.image.height:
            raise ValueError(
                "Can't load texture starting at an y of {} "
                "when the image is only {} high.".format(y, texture.image.height)
            )
        if x + width > texture.image.width:
            raise ValueError(
                "Can't load texture ending at an x of {} "
                "when the image is only {} wide.".format(x + width, texture.image.width)
            )
        if y + height > texture.image.height:
            raise ValueError(
                "Can't load texture ending at an y of {} "
                "when the image is only {} high.".format(
                    y + height, texture.image.height
                )
            )

        image = texture.image.crop((x, y, x + width, y + height))
    else:
        image = texture.image

    if flipped_diagonally:
        image = image.transpose(PIL.Image.Transpose.TRANSPOSE)

    if flipped_horizontally:
        image = image.transpose(PIL.Image.Transpose.FLIP_LEFT_RIGHT)

    if flipped_vertically:
        image = image.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)

    texture = Texture(
        name,
        image,
        hit_box_algorithm=hit_box_algorithm,
        hit_box_detail=hit_box_detail,
    )
    Texture.cache[name] = texture
    return texture


def cleanup_texture_cache():
    """
    This cleans up the cache of textures. Useful when running unit tests so that
    the next test starts clean.
    """
    Texture.cache = Texture.cache.__class__()
    import gc
    gc.collect()


def load_texture_pair(file_name: str, hit_box_algorithm: str = "Simple"):
    """
    Load a texture pair, with the second being a mirror image of the first.
    Useful when doing animations and the character can face left/right.

    :param str file_name: Path to texture
    :param str hit_box_algorithm: The hit box algorithm
    """
    LOG.info("load_texture_pair: %s ", file_name)
    return [
        load_texture(file_name, hit_box_algorithm=hit_box_algorithm),
        load_texture(
            file_name, flipped_horizontally=True, hit_box_algorithm=hit_box_algorithm
        ),
    ]


def load_spritesheet(
    file_name: Union[str, Path],
    sprite_width: int,
    sprite_height: int,
    columns: int,
    count: int,
    margin: int = 0,
    hit_box_algorithm: Optional[str] = "Simple",
    hit_box_detail: float = 4.5,
) -> List[Texture]:
    """
    :param str file_name: Name of the file to that holds the texture.
    :param int sprite_width: Width of the sprites in pixels
    :param int sprite_height: Height of the sprites in pixels
    :param int columns: Number of tiles wide the image is.
    :param int count: Number of tiles in the image.
    :param int margin: Margin between images
    :param str hit_box_algorithm: One of None, 'None', 'Simple' (default) or 'Detailed'.
    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box
    :returns List: List of :class:`Texture` objects.
    """
    LOG.info("load_spritesheet: %s ", file_name)
    texture_list = []

    # If we should pull from local resources, replace with proper path
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
            f"{file_name}-{sprite_no}",
            image=image,
            hit_box_algorithm=hit_box_algorithm,
            hit_box_detail=hit_box_detail,
        )
        texture_list.append(texture)

    return texture_list


def make_circle_texture(diameter: int, color: Color, name: str = None) -> Texture:
    """
    Return a Texture of a circle with the given diameter and color.

    :param int diameter: Diameter of the circle and dimensions of the square :class:`Texture` returned.
    :param Color color: Color of the circle.
    :param str name: Custom or pre-chosen name for this texture

    :returns: New :class:`Texture` object.
    """
    name = name or Texture.build_cache_name(
        "circle_texture", diameter, color[0], color[1], color[2]
    )
    bg_color = (0, 0, 0, 0)  # fully transparent
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=color)
    return Texture(name, img)


def make_soft_circle_texture(
    diameter: int,
    color: Color,
    center_alpha: int = 255,
    outer_alpha: int = 0,
    name: str = None,
) -> Texture:
    """
    Return a :class:`Texture` of a circle with the given diameter and color, fading out at its edges.

    :param int diameter: Diameter of the circle and dimensions of the square :class:`Texture` returned.
    :param Color color: Color of the circle.
    :param int center_alpha: Alpha value of the circle at its center.
    :param int outer_alpha: Alpha value of the circle at its edges.
    :param str name: Custom or pre-chosen name for this texture

    :returns: New :class:`Texture` object.
    :rtype: arcade.Texture
    """
    # TODO: create a rectangle and circle (and triangle? and arbitrary poly where client passes
    # in list of points?) particle?
    name = Texture.build_cache_name(
        "soft_circle_texture",
        diameter,
        color[0],
        color[1],
        color[2],
        center_alpha,
        outer_alpha,
    )  # name must be unique for caching

    bg_color = (0, 0, 0, 0)  # fully transparent
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    max_radius = int(diameter // 2)
    center = max_radius  # for readability
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

    return Texture(name, img)


def make_soft_square_texture(
    size: int,
    color: Color,
    center_alpha: int = 255,
    outer_alpha: int = 0,
    name: str = None,
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
    # name must be unique for caching
    name = name or Texture.build_cache_name(
        "gradient-square", size, color, center_alpha, outer_alpha
    )

    bg_color = (0, 0, 0, 0)  # fully transparent
    img = PIL.Image.new("RGBA", (size, size), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    half_size = int(size // 2)
    for cur_size in range(0, half_size):
        alpha = int(lerp(outer_alpha, center_alpha, cur_size / half_size))
        clr = (color[0], color[1], color[2], alpha)
        # draw.ellipse((center - radius, center - radius, center + radius, center + radius), fill=clr)
        draw.rectangle(
            (cur_size, cur_size, size - cur_size, size - cur_size), clr, None
        )
    return Texture(name, img)
