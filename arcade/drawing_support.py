import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw
import math
import os

from typing import List, Tuple

from arcade import lerp
from arcade import RectList
from arcade import Color


def get_points_for_thick_line(start_x: float, start_y:
                              float, end_x: float, end_y: float,
                              line_width: float):
    vector_x = start_x - end_x
    vector_y = start_y - end_y
    perpendicular_x = vector_y
    perpendicular_y = -vector_x
    length = math.sqrt(vector_x * vector_x + vector_y * vector_y)
    normal_x = perpendicular_x / length
    normal_y = perpendicular_y / length
    r1_x = start_x + normal_x * line_width / 2
    r1_y = start_y + normal_y * line_width / 2
    r2_x = start_x - normal_x * line_width / 2
    r2_y = start_y - normal_y * line_width / 2
    r3_x = end_x + normal_x * line_width / 2
    r3_y = end_y + normal_y * line_width / 2
    r4_x = end_x - normal_x * line_width / 2
    r4_y = end_y - normal_y * line_width / 2
    points = (r1_x, r1_y), (r2_x, r2_y), (r4_x, r4_y), (r3_x, r3_y)
    return points


def get_four_byte_color(color: Color) -> Color:
    """
    Given a RGB list, it will return RGBA.
    Given a RGBA list, it will return the same RGBA.

    :param Color color: Three or four byte tuple

    :returns:  return: Four byte RGBA tuple
    """

    if len(color) == 4:
        return color
    elif len(color) == 3:
        return color[0], color[1], color[2], 255
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def get_four_float_color(color: Color) -> Tuple[float, float, float, float]:
    """
    Given a 3 or 4 RGB/RGBA color where each color goes 0-255, this
    returns a RGBA tuple where each item is a scaled float from 0 to 1.

    :param Color color: Three or four byte tuple
    :return: Four floats as a RGBA tuple
    """
    if len(color) == 4:
        return color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255  # type: ignore
    elif len(color) == 3:
        return color[0] / 255, color[1] / 255, color[2] / 255, 1.0
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def make_transparent_color(color: Color, transparency: float):
    """
    Given a RGB color, along with an alpha, returns a RGBA color tuple.

    :param Color color: Three or four byte RGBA color
    :param float transparency: Transparency
    """
    return color[0], color[1], color[2], transparency


def rotate_point(x: float, y: float, cx: float, cy: float,
                 angle: float) -> Tuple[float, float]:
    """
    Rotate a point around a center.

    :param x: x value of the point you want to rotate
    :param y: y value of the point you want to rotate
    :param cx: x value of the center point you want to rotate around
    :param cy: y value of the center point you want to rotate around
    :param angle: Angle, in degrees, to rotate
    :return: Return rotated (x, y) pair
    :rtype: (float, float)
    """
    temp_x = x - cx
    temp_y = y - cy

    # now apply rotation
    rotated_x = temp_x * math.cos(math.radians(angle)) - temp_y * math.sin(math.radians(angle))
    rotated_y = temp_x * math.sin(math.radians(angle)) + temp_y * math.cos(math.radians(angle))

    # translate back
    rounding_precision = 2
    x = round(rotated_x + cx, rounding_precision)
    y = round(rotated_y + cy, rounding_precision)

    return [x, y]


class Texture:
    """
    Class that represents a texture.
    Usually created by the ``load_texture`` or ``load_textures`` commands.

    Attributes:
        :name:
        :image:
        :scale:
        :width: Width of the texture image in pixels
        :height: Height of the texture image in pixels

    """

    def __init__(self, name, image=None):
        self.name = name
        self.texture = None
        self.image = image
        self.scale = 1
        if image:
            self.width = image.width
            self.height = image.height
        else:
            self.width = 0
            self.height = 0

        self._sprite = None
        self._sprite_list = None
        self.unscaled_hitbox_points = None

    # noinspection PyUnusedLocal
    def draw(self, center_x: float, center_y: float, width: float,
             height: float, angle: float = 0,
             alpha: int = 255, transparent: bool = True,
             repeat_count_x=1, repeat_count_y=1):
        """

        Args:
            center_x:
            center_y:
            width:
            height:
            angle:
            alpha: Currently unused.
            transparent:  Currently unused.
            repeat_count_x: Currently unused.
            repeat_count_y:  Currently unused.

        Returns:

        """

        from arcade.sprite import Sprite
        from arcade.sprite_list import SpriteList

        if self._sprite is None:
            self._sprite = Sprite()
            self._sprite._texture = self
            self._sprite.textures = [self]

            self._sprite_list = SpriteList()
            self._sprite_list.append(self._sprite)

        self._sprite.center_x = center_x
        self._sprite.center_y = center_y
        self._sprite.width = width
        self._sprite.height = height
        self._sprite.angle = angle
        self._sprite.alpha = alpha

        self._sprite_list.draw()


def load_textures(file_name: str,
                  image_location_list: RectList,
                  mirrored: bool = False,
                  flipped: bool = False,
                  scale: float = 1) -> List['Texture']:
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
    :param float scale: Scale factor to apply on each new texture.


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
        cache_name = "{}{}{}{}{}{}{}{}".format(file_name, x, y, width, height, scale, flipped, mirrored)
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
            result.scale = scale
        texture_info_list.append(result)

    return texture_info_list


def calculate_points(image):
    """
    Given an image, this returns points that make up a hit box around it. Attempts
    to trim out transparent pixels.

    :param Image image:

    :Returns: List of points

    """
    left_border = 0
    good = True
    while good and left_border < image.width:
        for row in range(image.height):
            pos = (left_border, row)
            pixel = image.getpixel(pos)
            if type(pixel) is int or len(pixel) != 4:
                raise TypeError("Error, calculate_points called on image not in RGBA format")
            else:
                if pixel[3] != 0:
                    good = False
                    break
        if good:
            left_border += 1

    right_border = image.width - 1
    good = True
    while good and right_border > 0:
        for row in range(image.height):
            pos = (right_border, row)
            pixel = image.getpixel(pos)
            if pixel[3] != 0:
                good = False
                break
        if good:
            right_border -= 1

    top_border = 0
    good = True
    while good and top_border < image.height:
        for column in range(image.width):
            pos = (column, top_border)
            pixel = image.getpixel(pos)
            if pixel[3] != 0:
                good = False
                break
        if good:
            top_border += 1

    bottom_border = image.height - 1
    good = True
    while good and bottom_border > 0:
        for column in range(image.width):
            pos = (column, bottom_border)
            pixel = image.getpixel(pos)
            if pixel[3] != 0:
                good = False
                break
        if good:
            bottom_border -= 1

    def _check_corner_offset(start_x, start_y, x_direction, y_direction):

        bad = False
        offset = 0
        while not bad:
            y = start_y + (offset * y_direction)
            x = start_x
            for count in range(offset + 1):
                pixel = image.getpixel((x, y))
                # print(f"({x}, {y}) = {pixel} | ", end="")
                if pixel[3] != 0:
                    bad = True
                    break
                y -= y_direction
                x += x_direction
            # print(f" - {bad}")
            offset += 1
        # print(f"offset: {offset}")
        return offset

    def _r(point, height, width):
        return point[0] - width / 2, (height - point[1]) - height / 2

    top_left_corner_offset = _check_corner_offset(left_border, top_border, 1, 1)
    top_right_corner_offset = _check_corner_offset(right_border, top_border, -1, 1)
    bottom_left_corner_offset = _check_corner_offset(left_border, bottom_border, 1, -1)
    bottom_right_corner_offset = _check_corner_offset(right_border, bottom_border, -1, -1)

    p1 = left_border + top_left_corner_offset, top_border
    p2 = right_border - top_right_corner_offset, top_border
    p3 = right_border, top_border + top_right_corner_offset
    p4 = right_border, bottom_border - bottom_right_corner_offset
    p5 = right_border - bottom_right_corner_offset, bottom_border
    p6 = left_border + bottom_left_corner_offset, bottom_border
    p7 = left_border, bottom_border - bottom_left_corner_offset
    p8 = left_border, top_border + top_left_corner_offset

    result = []

    h = image.height
    w = image.width
    result.append(_r(p1, h, w))
    if top_left_corner_offset:
        result.append(_r(p2, h, w))

    result.append(_r(p3, h, w))
    if top_right_corner_offset:
        result.append(_r(p4, h, w))

    result.append(_r(p5, h, w))
    if bottom_right_corner_offset:
        result.append(_r(p6, h, w))

    result.append(_r(p7, h, w))
    if bottom_left_corner_offset:
        result.append(_r(p8, h, w))

    # Remove duplicates
    result = list(dict.fromkeys(result))

    return result

def load_texture(file_name: str, x: float = 0, y: float = 0,
                 width: float = 0, height: float = 0,
                 mirrored: bool = False,
                 flipped: bool = False,
                 scale: float = 1) -> Texture:
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

    :Returns: The new texture.
    :raises: None
    """

    # See if we already loaded this texture, and we can just use a cached version.
    cache_name = "{}{}{}{}{}{}{}{}".format(file_name, x, y, width, height, scale, flipped, mirrored)
    if cache_name in load_texture.texture_cache:  # type: ignore # dynamic attribute on function obj
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
    result.unscaled_hitbox_points = calculate_points(image)
    result.scale = scale
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
    name = "{}:{}:{}:{}".format("gradientsquare", size, color, center_alpha,
                                outer_alpha)  # name must be unique for caching
    return Texture(name, img)


def _lerp_color(start_color: Color, end_color: Color, u: float) -> Color:
    return (
        int(lerp(start_color[0], end_color[0], u)),
        int(lerp(start_color[1], end_color[1], u)),
        int(lerp(start_color[2], end_color[2], u))
    )


load_texture.texture_cache = dict()  # type: ignore


# --- END TEXTURE FUNCTIONS # # #


def trim_image(image: PIL.Image) -> PIL.Image:
    """
    Returns an image with extra whitespace cropped out.
    """
    bbox = image.getbbox()
    return image.crop(bbox)
