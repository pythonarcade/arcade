from __future__ import annotations

from typing import Dict, Optional, TYPE_CHECKING, Union, List
from pathlib import Path
from weakref import WeakValueDictionary

if TYPE_CHECKING:
    from arcade import Texture
    from arcade.hitbox import HitBoxAlgorithm


class TextureBucket:
    """
    A simple dict based cache for textures.
    """
    def __init__(self):
        self._entries: Dict[str, "Texture"] = {}

    def put(self, name: str, texture: "Texture") -> None:
        self._entries[name] = texture

    def get(self, name: str) -> Optional["Texture"]:
        return self._entries.get(name)

    def delete(self, name: str, ignore_error: bool = True) -> None:
        try:
            del self._entries[name]
        except KeyError:
            if not ignore_error:
                raise

    def delete_by_value(self, texture: "Texture", ignore_error: bool = True) -> None:
        for name, value in self._entries.items():
            if value is texture:
                del self._entries[name]
                return
        if not ignore_error:
            raise KeyError(f"Texture {texture} not found")

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)


class WeakTextureBucket(TextureBucket):
    """
    A simple WeakValueDictionary based cache for textures.
    """
    def __init__(self):
        self._entries: WeakValueDictionary[str, "Texture"] = WeakValueDictionary()


class TextureCache:
    """
    A cache for arcade textures.

    The creation of a texture is an expensive operation for several reasons.
    * Creating a texture from a file has a cost
    * Creating a texture from a PIL image has a cost
    * Once the texture is created it's expensive to calculate hit box points

    This cache is intended to reduce the cost of creating textures by reusing
    existing ones. We also re-use the internal images on the existing textures
    for making different configurations of the same texture such as flipped
    and rotated versions including textures with different hit box configurations
    for the same image.
    """

    def __init__(self):
        self._strong_entries = TextureBucket()
        self._weak_entires = WeakTextureBucket()
        self._strong_file_entries = TextureBucket()
        self._weak_file_entries = WeakTextureBucket()

    def put(
        self,
        texture: "Texture",
        *,
        file_path: Optional[Union[str, Path]] = None,
        strong: bool = True,
    ) -> None:
        """
        Add a texture to the cache.

        :param texture: The texture to add
        :param file_path: The path to the file the texture was loaded from
        :param strong: If True the cache will keep the texture alive
        """
        # TODO: Consider using Texture.origin instead of file_path
        #       Consider also caching origin that is not a file name
        name = texture.cache_name
        if strong:
            self._strong_entries.put(name, texture)
            if self._strong_file_entries.get(file_path): # type: ignore  # pending https://github.com/pythonarcade/arcade/issues/1752
                raise ValueError(f"File path {file_path} already in cache")
            if file_path:
                self._strong_file_entries.put(str(file_path), texture)
        else:
            self._weak_entires.put(name, texture)
            if self._weak_file_entries.get(file_path): # type: ignore  # pending https://github.com/pythonarcade/arcade/issues/1752
                raise ValueError(f"File path {file_path} already in cache")
            if file_path:
                self._weak_file_entries.put(str(file_path), texture)

    def get(self, name: str) -> Optional["Texture"]:
        """
        Get a texture from the cache by cache name

        :param name: The cache name of the texture
        :return: The texture if found, otherwise None
        """
        return (
            self._strong_entries.get(name)
            or self._weak_entires.get(name)
        )

    def get_with_config(self, hash: str, hit_box_algorithm: "HitBoxAlgorithm") -> Optional["Texture"]:
        """
        Attempts to find a texture with a specific configuration.

        :param image_data: The image data to search for
        :param hit_box_algorithm: The hit box algorithm to search for
        :return: The texture if found, otherwise None
        """
        from arcade import Texture
        name = Texture.create_cache_name(
            hash=hash,
            hit_box_algorithm=hit_box_algorithm,
        )
        return self.get(name)

    def get_file(self, file_path: str) -> Optional["Texture"]:
        """
        Get a texture from the cache by file path.

        :param file_path: The path to the file the texture was loaded from
        """
        return (
            self._strong_file_entries.get(file_path)
            or self._weak_file_entries.get(file_path)
        )

    def delete(self, texture_or_name: Union["Texture", str], ignore_error: bool = True) -> None:
        """
        Delete a texture from the cache by cache name.

        :param texture_or_name: The texture or cache name to delete
        :param ignore_error: If True, ignore errors when deleting
        """
        from arcade import Texture

        if isinstance(texture_or_name, Texture):
            texture = texture_or_name
            name = texture.cache_name
            # Delete from texture buckets
            self._strong_entries.delete(name, ignore_error=ignore_error)
            self._weak_entires.delete(name, ignore_error=ignore_error)
            # Delete from file buckets
            self._strong_file_entries.delete_by_value(texture)
            self._weak_file_entries.delete_by_value(texture)
        elif isinstance(texture_or_name, str):
            name = texture_or_name
            # Delete from texture buckets
            self._strong_entries.delete(name, ignore_error=ignore_error)
            self._weak_entires.delete(name, ignore_error=ignore_error)
            # Delete from file buckets
            self._strong_file_entries.delete(name, ignore_error=ignore_error)
            self._weak_file_entries.delete(name, ignore_error=ignore_error)
        else:
            raise TypeError(f"Expected Texture or str, got {type(texture_or_name)}")

    def clear(self) -> None:
        """Clear the cache"""
        self._strong_entries.clear()
        self._weak_entires.clear()
        self._strong_file_entries.clear()
        self._weak_file_entries.clear()

    def get_all_textures(self) -> List["Texture"]:
        """Get all unique textures in the cache"""
        return (
            list(self._strong_entries._entries.values())
            + list(self._weak_entires._entries.values())
            + list(self._strong_file_entries._entries.values())
            + list(self._weak_file_entries._entries.values())
        )

    def __len__(self) -> int:
        """Count the number of unique textures"""
        return len(set(self.get_all_textures()))

    def __contains__(self, texture: "Texture") -> bool:
        return texture in self.get_all_textures()

    def __iter__(self):
        return iter(self.get_all_textures())

    def __getitem__(self, name: str) -> Optional["Texture"]:
        return self.get(name)

    def __setitem__(self, name: str, texture: "Texture") -> None:
        self.put(texture, strong=True)

    def __delitem__(self, name: str) -> None:
        self.delete(name)
