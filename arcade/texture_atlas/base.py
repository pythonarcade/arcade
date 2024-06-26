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
import logging
from typing import (
    Dict,
    Optional,
    TYPE_CHECKING,
)

import arcade
if TYPE_CHECKING:
    from arcade import ArcadeContext, Texture
    from arcade.texture import ImageData

# The amount of pixels we increase the atlas when scanning for a reasonable size.
# It must divide. Must be a power of two number like 64, 256, 512 etx
RESIZE_STEP = 128
UV_TEXTURE_WIDTH = 4096
LOG = logging.getLogger(__name__)


class ImageDataRefCounter:
    """
    Helper class to keep track of how many times an image is used
    by a texture in the atlas to determine when it's safe to remove it.

    Multiple Texture instances can and will use the same ImageData
    instance.
    """
    def __init__(self) -> None:
        self._data: Dict[str, int] = {}
        self._num_decref = 0

    def inc_ref(self, image_data: "ImageData") -> None:
        """Increment the reference count for an image."""
        self._data[image_data.hash] = self._data.get(image_data.hash, 0) + 1

    def dec_ref(self, image_data: "ImageData") -> int:
        """
        Decrement the reference count for an image returning the new value.
        """
        return self.dec_ref_by_hash(image_data.hash)

    def dec_ref_by_hash(self, hash: str) -> int:
        """
        Decrement the reference count for an image by hash returning the new value.
        """
        if hash not in self._data:
            raise RuntimeError(f"Image {hash} not in ref counter")

        val = self._data[hash] - 1
        self._data[hash] = val

        if val < 0:
            raise RuntimeError(f"Image {hash} ref count went below zero")
        if val == 0:
            del self._data[hash]

        self._num_decref += 1

        return val

    def get_ref_count(self, image_data: "ImageData") -> int:
        """
        Get the reference count for an image.

        Args:
            image_data (ImageData): The image to get the reference count for
        """
        return self._data.get(image_data.hash, 0)

    def count_all_refs(self) -> int:
        """Helper function to count the total number of references."""
        return sum(self._data.values())

    def get_total_decref(self, reset=True) -> int:
        """
        Get the total number of decrefs.

        Args:
            reset (bool): Reset the counter after getting the value
        """
        num_decref = self._num_decref
        if reset:
            self._num_decref = 0
        return num_decref

    def clear(self) -> None:
        """Clear the reference counter."""
        self._data.clear()
        self._num_decref = 0

    def debug_print(self) -> None:
        """Debug print the reference counter."""
        print(f"{self.__class__.__name__}:")
        for key, val in self._data.items():
            print(f"  {key}: {val}")

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ref_count={self.count_all_refs()} data={self._data}>"


class UniqueTextureRefCounter:
    """
    Helper class to keep track of how many times a unique texture is used.
    A "unique texture" is based on the ``atlas_name`` of the texture meaning
    a texture using the same image and the same vertex order.
    """
    def __init__(self) -> None:
        self._data: Dict[str, int] = {}
        self._num_decref = 0

    def inc_ref(self, image_data: "Texture") -> None:
        """Increment the reference count for an image."""
        self._data[image_data.atlas_name] = self._data.get(image_data.atlas_name, 0) + 1

    def dec_ref(self, image_data: "Texture") -> int:
        """
        Decrement the reference count for an image returning the new value.
        """
        return self.dec_ref_by_atlas_name(image_data.atlas_name)

    def dec_ref_by_atlas_name(self, atlas_name: str) -> int:
        """
        Decrement the reference count for an image by name returning the new value.
        """
        if atlas_name not in self._data:
            raise RuntimeError(f"Image {atlas_name} not in ref counter")

        val = self._data[atlas_name] - 1
        self._data[atlas_name] = val

        if val < 0:
            raise RuntimeError(f"Image {atlas_name} ref count went below zero")
        if val == 0:
            del self._data[atlas_name]

        self._num_decref += 1

        return val

    def get_ref_count(self, image_data: "ImageData") -> int:
        """
        Get the reference count for an image.

        Args:
            image_data (ImageData): The image to get the reference count for
        """
        return self._data.get(image_data.hash, 0)

    def count_all_refs(self) -> int:
        """Helper function to count the total number of references."""
        return sum(self._data.values())

    def get_total_decref(self, reset=True) -> int:
        """
        Get the total number of decrefs.

        Args:
            reset (bool): Reset the counter after getting the value
        """
        num_decref = self._num_decref
        if reset:
            self._num_decref = 0
        return num_decref

    def clear(self) -> None:
        """Clear the reference counter."""
        self._data.clear()
        self._num_decref = 0

    def debug_print(self) -> None:
        """Debug print the reference counter."""
        print(f"{self.__class__.__name__}:")
        for key, val in self._data.items():
            print(f"  {key}: {val}")

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ref_count={self.count_all_refs()} data={self._data}>"


class TextureAtlasBase(abc.ABC):
    """Generic base for texture atlases."""

    def __init__(self, ctx: Optional["ArcadeContext"]):
        self._ctx = ctx or arcade.get_window().ctx

    @property
    def ctx(self) -> "ArcadeContext":
        return self._ctx

    # NOTE: AtlasRegion only makes sense for 2D atlas. Figure it out.
    # @abc.abstractmethod
    # def add(self, texture: "Texture") -> Tuple[int, AtlasRegion]:
    #     """Add a texture to the atlas."""
    #     raise NotImplementedError

    @abc.abstractmethod
    def remove(self, texture: "Texture") -> None:
        """Remove a texture from the atlas."""
        raise NotImplementedError
