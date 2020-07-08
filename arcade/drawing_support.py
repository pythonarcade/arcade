"""
Functions used to support drawing. No Pyglet/OpenGL here.
"""

import math

import pymunkoptions
pymunkoptions.options["debug"] = False
import pymunk

from PIL import Image

from pymunk import autogeometry

from typing import List, Tuple, cast

from arcade import Color
from arcade import RGBA


def get_points_for_thick_line(start_x: float, start_y: float,
                              end_x: float, end_y: float,
                              line_width: float):
    """
    Function used internally for Arcade. OpenGL draws triangles only, so a think
    line must be two triangles that make up a rectangle. This calculates those
    points.
    """
    vector_x = start_x - end_x
    vector_y = start_y - end_y
    perpendicular_x = vector_y
    perpendicular_y = -vector_x
    length = math.sqrt(vector_x * vector_x + vector_y * vector_y)
    if length == 0:
        normal_x = 1.0
        normal_y = 1.0
    else:
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


def get_four_byte_color(color: Color) -> RGBA:
    """
    Given a RGB list, it will return RGBA.
    Given a RGBA list, it will return the same RGBA.

    :param Color color: Three or four byte tuple

    :returns:  return: Four byte RGBA tuple
    """

    if len(color) == 4:
        return cast(RGBA, color)
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
                 angle_degrees: float) -> List[float]:
    """
    Rotate a point around a center.

    :param x: x value of the point you want to rotate
    :param y: y value of the point you want to rotate
    :param cx: x value of the center point you want to rotate around
    :param cy: y value of the center point you want to rotate around
    :param angle_degrees: Angle, in degrees, to rotate
    :return: Return rotated (x, y) pair
    :rtype: (float, float)
    """
    temp_x = x - cx
    temp_y = y - cy

    # now apply rotation
    angle_radians = math.radians(angle_degrees)
    cos_angle = math.cos(angle_radians)
    sin_angle = math.sin(angle_radians)
    rotated_x = temp_x * cos_angle - temp_y * sin_angle
    rotated_y = temp_x * sin_angle + temp_y * cos_angle

    # translate back
    rounding_precision = 2
    x = round(rotated_x + cx, rounding_precision)
    y = round(rotated_y + cy, rounding_precision)

    return [x, y]

def calculate_hit_box_points_simple(image):
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

    # If the image is empty, return an empty set
    if bottom_border == 0:
        return []

    def _check_corner_offset(start_x, start_y, x_direction, y_direction):

        bad = False
        offset = 0
        while not bad:
            y = start_y + (offset * y_direction)
            x = start_x
            for count in range(offset + 1):
                my_pixel = image.getpixel((x, y))
                # print(f"({x}, {y}) = {pixel} | ", end="")
                if my_pixel[3] != 0:
                    bad = True
                    break
                y -= y_direction
                x += x_direction
            # print(f" - {bad}")
            if not bad:
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
    p2 = (right_border + 1) - top_right_corner_offset, top_border
    p3 = (right_border + 1), top_border + top_right_corner_offset
    p4 = (right_border + 1), (bottom_border + 1) - bottom_right_corner_offset
    p5 = (right_border + 1) - bottom_right_corner_offset, (bottom_border + 1)
    p6 = left_border + bottom_left_corner_offset, (bottom_border + 1)
    p7 = left_border, (bottom_border + 1) - bottom_left_corner_offset
    p8 = left_border, top_border + top_left_corner_offset

    result = []

    h = image.height
    w = image.width

    result.append(_r(p7, h, w))
    if bottom_left_corner_offset:
        result.append(_r(p6, h, w))

    result.append(_r(p5, h, w))
    if bottom_right_corner_offset:
        result.append(_r(p4, h, w))

    result.append(_r(p3, h, w))
    if top_right_corner_offset:
        result.append(_r(p2, h, w))

    result.append(_r(p1, h, w))
    if top_left_corner_offset:
        result.append(_r(p8, h, w))

    # Remove duplicates
    result = tuple(dict.fromkeys(result))

    return result

def calculate_hit_box_points_detailed(image: Image, hit_box_detail: float = 4.5):
    """
    Given an image, this returns points that make up a hit box around it. Attempts
    to trim out transparent pixels.

    :param Image image: Image get hit box from.
    :param int hit_box_detail: How detailed to make the hit box. There's a
                               trade-off in number of points vs. accuracy.

    :Returns: List of points

    """

    def sample_func(sample_point):
        """ Method used to sample image. """
        if sample_point[0] < 0 \
                or sample_point[1] < 0 \
                or sample_point[0] >= image.width \
                or sample_point[1] >= image.height:
            return 0

        point_tuple = sample_point[0], sample_point[1]
        color = image.getpixel(point_tuple)
        if color[3] > 0:
            return 255
        else:
            return 0

    # Do a quick check if it is a full tile
    p1 = 0, 0
    p2 = 0, image.height - 1
    p3 = image.width - 1, image.height - 1
    p4 = image.width - 1, 0

    if sample_func(p1) and sample_func(p2) and sample_func(p3) and sample_func(p4):
        # Do a quick check if it is a full tile
        p1 = (-image.width / 2, -image.height / 2)
        p2 = (image.width / 2, -image.height / 2)
        p3 = (image.width / 2, image.height / 2)
        p4 = (-image.width / 2, image.height / 2)

        return p1, p2, p3, p4

    # Get the bounding box
    logo_bb = pymunk.BB(-1, -1, image.width, image.height)

    # Set of lines that trace the image
    line_set = pymunk.autogeometry.PolylineSet()

    # Collect the line segments
    def _segment_func(v0, v1):
        line_set.collect_segment(v0, v1)

    # How often to sample?
    downres = 1
    horizontal_samples = int(image.width / downres)
    vertical_samples = int(image.height / downres)

    # Run the trace
    pymunk.autogeometry.march_soft(
        logo_bb,
        horizontal_samples, vertical_samples,
        99,
        _segment_func,
        sample_func)

    # Select which line set to use
    if len(line_set) == 0:
        return []

    selected_line_set = line_set[0]
    selected_range = None
    if len(line_set) > 1:
        # We have more than one line set. Try and find one that covers most of
        # the sprite.
        for line in line_set:
            min_x = None
            min_y = None
            max_x = None
            max_y = None
            for point in line:
                if min_x is None or point.x < min_x:
                    min_x = point.x
                if max_x is None or point.x > max_x:
                    max_x = point.x
                if min_y is None or point.y < min_y:
                    min_y = point.y
                if max_y is None or point.y > max_y:
                    max_y = point.y

            if min_x is None or max_x is None or min_y is None or max_y is None:
                raise ValueError("No points in bounding box.")

            my_range = max_x - min_x + max_y + min_y
            if selected_range is None or my_range > selected_range:
                selected_range = my_range
                selected_line_set = line

    # Reduce number of vertices
    # original_points = len(selected_line_set)
    selected_line_set = pymunk.autogeometry.simplify_curves(selected_line_set,
                                                            hit_box_detail)
    # downsampled_points = len(selected_line_set)

    # Convert to normal points, offset fo 0,0 is center, flip the y
    hh = image.height / 2
    hw = image.width / 2
    points = []
    for vec2 in selected_line_set:
        point = round(vec2.x - hw), round(image.height - (vec2.y - hh) - image.height)
        points.append(point)

    if len(points) > 1 and points[0] == points[-1]:
        points.pop()

    # print(f"{sprite.texture.name} Line-sets={len(line_set)}, Original points={original_points}, Downsampled points={downsampled_points}")
    return points
