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
from typing import (
    Optional,
    Tuple,
    TYPE_CHECKING,
)
import PIL.Image
import arcade

if TYPE_CHECKING:
    from arcade import ArcadeContext, Texture
    from arcade.texture import ImageData
    from arcade.texture_atlas import AtlasRegion
    from arcade.gl import Framebuffer, Texture2D

# The amount of pixels we increase the atlas when scanning for a reasonable size.
# It must be a power of two number like 64, 256, 512 ..
RESIZE_STEP = 128
UV_TEXTURE_WIDTH = 4096
# Texture coordinates for a texture (4 x vec2)
TexCoords = Tuple[float, float, float, float, float, float, float, float]


class TextureAtlasBase(abc.ABC):
    """Abstract base class for texture atlases"""

    _fbo: Framebuffer
    _texture: Texture2D

    def __init__(self, ctx: Optional["ArcadeContext"]):
        self._ctx = ctx or arcade.get_window().ctx
        self._size: Tuple[int, int] = 0, 0
        self._layers: int = 1

    @property
    def ctx(self) -> "ArcadeContext":
        return self._ctx

    @property
    def fbo(self) -> Framebuffer:
        """The framebuffer object for this atlas"""
        return self._fbo

    @property
    def texture(self) -> "Texture2D":
        """
        The atlas texture.
        """
        return self._texture

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
        Only relevant for texture arrays and 3D textures.
        """
        return self._layers

    @property
    def size(self) -> Tuple[int, int]:
        """
        The width and height of the texture atlas in pixels
        """
        return self._size

    # --- Core ---

    @abc.abstractmethod
    def add(self, texture: "Texture") -> Tuple[int, AtlasRegion]:
        """Add a texture to the atlas."""
        ...

    @abc.abstractmethod
    def remove(self, texture: "Texture") -> None:
        """Remove a texture from the atlas."""
        ...

    @abc.abstractmethod
    def resize(self, *args, **kwargs) -> None:
        """Resize the atlas."""
        ...

    @abc.abstractmethod
    def rebuild(self) -> None:
        """Rebuild the atlas."""
        ...

    @abc.abstractmethod
    def has_image(self, image_data: "ImageData") -> bool:
        """Check if the atlas has an image."""
        ...

    @abc.abstractmethod
    def has_texture(self, texture: "Texture") -> bool:
        """Check if the atlas has a texture."""
        ...

    @abc.abstractmethod
    def has_unique_texture(self, texture: "Texture") -> bool:
        """Check if the atlas has a unique texture."""
        ...

    @abc.abstractmethod
    def get_texture_id(self, texture: "Texture") -> int:
        """Get the texture ID."""
        ...

    @abc.abstractmethod
    def get_texture_region_info(self, atlas_name: str) -> AtlasRegion:
        """Get the texture region info."""
        ...

    @abc.abstractmethod
    def get_image_region_info(self, hash: str) -> AtlasRegion:
        """Get the image region info."""
        ...

    @abc.abstractmethod
    def use_uv_texture(self, unit: int = 0) -> None:
        """Use the UV texture."""
        ...

    # --- Utility ---

    @abc.abstractmethod
    @contextlib.contextmanager
    def render_into(
        self,
        texture: "Texture",
        projection: Optional[Tuple[float, float, float, float]] = None,
    ):
        """Render into the texture's atlas region."""
        yield self._fbo

    @abc.abstractmethod
    def write_image(self, image: PIL.Image.Image, x: int, y: int) -> None:
        """Write an image to the atlas."""
        ...

    @abc.abstractmethod
    def read_texture_image_from_atlas(self, texture: "Texture") -> PIL.Image.Image:
        """Read the texture image from the atlas."""
        ...

    @abc.abstractmethod
    def update_texture_image(self, texture: "Texture"):
        """Update the texture image from the atlas"""
        ...

    @abc.abstractmethod
    def update_texture_image_from_atlas(self, texture: "Texture") -> None:
        """Update the texture image from the atlas."""
        ...

    # --- Debugging ---

    @abc.abstractmethod
    def to_image(self) -> PIL.Image.Image:
        """Convert the atlas to an image."""
        ...

    @abc.abstractmethod
    def show(self) -> None:
        """Show the atlas."""
        ...


__all__ = (
    "TextureAtlasBase",
    "RESIZE_STEP",
    "UV_TEXTURE_WIDTH",
)
