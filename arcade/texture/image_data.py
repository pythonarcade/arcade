import hashlib
from typing import Optional, Tuple
import PIL.Image


class ImageData:
    """
    A class holding the image for a texture with other metadata such as the hash.
    This information is used internally by the texture atlas to identify unique textures.

    If a hash is not provided, it will be calculated.
    It's important that all hashes are of the same type.
    By default, the hash is calculated using the sha256 algorithm.

    The ability to provide a hash directly is mainly there
    for ensuring we can load and save texture atlases to disk.

    :param PIL.Image.Image image: The image for this texture
    :param str hash: The hash of the image
    """
    __slots__ = ("image", "hash", "__weakref__")
    hash_func = "sha256"

    def __init__(self, image: PIL.Image.Image, hash: Optional[str] = None):
        self.image = image
        self.hash = hash or self.calculate_hash(image)

    @classmethod
    def calculate_hash(cls, image: PIL.Image.Image) -> str:
        """
        Calculates the hash of an image.

        The algorithm used is defined by the ``hash_func`` class variable.
        """
        hash = hashlib.new(cls.hash_func)
        hash.update(image.tobytes())
        return hash.hexdigest()

    @property
    def width(self) -> int:
        """
        The width of the image
        """
        return self.image.width

    @property
    def height(self) -> int:
        """
        The height of the image
        """
        return self.image.height

    @property
    def size(self) -> Tuple[int, int]:
        """
        The size of the image
        """
        return self.image.size

    # ImageData uniqueness is based on the hash
    # -----------------------------------------
    def __hash__(self) -> int:
        return hash(self.hash)

    def __eq__(self, other) -> bool:
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        return self.hash == other.hash

    def __ne__(self, other) -> bool:
        if other is None:
            return True
        if not isinstance(other, self.__class__):
            return True
        return self.hash != other.hash

    # -----------------------------------------

    def __repr__(self):
        return f"<ImageData width={self.width}, height={self.height}, hash={self.hash}>"
