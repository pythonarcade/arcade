"""
Code related to working with textures.
"""

import math
from pathlib import Path

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

from typing import Optional
from typing import List
from typing import Union

from arcade import lerp
from arcade import RectList
from arcade import Color
from arcade import calculate_hit_box_points_simple
from arcade import calculate_hit_box_points_detailed
from arcade.resources import resolve_resource_path


def _lerp_color(start_color: Color, end_color: Color, u: float) -> Color:
    return (
        int(lerp(start_color[0], end_color[0], u)),
        int(lerp(start_color[1], end_color[1], u)),
        int(lerp(start_color[2], end_color[2], u))
    )


class Matrix3x3:
    def __init__(self):
        self.reset()

    def reset(self):
        self.v = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        return self

    def multiply(self, o: List[float]):
        v = self.v
        self.v = [v[0] * o[0] + v[3] * o[1] + v[6] * o[2],
                  v[1] * o[0] + v[4] * o[1] + v[7] * o[2],
                  v[2] * o[0] + v[5] * o[1] + v[8] * o[2],
                  v[0] * o[3] + v[3] * o[4] + v[6] * o[5],
                  v[1] * o[3] + v[4] * o[4] + v[7] * o[5],
                  v[2] * o[3] + v[5] * o[4] + v[8] * o[5],
                  v[0] * o[6] + v[3] * o[7] + v[6] * o[8],
                  v[1] * o[6] + v[4] * o[7] + v[7] * o[8],
                  v[2] * o[6] + v[5] * o[7] + v[8] * o[8]]
        return self

    def scale(self, sx: float, sy: float):
        return self.multiply([1.0 / sx, 0.0, 0.0, 0.0, 1.0 / sy, 0.0, 0.0, 0.0, 1.0])

    def translate(self, tx: float, ty: float):
        return self.multiply([1.0, 0.0, 0.0, 0.0, 1.0, 0.0, -tx, ty, 1.0])

    def rotate(self, phi: float):
        s = math.sin(math.radians(phi))
        c = math.cos(math.radians(phi))
        return self.multiply([c, s, 0.0, -s, c, 0.0, 0.0, 0.0, 1.0])

    def shear(self, sx: float, sy: float):
        return self.multiply([1.0, sy, 0.0, sx, 1.0, 0.0, 0.0, 0.0, 1.0])


class Texture:
    """
    Class that represents a texture.
    Usually created by the :class:`load_texture` or :class:`load_textures` commands.

    Attributes:
        :name: Unique name of the texture. Used by load_textures for caching.
               If you are manually creating a texture, you can just set this
               to whatever.
        :image: A :py:class:`PIL.Image.Image` object.
        :width: Width of the texture in pixels.
        :height: Height of the texture in pixels.
    """

    def __init__(self,
                 name: str,
                 image: PIL.Image.Image = None,
                 hit_box_algorithm: str = "Simple",
                 hit_box_detail: float = 4.5):
        """
        Create a texture, given a PIL Image object.

        :param str name: Name of texture. Used for caching, so must be unique for each texture.
        :param PIL.Image.Image image: Image to use as a texture.
        :param str hit_box_algorithm: One of 'None', 'Simple' or 'Detailed'. \
        Defaults to 'Simple'. Use 'Simple' for the :data:`PhysicsEngineSimple`, \
        :data:`PhysicsEnginePlatformer` \
        and 'Detailed' for the :data:`PymunkPhysicsEngine`.

            .. figure:: images/hit_box_algorithm_none.png
               :width: 40%

               hit_box_algorithm = "None"

            .. figure:: images/hit_box_algorithm_simple.png
               :width: 55%

               hit_box_algorithm = "Simple"

            .. figure:: images/hit_box_algorithm_detailed.png
               :width: 75%

               hit_box_algorithm = "Detailed"
        :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box

        """
        from arcade.sprite import Sprite
        from arcade.sprite_list import SpriteList

        if image:
            assert isinstance(image, PIL.Image.Image)
        self.name = name
        self.image = image
        self._sprite: Optional[Sprite] = None
        self._sprite_list: Optional[SpriteList] = None
        self._hit_box_points = None

        if hit_box_algorithm != "Simple" and \
           hit_box_algorithm != "Detailed" and \
           hit_box_algorithm != "None":
           raise ValueError("hit_box_algorithm must be 'Simple', 'Detailed', or 'None'.")
        self._hit_box_algorithm = hit_box_algorithm

        self._hit_box_detail = hit_box_detail

    @property
    def width(self) -> int:
        """
        Width of the texture in pixels.
        """
        if self.image:
            return self.image.width
        else:
            return 0

    @property
    def height(self) -> int:
        """
        Height of the texture in pixels.
        """
        if self.image:
            return self.image.height
        else:
            return 0

    @property
    def hit_box_points(self):
        if self._hit_box_points is not None:
            return self._hit_box_points
        else:
            if self._hit_box_algorithm == "Simple":
                self._hit_box_points = calculate_hit_box_points_simple(self.image)
            elif self._hit_box_algorithm == "Detailed":
                self._hit_box_points = calculate_hit_box_points_detailed(self.image, self._hit_box_detail)
            else:
                p1 = (-self.image.width / 2, -self.image.height / 2)
                p2 = (self.image.width / 2, -self.image.height / 2)
                p3 = (self.image.width / 2, self.image.height / 2)
                p4 = (-self.image.width / 2, self.image.height / 2)

                self._hit_box_points = p1, p2, p3, p4

            return self._hit_box_points

    def _create_cached_sprite(self):
        from arcade.sprite import Sprite
        from arcade.sprite_list import SpriteList

        if self._sprite is None:
            self._sprite = Sprite()
            self._sprite.texture = self
            self._sprite.textures = [self]

            self._sprite_list = SpriteList()
            self._sprite_list.append(self._sprite)

    def draw_sized(self,
                   center_x: float, center_y: float,
                   width: float,
                   height: float,
                   angle: float = 0,
                   alpha: int = 255):

        self._create_cached_sprite()
        if self._sprite and self._sprite_list:
            self._sprite.center_x = center_x
            self._sprite.center_y = center_y
            self._sprite.height = height
            self._sprite.width = width
            self._sprite.angle = angle
            self._sprite.alpha = alpha
            self._sprite_list.draw()

    def draw_transformed(self,
                         left: float,
                         bottom: float,
                         width: float,
                         height: float,
                         angle: float = 0,
                         alpha: int = 255,
                         texture_transform: Matrix3x3 = Matrix3x3()):

        self._create_cached_sprite()
        if self._sprite and self._sprite_list:
            self._sprite.center_x = left + width / 2
            self._sprite.center_y = bottom + height / 2
            self._sprite.width = width
            self._sprite.height = height
            self._sprite.angle = angle
            self._sprite.alpha = alpha
            self._sprite.texture_transform = texture_transform
            self._sprite_list.draw()

    def draw_scaled(self, center_x: float, center_y: float,
                    scale: float = 1.0,
                    angle: float = 0,
                    alpha: int = 255):

        """
        Draw the texture.

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


def load_textures(file_name: Union[str, Path],
                  image_location_list: RectList,
                  mirrored: bool = False,
                  flipped: bool = False) -> List[Texture]:
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

    :returns: List of :class:`Texture`'s.

    :raises: ValueError
    """
    # See if we already loaded this texture file, and we can just use a cached version.
    cache_file_name = "{}".format(file_name)
    if cache_file_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
        texture = load_texture.texture_cache[cache_file_name]  # type: ignore # dynamic attribute on function obj
        source_image = texture.image
    else:
        file_name = resolve_resource_path(file_name)

        source_image = PIL.Image.open(file_name)
        result = Texture(cache_file_name, source_image)
        load_texture.texture_cache[cache_file_name] = result  # type: ignore # dynamic attribute on function obj

    source_image_width, source_image_height = source_image.size
    texture_info_list = []
    for image_location in image_location_list:
        x, y, width, height = image_location

        if width <= 0:
            raise ValueError("Texture has a width of {}, must be > 0."
                             .format(width))
        if x > source_image_width:
            raise ValueError("Can't load texture starting at an x of {} "
                             "when the image is only {} across."
                             .format(x, source_image_width))
        if y > source_image_height:
            raise ValueError("Can't load texture starting at an y of {} "
                             "when the image is only {} high."
                             .format(y, source_image_height))
        if x + width > source_image_width:
            raise ValueError("Can't load texture ending at an x of {} "
                             "when the image is only {} wide."
                             .format(x + width, source_image_width))
        if y + height > source_image_height:
            raise ValueError("Can't load texture ending at an y of {} "
                             "when the image is only {} high."
                             .format(y + height, source_image_height))

        # See if we already loaded this texture, and we can just use a cached version.
        cache_name = "{}{}{}{}{}{}{}".format(file_name, x, y, width, height, flipped, mirrored)
        if cache_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
            result = load_texture.texture_cache[cache_name]  # type: ignore # dynamic attribute on function obj
        else:
            image = source_image.crop((x, y, x + width, y + height))
            # image = _trim_image(image)

            if mirrored:
                image = PIL.ImageOps.mirror(image)

            if flipped:
                image = PIL.ImageOps.flip(image)
            result = Texture(cache_name, image)
            load_texture.texture_cache[cache_name] = result  # type: ignore # dynamic attribute on function obj
        texture_info_list.append(result)

    return texture_info_list


def load_texture(file_name: Union[str, Path],
                 x: float = 0,
                 y: float = 0,
                 width: float = 0, height: float = 0,
                 flipped_horizontally: bool = False,
                 flipped_vertically: bool = False,
                 flipped_diagonally: bool = False,
                 can_cache: bool = True,
                 mirrored = None,
                 hit_box_algorithm = "Simple",
                 hit_box_detail: float = 4.5) -> Texture:
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
    :param bool can_cache: If a texture has already been loaded, load_texture will return the same texture in order \
    to save time. Sometimes this is not desirable, as resizing a cached texture will cause all other textures to \
    resize with it. Setting can_cache to false will prevent this issue at the experience of additional resources.
    :param bool mirrored: Deprecated.
    :param str hit_box_algorithm: One of 'None', 'Simple' or 'Detailed'. \
    Defaults to 'Simple'. Use 'Simple' for the :data:`PhysicsEngineSimple`, \
    :data:`PhysicsEnginePlatformer` \
    and 'Detailed' for the :data:`PymunkPhysicsEngine`.

        .. figure:: images/hit_box_algorithm_none.png
           :width: 40%

           hit_box_algorithm = "None"

        .. figure:: images/hit_box_algorithm_simple.png
           :width: 55%

           hit_box_algorithm = "Simple"

        .. figure:: images/hit_box_algorithm_detailed.png
           :width: 75%

           hit_box_algorithm = "Detailed"
    :param float hit_box_detail: Float, defaults to 4.5. Used with 'Detailed' to hit box

    :returns: New :class:`Texture` object.

    :raises: ValueError
    """

    if mirrored is not None:
        from warnings import warn
        warn("In load_texture, the 'mirrored' parameter is deprecated. Use 'flipped_horizontally' instead.",
             DeprecationWarning)
        flipped_horizontally = mirrored

    # See if we already loaded this texture, and we can just use a cached version.
    cache_name = "{}-{}-{}-{}-{}-{}-{}-{}-{}".format(file_name,
                                                     x,
                                                     y,
                                                     width,
                                                     height,
                                                     flipped_horizontally,
                                                     flipped_vertically,
                                                     flipped_diagonally,
                                                     hit_box_algorithm)
    if can_cache and cache_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
        return load_texture.texture_cache[cache_name]  # type: ignore # dynamic attribute on function obj

    # See if we already loaded this texture file, and we can just use a cached version.
    cache_file_name = f"{file_name}"
    if cache_file_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
        texture = load_texture.texture_cache[cache_file_name]  # type: ignore # dynamic attribute on function obj
        source_image = texture.image
    else:
        # If we should pull from local resources, replace with proper path
        file_name = resolve_resource_path(file_name)

        source_image = PIL.Image.open(file_name).convert('RGBA')
        result = Texture(cache_file_name, source_image,
                         hit_box_algorithm=hit_box_algorithm,
                         hit_box_detail=hit_box_detail)
        load_texture.texture_cache[cache_file_name] = result  # type: ignore # dynamic attribute on function obj

    source_image_width, source_image_height = source_image.size

    if x != 0 or y != 0 or width != 0 or height != 0:
        if x > source_image_width:
            raise ValueError("Can't load texture starting at an x of {} "
                             "when the image is only {} across."
                             .format(x, source_image_width))
        if y > source_image_height:
            raise ValueError("Can't load texture starting at an y of {} "
                             "when the image is only {} high."
                             .format(y, source_image_height))
        if x + width > source_image_width:
            raise ValueError("Can't load texture ending at an x of {} "
                             "when the image is only {} wide."
                             .format(x + width, source_image_width))
        if y + height > source_image_height:
            raise ValueError("Can't load texture ending at an y of {} "
                             "when the image is only {} high."
                             .format(y + height, source_image_height))

        image = source_image.crop((x, y, x + width, y + height))
    else:
        image = source_image

    # image = _trim_image(image)
    if flipped_diagonally:
        image = image.transpose(PIL.Image.TRANSPOSE)

    if flipped_horizontally:
        image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)

    if flipped_vertically:
        image = image.transpose(PIL.Image.FLIP_TOP_BOTTOM)

    result = Texture(cache_name, image,
                     hit_box_algorithm=hit_box_algorithm,
                     hit_box_detail=hit_box_detail)
    load_texture.texture_cache[cache_name] = result  # type: ignore # dynamic attribute on function obj
    return result


load_texture.texture_cache = dict()  # type: ignore


def cleanup_texture_cache():
    """
    This cleans up the cache of textures. Useful when running unit tests so that
    the next test starts clean.
    """
    load_texture.texture_cache = dict()
    import gc
    gc.collect()

def load_texture_pair(filename, hit_box_algorithm: str = "Simple"):
    """
    Load a texture pair, with the second being a mirror image of the first.
    Useful when doing animations and the character can face left/right.
    """
    return [
        load_texture(filename,
                     hit_box_algorithm=hit_box_algorithm),
        load_texture(filename,
                     flipped_horizontally=True,
                     hit_box_algorithm=hit_box_algorithm)
    ]

def load_spritesheet(file_name: Union[str, Path],
                     sprite_width: int,
                     sprite_height: int,
                     columns: int,
                     count: int,
                     margin: int = 0) -> List[Texture]:
    """

    :param str file_name: Name of the file to that holds the texture.
    :param int sprite_width: Width of the sprites in pixels
    :param int sprite_height: Height of the sprites in pixels
    :param int columns: Number of tiles wide the image is.
    :param int count: Number of tiles in the image.
    :param int margin: Margin between images

    :returns List: List of :class:`Texture` objects.
    """

    texture_list = []

    # If we should pull from local resources, replace with proper path
    file_name = resolve_resource_path(file_name)

    source_image = PIL.Image.open(file_name).convert('RGBA')
    for sprite_no in range(count):
        row = sprite_no // columns
        column = sprite_no % columns
        start_x = (sprite_width + margin) * column
        start_y = (sprite_height + margin) * row
        image = source_image.crop((start_x, start_y, start_x + sprite_width, start_y + sprite_height))
        texture = Texture(f"{file_name}-{sprite_no}", image)
        texture_list.append(texture)

    return texture_list


def make_circle_texture(diameter: int, color: Color) -> Texture:
    """
    Return a Texture of a circle with the given diameter and color.

    :param int diameter: Diameter of the circle and dimensions of the square :class:`Texture` returned.
    :param Color color: Color of the circle.

    :returns: New :class:`Texture` object.
    """
    bg_color = (0, 0, 0, 0)  # fully transparent
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=color)
    name = "{}:{}:{}".format("circle_texture", diameter, color)  # name must be unique for caching
    return Texture(name, img)


def make_soft_circle_texture(diameter: int, color: Color, center_alpha: int = 255, outer_alpha: int = 0) -> Texture:
    """
    Return a :class:`Texture` of a circle with the given diameter and color, fading out at its edges.

    :param int diameter: Diameter of the circle and dimensions of the square :class:`Texture` returned.
    :param Color color: Color of the circle.
    :param int center_alpha: Alpha value of the circle at its center.
    :param int outer_alpha: Alpha value of the circle at its edges.

    :returns: New :class:`Texture` object.
    :rtype: arcade.Texture
    """
    # TODO: create a rectangle and circle (and triangle? and arbitrary poly where client passes
    # in list of points?) particle?
    bg_color = (0, 0, 0, 0)  # fully transparent
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    max_radius = int(diameter // 2)
    center = max_radius  # for readability
    for radius in range(max_radius, 0, -1):
        alpha = int(lerp(center_alpha, outer_alpha, radius / max_radius))
        clr = (color[0], color[1], color[2], alpha)
        draw.ellipse((center - radius, center - radius, center + radius - 1, center + radius - 1), fill=clr)
    name = "{}:{}:{}:{}:{}".format("soft_circle_texture", diameter, color, center_alpha,
                                   outer_alpha)  # name must be unique for caching
    return Texture(name, img)


def make_soft_square_texture(size: int, color: Color, center_alpha: int = 255, outer_alpha: int = 0) -> Texture:
    """
    Return a :class:`Texture` of a square with the given diameter and color, fading out at its edges.

    :param int size: Diameter of the square and dimensions of the square Texture returned.
    :param Color color: Color of the square.
    :param int center_alpha: Alpha value of the square at its center.
    :param int outer_alpha: Alpha value of the square at its edges.

    :returns: New :class:`Texture` object.
    """

    bg_color = (0, 0, 0, 0)  # fully transparent
    img = PIL.Image.new("RGBA", (size, size), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    half_size = int(size // 2)
    for cur_size in range(0, half_size):
        alpha = int(lerp(outer_alpha, center_alpha, cur_size / half_size))
        clr = (color[0], color[1], color[2], alpha)
        # draw.ellipse((center-radius, center-radius, center+radius, center+radius), fill=clr)
        draw.rectangle((cur_size, cur_size, size - cur_size, size - cur_size), clr, None)
    name = "{}:{}:{}:{}:{}".format("gradientsquare", size, color, center_alpha,
                                   outer_alpha)  # name must be unique for caching
    return Texture(name, img)


# --- END TEXTURE FUNCTIONS # # #


def trim_image(image: PIL.Image.Image) -> PIL.Image.Image:
    """
    Crops the extra whitespace out of an image.

    :returns: New :py:class:`PIL.Image.Image` object.
    """
    bbox = image.getbbox()
    return image.crop(bbox)
