from __future__ import annotations

from typing import TYPE_CHECKING

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
    PIL.Image object is to avoid re-calculating the hash in addition
    to eliminating the need to load it and convert the pixel format.
    """

    def __init__(self):
        self._entries: dict[str, "ImageData"] = {}

    def put(self, name: str, image: "ImageData"):
        """
        Add an image to the cache.

        An entry can only be cached as either strong or weak, not both.
        If and existing entry is found, it will be replaced.

        Args:
            name: Name of the image
            image: ImageData object
        """
        from arcade.texture import ImageData

        if not isinstance(image, ImageData):
            raise TypeError("image must be an instance of ImageData")

        self._entries[name] = image

    def get(self, name: str) -> ImageData | None:
        """
        Attempts to retrieve an entry from the cache.

        Args:
            name: Name of the image
        Returns:
            ImageData instance or ``None`` if not found
        """
        return self._entries.get(name)

    def delete(self, name: str, raise_if_not_exist: bool = False) -> None:
        """
        Attempts to delete an entry from the cache.

        Args:
            name:
                Name of the image
            raise_if_not_exist:
                If ``True``, raises ``KeyError`` if the entry does not exist
        """
        try:
            del self._entries[name]
        except KeyError:
            if raise_if_not_exist:
                raise

    def flush(self):
        """Clears the cache."""
        self._entries.clear()

    def __len__(self):
        return len(self._entries)

    def __getitem__(self, name: str) -> ImageData | None:
        return self.get(name)

    def __setitem__(self, name: str, image: ImageData):
        self.put(name, image)

    def __delitem__(self, name: str):
        self.delete(name, raise_if_not_exist=True)
