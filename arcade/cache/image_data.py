from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING
from weakref import WeakValueDictionary

if TYPE_CHECKING:
    from arcade.texture import ImageData


class ImageDataCache:
    """
    Simple cache for ImageData objects.

    These are usually cached using the absolute path to the file
    or some custom unique name if generated from code.

    We are not caching by image hash because this defeats the purpose
    of this cache. We want to obtain and image based on a value that
    can be constructed without knowing the pixel data.

    The reasoning for caching the ImageData object instead of the
    PIL.Image object is to avoid re-calculating the hash.
    """
    def __init__(self):
        self._entries_strong: Dict[str, "ImageData"] = {}
        self._entries_weak: WeakValueDictionary[str, "ImageData"] = WeakValueDictionary()

    def put(self, name: str, image: "ImageData", weak=False):
        """
        Add an image to the cache.

        An entry can only be cached as either strong or weak, not both.
        If and existing entry is found, it will be replaced.

        :param name: Name of the image
        :param image: ImageData object
        :param weak: If True, the image will be weakly referenced.
        """
        from arcade.texture import ImageData
        if not isinstance(image, ImageData):
            raise TypeError("image must be an instance of ImageData")
        if weak:
            if self._entries_strong.get(name):
                del self._entries_strong[name]
            self._entries_weak[name] = image
        else:
            if self._entries_weak.get(name):
                del self._entries_weak[name]
            self._entries_strong[name] = image

    def get(self, name: str) -> Optional["ImageData"]:
        """
        Attempts to retrieve an entry from the cache.

        :param name: Name of the image
        :return: ImageData object or None if not found
        """
        return self._entries_strong.get(name) or self._entries_weak.get(name)

    def delete(self, name: str) -> None:
        """
        Attempts to delete an entry from the cache.
        Fails silently if the entry does not exist.

        :param name: Name of the image
        """
        try:
            del self._entries_strong[name]
        except KeyError:
            pass
        try:
            del self._entries_weak[name]
        except KeyError:
            pass

    def clear(self):
        """Clears the cache."""
        self._entries_strong.clear()
        self._entries_weak.clear()

    def __len__(self):
        return len(self._entries_strong) + len(self._entries_weak)

    def __getitem__(self, name: str) -> Optional["ImageData"]:
        return self.get(name)

    def __setitem__(self, name: str, image: "ImageData"):
        self.put(name, image)

    def __delitem__(self, name: str):
        self.delete(name)
