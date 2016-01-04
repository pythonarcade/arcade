import sys
import math

import PIL.Image

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT


def draw_arc_filled(cx, cy,
                    width, height,
                    color,
                    start_angle, end_angle,
                    angle=0, num_segments=128):
    """
    Draw a filled in arc. Useful for drawing pie-wedges, or Pac-Man.

    Args:
        :cx (float): x position that is the center of the arc.
        :cy (float): y position that is the center of the arc.
        :width (float): width of the arc.
        :height (float): height of the arc.
        :color (tuple): color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :start_angle (float): start angle of the arc in degrees.
        :end_angle (float): end angle of the arc in degrees.
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
    >>> arcade.draw_arc_filled(-0.5, -0.52, 0.05, 0.12, \
arcade.color.BOTTLE_GREEN, 0, 45)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslate(cx, cy, 0)
    GL.glRotatef(angle, 0, 0, 1)

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


def draw_arc_outline(cx, cy,
                     width, height,
                     color,
                     start_angle, end_angle,
                     line_width=1, angle=0, num_segments=128):
    """
    Draw the outside edge of an arc. Useful for drawing curved lines.

    Args:
        :cx (float): x position that is the center of the arc.
        :cy (float): y position that is the center of the arc.
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
    >>> arcade.draw_arc_outline(-0.5, -0.73, 0.05, 0.12, \
arcade.color.BRIGHT_MAROON, 90, 360)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslate(cx, cy, 0)
    GL.glRotatef(angle, 0, 0, 1)
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


def draw_circle_filled(cx, cy, radius, color, num_segments=128):
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
    >>> arcade.draw_circle_filled(0.4, -0.05, 0.06, arcade.color.GREEN, 3)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """
    width = radius
    height = radius
    draw_ellipse_filled(cx, cy, width, height, color, num_segments)


def draw_circle_outline(cx, cy, radius, color, line_width=1, num_segments=128):
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
    >>> arcade.draw_circle_outline(0, -0.05, 0.06, arcade.color.WISTERIA, 3)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """
    width = radius
    height = radius
    draw_ellipse_outline(cx, cy, width, height,
                         color, line_width, num_segments)


def draw_ellipse_filled(cx, cy,
                        width, height,
                        color,
                        angle=0, num_segments=128):
    """
    Draw a filled in ellipse.

    Args:
        :cx (float): x position that is the center of the circle.
        :cy (float): y position that is the center of the circle.
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
    >>> arcade.draw_ellipse_filled(-0.8, -0.73, 0.05, 0.12, arcade.color.AMBER)
    >>> arcade.draw_ellipse_filled(-0.8, -0.52, 0.05, 0.12, \
arcade.color.BLACK_BEAN, 45)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslate(cx, cy, 0)
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


def draw_ellipse_outline(cx, cy,
                         width, height,
                         color, line_width=1, angle=0, num_segments=128):
    """
    Draw the outline of an ellipse.

    Args:
        :cx (float): x position that is the center of the circle.
        :cy (float): y position that is the center of the circle.
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
    >>> arcade.draw_ellipse_outline(0.8, -0.09, 0.05, 0.12, \
arcade.color.AMBER, 3)
    >>> arcade.draw_ellipse_outline(0.8, 0.12, 0.05, 0.12, \
arcade.color.BLACK_BEAN, 3, 45)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslate(cx, cy, 0)
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


def draw_line(x1, y1, x2, y2, color, line_width=1):
    """
    Draw a line.


    Args:
        :x1 (float): x position of line starting point.
        :y1 (float): y position of line starting point.
        :x2 (float): x position of line ending point.
        :y2 (float): y position of line ending point.
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
    >>> arcade.draw_line(-0.1, 0.65, 0, 0.5, arcade.color.WOOD_BROWN, 3)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
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
    GL.glVertex3f(x1, y1, 0.5)
    GL.glVertex3f(x2, y2, 0.5)
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
    >>> point_list = ((0.7, 0.5), \
(0.9, 0.5), \
(0.7, 0.6), \
(0.9, 0.6), \
(0.7, 0.7), \
(0.9, 0.7)\
)
    >>> arcade.draw_line_strip(point_list, \
arcade.color.TROPICAL_RAIN_FOREST, 3)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
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
    >>> point_list = ((0.3, 0.5), \
(0.5, 0.5), \
(0.3, 0.6), \
(0.5, 0.6), \
(0.3, 0.7), \
(0.5, 0.7))
    >>> arcade.draw_lines(point_list, arcade.color.BLUE, 3)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
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
    >>> arcade.draw_point(-0.8, 0.65, arcade.color.RED, 10)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
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
    >>> point_list = ((-0.45, 0.65), (-0.45, 0.60), (-0.45, 0.55), \
(-0.35, 0.65), (-0.35, 0.60), (-0.35, 0.55))
    >>> arcade.draw_points(point_list, arcade.color.ZAFFRE, 10)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
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
    >>> point_list = ((-0.5, -0.2), (-0.45, -0.2), (-0.4, -0.15), \
(-0.4, -0.05), (-0.45, 0), (-0.5, 0))
    >>> arcade.draw_polygon_filled(point_list, arcade.color.SPANISH_VIOLET)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
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
    >>> point_list = ((-0.9, -0.2), (-0.85, -0.2), (-0.8, -0.15), \
(-0.8, -0.05), (-0.85, 0), (-0.9, 0))
    >>> arcade.draw_polygon_outline(point_list, arcade.color.SPANISH_VIOLET, 3)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()


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


def draw_rect_outline(x, y, width, height, color, line_width=1, angle=0):
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
    >>> arcade.draw_rect_outline(-0.075, -0.5, 0.15, 0.35, \
arcade.color.BRITISH_RACING_GREEN, 2)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running
    >>> # arcade.run()
    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glRotatef(angle, 0, 0, 1)

    # Set line width
    GL.glLineWidth(line_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex3f(x, y, 0.5)
    GL.glVertex3f(x + width, y, 0.5)
    GL.glVertex3f(x + width, y - height, 0.5)
    GL.glVertex3f(x, y - height, 0.5)
    GL.glEnd()


def draw_rect_filled(x, y, width, height, color, angle=0):
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
    >>> arcade.draw_rect_filled(0.3, -0.5, .15, .35, arcade.color.BLUSH)
    >>> # Enable the following to keep the window up after running
    >>> # arcade.run()
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

    if angle:
        GL.glRotatef(angle, 0, 0, 1)

    GL.glBegin(GL.GL_QUADS)
    GL.glVertex3f(x, y, 0.5)
    GL.glVertex3f(x + width, y, 0.5)
    GL.glVertex3f(x + width, y - height, 0.5)
    GL.glVertex3f(x, y - height, 0.5)
    GL.glEnd()


def draw_text(text, x, y, color):
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
    >>> arcade.draw_text("This is a test",-0.2, 0.05, arcade.color.BLACK)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()
    """

    GL.glLoadIdentity()
    GL.glDisable(GL.GL_TEXTURE_2D)
    w = float(GLUT.glutGet(GLUT.GLUT_WINDOW_WIDTH))
    h = float(GLUT.glutGet(GLUT.GLUT_WINDOW_HEIGHT))

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glRasterPos(x, y)
    for character in text:
        GLUT.glutBitmapCharacter(GLUT.GLUT_BITMAP_8_BY_13, ord(character))


def load_texture(fileName):
    """
    Load image from disk and create a texture.

    Args:
        :filename (str): Name of the file to that holds the texture.
    Returns:
        Integer identifier for the new texture.
    Raises:
        None
    """
    image = PIL.Image.open(fileName)
    width = image.size[0]
    height = image.size[1]
    image_bytes = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)

    my_texture = GL.glGenTextures(1)

    GL.glBindTexture(GL.GL_TEXTURE_2D, my_texture)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
    GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_REPEAT)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER,
                       GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER,
                       GL.GL_LINEAR_MIPMAP_LINEAR)
    GLU.gluBuild2DMipmaps(GL.GL_TEXTURE_2D, GL.GL_RGBA, width, height,
                          GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image_bytes)

    return my_texture, width, height


def draw_texture_rect(x, y, width, height, texture, angle=0, alpha=1):
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
    >>> texture, width, height = \
arcade.load_texture("examples/images/playerShip1_orange.png")
    >>> scale = 0.002
    >>> arcade.draw_texture_rect(0.8, -0.6, scale * width, \
scale * height, texture, 0)
    >>> arcade.swap_buffers()
    >>> # Enable the following to keep the window up after running.
    >>> # arcade.run()


    """

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(x, y, 0)
    GL.glRotatef(angle, 0, 0, 1)

    GL.glColor4f(1, 1, 1, alpha)
    z = 0.5

    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glBegin(GL.GL_POLYGON)
    GL.glNormal3f(0.0, 0.0, 1.0)
    GL.glTexCoord2f(0, 0)
    GL.glVertex3f(-width/2, height/2, z)
    GL.glTexCoord2f(1, 0)
    GL.glVertex3f(width/2, height/2, z)
    GL.glTexCoord2f(1, 1)
    GL.glVertex3f(width/2, -height/2, z)
    GL.glTexCoord2f(0, 1)
    GL.glVertex3f(-width/2, -height/2, z)
    GL.glEnd()
