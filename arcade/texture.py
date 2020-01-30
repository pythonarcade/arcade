"""
Code related to working with textures.
"""

import os

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

from typing import Optional
from typing import List

from arcade import lerp
from arcade import RectList
from arcade import Color
from arcade import calculate_points

def _lerp_color(start_color: Color, end_color: Color, u: float) -> Color:
    return (
        int(lerp(start_color[0], end_color[0], u)),
        int(lerp(start_color[1], end_color[1], u)),
        int(lerp(start_color[2], end_color[2], u))
    )


class Texture:
    """
    Class that represents a texture.
    Usually created by the ``load_texture`` or ``load_textures`` commands.

    Attributes:
        :name:
        :image:
        :width: Width of the texture image in pixels
        :height: Height of the texture image in pixels

    """

    def __init__(self, name: str, image=None):
        from arcade.sprite import Sprite
        from arcade.sprite_list import SpriteList

        self.name = name
        self.texture = None
        self.image = image
        self._sprite: Optional[Sprite] = None
        self._sprite_list: Optional[SpriteList] = None
        self.hit_box_points = None

    @property
    def width(self) -> int:
        """
        Width of the texture in pixels
        """
        return self.image.width

    @property
    def height(self) -> int:
        """
        Height of the texture in pixels
        """
        return self.image.height

    def _create_cached_sprite(self):
        from arcade.sprite import Sprite
        from arcade.sprite_list import SpriteList

        if self._sprite is None:
            self._sprite = Sprite()
            self._sprite._texture = self
            self._sprite.textures = [self]

            self._sprite_list = SpriteList()
            self._sprite_list.append(self._sprite)

    def draw_sized(self,
                   center_x: float, center_y: float,
                   width: float,
                   height: float,
                   angle: float,
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

    def draw_scaled(self, center_x: float, center_y: float,
                    scale: float = 1.0,
                    angle: float = 0,
                    alpha: int = 255):

        """
        Draw the texture

        :param center_x: x location of where to draw the texture
        :param center_y: y location of where to draw the texture
        :param scale: Scale to draw rectangle. If none, defaults to 1
        :param angle: angle to rotate the texture
        :param alpha: transparency of texture. 0-255
        """

        self._create_cached_sprite()
        if self._sprite and self._sprite_list:
            self._sprite.center_x = center_x
            self._sprite.center_y = center_y
            self._sprite.scale = scale
            self._sprite.angle = angle
            self._sprite.alpha = alpha
            self._sprite_list.draw()


def load_textures(file_name: str,
                  image_location_list: RectList,
                  mirrored: bool = False,
                  flipped: bool = False) -> List['Texture']:
    """
    Load a set of textures off of a single image file.

    Note, if the code is to load only part of the image, the given x, y
    coordinates will start with the origin (0, 0) in the upper left of the
    image. When drawing, Arcade uses (0, 0)
    in the lower left corner when drawing. Be careful about this reversal.

    For a longer explanation of why computers sometimes start in the upper
    left, see:
    http://programarcadegames.com/index.php?chapter=introduction_to_graphics&lang=en#section_5

    :param str file_name: Name of the file.
    :param RectList image_location_list: List of image sub-locations. Each rectangle should be
           a list of four floats. ``[x, y, width, height]``.
    :param bool mirrored: If set to true, the image is mirrored left to right.
    :param bool flipped: If set to true, the image is flipped upside down.

    :Returns: List of textures loaded.
    :Raises: ValueError
    """
    # See if we already loaded this texture file, and we can just use a cached version.
    cache_file_name = "{}".format(file_name)
    if cache_file_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
        texture = load_texture.texture_cache[cache_file_name]  # type: ignore # dynamic attribute on function obj
        source_image = texture.image
    else:
        # If we should pull from local resources, replace with proper path
        if str(file_name).startswith(":resources:"):
            import os
            path = os.path.dirname(os.path.abspath(__file__))
            file_name = f"{path}/resources/{file_name[11:]}"

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


def load_texture(file_name: str,
                 x: float = 0,
                 y: float = 0,
                 width: float = 0, height: float = 0,
                 mirrored: bool = False,
                 flipped: bool = False,
                 scale: float = 1,
                 can_cache: bool = True) -> Texture:
    """
    Load image from disk and create a texture.

    Note, if the code is to load only part of the image, the given x, y
    coordinates will start with the origin (0, 0) in the upper left of the
    image. When drawing, Arcade uses (0, 0)
    in the lower left corner when drawing. Be careful about this reversal.

    For a longer explanation of why computers sometimes start in the upper
    left, see:
    http://programarcadegames.com/index.php?chapter=introduction_to_graphics&lang=en#section_5

    :param str file_name: Name of the file to that holds the texture.
    :param float x: X position of the crop area of the texture.
    :param float y: Y position of the crop area of the texture.
    :param float width: Width of the crop area of the texture.
    :param float height: Height of the crop area of the texture.
    :param bool mirrored: True if we mirror the image across the y axis
    :param bool flipped: True if we flip the image across the x axis
    :param float scale: Scale factor to apply on the new texture.
    :param bool can_cache: If a texture has already been loaded, load_texture will return the same texture in order \
    to save time. Somtimes this is not desirable, as resizine a cached texture will cause all other textures to \
    resize with it. Setting can_cache to false will prevent this issue at the expence of additional resources.

    :Returns: The new texture.
    :raises: None
    """

    # See if we already loaded this texture, and we can just use a cached version.
    cache_name = "{}{}{}{}{}{}{}{}".format(file_name, x, y, width, height, scale, flipped, mirrored)
    if can_cache and cache_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
        return load_texture.texture_cache[cache_name]  # type: ignore # dynamic attribute on function obj

    # See if we already loaded this texture file, and we can just use a cached version.
    cache_file_name = f"{file_name}"
    if cache_file_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
        texture = load_texture.texture_cache[cache_file_name]  # type: ignore # dynamic attribute on function obj
        source_image = texture.image
    else:
        # If we should pull from local resources, replace with proper path
        if str(file_name).startswith(":resources:"):
            import os
            path = os.path.dirname(os.path.abspath(__file__))
            file_name = f"{path}/resources/{file_name[11:]}"

        source_image = PIL.Image.open(file_name).convert('RGBA')
        result = Texture(cache_file_name, source_image)
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
    if mirrored:
        image = PIL.ImageOps.mirror(image)

    if flipped:
        image = PIL.ImageOps.flip(image)

    result = Texture(cache_name, image)
    load_texture.texture_cache[cache_name] = result  # type: ignore # dynamic attribute on function obj
    result.hit_box_points = calculate_points(image)
    return result


def load_spritesheet(file_name: str,
                     sprite_width: int,
                     sprite_height: int,
                     columns: int,
                     count: int) -> List:
    """
    Load a set of textures based on a single sprite sheet.

    Args:
        file_name:
        sprite_width:
        sprite_height:
        columns:
        count:

    Returns:

    """

    texture_list = []

    # If we should pull from local resources, replace with proper path
    if str(file_name).startswith(":resources:"):
        path = os.path.dirname(os.path.abspath(__file__))
        file_name = f"{path}/resources/{file_name[11:]}"

    source_image = PIL.Image.open(file_name).convert('RGBA')
    for sprite_no in range(count):
        row = sprite_no // columns
        column = sprite_no % columns
        start_x = sprite_width * column
        start_y = sprite_height * row
        image = source_image.crop((start_x, start_y, start_x + sprite_width, start_y + sprite_height))
        texture = Texture(f"{file_name}-{sprite_no}", image)
        texture_list.append(texture)

    return texture_list


def make_circle_texture(diameter: int, color: Color) -> Texture:
    """
    Return a Texture of a circle with given diameter and color

    :param int diameter: Diameter of the circle and dimensions of the square Texture returned
    :param Color color: Color of the circle
    :Returns: A Texture object
    :Raises: None
    """
    bg_color = (0, 0, 0, 0)  # fully transparent
    img = PIL.Image.new("RGBA", (diameter, diameter), bg_color)
    draw = PIL.ImageDraw.Draw(img)
    draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=color)
    name = "{}:{}:{}".format("circle_texture", diameter, color)  # name must be unique for caching
    return Texture(name, img)


def make_soft_circle_texture(diameter: int, color: Color, center_alpha: int = 255, outer_alpha: int = 0) -> Texture:
    """
    Return a Texture of a circle with given diameter, color, and alpha values at its center and edges

    Args:
        :diameter (int): Diameter of the circle and dimensions of the square Texture returned
        :color (Color): Color of the circle
        :center_alpha (int): alpha value of circle at its center
        :outer_alpha (int): alpha value of circle at its edge
    Returns:
        A Texture object
    Raises:
        None
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
    Return a Texture of a circle with given diameter and color, fading out at the edges.

    Args:
        :diameter (int): Diameter of the circle and dimensions of the square Texture returned
        :color (Color): Color of the circle
    Returns:
        The new texture.
    Raises:
        None
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


load_texture.texture_cache = dict()  # type: ignore


# --- END TEXTURE FUNCTIONS # # #


def trim_image(image: PIL.Image) -> PIL.Image:
    """
    Returns an image with extra whitespace cropped out.
    """
    bbox = image.getbbox()
    return image.crop(bbox)
