"""
Metadata about where an image is located in the atlas.
"""

from typing import TYPE_CHECKING, Optional
from .base import TextureAtlasBase, TexCoords

if TYPE_CHECKING:
    from arcade.texture import ImageData


class AtlasRegion:
    """
    Stores information about where a texture is located.

    The texture coordinates are stored as a tuple of 8 floats
    (4 points, 2 floats each) in the following order:
    upper_left, upper_right, lower_left, lower_right.

    Layout::

        (0, 1)                                 (1, 1)
        +--------------------------------------+
        |          Atlas Texture               |
        |                                      |
        | (2)               (3)                |
        +-----------------+                    |
        |   Image         |                    |
        |                 |                    |
        |                 |                    |
        |                 |                    |
        |                 |                    |
        | (0)             | (1)                |
        +-----------------+--------------------+
        (0, 0)                                 (1, 0)

    :param atlas: The atlas this region belongs to
    :param texture: The arcade texture
    :param x: The x position of the texture
    :param y: The y position of the texture
    :param width: The width of the texture in pixels
    :param height: The height of the texture in pixels
    :param texture_coordinates: The texture coordinates (optional)
    """

    __slots__ = (
        "x",
        "y",
        "width",
        "height",
        "texture_coordinates",
    )

    def __init__(
        self,
        atlas: "TextureAtlasBase",
        x: int,
        y: int,
        width: int,
        height: int,
        texture_coordinates: Optional[TexCoords] = None,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # Calculate texture coordinates if not provided
        if texture_coordinates:
            self.texture_coordinates = texture_coordinates
        else:
            # start_x, start_y, width, height
            # Width and height
            _width = self.width / atlas.width
            _height = self.height / atlas.height
            # upper_left, upper_right, lower_left, lower_right
            self.texture_coordinates = (
                # upper_left
                self.x / atlas.width,
                self.y / atlas.height,
                # upper_right
                (self.x / atlas.width) + _width,
                (self.y / atlas.height),
                # lower_left
                (self.x / atlas.width),
                (self.y / atlas.height) + _height,
                # lower_right
                (self.x / atlas.width) + _width,
                (self.y / atlas.height) + _height,
            )

    def verify_image_size(self, image_data: "ImageData"):
        """
        Verify the image has the right size.
        The internal image of a texture can be tampered with
        at any point causing an atlas update to fail.
        """
        if image_data.size != (self.width, self.height):
            raise ValueError(
                (
                    f"ImageData '{image_data.hash}' change their internal image "
                    f"size from {self.width}x{self.height} to "
                    f"{image_data.width}x{image_data.height}. "
                    "It's not possible to fit this into the old allocated area in the atlas. "
                )
            )

    def __repr__(self) -> str:
        return (
            f"<AtlasRegion x={self.x} y={self.y} width={self.width} "
            f"height={self.height} uvs={self.texture_coordinates}>"
        )
