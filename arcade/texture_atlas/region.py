"""
Metadata about where an image is located in the atlas.
"""

from typing import TYPE_CHECKING, Optional

from .base import TexCoords, TextureAtlasBase

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
        #: X position of the texture in the atlas
        self.x = x
        #: Y position of the texture in the atlas
        self.y = y
        #: Width of the texture in pixels
        self.width = width
        #: Height of the texture in pixels
        self.height = height
        # Calculate texture coordinates if not provided
        if texture_coordinates:
            #: The calculated texture coordinates for this region
            self.texture_coordinates = texture_coordinates
        else:
            # start_x, start_y, width, height
            # Width and height
            _width = self.width / atlas.width
            _height = self.height / atlas.height
            # Half pixel correction
            hp_x, hp_y = 0.5 / atlas.width, 0.5 / atlas.height
            # Upper left corner. Note that are mapping the texture upside down and corners
            # are named as from the vertex position point of view.
            ul_x, ul_y = self.x / atlas.width, self.y / atlas.height

            # upper_left, upper_right, lower_left, lower_right
            self.texture_coordinates = (
                # upper_left
                ul_x + hp_x,
                ul_y + hp_y,
                # upper_right
                ul_x + _width - hp_x,
                ul_y + hp_y,
                # lower_left
                ul_x + hp_x,
                ul_y + _height - hp_y,
                # lower_right
                ul_x + _width - hp_x,
                ul_y + _height - hp_y,
            )

    def verify_image_size(self, image_data: "ImageData"):
        """
        Verify the image size.

        The internal image of a texture can potentially be tampered with
        at any point causing an atlas update to fail.
        """
        if image_data.size != (self.width, self.height):
            raise RuntimeError(
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
