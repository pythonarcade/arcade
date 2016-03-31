import sys
import math
import ctypes

import PIL.Image
import PIL.ImageOps

import pyglet

import pyglet.gl as GL
import pyglet.gl.glu as GLU

from sympy import Symbol, nsolve
import sympy
import mpmath
mpmath.mp.dps = 15


class Texture():
    """
    Simple class that represents a texture
    """
    def __init__(self, id, width, height):
        self.id = id
        self.width = width
        self.height = height


def trim_image(image):
    """
    Returns an image with extra whitespace cropped out.

    >>> name = "doc/source/examples/images/playerShip1_orange.png"
    >>> source_image = PIL.Image.open(name)
    >>> cropped_image = trim_image(source_image)
    >>> print(source_image.height, cropped_image.height)
    75 75
    """
    bbox = image.getbbox()
    return image.crop(bbox)


def draw_arc_filled(center_x, center_y,
                    width, height,
                    color,
                    start_angle, end_angle,
                    tilt_angle=0):
    """
    Draw a filled in arc. Useful for drawing pie-wedges, or Pac-Man.

    Args:
        :center_x (float): x position that is the center of the arc.
        :center_y (float): y position that is the center of the arc.
        :width (float): width of the arc.
        :height (float): height of the arc.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :start_angle (float): start angle of the arc in degrees.
        :end_angle (float): end angle of the arc in degrees.
        :tilt_angle (float): angle the arc is tilted.
        :num_segments (int): number of line segments that would make up the
         whole ellipse that this arc is part of. Higher is better quality and
         slower render time.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_arc_filled(150, 144, 15, 36, \
arcade.color.BOTTLE_GREEN, 90, 360, 45)
    >>> color = (255, 0, 0, 127)
    >>> arcade.draw_arc_filled(150, 154, 15, 36, color, 90, 360, 45)
    >>> arcade.finish_render()
    >>> arcade.close_window()
    """
    num_segments = 128
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(center_x, center_y, 0)
    GL.glRotatef(tilt_angle, 0, 0, 1)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_TRIANGLE_FAN)

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)
    GL.glVertex3f(0, 0, 0.5)

    for i in range(start_segment, end_segment + 1):
        theta = 2.0 * 3.1415926 * i / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        GL.glVertex3f(x, y, 0.5)

    GL.glEnd()
    GL.glLoadIdentity()


def draw_arc_outline(center_x, center_y, width, height, color, start_angle, end_angle, line_width=1, tilt_angle=0):
    """
    Draw the outside edge of an arc. Useful for drawing curved lines.

    Args:
        :center_x (float): x position that is the center of the arc.
        :center_y (float): y position that is the center of the arc.
        :width (float): width of the arc.
        :height (float): height of the arc.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :start_angle (float): start angle of the arc in degrees.
        :end_angle (float): end angle of the arc in degrees.
        :line_width (float): width of line in pixels.
        :angle (float): angle the arc is tilted.
        :num_segments (int): number of line segments that would make up the
         whole ellipse that this arc is part of. Higher is better quality and
         slower render time.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_arc_outline(150, 81, 15, 36, \
arcade.color.BRIGHT_MAROON, 90, 360)
    >>> transparent_color = (255, 0, 0, 127)
    >>> arcade.draw_arc_outline(150, 71, 15, 36, \
transparent_color, 90, 360)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    num_segments = 128
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(center_x, center_y, 0)
    GL.glRotatef(tilt_angle, 0, 0, 1)
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINE_STRIP)

    start_segment = int(start_angle / 360 * num_segments)
    end_segment = int(end_angle / 360 * num_segments)

    for i in range(start_segment, end_segment + 1):
        theta = 2.0 * 3.1415926 * i / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        GL.glVertex3f(x, y, 0.5)

    GL.glEnd()
    GL.glLoadIdentity()

def draw_fancy_math_arc_outline(start_x, start_y, end_x, end_y, height, color, line_width=5, tilt_angle=0):
    temp_x = end_x - start_x
    temp_x = temp_x**2
    temp_y = end_y - start_y
    temp_y = temp_y**2
    z = temp_x + temp_y
    distance = math.sqrt(z)

    a = height
    b = height
    c = distance

    square_c = c**2
    square_c = square_c * -1

    square_b = b**2

    square_a = a**2

    numerator = square_c + square_b + square_a
    denominator = 2 * a * b

    cosine = numerator / denominator

    radian = math.acos(cosine)

    angle = radian*(180/math.pi)
    print(angle)


    h = height**2

    cx = Symbol('cx')
    cy = Symbol('cy')
    center_vars = nsolve(((start_x-cx)**2 + (start_y-cy)**2-h,(end_x-cx)**2 + (end_y-cy)**2-h), (cx,cy), (-1,1))
    print(center_vars)
    center_x = center_vars[0]
    center_y = center_vars[1]
    print(center_x, center_y)
    start_a = math.atan2(start_y-center_y,start_x-center_x)
    end_a = math.atan2(end_y-center_y,end_x-center_x)
    start_angle = start_a*(180/math.pi)
    end_angle = end_a*(180/math.pi)
    print(start_angle, end_angle)
    if end_angle < 0:
        end_angle *= -1
    else:
        end_angle = 180 - end_angle
    if start_angle < 0:
        start_angle *= -1
    else:
        start_angle = 180 - start_angle
    if end_angle < start_angle:
        temp = end_angle
        end_angle = start_angle
        start_angle = temp
    print(start_angle, end_angle)

    arcade.draw_arc_outline(center_x, center_y, distance, height, color, start_angle, end_angle, line_width, tilt_angle)

def draw_fancy_math_arc_filled(start_x, start_y, end_x, end_y, height, color, tilt_angle=0):
    temp_x = end_x - start_x
    temp_x = temp_x**2
    temp_y = end_y - start_y
    temp_y = temp_y**2
    z = temp_x + temp_y
    distance = math.sqrt(z)

    a = height
    b = height
    c = distance

    square_c = c**2
    square_c = square_c * -1

    square_b = b**2

    square_a = a**2

    numerator = square_c + square_b + square_a
    denominator = 2 * a * b

    cosine = numerator / denominator

    radian = math.acos(cosine)

    angle = radian*(180/math.pi)
    print(angle)


    h = height**2

    cx = Symbol('cx')
    cy = Symbol('cy')
    center_vars = nsolve(((start_x-cx)**2 + (start_y-cy)**2-h,(end_x-cx)**2 + (end_y-cy)**2-h), (cx,cy), (-1,1))
    print(center_vars)
    center_x = center_vars[0]
    center_y = center_vars[1]
    print(center_x, center_y)
    start_a = math.atan2(start_y-center_y,start_x-center_x)
    end_a = math.atan2(end_y-center_y,end_x-center_x)
    start_angle = start_a*(180/math.pi)
    end_angle = end_a*(180/math.pi)
    print(start_angle, end_angle)
    if end_angle < 0:
        end_angle *= -1
    else:
        end_angle = 180 - end_angle
    if start_angle < 0:
        start_angle *= -1
    else:
        start_angle = 180 - start_angle
    if end_angle < start_angle:
        temp = end_angle
        end_angle = start_angle
        start_angle = temp
    print(start_angle, end_angle)

    arcade.draw_arc_filled(center_x, center_y, distance, height, color, start_angle, end_angle, tilt_angle)

def draw_parabola_filled(start_x, start_y, end_x, height, color, tilt_angle=0):
    cx = (start_x+end_x)/2
    cy = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    arcade.draw_arc_filled(center_x, center_y, width, height, color, start_angle, end_angle, tilt_angle)

def draw_parabola_outline(start_x, start_y, end_x, height, color, line_width=5, tilt_angle=0):
    cx = (start_x+end_x)/2
    cy = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    arcade.draw_arc_outline(center_x, center_y, width, height, color, start_angle, end_angle, line_width, tilt_angle)



def draw_circle_filled(center_x, center_y, radius, color, num_segments=128):
    """
    Draw a filled-in circle.

    Args:
        :cx (float): x position that is the center of the circle.
        :cy (float): y position that is the center of the circle.
        :radius (float): width of the circle.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :num_segments (int): number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_circle_filled(420, 285, 18, arcade.color.GREEN, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    width = radius
    height = radius
    draw_ellipse_filled(center_x, center_y, width, height, color, num_segments) 
    
    
def draw_small_filled_circle(center_x, center_y, color):
    # Draws a circle with a default small radius
    radius = 10
    
    draw_circle_filled(center_x, center_y, radius, color)
    
def draw_medium_filled_circle(center_x, center_y, color):
    # Draws a circle with a default medium radius
    radius = 25
    
    draw_circle_filled(center_x, center_y, radius, color)

def draw_large_filled_circle(center_x, center_y, color):
    # Draws a circle with a default large radius
    radius = 40
    
    draw_circle_filled(center_x, center_y, radius, color)


def draw_standard_circle(center_x, center_y, color, size, filled, adjustment = 0):
    #Draws a general circle with a limited number of specifications
    
    """This function is meant to encapsule all of the different kinds of circles that a person might want drawn. 
    The arguments are the circle's specifications given in an order that a person would use to describe what they want
    (i.e. "I want a 'large' 'solid 'red' circle at 'this spot'.)
    
    The arguments are as such;
    size = The radius of the circle expressed in descriptive words like "small" or "s", "medium" or "m", or "large" or "l".
    adjustment = A customizable adjustment to the size of the standard circle. Can be positive or negative or can be entirely ignored.
    filled = If the circle is an outline or is a solid color expressed with words like "filled" or "solid" and "outline" or "hollow".
    color = The color of the circle.
    center_x = The center's x coordinate.
    center_y = The center's y coordinate.
    
    Example:
    
    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_standard_circle(500, 200, arcade.color.BLUE, "small", "solid") #Draws a small solid blue circle at (500, 200)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    #--size--
    if size.lower() == "small" or size.lower() == "s":
        radius = 10 + adjustment
    
    elif size.lower() == "medium" or size.lower() == "m":
        radius = 25 + adjustment
        
    elif size.lower() == "large" or size.lower() == "l":
        radius = 40 + adjustment
     
    #--filled--
    if filled == "filled" or filled == "solid":
        draw_circle_filled(center_x, center_y, radius, color)
         
    elif filled == "outline" or filled == "hollow":
        draw_circle_outline(center_x, center_y, radius, color)


def draw_circle_outline(center_x, center_y, radius, color, line_width=1, num_segments=128):
    """
    Draw the outline of a circle.

    Args:
        :cx (float): x position that is the center of the circle.
        :cy (float): y position that is the center of the circle.
        :radius (float): width of the circle.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the circle outline in pixels.
        :num_segments (int): number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_circle_outline(300, 285, 18, arcade.color.WISTERIA, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    width = radius
    height = radius
    draw_ellipse_outline(center_x, center_y, width, height,
                         color, line_width, num_segments)


def draw_ellipse_filled(center_x, center_y, width, height, color, angle=0):
    """
    Draw a filled in ellipse.

    Args:
        :center_x (float): x position that is the center of the circle.
        :center_y (float): y position that is the center of the circle.
        :height (float): height of the ellipse.
        :width (float): width of the ellipse.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :angle (float): Angle in degrees to tilt the ellipse.
        :num_segments (int): number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_ellipse_filled(60, 81, 15, 36, arcade.color.AMBER)
    >>> color = (127, 0, 127, 127)
    >>> arcade.draw_ellipse_filled(60, 144, 15, 36, color, 45)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    num_segments=128

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(center_x, center_y, 0)
    GL.glRotatef(angle, 0, 0, 1)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_TRIANGLE_FAN)

    GL.glVertex3f(0, 0, 0.5)

    for i in range(num_segments + 1):
        theta = 2.0 * 3.1415926 * i / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        GL.glVertex3f(x, y, 0.5)

    GL.glEnd()
    GL.glLoadIdentity()


def draw_ellipse_outline(center_x, center_y, width, height, color, line_width=1, angle=0):
    """
    Draw the outline of an ellipse.

    Args:
        :center_x (float): x position that is the center of the circle.
        :center_y (float): y position that is the center of the circle.
        :height (float): height of the ellipse.
        :width (float): width of the ellipse.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the circle outline in pixels.
        :angle (float): Angle in degrees to tilt the ellipse.
        :num_segments (int): number of triangle segments that make up this
         circle. Higher is better quality, but slower render time.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_ellipse_outline(540, 273, 15, 36, arcade.color.AMBER, 3)
    >>> color = (127, 0, 127, 127)
    >>> arcade.draw_ellipse_outline(540, 336, 15, 36, color, 3, 45)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    num_segments=128

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(center_x, center_y, 0)
    GL.glRotatef(angle, 0, 0, 1)
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINE_LOOP)
    for i in range(num_segments):
        theta = 2.0 * 3.1415926 * i / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        GL.glVertex3f(x, y, 0.5)

    GL.glEnd()
    GL.glLoadIdentity()

##### BEGIN OVAL FUNCTIONS #####

# draw any oval with 1 function with max parameters
def draw_oval(center_x, center_y, width, height, color, border_width=0, angle=0):
    if border_width <= 0:
        draw_oval_filled_custom(center_x, center_y, width, height, color, angle)
    else:
        draw_oval_outline_custom(center_x, center_y, width, height, color, border_width, angle)
        

# draw a custom oval that is filled
def draw_oval_filled_custom(center_x, center_y, width, height, color, angle=0):
    
    draw_ellipse_filled(center_x, center_y, width, height, color, angle)

# draw a custom oval outline
def draw_oval_outline_custom(center_x, center_y, width, height, color, border_width=5, angle=0):

    if border_width <= 0:
        draw_ellipse_filled(center_x, center_y, width, height, color, angle)
    else:
        draw_ellipse_outline(center_x, center_y, width, height, color, border_width, angle)

# draw a semi custom filled oval using word descriptions for width and height
def draw_described_oval_filled(center_x, center_y, width, height, color, angle=0):
    if width.lower() == "very fat" or width.lower() == "vf" or width.lower() == "huge" or width.lower() == "h":
        width = 200
    elif width.lower() == "fat" or width.lower() == "f" or width.lower() == "big" or width.lower() == "b" or height.lower() == "large" or height.lower() == "l" or height.lower() == "max":
        width = 100
    elif width.lower() == "medium" or width.lower() == "m" or width.lower() == "average" or width.lower() == "a" or height.lower() == "mid":
        width = 50
    elif width.lower() == "skinny" or width.lower() == "s" or width.lower() == "small" or height.lower() == "min":
        width = 25
    elif width.lower() == "very skinny" or width.lower() == "vs" or width.lower() == "tiny" or width.lower() == "t":
        width = 12.5
    else:
        width = -1

    if height.lower() == "very tall" or height.lower() == "vt" or height.lower() == "huge" or height.lower() == "h":
        height = 200
    elif height.lower() == "tall" or height.lower() == "t" or height.lower() == "big" or height.lower() == "b" or height.lower() == "large" or height.lower() == "l" or height.lower() == "max":
        height = 100
    elif height.lower() == "medium" or height.lower() == "m" or height.lower() == "average" or height.lower() == "a" or height.lower() == "mid":
        height = 50
    elif height.lower() == "short" or height.lower() == "s" or height.lower() == "small" or height.lower() == "min":
        height = 25
    elif height.lower() == "very short" or height.lower() == "vs" or height.lower() == "tiny" or height.lower() == "t":
        height = 12.5
    else:
        height = -1

    if width != -1 and height != -1:
        draw_oval_filled_custom(center_x, center_y, width, height, color, angle)
        

# draw a semi custom outlined oval using word descriptions for width and height
def draw_described_oval_outline(center_x, center_y, width, height, color, border_width = 5, angle=0):
    if width.lower() == "very fat" or width.lower() == "vf" or width.lower() == "huge" or width.lower() == "h":
        width = 200
    elif width.lower() == "fat" or width.lower() == "f" or width.lower() == "big" or width.lower() == "b" or height.lower() == "large" or height.lower() == "l" or height.lower() == "max":
        width = 100
    elif width.lower() == "medium" or width.lower() == "m" or width.lower() == "average" or width.lower() == "a" or height.lower() == "mid":
        width = 50
    elif width.lower() == "skinny" or width.lower() == "s" or width.lower() == "small" or height.lower() == "min":
        width = 25
    elif width.lower() == "very skinny" or width.lower() == "vs" or width.lower() == "tiny" or width.lower() == "t":
        width = 12.5
    else:
        width = -1
        
    if height.lower() == "very tall" or height.lower() == "vt" or height.lower() == "huge" or height.lower() == "h":
        height = 200
    elif height.lower() == "tall" or height.lower() == "t" or height.lower() == "big" or height.lower() == "b" or height.lower() == "large" or height.lower() == "l" or height.lower() == "max":
        height = 100
    elif height.lower() == "medium" or height.lower() == "m" or height.lower() == "average" or height.lower() == "a" or height.lower() == "mid":
        height = 50
    elif height.lower() == "short" or height.lower() == "s" or height.lower() == "small" or height.lower() == "min":
        height = 25
    elif height.lower() == "very short" or height.lower() == "vs" or height.lower() == "tiny" or height.lower() == "t":
        height = 12.5
    else:
        height = -1

    if width != -1 and height != -1:
        draw_oval_outline_custom(center_x, center_y, width, height, color, border_width, angle)
    

# draw a generic oval that is filled
def draw_oval_filled(center_x, center_y, size, color, angle=0):
    if size.lower() == "huge" or size.lower() == "h":
        draw_oval_filled_custom(center_x, center_y, 300, 150, color, angle=0)
    elif size.lower() == "large" or size.lower() == "l" or size.lower() == "big" or size.lower() == "b" or size.lower() == "max":
        draw_oval_filled_custom(center_x, center_y, 200, 100, color, angle=0)
    elif size.lower() == "medium" or size.lower() == "m" or size.lower() == "mid":
        draw_oval_filled_custom(center_x, center_y, 100, 50, color, angle=0)
    elif size.lower() == "small" or size.lower() == "s" or size.lower() == "min":
        draw_oval_filled_custom(center_x, center_y, 50, 25, color, angle=0)
    elif size.lower() == "tiny" or size.lower() == "t":
        draw_oval_filled_custom(center_x, center_y, 25, 12.5, color, angle=0)

# drsw a generic oval outline
def draw_oval_outline(center_x, center_y, size, color, angle=0):
    if size.lower() == "huge" or size.lower() == "h":
        draw_oval_outline_custom(center_x, center_y, 300, 150, color, 5, angle=0)
    elif size.lower() == "large" or size.lower() == "l" or size.lower() == "big" or size.lower() == "b" or size.lower() == "max":
        draw_oval_outline_custom(center_x, center_y, 200, 100, color, 5, angle=0)
    elif size.lower() == "medium" or size.lower() == "m" or size.lower() == "mid":
        draw_oval_outline_custom(center_x, center_y, 100, 50, color, 5, angle=0)
    elif size.lower() == "small" or size.lower() == "s" or size.lower() == "min":
        draw_oval_outline_custom(center_x, center_y, 50, 25, color, 5, angle=0)
    elif size.lower() == "tiny" or size.lower() == "t":
        draw_oval_outline_custom(center_x, center_y, 25, 12.5, color, 5, angle=0)

# set of functions that draw generic ovals that are filled
def draw_huge_oval_filled(center_x, center_y, color, angle=0):
    draw_oval_filled_custom(center_x, center_y, 300, 150, color, angle)

def draw_large_oval_filled(center_x, center_y, color, angle=0):
    draw_oval_filled_custom(center_x, center_y, 200, 100, color, angle)

def draw_medium_oval_filled(center_x, center_y, color, angle=0):
    draw_oval_filled_custom(center_x, center_y, 100, 50, color, angle)

def draw_small_oval_filled(center_x, center_y, color, angle=0):
    draw_oval_filled_custom(center_x, center_y, 50, 25, color, angle)

def draw_tiny_oval_filled(center_x, center_y, color, angle=0):
    draw_oval_filled_custom(center_x, center_y, 25, 12.5, color, angle)

# set of functions that draw generic oval outlines
def draw_huge_oval_outline(center_x, center_y, color, angle=0):
    draw_oval_outline_custom(center_x, center_y, 300, 150, color, 5, angle)

def draw_large_oval_outline(center_x, center_y, color, angle=0):
    draw_oval_outline_custom(center_x, center_y, 200, 100, color, 5, angle)

def draw_medium_oval_outline(center_x, center_y, color, angle=0):
    draw_oval_outline_custom(center_x, center_y, 100, 50, color, 5, angle)

def draw_small_oval_outline(center_x, center_y, color, angle=0):
    draw_oval_outline_custom(center_x, center_y, 50, 25, color, 5, angle)

def draw_tiny_oval_outline(center_x, center_y, color, angle=0):
    draw_oval_outline_custom(center_x, center_y, 25, 12.5, color, 5, angle)

# set of functions for drawing ovals of varying sizes with specified fill or outline
def draw_huge_oval(center_x, center_y, color, fill = True, angle=0):
    if fill == True:
        draw_oval_filled_custom(center_x, center_y, 300, 150, color, angle)
    else:
        draw_oval_outline_custom(center_x, center_y, 300, 150, color, 5, angle)

def draw_large_oval(center_x, center_y, color, fill = True, angle=0):
    if fill == True:
        draw_oval_filled_custom(center_x, center_y, 200, 100, color, angle)
    else:
        draw_oval_outline_custom(center_x, center_y, 200, 100, color, 5, angle)

def draw_medium_oval(center_x, center_y, color, fill = True, angle=0):
    if fill == True:
        draw_oval_filled_custom(center_x, center_y, 100, 50, color, angle)
    else:
        draw_oval_outline_custom(center_x, center_y, 100, 50, color, 5, angle)

def draw_small_oval(center_x, center_y, color, fill = True, angle=0):
    if fill == True:
        draw_oval_filled_custom(center_x, center_y, 50, 25, color, angle)
    else:
        draw_oval_outline_custom(center_x, center_y, 50, 25, color, 5, angle)

def draw_tiny_oval(center_x, center_y, color, fill = True, angle=0):
    if fill == True:
        draw_oval_filled_custom(center_x, center_y, 25, 12.5, color, angle)
    else:
        draw_oval_outline_custom(center_x, center_y, 25, 12.5, color, 5, angle)

    
##### END OVAL FUNCTIONS #####


def draw_line(start_x, start_y, end_x, end_y, color, line_width=1):
    """
    Draw a line.


    Args:
        :start_x (float): x position of line starting point.
        :start_y (float): y position of line starting point.
        :end_x (float): x position of line ending point.
        :end_y (float): y position of line ending point.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_line(270, 495, 300, 450, arcade.color.WOOD_BROWN, 3)
    >>> color = (127, 0, 127, 127)
    >>> arcade.draw_line(280, 495, 320, 450, color, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()

    # Set line width
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINES)
    GL.glVertex3f(start_x, start_y, 0.5)
    GL.glVertex3f(end_x, end_y, 0.5)
    GL.glEnd()

def draw_thin_line(start_x, start_y, end_x, end_y, color, line_width=.5):
    """
    Draw a thin line.

    Args:
        :start_x (float): x position of line starting point.
        :start_y (float): y position of line starting point.
        :end_x (float): x position of line ending point.
        :end_y (float): y position of line ending point.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_line(270, 495, 300, 450, arcade.color.WOOD_BROWN, 3)
    >>> color = (127, 0, 127, 127)
    >>> arcade.draw_line(280, 495, 320, 450, color, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()

    # Set line width
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINES)
    GL.glVertex3f(start_x, start_y, 0.5)
    GL.glVertex3f(end_x, end_y, 0.5)
    GL.glEnd()
    
def draw_medium_line(start_x, start_y, end_x, end_y, color, line_width=1):
    """
    Draw a medium thickness line.

    Args:
        :start_x (float): x position of line starting point.
        :start_y (float): y position of line starting point.
        :end_x (float): x position of line ending point.
        :end_y (float): y position of line ending point.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_line(270, 495, 300, 450, arcade.color.WOOD_BROWN, 3)
    >>> color = (127, 0, 127, 127)
    >>> arcade.draw_line(280, 495, 320, 450, color, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()

    # Set line width
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINES)
    GL.glVertex3f(start_x, start_y, 0.5)
    GL.glVertex3f(end_x, end_y, 0.5)
    GL.glEnd()

def draw_thick_line(start_x, start_y, end_x, end_y, color, line_width=2):
    """
    Draw a thick line.

    Args:
        :start_x (float): x position of line starting point.
        :start_y (float): y position of line starting point.
        :end_x (float): x position of line ending point.
        :end_y (float): y position of line ending point.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_line(270, 495, 300, 450, arcade.color.WOOD_BROWN, 3)
    >>> color = (127, 0, 127, 127)
    >>> arcade.draw_line(280, 495, 320, 450, color, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()

    # Set line width
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINES)
    GL.glVertex3f(start_x, start_y, 0.5)
    GL.glVertex3f(end_x, end_y, 0.5)
    GL.glEnd()
    
def draw_line_strip(point_list, color, line_width=1):
    """
    Draw a line strip. A line strip is a set of continuously connected
    line segments.

    Args:
        :point_list (tuple): List of points making up the line. Each point is
         in a list. So it is a list of lists.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> point_list = ((510, 450), \
(570, 450), \
(510, 480), \
(570, 480), \
(510, 510), \
(570, 510))
    >>> arcade.draw_line_strip(point_list, arcade.color.TROPICAL_RAIN_FOREST, \
3)
    >>> color = (127, 0, 127, 127)
    >>> point_list = ((510, 455), \
(570, 455), \
(510, 485), \
(570, 485), \
(510, 515), \
(570, 515))
    >>> arcade.draw_line_strip(point_list, color, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    # Set line width
    GL.glLineWidth(line_width)

    GL.glLoadIdentity()

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINE_STRIP)
    for point in point_list:
        GL.glVertex3f(point[0], point[1], 0.5)
    GL.glEnd()


def draw_lines(point_list, color, line_width=1):
    """
    Draw a set of lines.

    Draw a line between each pair of points specified.

    Args:
        :point_list (tuple): List of points making up the lines. Each point is
         in a list. So it is a list of lists.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> point_list = ((390, 450), \
(450, 450), \
(390, 480), \
(450, 480), \
(390, 510), \
(450, 510))
    >>> arcade.draw_lines(point_list, arcade.color.BLUE, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()

    # Set line width
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINES)
    for point in point_list:
        GL.glVertex3f(point[0], point[1], 0.5)
    GL.glEnd()


def draw_point(x, y, color, size):
    """
    Draw a point.

    Args:
        :x (float): x position of point.
        :y (float): y position of point.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :size (float): Size of the point in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_point(60, 495, arcade.color.RED, 10)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    GL.glLoadIdentity()

    GL.glPointSize(size)
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)
    GL.glBegin(GL.GL_POINTS)
    GL.glVertex3f(x, y, 0.5)
    GL.glEnd()


def draw_points(point_list, color, size):
    """
    Draw a set of points.

    Args:
        :point_list (tuple): List of points Each point is
         in a list. So it is a list of lists.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :size (float): Size of the point in pixels.
    Returns:
        None
    Raises:
        None

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> point_list = ((165, 495), \
(165, 480), \
(165, 465), \
(195, 495), \
(195, 480), \
(195, 465))
    >>> arcade.draw_points(point_list, arcade.color.ZAFFRE, 10)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    GL.glLoadIdentity()

    GL.glPointSize(size)
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)
    GL.glBegin(GL.GL_POINTS)
    for point in point_list:
        GL.glVertex3f(point[0], point[1], 0.5)
    GL.glEnd()


def draw_polygon_filled(point_list, color):
    """
    Draw a polygon that is filled in.

    Args:
        :point_list (tuple): List of points making up the lines. Each point is
         in a list. So it is a list of lists.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
    Returns:
        None
    Raises:
        None

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> point_list = ((150, 240), \
(165, 240), \
(180, 255), \
(180, 285), \
(165, 300), \
(150, 300))
    >>> arcade.draw_polygon_filled(point_list, arcade.color.SPANISH_VIOLET)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_POLYGON)
    for point in point_list:
        GL.glVertex3f(point[0], point[1], 0.5)
    GL.glEnd()


def draw_polygon_outline(point_list, color, line_width=1):
    """
    Draw a polygon outline. Also known as a "line loop."

    Args:
        :point_list (tuple): List of points making up the lines. Each point is
         in a list. So it is a list of lists.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): Width of the line in pixels.
    Returns:
        None
    Raises:
        None

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> point_list = ((30, 240), \
(45, 240), \
(60, 255), \
(60, 285), \
(45, 300), \
(30, 300))
    >>> arcade.draw_polygon_outline(point_list, arcade.color.SPANISH_VIOLET, 3)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    # Set line width
    GL.glLineWidth(line_width)

    GL.glLoadIdentity()

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINE_LOOP)
    for point in point_list:
        GL.glVertex3f(point[0], point[1], 0.5)
    GL.glEnd()


def draw_rectangle_outline(x, y, width, height, color, line_width=1, angle=0):
    """
    Draw a rectangle outline.

    Args:
        :x (float): x coordinate of top left rectangle point.
        :y (float): y coordinate of top left rectangle point.
        :width (float): width of the rectangle.
        :height (float): height of the rectangle.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :line_width (float): width of the lines, in pixels.
        :angle (float): rotation of the rectangle. Defaults to zero.

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_rectangle_outline(278, 150, 45, 105, \
arcade.color.BRITISH_RACING_GREEN, 2)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(x + width / 2, y + height / 2, 0)
    if angle:
        GL.glRotatef(angle, 0, 0, 1)
    GL.glTranslatef(width / 2, height / 2, 0)

    # Set line width
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex3f(0, 0, 0.5)
    GL.glVertex3f(width, 0, 0.5)
    GL.glVertex3f(width, 0 - height, 0.5)
    GL.glVertex3f(0, 0 - height, 0.5)
    GL.glEnd()


def draw_rectangle_filled(x, y, width, height, color, angle=0):
    """
    Draw a filled-in rectangle.

    Args:
        :x (float): x coordinate of top left rectangle point.
        :y (float): y coordinate of top left rectangle point.
        :width (float): width of the rectangle.
        :height (float): height of the rectangle.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :angle (float): rotation of the rectangle. Defaults to zero.

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_rectangle_filled(390, 150, 45, 105, arcade.color.BLUSH)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glLoadIdentity()
    GL.glTranslatef(x, y, 0)
    if angle:
        GL.glRotatef(angle, 0, 0, 1)
    GL.glTranslatef(-width / 2, height / 2, 0)

    GL.glBegin(GL.GL_QUADS)
    GL.glVertex3f(0, 0, 0.5)
    GL.glVertex3f(width, 0, 0.5)
    GL.glVertex3f(width, 0 - height, 0.5)
    GL.glVertex3f(0, 0 - height, 0.5)
    GL.glEnd()


def draw_text(text, x, y, color, size):
    """
    Draw text to the screen.

    Args:
        :text (str): Text to display.
        :x (float): x coordinate of top left text point.
        :y (float): y coordinate of top left text point.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_text("Text Example", 250, 300, arcade.color.BLACK, 10)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    if len(color) == 3:
        color = (color[0], color[1], color[2], 255)

    label = pyglet.text.Label(text,
                              font_name='Times New Roman',
                              font_size=size,
                              x=x, y=y,
                              color=color)
    GL.glLoadIdentity()

    label.draw()


def load_textures(file_name, image_location_list,
                  mirrored=False, flipped=False):
    """
    Load a set of textures off of a single image file.

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> top_trim = 100
    >>> ltrim = 2
    >>> rtrim = 2
    >>> image_location_list = [
    ... [520 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [520 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [520 + ltrim, 0 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 1548 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 1290 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 516 + top_trim, 128 - ltrim - rtrim, 256 - top_trim],
    ... [390 + ltrim, 258 + top_trim, 128 - ltrim - rtrim, 256 - top_trim]]
    >>> texture_info_list = arcade.load_textures( \
"doc/source/examples/images/spritesheet_complete.png", image_location_list)
    >>> arcade.close_window()
    """
    source_image = PIL.Image.open(file_name)

    source_image_width, source_image_height = source_image.size
    texture_info_list = []
    for image_location in image_location_list:
        x, y, width, height = image_location

        if x > source_image_width:
            raise SystemError("Can't load texture starting at an x of {} " +
                              "when the image is only {} across."
                              .format(x, source_image_width))
        if y > source_image_height:
            raise SystemError("Can't load texture starting at an y of {} " +
                              "when the image is only {} high."
                              .format(y, source_image_height))
        if x + width > source_image_width:
            raise SystemError("Can't load texture ending at an x of {} " +
                              "when the image is only {} wide."
                              .format(x + width, source_image_width))
        if y + height > source_image_height:
            raise SystemError("Can't load texture ending at an y of {} " +
                              "when the image is only {} high."
                              .format(y + height, source_image_height))

        image = source_image.crop((x, y, x + width, y + height))
        # image = _trim_image(image)

        if mirrored:
            image = PIL.ImageOps.mirror(image)

        if flipped:
            image = PIL.ImageOps.flip(image)

        image_width, image_height = image.size
        image_bytes = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

        texture = GL.GLuint(0)
        GL.glGenTextures(1, ctypes.byref(texture))

        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

        # The code below should be enabled, but it freaks out
        # during CI (AppVeyor).
        # GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
        #                    GL.GL_CLAMP_TO_BORDER)
        # GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
        #                    GL.GL_CLAMP_TO_BORDER)

        # The code below should be disabled, but keeping it here for
        # CI
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
                           GL.GL_REPEAT)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
                           GL.GL_REPEAT)

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,
                           GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,
                           GL.GL_LINEAR_MIPMAP_LINEAR)
        GLU.gluBuild2DMipmaps(GL.GL_TEXTURE_2D, GL.GL_RGBA,
                              image_width, image_height,
                              GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image_bytes)

        texture_info_list.append(Texture(texture, width, height))

    return texture_info_list


def load_texture(file_name, x=0, y=0, width=0, height=0):
    """
    Load image from disk and create a texture.

    Args:
        :filename (str): Name of the file to that holds the texture.
    Returns:
        Integer identifier for the new texture.
    Raises:
        None

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> name = "doc/source/examples/images/meteorGrey_big1.png"
    >>> texture = load_texture(name, 1, 1, 50, 50)
    >>> arcade.close_window()
    """
    source_image = PIL.Image.open(file_name)

    source_image_width, source_image_height = source_image.size

    if x != 0 or y != 0 or width != 0 or height != 0:
        if x > source_image_width:
            raise SystemError("Can't load texture starting at an x of {} " +
                              "when the image is only {} across."
                              .format(x, source_image_width))
        if y > source_image_height:
            raise SystemError("Can't load texture starting at an y of {} " +
                              "when the image is only {} high."
                              .format(y, source_image_height))
        if x + width > source_image_width:
            raise SystemError("Can't load texture ending at an x of {} " +
                              "when the image is only {} wide."
                              .format(x + width, source_image_width))
        if y + height > source_image_height:
            raise SystemError("Can't load texture ending at an y of {} " +
                              "when the image is only {} high."
                              .format(y + height, source_image_height))

        image = source_image.crop((x, y, x + width, y + height))
    else:
        image = source_image

    # image = _trim_image(image)

    image_width, image_height = image.size
    image_bytes = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    texture = GL.GLuint(0)
    GL.glGenTextures(1, ctypes.byref(texture))

    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

    # The code below should be enabled, but it freaks out
    # during CI (AppVeyor).
    # GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
    #                    GL.GL_CLAMP_TO_BORDER)
    # GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
    #                    GL.GL_CLAMP_TO_BORDER)

    # The code below should be disabled, but keeping it here for
    # CI
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
                       GL.GL_REPEAT)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
                       GL.GL_REPEAT)

    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,
                       GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,
                       GL.GL_LINEAR_MIPMAP_LINEAR)
    GLU.gluBuild2DMipmaps(GL.GL_TEXTURE_2D, GL.GL_RGBA,
                          image_width, image_height,
                          GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image_bytes)

    return Texture(texture, image_width, image_height)


def draw_texture_rectangle(x, y, width, height, texture,
                      angle=0, alpha=1, transparent=True):
    """
    Draw a textured rectangle on-screen.

    Args:
        :x (float): x coordinate of top left rectangle point.
        :y (float): y coordinate of top left rectangle point.
        :width (float): width of the rectangle.
        :height (float): height of the rectangle.
        :texture (int): identifier of texture returned from load_texture() call
        :angle (float): rotation of the rectangle. Defaults to zero.
        :alpha (float): Transparency of image.
    Returns:
        None
    Raises:
        None

    :Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_text("draw_bitmap", 483, 3, arcade.color.BLACK, 12)
    >>> name = "doc/source/examples/images/playerShip1_orange.png"
    >>> texture = arcade.load_texture(name)
    >>> scale = .6
    >>> arcade.draw_texture_rectangle(540, 120, scale * texture.width, \
scale * texture.height, texture, 0)
    >>> arcade.draw_texture_rectangle(540, 60, scale * texture.width, \
scale * texture.height, texture, 90)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """

    if transparent:
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    else:
        GL.glDisable(GL.GL_BLEND)

    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(x, y, 0)
    GL.glRotatef(angle, 0, 0, 1)

    GL.glColor4f(1, 1, 1, alpha)
    z = 0.5

    GL.glBindTexture(GL.GL_TEXTURE_2D, texture.id)
    GL.glBegin(GL.GL_POLYGON)
    GL.glNormal3f(0.0, 0.0, 1.0)
    GL.glTexCoord2f(0, 0)
    GL.glVertex3f(-width/2, -height/2, z)
    GL.glTexCoord2f(1, 0)
    GL.glVertex3f(width/2, -height/2, z)
    GL.glTexCoord2f(1, 1)
    GL.glVertex3f(width/2, height/2, z)
    GL.glTexCoord2f(0, 1)
    GL.glVertex3f(-width/2, height/2, z)
    GL.glEnd()


class VertexBuffer():
    def __init__(self, vbo_id, size, width, height, color):
        self.vbo_id = vbo_id
        self.size = size
        self.width = width
        self.height = height
        self.color = color


def create_rect(width, height, color):
    data = [-width / 2, -height / 2,
            width / 2, -height / 2,
            width / 2, height / 2,
            -width / 2, height / 2]

    vbo_id = GL.GLuint()

    GL.glGenBuffers(1, ctypes.pointer(vbo_id))

    v2f = data
    data2 = (GL.GLfloat*len(v2f))(*v2f)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo_id)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    GL.GL_STATIC_DRAW)

    shape = VertexBuffer(vbo_id, len(v2f)//2, width, height, color)
    return shape


def render_rect_filled(shape, x, y, color, angle=0):
    # Set color
    if len(color) == 4:
        GL.glColor4ub(shape.color[0], shape.color[1], shape.color[2],
                      shape.color[3])
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    elif len(color) == 3:
        GL.glDisable(GL.GL_BLEND)
        GL.glColor4ub(shape.color[0], shape.color[1], shape.color[2], 255)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, shape.vbo_id)
    GL.glVertexPointer(2, GL.GL_FLOAT, 0, 0)

    GL.glLoadIdentity()
    GL.glTranslatef(x + shape.width / 2, y + shape.height / 2, 0)
    if angle != 0:
        GL.glRotatef(angle, 0, 0, 1)

    GL.glDrawArrays(GL.GL_QUADS, 0, shape.size)


def create_ellipse(width, height, color, num_segments=64):
    data = []

    for i in range(num_segments + 1):
        theta = 2.0 * 3.1415926 * i / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        data.extend([x, y])

    vbo_id = GL.GLuint()

    GL.glGenBuffers(1, ctypes.pointer(vbo_id))

    v2f = data
    data2 = (GL.GLfloat*len(v2f))(*v2f)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo_id)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, ctypes.sizeof(data2), data2,
                    GL.GL_STATIC_DRAW)

    shape = VertexBuffer(vbo_id, len(v2f)//2, width, height, color)
    return shape


def render_ellipse_filled(shape, x, y, color, angle=0):
    # Set color
    if len(color) == 4:
        GL.glColor4ub(shape.color[0], shape.color[1], shape.color[2],
                      shape.color[3])
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    elif len(color) == 3:
        GL.glDisable(GL.GL_BLEND)
        GL.glColor4ub(shape.color[0], shape.color[1], shape.color[2], 255)

    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, shape.vbo_id)
    GL.glVertexPointer(2, GL.GL_FLOAT, 0, 0)

    GL.glLoadIdentity()
    GL.glTranslatef(x, y, 0)
    if angle:
        GL.glRotatef(angle, 0, 0, 1)

    GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, shape.size)
# def _test():
#     import doctest
#     doctest.testmod()

if __name__ == "__main__":
    _test()
