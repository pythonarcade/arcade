import sys
import math
import ctypes
import PIL.Image
import PIL.ImageOps
import pyglet
import pyglet.gl as GL
import pyglet.gl.glu as GLU


class Texture():
    """
    Class that represents a texture.
    Usually created by the ``load_texture`` or ``load_textures`` commands.
    """

    def __init__(self, id, width, height):
        """
        Args:
            :id (str): Id of the texture.
            :width (int): Width of the texture.
            :height (int): Height of the texture.
        Raises:
            :ValueError:
        """
        # Check values before attempting to create Texture object
        if height < 0:
            raise ValueError("Height entered is less than zero. Height must "
                             "be a positive number. Texture id: " + self.id)

        if width < 0:
            raise ValueError("Width entered is less than zero. Width must be "
                             "a positive number. Texture id: " + self.id)

        # Values seem to be clear, create object
        self.id = id
        self.width = width
        self.height = height


def load_textures(file_name, image_location_list,
                  mirrored=False, flipped=False):
    """
    Load a set of textures off of a single image file.

    Args:
        :file_name: Name of the file.
        :image_location_list: List of image locations. Each location should be
         a list of four numbers. ``[x, y, width, height]``.
        :mirrored=False: If set to true, the image is mirrored left to right.
        :flipped=False: If set to true, the image is flipped upside down.
    Returns:
        :list: List of textures loaded.
    Raises:
        :SystemError:

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

        # Appveyor work-around
        appveyor = True
        if not appveyor:
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
                               GL.GL_CLAMP_TO_BORDER)
            GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
                               GL.GL_CLAMP_TO_BORDER)
        else:
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


def load_texture(file_name, x=0, y=0, width=0, height=0, scale=1):
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

    # See if we already loaded this file, and we can just use a cached version.
    if file_name in load_texture.texture_cache:
        return load_texture.texture_cache[file_name]

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

    # Appveyor work-around
    appveyor = True
    if not appveyor:
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S,
                           GL.GL_CLAMP_TO_BORDER)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T,
                           GL.GL_CLAMP_TO_BORDER)
    else:
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

    image_width *= scale
    image_height *= scale

    result = Texture(texture, image_width, image_height)
    load_texture.texture_cache[file_name] = result
    return result

load_texture.texture_cache = dict()

# --- END TEXTURE FUNCTIONS # # #


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

# --- BEGIN ARC FUNCTIONS # # #


def draw_arc_filled(center_x, center_y,
                    width, height,
                    color,
                    start_angle, end_angle,
                    tilt_angle=0):
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


def draw_arc_outline(center_x, center_y, width, height, color, start_angle,
                     end_angle, border_width=1, tilt_angle=0):
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
    GL.glLineWidth(border_width)

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

# --- END ARC FUNCTIONS # # #


# --- BEGIN PARABOLA FUNCTIONS # # #

def draw_parabola_filled(start_x, start_y, end_x, height, color, tilt_angle=0):
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

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_parabola_filled(150, 150, 200, 50, \
arcade.color.BOTTLE_GREEN)
    >>> color = (255, 0, 0, 127)
    >>> arcade.draw_parabola_filled(160, 160, 210, 50, color)
    >>> arcade.finish_render()
    >>> arcade.close_window()
    """
    center_x = (start_x+end_x)/2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    draw_arc_filled(center_x, center_y, width, height, color,
                    start_angle, end_angle, tilt_angle)


def draw_parabola_outline(start_x, start_y, end_x, height, color,
                          border_width=1, tilt_angle=0):
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

    Example:

    >>> import arcade
    >>> arcade.open_window("Drawing Example", 800, 600)
    >>> arcade.set_background_color(arcade.color.WHITE)
    >>> arcade.start_render()
    >>> arcade.draw_parabola_outline(150, 150, 200, 50, \
arcade.color.BOTTLE_GREEN, 10, 15)
    >>> color = (255, 0, 0, 127)
    >>> arcade.draw_parabola_outline(160, 160, 210, 50, color, 20)
    >>> arcade.finish_render()
    >>> arcade.close_window()
    """
    center_x = (start_x+end_x)/2
    center_y = start_y + height
    start_angle = 0
    end_angle = 180
    width = (start_x - end_x)
    draw_arc_outline(center_x, center_y, width, height, color,
                     start_angle, end_angle, border_width, tilt_angle)

# --- END PARABOLA FUNCTIONS # # #


# --- BEGIN CIRCLE FUNCTIONS # # #

def draw_circle_filled(center_x, center_y, radius, color):
    """
    Draw a filled-in circle.

    Args:
        :center_x: x position that is the center of the circle.
        :center_y: y position that is the center of the circle.
        :radius: width of the circle.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
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
    >>> arcade.draw_circle_filled(420, 285, 18, arcade.color.GREEN)
    >>> arcade.finish_render()
    >>> arcade.quick_run(0.25)
    """
    width = radius
    height = radius
    draw_ellipse_filled(center_x, center_y, width, height, color)


def draw_circle_outline(center_x, center_y, radius, color, border_width=1):
    """
    Draw the outline of a circle.

    Args:
        :center_x: x position that is the center of the circle.
        :center_y: y position that is the center of the circle.
        :radius: width of the circle.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :border_width: Width of the circle outline in pixels.
        :num_segments: number of triangle segments that make up this
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
    num_segments = 128
    width = radius
    height = radius
    draw_ellipse_outline(center_x, center_y, width, height,
                         color, border_width)

# --- END CIRCLE FUNCTIONS # # #


# --- BEGIN ELLIPSE FUNCTIONS # # #

def create_ellipse(width, height, color):
    """
    This creates an ellipse vertex buffer object (VBO). It can later be
    drawn with ``render_ellipse_filled``. This method of drawing an ellipse
    is much faster than calling ``draw_ellipse_filled`` each frame.
    """
    num_segments = 64

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


def render_ellipse_filled(shape, center_x, center_y, color, angle=0):
    """
    Render an ellipse previously created with the ``create_ellipse`` function.
    """
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
    GL.glTranslatef(center_x, center_y, 0)
    if angle:
        GL.glRotatef(angle, 0, 0, 1)

    GL.glDrawArrays(GL.GL_TRIANGLE_FAN, 0, shape.size)


def draw_ellipse_filled(center_x, center_y,
                        width, height, color, tilt_angle=0):
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
        :num_segments: number of triangle segments that make up this
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

    GL.glVertex3f(0, 0, 0.5)

    for i in range(num_segments + 1):
        theta = 2.0 * 3.1415926 * i / num_segments

        x = width * math.cos(theta)
        y = height * math.sin(theta)

        GL.glVertex3f(x, y, 0.5)

    GL.glEnd()
    GL.glLoadIdentity()


def draw_ellipse_outline(center_x, center_y, width, height, color,
                         border_width=1, tilt_angle=0):
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

    num_segments = 128

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)
    GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)

    GL.glLoadIdentity()
    GL.glTranslatef(center_x, center_y, 0)
    GL.glRotatef(tilt_angle, 0, 0, 1)
    GL.glLineWidth(border_width)

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

# --- END ELLIPSE FUNCTIONS # # #


# --- BEGIN LINE FUNCTIONS # # #

def draw_line(start_x, start_y, end_x, end_y, color, border_width=1):

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
    GL.glLineWidth(border_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINES)
    GL.glVertex3f(start_x, start_y, 0.5)
    GL.glVertex3f(end_x, end_y, 0.5)
    GL.glEnd()


def draw_line_strip(point_list, color, border_width=1):
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
    GL.glLineWidth(border_width)

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


def draw_lines(point_list, color, border_width=1):
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
    GL.glLineWidth(border_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINES)
    for point in point_list:
        GL.glVertex3f(point[0], point[1], 0.5)
    GL.glEnd()

# --- END LINE FUNCTIONS # # #

# --- BEGIN POINT FUNCTIONS # # #


def draw_point(x, y, color, size):
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
        :point_list: List of points Each point is
         in a list. So it is a list of lists.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :size: Size of the point in pixels.
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

# --- END POINT FUNCTIONS # # #

# --- BEGIN POLYGON FUNCTIONS # # #


def draw_polygon_filled(point_list, color):
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


def draw_polygon_outline(point_list, color, border_width=1):
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
    GL.glLineWidth(border_width)

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


def draw_triangle_filled(x1, y1,
                         x2, y2,
                         x3, y3, color):
    """
    Draw a filled in triangle.

    Args:
        :x1: x value of first coordinate.
        :y1: y value of first coordinate.
        :x2: x value of second coordinate.
        :y2: y value of second coordinate.
        :x3: x value of third coordinate.
        :y3: y value of third coordinate.
        :y3: Color of triangle.
    Returns:
        None
    Raises:
        None
    """
    first_point = [x1, y1]
    second_point = [x2, y2]
    third_point = [x3, y3]
    point_list = (first_point, second_point, third_point)
    draw_polygon_filled(point_list, color)


def draw_triangle_outline(x1, y1,
                          x2, y2,
                          x3, y3, color, border_width=1):
    """
    Draw a the outline of a triangle.

    Args:
        :x1: x value of first coordinate.
        :y1: y value of first coordinate.
        :x2: x value of second coordinate.
        :y2: y value of second coordinate.
        :x3: x value of third coordinate.
        :y3: y value of third coordinate.
        :y3: Color of triangle.
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

def create_rectangle(width, height, color):
    """
    This function creates a rectangle using a vertex buffer object.
    Creating the rectangle, and then later drawing it with ``render_rectangle``
    is faster than calling ``draw_rectangle``.
    """
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


def render_rectangle_filled(shape, center_x, center_y, color, tilt_angle=0):
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
    GL.glTranslatef(center_x + shape.width / 2, center_y + shape.height / 2, 0)
    if tilt_angle != 0:
        GL.glRotatef(tilt_angle, 0, 0, 1)

    GL.glDrawArrays(GL.GL_QUADS, 0, shape.size)


def draw_rectangle_outline(x, y, width, height, color, border_width=1,
                           tilt_angle=0):
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
    GL.glTranslatef(x, y, 0)
    if tilt_angle:
        GL.glRotatef(tilt_angle, 0, 0, 1)

    # Set line width
    GL.glLineWidth(border_width)

    # Set color
    if len(color) == 4:
        GL.glColor4ub(color[0], color[1], color[2], color[3])
    elif len(color) == 3:
        GL.glColor4ub(color[0], color[1], color[2], 255)

    GL.glBegin(GL.GL_LINE_LOOP)
    GL.glVertex3f(-width // 2, -height // 2, 0.5)
    GL.glVertex3f(width // 2, -height // 2, 0.5)
    GL.glVertex3f(width // 2, height // 2, 0.5)
    GL.glVertex3f(-width // 2, height // 2, 0.5)
    GL.glEnd()


def draw_rectangle_filled(x, y, width, height, color, tilt_angle=0):
    """
    Draw a filled-in rectangle.

    Args:
        :x: x coordinate of top left rectangle point.
        :y: y coordinate of top left rectangle point.
        :width: width of the rectangle.
        :height: height of the rectangle.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
         RGBA format.
        :angle: rotation of the rectangle. Defaults to zero.

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
    if tilt_angle:
        GL.glRotatef(tilt_angle, 0, 0, 1)

    GL.glBegin(GL.GL_QUADS)
    GL.glVertex3f(-width // 2, -height // 2, 0.5)
    GL.glVertex3f(width // 2, -height // 2, 0.5)
    GL.glVertex3f(width // 2, height // 2, 0.5)
    GL.glVertex3f(-width // 2, height // 2, 0.5)
    GL.glEnd()


def draw_rectangle(center_x, center_y, width, height, color, border_width=0,
                   tilt_angle=0):
    if border_width <= 0:
        draw_rectangle_filled(center_x, center_y, width, height, color,
                              tilt_angle)
    else:
        draw_rectangle_outline(center_x, center_y, width, height, color,
                               border_width, tilt_angle)


def draw_texture_rectangle(center_x, center_y, width, height, texture,
                           angle=0, alpha=1, transparent=True):
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
    GL.glTranslatef(center_x, center_y, 0)
    if angle != 0:
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

# --- END RECTANGLE FUNCTIONS # # #

# --- BEGIN TEXT FUNCTIONS # # #


def draw_text(text, start_x, start_y, color, size):
    """
    Draw text to the screen.

    Args:
        :text: Text to display.
        :start_x: x coordinate of top left text point.
        :start_y: y coordinate of top left text point.
        :color: color, specified in a list of 3 or 4 bytes in RGB or
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
                              x=start_x, y=start_y,
                              color=color)
    GL.glLoadIdentity()

    label.draw()

# --- END TEXT FUNCTIONS # # #


class VertexBuffer():
    """
    This class represents a
    `vertex buffer object`_.

    .. _vertex buffer object:
       https://en.wikipedia.org/wiki/Vertex_Buffer_Object
    """
    def __init__(self, vbo_id, size, width, height, color):
        self.vbo_id = vbo_id
        self.size = size
        self.width = width
        self.height = height
        self.color = color

# def _test():
#     import doctest
#     doctest.testmod()


if __name__ == "__main__":
    _test()
