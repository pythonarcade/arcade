"""
This module contains commands for basic graphics drawing commands.
(Drawing primitives.)

Many of these commands are slow, because they load everything to the
graphics card each time a shape is drawn. For faster drawing, see the
Buffered Draw Commands.
"""
# pylint: disable=too-many-arguments, too-many-locals, too-few-public-methods

import math
import PIL.Image
import PIL.ImageOps
import numpy as np

import pyglet.gl as gl

from typing import List

from arcade.window_commands import get_projection
from arcade.window_commands import get_window
from arcade.arcade_types import Color
from arcade.arcade_types import PointList
from arcade import shader
from arcade.earclip import earclip


line_vertex_shader = '''
    #version 330
    uniform mat4 Projection;
    in vec2 in_vert;
    in vec4 in_color;
    out vec4 v_color;
    void main() {
       gl_Position = Projection * vec4(in_vert, 0.0, 1.0);
       v_color = in_color;
    }
'''

line_fragment_shader = '''
    #version 330
    in vec4 v_color;
    out vec4 f_color;
    void main() {
        f_color = v_color;
    }
'''


def get_four_byte_color(color: Color) -> Color:
    """
    Given a RGB list, it will return RGBA.
    Given a RGBA list, it will return the same RGBA.

    :param color: Color
    :return: color: Color
    """
    if len(color) == 4:
        return color
    elif len(color) == 3:
        return color[0], color[1], color[2], 255
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def get_four_float_color(color: Color) -> (float, float, float, float):
    """
    Given a 3 or 4 RGB/RGBA color where each color goes 0-255, this
    returns a RGBA list where each item is a scaled float from 0 to 1.

    :param color:
    :return:
    """
    if len(color) == 4:
        return color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255
    elif len(color) == 3:
        return color[0] / 255, color[1] / 255, color[2] / 255, 1.0
    else:
        raise ValueError("This isn't a 3 or 4 byte color")


def make_transparent_color(color: Color, transparency: float):
    """
    Given a RGB color, along with an alpha, returns a RGBA color tuple.
    """
    return color[0], color[1], color[2], transparency


def rotate_point(x: float, y: float, cx: float, cy: float,
                 angle: float) -> (float, float):
    """
    Rotate a point around a center.

    :param x: x value of the point you want to rotate
    :param y: y value of the point you want to rotate
    :param cx: x value of the center point you want to rotate around
    :param cy: y value of the center point you want to rotate around
    :param angle: Angle, in degrees, to rotate
    :return: Return rotated (x, y) pair

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

    return x, y


class Texture:
    """
    Class that represents a texture.
    Usually created by the ``load_texture`` or ``load_textures`` commands.

    Attributes:
        :id: ID of the texture as assigned by OpenGL
        :width: Width of the texture image in pixels
        :height: Height of the texture image in pixels

    """

    def __init__(self, name, image=None):
        self.name = name
        self.image = image
        self.scale = 1
        if image:
            self.width = image.width
            self.height = image.height
        else:
            self.width = 0
            self.height = 0

        self._sprite = None


    def draw(self, center_x: float, center_y: float, width: float,
             height: float, angle: float=0,
             alpha: float=1, transparent: bool=True,
             repeat_count_x=1, repeat_count_y=1):

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

        self._sprite_list.draw()


def load_textures(file_name: str,
                  image_location_list: PointList,
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

    Args:
        :file_name: Name of the file.
        :image_location_list: List of image locations. Each location should be
         a list of four floats. ``[x, y, width, height]``.
        :mirrored=False: If set to true, the image is mirrored left to right.
        :flipped=False: If set to true, the image is flipped upside down.
    Returns:
        :list: List of textures loaded.
    Raises:
        :SystemError:
    """
    source_image = PIL.Image.open(file_name)

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

        image = source_image.crop((x, y, x + width, y + height))
        # image = _trim_image(image)

        if mirrored:
            image = PIL.ImageOps.mirror(image)

        if flipped:
            image = PIL.ImageOps.flip(image)

        texture_info_list.append(Texture(image=image))

    return texture_info_list


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

    Args:
        :filename (str): Name of the file to that holds the texture.
        :x (float): X position of the crop area of the texture.
        :y (float): Y position of the crop area of the texture.
        :width (float): Width of the crop area of the texture.
        :height (float): Height of the crop area of the texture.
        :scale (float): Scale factor to apply on the new texture.
    Returns:
        The new texture.
    Raises:
        None

    """

    # See if we already loaded this file, and we can just use a cached version.
    cache_name = "{}{}{}{}{}{}{}{}".format(file_name, x, y, width, height, scale, flipped, mirrored)
    if cache_name in load_texture.texture_cache:
        return load_texture.texture_cache[cache_name]

    source_image = PIL.Image.open(file_name)

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
    load_texture.texture_cache[cache_name] = result
    result.scale = scale
    return result


load_texture.texture_cache = dict()


# --- END TEXTURE FUNCTIONS # # #


def trim_image(image: PIL.Image) -> PIL.Image:
    """
    Returns an image with extra whitespace cropped out.
    """
    bbox = image.getbbox()
    return image.crop(bbox)


# --- BEGIN ARC FUNCTIONS # # #


def draw_arc_filled(center_x: float, center_y: float,
                    width: float, height: float,
                    color: Color,
                    start_angle: float, end_angle: float,
                    tilt_angle: float = 0,
                    num_segments: int = 128):
    """
    Draw a filled in arc. Useful for drawing pie-wedges, or Pac-Man.

    Args:
        :center_x: x position that is the center of the arc.
        :center_y: y position that is the center of the arc.
        :width: width of the arc.
        :height: height of the arc.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :start_angle: start angle of the arc in degrees.
        :end_angle: end angle of the arc in degrees.
        :tilt_angle: angle the arc is tilted.
    Returns:
        None
    Raises:
        None
    """
    unrotated_point_list = [[0, 0]]

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)

    for segment in range(start_segment, end_segment + 1):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        unrotated_point_list.append((x, y))

    if tilt_angle == 0:
        uncentered_point_list = unrotated_point_list
    else:
        uncentered_point_list = []
        for point in unrotated_point_list:
            uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

    point_list = []
    for point in uncentered_point_list:
        point_list.append((point[0] + center_x, point[1] + center_y))

    _generic_draw_line_strip(point_list, color, 1, gl.GL_TRIANGLE_FAN)


def draw_arc_outline(center_x: float, center_y: float, width: float,
                     height: float, color: Color,
                     start_angle: float, end_angle: float,
                     border_width: float = 1, tilt_angle: float = 0,
                     num_segments: int = 128):
    """
    Draw the outside edge of an arc. Useful for drawing curved lines.

    Args:
        :center_x: x position that is the center of the arc.
        :center_y: y position that is the center of the arc.
        :width: width of the arc.
        :height: height of the arc.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :start_angle: start angle of the arc in degrees.
        :end_angle: end angle of the arc in degrees.
        :border_width: width of line in pixels.
        :angle: angle the arc is tilted.
    Returns:
        None
    Raises:
        None
    """
    unrotated_point_list = []

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)

    inside_width = width - border_width / 2
    outside_width = width + border_width / 2
    inside_height = height - border_width / 2
    outside_height = height + border_width / 2

    for segment in range(start_segment, end_segment + 1):
        theta = 2.0 * math.pi * segment / num_segments

        x1 = inside_width * math.cos(theta)
        y1 = inside_height * math.sin(theta)

        x2 = outside_width * math.cos(theta)
        y2 = outside_height * math.sin(theta)

        unrotated_point_list.append((x1, y1))
        unrotated_point_list.append((x2, y2))

    if tilt_angle == 0:
        uncentered_point_list = unrotated_point_list
    else:
        uncentered_point_list = []
        for point in unrotated_point_list:
            uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

    point_list = []
    for point in uncentered_point_list:
        point_list.append((point[0] + center_x, point[1] + center_y))

    _generic_draw_line_strip(point_list, color, 1, gl.GL_TRIANGLE_STRIP)


# --- END ARC FUNCTIONS # # #


# --- BEGIN PARABOLA FUNCTIONS # # #

def draw_parabola_filled(start_x: float, start_y: float, end_x: float,
                         height: float, color: Color,
                         tilt_angle: float = 0):
    """
    Draws a filled in parabola.

    Args:
        :start_x: The starting x position of the parabola
        :start_y: The starting y position of the parabola
        :end_x: The ending x position of the parabola
        :height: The height of the parabola
        :color: The color of the parabola
        :tilt_angle: The angle of the tilt of the parabola
    Returns:
        None
    Raises:
        None

    """
    center_x = (start_x + end_x) / 2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    draw_arc_filled(center_x, center_y, width, height, color,
                    start_angle, end_angle, tilt_angle)


def draw_parabola_outline(start_x: float, start_y: float, end_x: float,
                          height: float, color: Color,
                          border_width: float = 1, tilt_angle: float = 0):
    """
    Draws the outline of a parabola.

    Args:
        :start_x: The starting x position of the parabola
        :start_y: The starting y position of the parabola
        :end_x: The ending x position of the parabola
        :height: The height of the parabola
        :color: The color of the parabola
        :border_width: The width of the parabola
        :tile_angle: The angle of the tilt of the parabola
    Returns:
        None
    Raises:
        None

    """
    center_x = (start_x + end_x) / 2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    draw_arc_outline(center_x, center_y, width, height, color,
                     start_angle, end_angle, border_width, tilt_angle)


# --- END PARABOLA FUNCTIONS # # #


# --- BEGIN CIRCLE FUNCTIONS # # #

def draw_circle_filled(center_x: float, center_y: float, radius: float,
                       color: Color):
    """
    Draw a filled-in circle.

    Args:
        :center_x: x position that is the center of the circle.
        :center_y: y position that is the center of the circle.
        :radius: width of the circle.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :num_segments (int): float of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    Returns:
        None
    Raises:
        None
    """
    width = radius
    height = radius
    draw_ellipse_filled(center_x, center_y, width, height, color)


def draw_circle_outline(center_x: float, center_y: float, radius: float,
                        color: Color, border_width: float = 1):
    """
    Draw the outline of a circle.

    Args:
        :center_x: x position that is the center of the circle.
        :center_y: y position that is the center of the circle.
        :radius: width of the circle.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: Width of the circle outline in pixels.
        :num_segments: float of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    Returns:
        None
    Raises:
        None
    """
    width = radius
    height = radius
    draw_ellipse_outline(center_x, center_y, width, height,
                         color, border_width)


# --- END CIRCLE FUNCTIONS # # #


# --- BEGIN ELLIPSE FUNCTIONS # # #

def draw_ellipse_filled(center_x: float, center_y: float,
                        width: float, height: float, color: Color,
                        tilt_angle: float = 0, num_segments: int = 128):
    """
    Draw a filled in ellipse.

    Args:
        :center_x: x position that is the center of the circle.
        :center_y: y position that is the center of the circle.
        :height: height of the ellipse.
        :width: width of the ellipse.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :angle: Angle in degrees to tilt the ellipse.
        :num_segments: float of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    Returns:
        None
    Raises:
        None
    """

    unrotated_point_list = []

    for segment in range(num_segments):
        theta = 2.0 * 3.1415926 * segment / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        unrotated_point_list.append((x, y))

    if tilt_angle == 0:
        uncentered_point_list = unrotated_point_list
    else:
        uncentered_point_list = []
        for point in unrotated_point_list:
            uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

    point_list = []
    for point in uncentered_point_list:
        point_list.append((point[0] + center_x, point[1] + center_y))

    _generic_draw_line_strip(point_list, color, 1, gl.GL_TRIANGLE_FAN)


def draw_ellipse_outline(center_x: float, center_y: float, width: float,
                         height: float, color: Color,
                         border_width: float = 1, tilt_angle: float = 0,
                         num_segments = 128):
    """
    Draw the outline of an ellipse.

    Args:
        :center_x: x position that is the center of the circle.
        :center_y: y position that is the center of the circle.
        :height: height of the ellipse.
        :width: width of the ellipse.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: Width of the circle outline in pixels.
        :tilt_angle: Angle in degrees to tilt the ellipse.
    Returns:
        None
    Raises:
        None
    """

    if border_width == 1:
        unrotated_point_list = []

        for segment in range(num_segments):
            theta = 2.0 * 3.1415926 * segment / num_segments

            x = width * math.cos(theta)
            y = height * math.sin(theta)

            unrotated_point_list.append((x, y))

        if tilt_angle == 0:
            uncentered_point_list = unrotated_point_list
        else:
            uncentered_point_list = []
            for point in unrotated_point_list:
                uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

        point_list = []
        for point in uncentered_point_list:
            point_list.append((point[0] + center_x, point[1] + center_y))

        _generic_draw_line_strip(point_list, color, border_width, gl.GL_LINE_LOOP)
    else:

        unrotated_point_list = []

        start_segment = 0
        end_segment = num_segments

        inside_width = width - border_width / 2
        outside_width = width + border_width / 2
        inside_height = height - border_width / 2
        outside_height = height + border_width / 2

        for segment in range(start_segment, end_segment + 1):
            theta = 2.0 * math.pi * segment / num_segments

            x1 = inside_width * math.cos(theta)
            y1 = inside_height * math.sin(theta)

            x2 = outside_width * math.cos(theta)
            y2 = outside_height * math.sin(theta)

            unrotated_point_list.append((x1, y1))
            unrotated_point_list.append((x2, y2))

        if tilt_angle == 0:
            uncentered_point_list = unrotated_point_list
        else:
            uncentered_point_list = []
            for point in unrotated_point_list:
                uncentered_point_list.append(rotate_point(point[0], point[1], 0, 0, tilt_angle))

        point_list = []
        for point in uncentered_point_list:
            point_list.append((point[0] + center_x, point[1] + center_y))

        _generic_draw_line_strip(point_list, color, 1, gl.GL_TRIANGLE_STRIP)

# --- END ELLIPSE FUNCTIONS # # #


# --- BEGIN LINE FUNCTIONS # # #

def _generic_draw_line_strip(point_list: PointList,
                             color: Color,
                             line_width: float = 1,
                             mode: int = gl.GL_LINE_STRIP):
    """
    Draw a line strip. A line strip is a set of continuously connected
    line segments.

    Args:
        :point_list: List of points making up the line. Each point is
         in a list. So it is a list of lists.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: Width of the line in pixels.
    Returns:
        None
    Raises:
        None
    """
    program = shader.program(
        vertex_shader=line_vertex_shader,
        fragment_shader=line_fragment_shader,
    )
    buffer_type = np.dtype([('vertex', '2f4'), ('color', '4B')])
    data = np.zeros(len(point_list), dtype=buffer_type)

    data['vertex'] = point_list

    color = get_four_byte_color(color)
    data['color'] = color

    vbo = shader.buffer(data.tobytes())
    vbo_desc = shader.BufferDescription(
        vbo,
        '2f 4B',
        ('in_vert', 'in_color'),
        normalized=['in_color']
    )

    vao_content = [vbo_desc]

    vao = shader.vertex_array(program, vao_content)
    with vao:
        program['Projection'] = get_projection().flatten()
        gl.glLineWidth(line_width)
        gl.glPointSize(line_width)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glHint(gl.GL_POLYGON_SMOOTH_HINT, gl.GL_NICEST)

        vao.render(mode=mode)


def draw_line_strip(point_list: PointList,
                    color: Color, line_width: float = 1):
    """
    Draw a multi-point line.

    Args:
        point_list:
        color:
        line_width:
    """
    if line_width == 1:
        _generic_draw_line_strip(point_list, color, line_width, gl.GL_LINE_STRIP)
    else:
        triangle_point_list = []
        # This needs a lot of improvement
        last_point = None
        for point in point_list:
            if last_point is not None:
                points = _get_points_for_thick_line(last_point[0], last_point[1], point[0], point[1], line_width)
                reordered_points = points[1], points[0], points[2], points[3]
                triangle_point_list.extend(reordered_points)
            last_point = point
        _generic_draw_line_strip(triangle_point_list, color, 1, gl.GL_TRIANGLE_STRIP)


def _get_points_for_thick_line(start_x: float, start_y:
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


def draw_line(start_x: float, start_y: float, end_x: float, end_y: float,
              color: Color, line_width: float=1):
    """
    Draw a line.

    Args:
        :start_x: x position of line starting point.
        :start_y: y position of line starting point.
        :end_x: x position of line ending point.
        :end_y: y position of line ending point.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    """

    points = (start_x, start_y), (end_x, end_y)
    if line_width == 1:
        draw_line_strip(points, color, line_width)
    else:
        points = _get_points_for_thick_line(start_x, start_y, end_x, end_y, line_width)
        triangle_point_list = points[1], points[0], points[2], points[3]
        _generic_draw_line_strip(triangle_point_list, color, 1, gl.GL_TRIANGLE_STRIP)


def draw_lines(point_list: PointList,
               color: Color,
               line_width: float=1):
    """
    Draw a set of lines.

    Draw a line between each pair of points specified.

    Args:
        :point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: Width of the line in pixels.
    Returns:
        None
    Raises:
        None
    """

    if line_width == 1:
        _generic_draw_line_strip(point_list, color, line_width, gl.GL_LINES)
    else:
        triangle_point_list = []
        last_point = None
        for point in point_list:
            if last_point is not None:
                points = _get_points_for_thick_line(last_point[0], last_point[1], point[0], point[1], line_width)
                reordered_points = points[1], points[0], points[2], points[0], points[2], points[3]
                triangle_point_list.extend(reordered_points)
                _generic_draw_line_strip(triangle_point_list, color, 1, gl.GL_TRIANGLES)
                last_point = None
            else:
                last_point = point


# --- BEGIN POINT FUNCTIONS # # #


def draw_point(x: float, y: float, color: Color, size: float):
    """
    Draw a point.

    Args:
        :x: x position of point.
        :y: y position of point.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :size: Size of the point in pixels.
    Returns:
        None
    Raises:
        None
    """
    if size == 1:
        point_list = [(x, y)]
        _generic_draw_line_strip(point_list, color, size, gl.GL_POINTS)
    else:
        draw_rectangle_filled(x, y, size / 2, size / 2, color)


def _get_points_for_points(point_list, size):
    new_point_list = []
    hs = size / 2
    for point in point_list:
        x = point[0]
        y = point[1]
        new_point_list.append((x - hs, y - hs))
        new_point_list.append((x + hs, y - hs))
        new_point_list.append((x + hs, y + hs))
    return new_point_list


def draw_points(point_list: PointList,
                color: Color, size: float = 1):
    """
    Draw a set of points.

    Args:
        :point_list: List of points Each point is
         in a list. So it is a list of lists.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :size: Size of the point in pixels.
    Returns:
        None
    Raises:
        None
    """
    if size == 1:
        _generic_draw_line_strip(point_list, color, size, gl.GL_POINTS)
    else:
        new_point_list = _get_points_for_points(point_list, size)
        _generic_draw_line_strip(new_point_list, color, 1, gl.GL_TRIANGLES)


# --- END POINT FUNCTIONS # # #

# --- BEGIN POLYGON FUNCTIONS # # #


def draw_polygon_filled(point_list: PointList,
                        color: Color):
    """
    Draw a polygon that is filled in.

    Args:
        :point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    Returns:
        None
    Raises:
        None
    """

    triangle_points = earclip(point_list)
    flattened_list = [i for g in triangle_points for i in g]
    _generic_draw_line_strip(flattened_list, color, 1, gl.GL_TRIANGLES)


def draw_polygon_outline(point_list: PointList,
                         color: Color, line_width: float=1):
    """
    Draw a polygon outline. Also known as a "line loop."

    Args:
        :point_list: List of points making up the lines. Each point is
         in a list. So it is a list of lists.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: Width of the line in pixels.
    Returns:
        None
    Raises:
        None
    """
    if line_width == 1:
        _generic_draw_line_strip(point_list, color, line_width, gl.GL_LINE_LOOP)
    else:
        new_point_list = [point for point in point_list]
        new_point_list.append(point_list[0])

        triangle_point_list = []
        # This needs a lot of improvement
        last_point = None
        for point in new_point_list:
            if last_point is not None:
                points = _get_points_for_thick_line(last_point[0], last_point[1], point[0], point[1], line_width)
                reordered_points = points[1], points[0], points[2], points[3]
                triangle_point_list.extend(reordered_points)
            last_point = point

        points = _get_points_for_thick_line(new_point_list[0][0], new_point_list[0][1], new_point_list[1][0], new_point_list[1][1], line_width)
        triangle_point_list.append(points[1])
        _generic_draw_line_strip(triangle_point_list, color, 1, gl.GL_TRIANGLE_STRIP)


def draw_triangle_filled(x1: float, y1: float,
                         x2: float, y2: float,
                         x3: float, y3: float, color: Color):
    """
    Draw a filled in triangle.

    Args:
        :x1: x value of first coordinate.
        :y1: y value of first coordinate.
        :x2: x value of second coordinate.
        :y2: y value of second coordinate.
        :x3: x value of third coordinate.
        :y3: y value of third coordinate.
        :color: Color of triangle.
    Returns:
        None
    Raises:
        None
    """

    first_point = (x1, y1)
    second_point = (x2, y2)
    third_point = (x3, y3)
    point_list = (first_point, second_point, third_point)
    _generic_draw_line_strip(point_list, color, 1, gl.GL_TRIANGLES)


def draw_triangle_outline(x1: float, y1: float,
                          x2: float, y2: float,
                          x3: float, y3: float, color: Color,
                          border_width: float = 1):
    """
    Draw a the outline of a triangle.

    Args:
        :x1: x value of first coordinate.
        :y1: y value of first coordinate.
        :x2: x value of second coordinate.
        :y2: y value of second coordinate.
        :x3: x value of third coordinate.
        :y3: y value of third coordinate.
        :color: Color of triangle.
        :border_width: Width of the border in pixels. Defaults to 1.
    Returns:
        None
    Raises:
        None
    """
    first_point = [x1, y1]
    second_point = [x2, y2]
    third_point = [x3, y3]
    point_list = (first_point, second_point, third_point)
    draw_polygon_outline(point_list, color, border_width)


# --- END POLYGON FUNCTIONS # # #


# --- BEGIN RECTANGLE FUNCTIONS # # #


def draw_lrtb_rectangle_outline(left: float, right: float, top: float,
                                bottom: float, color: Color,
                                border_width: float = 1):
    """
    Draw a rectangle by specifying left, right, top, and bottom edges.

    Args:
        :left: The x coordinate of the left edge of the rectangle.
        :right: The x coordinate of the right edge of the rectangle.
        :top: The y coordinate of the top of the rectangle.
        :bottom: The y coordinate of the rectangle bottom.
        :color: The color of the rectangle.
        :border_width: The width of the border in pixels. Defaults to one.
    Returns:
        None
    Raises:
        :AttributeErrror: Raised if left > right or top < bottom.

    """

    if left > right:
        raise AttributeError("Left coordinate must be less than or equal to "
                             "the right coordinate")

    if bottom > top:
        raise AttributeError("Bottom coordinate must be less than or equal to "
                             "the top coordinate")

    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    width = right - left
    height = top - bottom
    draw_rectangle_outline(center_x, center_y, width, height, color,
                           border_width)


def draw_xywh_rectangle_outline(bottom_left_x: float, bottom_left_y: float,
                                width: float, height: float,
                                color: Color,
                                border_width: float = 1):
    """
    Draw a rectangle extending from bottom left to top right

    Args:
        :bottom_left_x: The x coordinate of the left edge of the rectangle.
        :bottom_left_y: The y coordinate of the bottom of the rectangle.
        :width: The width of the rectangle.
        :height: The height of the rectangle.
        :color: The color of the rectangle.
        :border_width: The width of the border in pixels. Defaults to one.
    Returns:
        None
    Raises:
        None

    """
    center_x = bottom_left_x + (width / 2)
    center_y = bottom_left_y + (height / 2)
    draw_rectangle_outline(center_x, center_y, width, height, color,
                           border_width)


def draw_rectangle_outline(center_x: float, center_y: float, width: float,
                           height: float, color: Color,
                           border_width: float=1, tilt_angle: float=0):
    """
    Draw a rectangle outline.

    Args:
        :x: x coordinate of top left rectangle point.
        :y: y coordinate of top left rectangle point.
        :width: width of the rectangle.
        :height: height of the rectangle.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: width of the lines, in pixels.
        :angle: rotation of the rectangle. Defaults to zero.
    Returns:
        None
    Raises:
        None
    """

    if border_width == 1:
        p1 = -width // 2 + center_x, -height // 2 + center_y
        p2 = width // 2 + center_x, -height // 2 + center_y
        p3 = width // 2 + center_x, height // 2 + center_y
        p4 = -width // 2 + center_x, height // 2 + center_y

        if tilt_angle != 0:
            p1 = rotate_point(p1[0], p1[1], center_x, center_y, tilt_angle)
            p2 = rotate_point(p2[0], p2[1], center_x, center_y, tilt_angle)
            p3 = rotate_point(p3[0], p3[1], center_x, center_y, tilt_angle)
            p4 = rotate_point(p4[0], p4[1], center_x, center_y, tilt_angle)

        _generic_draw_line_strip((p1, p2, p3, p4), color, border_width, gl.GL_LINE_LOOP)
    else:
        inside_width = width - border_width / 2
        inside_height = height - border_width / 2
        outside_width = width + border_width / 2
        outside_height = height + border_width / 2

        i_lb = -inside_width // 2 + center_x, -inside_height // 2 + center_y
        i_rb = inside_width // 2 + center_x, -inside_height // 2 + center_y
        i_rt = inside_width // 2 + center_x, inside_height // 2 + center_y
        i_lt = -inside_width // 2 + center_x, inside_height // 2 + center_y

        o_lb = -outside_width // 2 + center_x, -outside_height // 2 + center_y
        o_rb = outside_width // 2 + center_x, -outside_height // 2 + center_y
        o_rt = outside_width // 2 + center_x, outside_height // 2 + center_y
        o_lt = -outside_width // 2 + center_x, outside_height // 2 + center_y

        point_list = o_lt, i_lt, o_rt, i_rt, o_rb, i_rb, o_lb, i_lb, o_lt, i_lt

        if tilt_angle != 0:
            point_list_2 = []
            for point in point_list:
                new_point = rotate_point(point[0], point[1], center_x, center_y, tilt_angle)
                point_list_2.append(new_point)
            point_list = point_list_2

        _generic_draw_line_strip(point_list, color, 1, gl.GL_TRIANGLE_STRIP)



def draw_lrtb_rectangle_filled(left: float, right: float, top: float,
                               bottom: float, color: Color):
    """
    Draw a rectangle by specifying left, right, top, and bottom edges.

    Args:
        :left: The x coordinate of the left edge of the rectangle.
        :right: The x coordinate of the right edge of the rectangle.
        :top: The y coordinate of the top of the rectangle.
        :bottom: The y coordinate of the rectangle bottom.
        :color: The color of the rectangle.
        :border_width: The width of the border in pixels. Defaults to one.
    Returns:
        None
    Raises:
        :AttributeErrror: Raised if left > right or top < bottom.

    """
    if left > right:
        raise AttributeError("Left coordinate {} must be less than or equal "
                             "to the right coordinate {}".format(left, right))

    if bottom > top:
        raise AttributeError("Bottom coordinate {} must be less than or equal "
                             "to the top coordinate {}".format(bottom, top))

    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    width = right - left
    height = top - bottom
    draw_rectangle_filled(center_x, center_y, width, height, color)


def draw_xywh_rectangle_filled(bottom_left_x: float, bottom_left_y: float,
                               width: float, height: float,
                               color: Color):
    """
    Draw a filled rectangle extending from bottom left to top right

    Args:
        :bottom_left_x: The x coordinate of the left edge of the rectangle.
        :bottom_left_y: The y coordinate of the bottom of the rectangle.
        :width: The width of the rectangle.
        :height: The height of the rectangle.
        :color: The color of the rectangle.
    Returns:
        None
    Raises:
        None

    """

    center_x = bottom_left_x + (width / 2)
    center_y = bottom_left_y + (height / 2)
    draw_rectangle_filled(center_x, center_y, width, height, color)


def draw_rectangle_filled(center_x: float, center_y: float, width: float,
                          height: float, color: Color,
                          tilt_angle: float=0):
    """
    Draw a filled-in rectangle.

    Args:
        :center_x: x coordinate of rectangle center.
        :center_y: y coordinate of rectangle center.
        :width: width of the rectangle.
        :height: height of the rectangle.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :angle: rotation of the rectangle. Defaults to zero.

    """
    p1 = -width // 2 + center_x, -height // 2 + center_y
    p2 = width // 2 + center_x, -height // 2 + center_y
    p3 = width // 2 + center_x, height // 2 + center_y
    p4 = -width // 2 + center_x, height // 2 + center_y

    if tilt_angle != 0:
        p1 = rotate_point(p1[0], p1[1], center_x, center_y, tilt_angle)
        p2 = rotate_point(p2[0], p2[1], center_x, center_y, tilt_angle)
        p3 = rotate_point(p3[0], p3[1], center_x, center_y, tilt_angle)
        p4 = rotate_point(p4[0], p4[1], center_x, center_y, tilt_angle)

    _generic_draw_line_strip((p1, p2, p4, p3), color, 1, gl.GL_TRIANGLE_STRIP)


def draw_texture_rectangle(center_x: float, center_y: float, width: float,
                           height: float, texture: Texture, angle: float=0,
                           alpha: float=1,
                           repeat_count_x=1, repeat_count_y=1):
    """
    Draw a textured rectangle on-screen.

    Args:
        :center_x: x coordinate of rectangle center.
        :center_y: y coordinate of rectangle center.
        :width: width of the rectangle.
        :height: height of the rectangle.
        :texture: identifier of texture returned from load_texture() call
        :angle: rotation of the rectangle. Defaults to zero.
        :alpha: Transparency of image.
    Returns:
        None
    Raises:
        None

    """

    texture.draw(center_x, center_y, width,
                 height, angle, alpha,
                 repeat_count_x, repeat_count_y)


def draw_xywh_rectangle_textured(bottom_left_x: float, bottom_left_y: float,
                                 width: float, height: float,
                                 texture: Texture, angle: float=0,
                                 alpha: float=1, transparent: bool=True,
                                 repeat_count_x=1, repeat_count_y=1):
    """
    Draw a texture extending from bottom left to top right.

    Args:
        :bottom_left_x: The x coordinate of the left edge of the rectangle.
        :bottom_left_y: The y coordinate of the bottom of the rectangle.
        :width: The width of the rectangle.
        :height: The height of the rectangle.
        :texture: identifier of texture returned from load_texture() call
        :angle: rotation of the rectangle. Defaults to zero.
        :alpha: Transparency of image.
    Returns:
        None
    Raises:
        None
    """

    center_x = bottom_left_x + (width / 2)
    center_y = bottom_left_y + (height / 2)
    draw_texture_rectangle(center_x, center_y, width, height, texture, angle, alpha, transparent, repeat_count_x,
                           repeat_count_y)


def get_pixel(x: int, y: int):
    """
    Given an x, y, will return RGB color value of that point.
    """
    a = (gl.GLubyte * 3)(0)
    gl.glReadPixels(x, y, 1, 1, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, a)
    red = a[0]
    green = a[1]
    blue = a[2]
    return (red, green, blue)


def get_image(x=0, y=0, width=None, height=None):
    """
    Get an image from the screen.
    You can save the image like:

    image = get_image()
    image.save('screenshot.png', 'PNG')
    """

    # Get the dimensions
    window = get_window()
    if width is None:
        width = window.width - x
    if height is None:
        height = window.height - y

    # Create an image buffer
    image_buffer = (gl.GLubyte * (4 * width * height))(0)

    gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_buffer)
    image = PIL.Image.frombytes("RGBA", (width, height), image_buffer)
    image = PIL.ImageOps.flip(image)

    # image.save('glutout.png', 'PNG')
    return image
