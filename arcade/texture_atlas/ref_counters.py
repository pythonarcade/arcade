"""
Reference counters for tracking textures and images in an atlas

* ImageDataRefCounter Tracks how many times an image is used by a texture
  so we can determine when it's safe to remove it.
* UniqueTextureRefCounter Tracks how many times a unique texture is used
  so we can determine when it's safe to remove it. A unique texture is
  simply a texture using the same image and the same vertex order.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from arcade.texture import ImageData, Texture


class ImageDataRefCounter:
    """
    Helper class to keep track of how many times an image is used
    by a texture in the atlas to determine when it's safe to remove it.

    Multiple Texture instances can and will use the same ImageData instance.
    """

    def __init__(self) -> None:
        self._data: Dict[str, int] = {}
        self._num_decref = 0

    def inc_ref(self, image_data: "ImageData") -> None:
        """Increment the reference counter for an image."""
        self._data[image_data.hash] = self._data.get(image_data.hash, 0) + 1

    def dec_ref(self, image_data: "ImageData") -> int:
        """
        Decrement the reference counter for an image returning the new value.
        """
        return self.dec_ref_by_hash(image_data.hash)

    def dec_ref_by_hash(self, hash: str) -> int:
        """
        Decrement the reference count for an image by hash returning the new value.

        Raises ``RuntimeError`` if the hash is no longer tracked meaning it doesn't exist
        and/or the reference count is already zero. Otherwise the updated ref counter
        is returned. When 0 is returned we removed the last reference to the image.
        """
        val = self._data.get(hash, 0) - 1
        if val < 0:
            raise RuntimeError("Reference counter is already zero or the hash doesn't exist.")

        if val == 0:
            del self._data[hash]
        else:
            self._data[hash] = val

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

        This is useful for quickly checking if images was removed from the atlas.
        We can then determine if the atlas needs to be rebuilt. Also for debugging
        purposes.

        Args:
            reset (bool): Reset the decref counter after getting the value
        """
        num_decref = self._num_decref
        if reset:
            self._num_decref = 0
        return num_decref

    def clear(self) -> None:
        """Clear the reference counters"""
        self._data.clear()
        self._num_decref = 0

    def debug_print(self) -> None:
        """print the keys and counters for debugging purposes."""
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
        Decrement the reference counter for an image returning the new value.
        """
        return self.dec_ref_by_atlas_name(image_data.atlas_name)

    def dec_ref_by_atlas_name(self, atlas_name: str) -> int:
        """
        Decrement the reference counter for an image by name returning the new value.

        Raises ``RuntimeError`` if the atlas name is no longer tracked meaning it doesn't exist
        and/or the reference count is already zero. Otherwise the updated ref counter
        is returned. When 0 is returned we removed the last reference to the texture.
        """
        val = self._data.get(atlas_name, 0) - 1
        if val < 0:
            raise RuntimeError("Reference counter is already zero or the atlas name doesn't exist.")

        if val == 0:
            del self._data[atlas_name]
        else:
            self._data[atlas_name] = val

        self._num_decref += 1
        return val

    def get_ref_count(self, image_data: "ImageData") -> int:
        """
        Get the reference counter for an image.

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

        This is useful to keep track of how many textures was removed from the atlas
        either for functional or debugging purposes.

        Args:
            reset (bool): Reset the counter after getting the value
        """
        num_decref = self._num_decref
        if reset:
            self._num_decref = 0
        return num_decref

    def clear(self) -> None:
        """Clear the reference counters"""
        self._data.clear()
        self._num_decref = 0

    def debug_print(self) -> None:
        """Print all the keys and counters for debugging purposes"""
        print(f"{self.__class__.__name__}:")
        for key, val in self._data.items():
            print(f"  {key}: {val}")

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} ref_count={self.count_all_refs()} data={self._data}>"
