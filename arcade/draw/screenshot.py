from typing import Optional

import PIL.Image
import PIL.ImageOps
from pyglet import gl

from arcade.window_commands import get_window


def get_pixel(x: int, y: int, components: int = 3) -> tuple[int, ...]:
    """
    Given an x, y, will return a color value of that point.

    :param x: x location
    :param y: y location
    :param components: Number of components to fetch. By default we fetch 3
        3 components (RGB). 4 components would be RGBA.

    """
    # noinspection PyCallingNonCallable,PyTypeChecker

    # The window may be 'scaled' on hi-res displays. Particularly Macs. OpenGL
    # won't account for this, so we need to.
    window = get_window()

    pixel_ratio = window.get_pixel_ratio()
    x = int(pixel_ratio * x)
    y = int(pixel_ratio * y)

    a = (gl.GLubyte * 4)(0)
    gl.glReadPixels(x, y, 1, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, a)
    return tuple(int(i) for i in a[:components])


def get_image(
    x: int = 0, y: int = 0, width: Optional[int] = None, height: Optional[int] = None
) -> PIL.Image.Image:
    """
    Get an image from the screen.

    Example::

        image = get_image()
        image.save('screenshot.png', 'PNG')

    :param x: Start (left) x location
    :param y: Start (top) y location
    :param width: Width of image. Leave blank for grabbing the 'rest' of the image
    :param height: Height of image. Leave blank for grabbing the 'rest' of the image
    :returns: A Pillow Image
    """
    window = get_window()

    pixel_ratio = window.get_pixel_ratio()
    x = int(pixel_ratio * x)
    y = int(pixel_ratio * y)

    if width is None:
        width = window.width - x
    if height is None:
        height = window.height - y

    width = int(pixel_ratio * width)
    height = int(pixel_ratio * height)

    # Create an image buffer
    # noinspection PyTypeChecker
    image_buffer = (gl.GLubyte * (4 * width * height))(0)

    gl.glReadPixels(x, y, width, height, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_buffer)
    image = PIL.Image.frombytes("RGBA", (width, height), image_buffer)
    image = PIL.ImageOps.flip(image)

    return image
