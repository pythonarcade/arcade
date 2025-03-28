"""
Original screenshot utilities from Arcade 2.

These functions are flawed because they only read from the screen.
"""

import PIL.Image
import PIL.ImageOps

from arcade.window_commands import get_window


def get_pixel(x: int, y: int, components: int = 3) -> tuple[int, ...]:
    """
    Given an x, y, will return a color value of that point.

    Args:
        x: x location
        y: y location
        components: Number of components to fetch. By default we fetch 3
            3 components (RGB). 4 components would be RGBA.
    """
    # The window may be 'scaled' on hi-res displays. Particularly Macs. OpenGL
    # won't account for this, so we need to.
    window = get_window()
    ctx = window.ctx

    pixel_ratio = window.get_pixel_ratio()
    x = int(pixel_ratio * x)
    y = int(pixel_ratio * y)

    data = ctx.screen.read(viewport=(x, y, 1, 1), components=components)
    return tuple(data)  # bytes gets converted to ints in the tuple creation


def get_image(
    x: int = 0,
    y: int = 0,
    width: int | None = None,
    height: int | None = None,
    components: int = 4,
) -> PIL.Image.Image:
    """
    Get an image from the screen.

    Example::

        # Create and image of the entire screen and save it to a file
        image = arcade.get_image()
        image.save('screenshot.png')

    Args:
        x: Start (left) x location
        y: Start (bottom) y location
        width: Width of image. Leave blank for grabbing the 'rest' of the image
        height: Height of image. Leave blank for grabbing the 'rest' of the image
        components: Number of components to fetch. By default we fetch 4 (4=RGBA, 3=RGB)
    """
    window = get_window()
    ctx = window.ctx

    if components not in (3, 4):
        raise ValueError("components must be 3 or 4")

    pixel_ratio = window.get_pixel_ratio()
    x = int(pixel_ratio * x)
    y = int(pixel_ratio * y)

    if width is None:
        width = window.width - x
    if height is None:
        height = window.height - y

    width = int(pixel_ratio * width)
    height = int(pixel_ratio * height)

    data = ctx.screen.read(viewport=(x, y, width, height), components=components)
    image = PIL.Image.frombytes("RGBA" if components == 4 else "RGB", (width, height), data)
    return PIL.ImageOps.flip(image)
