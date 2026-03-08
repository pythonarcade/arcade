"""
Texture Atlas for SpriteList

The long term goal is to rely on pyglet's texture atlas, but
it's still unclear what features we need supported in arcade
so need to prototype something to get started.

We're still building on pyglet's allocator.

Pyglet atlases are located here:
https://github.com/einarf/pyglet/blob/master/pyglet/image/atlas.py

Allocation:
Pyglet's allocator is a simple row based allocator only keeping
track of horizontal strips and how far in the x direction the
each strip is filled. We can't really "deallocate" unless it's
a region at the end of a strip and even doing that is awkward.

When an image is removed from the atlas we simply just lose that
region until we rebuild the atlas. It can be a good idea to count
the number of lost regions to use as an indicator later. When an
atlas is full we can first rebuild it if there are lost regions
instead of increasing the size.
"""

from __future__ import annotations

import abc
import contextlib
from pathlib import Path
from typing import TYPE_CHECKING

import PIL.Image

import arcade

if TYPE_CHECKING:
    from arcade import ArcadeContext, Texture
    from arcade.gl import Framebuffer, Texture2D
    from arcade.texture.texture import ImageData
    from arcade.texture_atlas.region import AtlasRegion

# The amount of pixels we increase the atlas when scanning for a reasonable size.
# It must be a power of two number like 64, 256, 512 ..
RESIZE_STEP = 128
UV_TEXTURE_WIDTH = 4096
# Texture coordinates for a texture (4 x vec2)
TexCoords = tuple[float, float, float, float, float, float, float, float]


class TextureAtlasBase(abc.ABC):
    """
    Abstract base class for texture atlases.

    A texture atlas is a large texture containing several textures
    so OpenGL can easily batch draw thousands or hundreds of thousands
    of sprites on one draw operation.
    """

    _fbo: Framebuffer
    _texture: Texture2D

    def __init__(self, ctx: ArcadeContext | None):
        self._ctx = ctx or arcade.get_window().ctx
        self._size: tuple[int, int] = 0, 0
        self._layers: int = 1
        self._version = 0

    @property
    def ctx(self) -> ArcadeContext:
        """The global Arcade OpenGL context."""
        return self._ctx

    @property
    def fbo(self) -> Framebuffer:
        """
        The framebuffer object for this atlas.

        This framebuffer has the atlas texture attached to it so
        we can render directly into the atlas texture.
        """
        return self._fbo

    @property
    def texture(self) -> Texture2D:
        """The OpenGL texture for this atlas."""
        return self._texture

    @property
    def version(self) -> int:
        """
        The version of the atlas.

        This is incremented every time the atlas is rebuilt or resized.
        It can be used to check if the atlas has changed since last
        time it was used.
        """
        return self._version

    @property
    def width(self) -> int:
        """Hight of the atlas in pixels."""
        return self._size[0]

    @property
    def height(self) -> int:
        """Width of the atlas in pixels."""
        return self._size[1]

    @property
    def layers(self) -> int:
        """
        Number of layers in the atlas.
        Only relevant for atlases using texture arrays.
        """
        return self._layers

    @property
    def size(self) -> tuple[int, int]:
        """The width and height of the texture atlas in pixels"""
        return self._size

    # --- Core ---

    @abc.abstractmethod
    def add(self, texture: Texture) -> tuple[int, AtlasRegion]:
        """
        Add a texture to the atlas.

        Args:
            texture: The texture to add
        Returns:
            texture_id, AtlasRegion tuple
        Raises:
            AllocatorException: If there are no room for the texture
        """
        ...

    @abc.abstractmethod
    def remove(self, texture: Texture) -> None:
        """
        Remove a texture from the atlas.

        This is only supported by static atlases. Dynamic atlases with
        garbage collection will remove texture using python's garbage
        collector.

        Args:
            texture: The texture to remove
        """
        ...

    @abc.abstractmethod
    def resize(self, size: tuple[int, int], force=False) -> None:
        """
        Resize the atlas.

        This will re-allocate all the images in the atlas to better fit
        the new size. Pixel data will be copied from the old atlas to the
        new one on the gpu meaning it will also persist anything that
        was rendered to the atlas.

        A failed resize will result in an AllocatorException. Unless the
        atlas is resized again to a working size the atlas will be in an
        undefined state.

        Args:
            size:
                The new size
            force:
                Force a resize even if the size is the same
        """
        ...

    @abc.abstractmethod
    def rebuild(self) -> None:
        """
        Rebuild the underlying atlas texture.

        This method also tries to organize the textures more efficiently ordering them by size.
        The texture ids will persist so the sprite list doesn't need to be rebuilt.
        """
        ...

    @abc.abstractmethod
    def has_image(self, image_data: ImageData) -> bool:
        """
        Check if an image is already in the atlas

        Args:
            image_data: The image data to check
        """
        ...

    @abc.abstractmethod
    def has_texture(self, texture: Texture) -> bool:
        """
        Check if a texture is already in the atlas.

        Args:
            texture: The texture to check
        """
        ...

    @abc.abstractmethod
    def has_unique_texture(self, texture: Texture) -> bool:
        """
        Check if the atlas already have a texture with the
        same image data and vertex order

        Args:
            texture: The texture to check
        """
        ...

    @abc.abstractmethod
    def get_texture_id(self, texture: Texture) -> int:
        """
        Get the internal id for a Texture in the atlas

        Args:
            texture: The texture to get
        """
        ...

    @abc.abstractmethod
    def get_texture_region_info(self, atlas_name: str) -> AtlasRegion:
        """
        Get the region info for a texture by atlas name

        Args:
            atlas_name: The name of the texture in the atlas
        """
        ...

    @abc.abstractmethod
    def get_image_region_info(self, hash: str) -> AtlasRegion:
        """
        Get the region info for and image by has

        Args:
            hash: The hash of the image
        """
        ...

    @abc.abstractmethod
    def use_uv_texture(self, unit: int = 0) -> None:
        """
        Bind the texture coordinate texture to a channel.
        In addition this method writes the texture
        coordinate to the texture if the data is stale.
        This is to avoid a full update every time a texture
        is added to the atlas.

        Args:
            unit: The texture unit to bind the uv texture
        """
        ...

    # --- Utility ---

    @abc.abstractmethod
    @contextlib.contextmanager
    def render_into(
        self,
        texture: Texture,
        projection: tuple[float, float, float, float] | None = None,
    ):
        """
        Render directly into a sub-section of the atlas.
        The sub-section is defined by the already allocated space
        of the texture supplied in this method.

        By default the projection will be set to match the texture area size
        were `0, 0` is the lower left corner and `width, height` (of texture)
        is the upper right corner.

        This method should should be used with the ``with`` statement::

            with atlas.render_into(texture):
                # Draw commands here

            # Specify projection
            with atlas.render_into(texture, projection=(0, 100, 0, 100))
                # Draw geometry

        Args:
            texture:
                The texture area to render into
            projection:
                The ortho projection to render with. This parameter can be
                left blank if no projection changes are needed.
                The tuple values are: (left, right, button, top)
        """
        yield self._fbo

    @abc.abstractmethod
    def write_image(self, image: PIL.Image.Image, x: int, y: int) -> None:
        """
        Write a PIL image to the atlas in a specific region.

        Args:
            image:
                The pillow image
            x:
                The x position to write the texture
            y:
                The y position to write the texture
        """
        ...

    @abc.abstractmethod
    def read_texture_image_from_atlas(self, texture: Texture) -> PIL.Image.Image:
        """
        Read the pixel data for a texture directly from the atlas texture on the GPU.
        The contents of this image can be altered by rendering into the atlas and
        is useful in situations were you need the updated pixel data on the python side.

        Args:
            texture: The texture to get the image for
        Returns:
            A pillow image containing the pixel data in the atlas
        """
        ...

    @abc.abstractmethod
    def update_texture_image(self, texture: Texture):
        """
        Updates the internal image of a texture in the atlas texture.
        The new image needs to be the exact same size as the original
        one meaning the texture already need to exist in the atlas.

        This can be used in cases were the image is manipulated in some way
        and we need a quick way to sync these changes to graphics memory.
        This operation is fairly expensive, but still orders of magnitude
        faster than removing the old texture, adding the new one and
        re-building the entire atlas.

        Args:
            texture: The texture to update
        """
        ...

    @abc.abstractmethod
    def update_texture_image_from_atlas(self, texture: Texture) -> None:
        """
        Update the Arcade Texture's internal image with the pixel data content
        from the atlas texture on the GPU. This can be useful if you render
        into the atlas and need to update the texture with the new pixel data.

        Args:
            texture: The texture to update
        """
        ...

    # --- Debugging ---

    @abc.abstractmethod
    def to_image(
        self,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: tuple[int, int, int] = (255, 0, 0),
    ) -> PIL.Image.Image:
        """
        Convert the atlas to a Pillow image.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        Args:
            flip:
                Flip the image horizontally
            components:
                Number of components. (3 = RGB, 4 = RGBA)
            draw_borders:
                Draw region borders into image
            border_color:
                RGB color of the borders
        Returns:
            A pillow image containing the atlas texture
        """
        ...

    @abc.abstractmethod
    def show(
        self,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Show the texture atlas using Pillow.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        Args:
            flip:
                Flip the image horizontally
            components:
                Number of components. (3 = RGB, 4 = RGBA)
            draw_borders:
                Draw region borders into image
            border_color:
                RGB color of the borders
        """
        self.to_image(
            flip=flip,
            components=components,
            draw_borders=draw_borders,
            border_color=border_color,
        ).show()
        ...

    @abc.abstractmethod
    def save(
        self,
        path: str | Path,
        flip: bool = False,
        components: int = 4,
        draw_borders: bool = False,
        border_color: tuple[int, int, int] = (255, 0, 0),
    ) -> None:
        """
        Save the texture atlas to a png.

        Borders can also be drawn into the image to visualize the
        regions of the atlas.

        Args:
            path:
                The path to save the atlas on disk
            flip:
                Flip the image horizontally
            components:
                Number of components. (3 = RGB, 4 = RGBA)
            draw_borders:
                Draw region borders into image
            border_color:
                RGB color of the borders
        """


__all__ = (
    "TextureAtlasBase",
    "RESIZE_STEP",
    "UV_TEXTURE_WIDTH",
)
