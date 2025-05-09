from pathlib import Path
from typing import TYPE_CHECKING

from arcade.texture.texture import Texture

if TYPE_CHECKING:
    from arcade import Texture
    from arcade.hitbox import HitBoxAlgorithm


class TextureBucket:
    """
    A simple dict based cache for textures.
    """

    def __init__(self):
        self._entries: dict[str, Texture] = {}

    def put(self, name: str, texture: Texture) -> None:
        """
        Add a texture to the cache.

        Args:
            name:
                The cache name of the texture
            texture:
                The texture to add
        """
        self._entries[name] = texture

    def get(self, name: str) -> Texture | None:
        """
        Get a texture from the cache by cache name.

        Args:
            name:
                The cache name of the texture
        Returns:
            The texture if found, otherwise ``None``
        """
        return self._entries.get(name)

    def delete(self, name: str, raise_if_not_exist: bool = True) -> None:
        """
        Delete a texture from the cache by cache name.

        Args:
            name:
                The cache name of the texture
            raise_if_not_exist:
                If ``True``, raises ``KeyError`` if the entry does not exist
        """
        try:
            del self._entries[name]
        except KeyError:
            if raise_if_not_exist:
                raise

    def delete_by_value(self, texture: "Texture") -> None:
        """
        Delete a texture from the cache by texture instance.

        Args:
            texture: The texture instance to delete
        """
        for name, value in self._entries.items():
            if value is texture:
                del self._entries[name]
                return

    def flush(self) -> None:
        """Clear the cache"""
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)


class TextureCache:
    """
    A cache for Arcade textures.

    The creation of a texture is an expensive operation for several reasons.
    * Loading an image from disk has a cost
    * Converting the image to a format suitable for OpenGL has a cost
    * Calculating the hash of the image has a cost
    * Creating the texture instance has a cost
    * Once the texture is created it's expensive to calculate hit box points

    This cache is intended to reduce the cost of creating textures by reusing
    existing ones. We also re-use the internal images on the existing textures
    for making different configurations of the same texture such as flipped
    and rotated versions including textures with different hit box configurations
    for the same image.
    """

    def __init__(self):
        self._entries = TextureBucket()
        self._file_entries = TextureBucket()

    def put(self, texture: "Texture") -> None:
        """
        Add a texture to the cache. It's important that the crop values
        and file path are correctly set on the texture before adding it to
        the cache.

        Args:
            texture: The texture to add
        """
        self._entries.put(texture.cache_name, texture)

        # Only cache by file path if it's the whole texture and not a crop
        # if texture.file_path and texture.crop_values in [None, (0, 0, 0, 0)]:
        #     self._file_entries.put(str(texture.file_path), texture)
        image_cache_name = texture.image_cache_name
        if image_cache_name:
            self._file_entries.put(image_cache_name, texture)

    def get(self, name: str) -> Texture | None:
        """
        Get a texture from the cache by cache name

        Args:
            name: The cache name of the texture
        Returns:
            The texture if found, otherwise ``None``
        """
        return self._entries.get(name)

    def get_with_config(self, hash: str, hit_box_algorithm: "HitBoxAlgorithm") -> Texture | None:
        """
        Attempts to find a texture with a specific configuration.

        Args:
            hash:
                The image hash
            hit_box_algorithm:
                The hit box algorithm to search for
        Returns:
            The texture if found, otherwise ``None``
        """
        from arcade import Texture

        name = Texture.create_cache_name(
            hash=hash,
            hit_box_algorithm=hit_box_algorithm,
        )
        return self.get(name)

    def get_texture_by_filepath(
        self,
        file_path: str | Path,
        crop: tuple[int, int, int, int] = (0, 0, 0, 0),
    ) -> Texture | None:
        """
        Get a texture from the cache by file path and crop values.

        Args:
            file_path: The path to the file the texture was loaded from
            crop: The crop values used when creating the texture
        """
        from arcade import Texture

        file_cache_name = Texture.create_image_cache_name(file_path, crop)
        return self._file_entries.get(file_cache_name)

    def delete(self, texture_or_name: Texture | str, raise_if_not_exist: bool = False) -> None:
        """
        Delete a texture from the cache by cache name.

        Args:
            texture_or_name:
                The texture or cache name to delete
            raise_if_not_exist:
                If ``True``, ignore errors when deleting
        """
        if isinstance(texture_or_name, Texture):
            texture = texture_or_name
            name = texture.cache_name
            # Delete from texture buckets
            self._entries.delete(name, raise_if_not_exist=raise_if_not_exist)
            # Delete from file bucket. Only present if file_path was provided
            self._file_entries.delete_by_value(texture)
        elif isinstance(texture_or_name, str):
            name = texture_or_name
            # Delete from texture buckets
            self._entries.delete(name, raise_if_not_exist=raise_if_not_exist)
            # Delete from file buckets
            self._file_entries.delete(name, raise_if_not_exist=False)
        else:
            raise TypeError(f"Expected Texture or str, got {type(texture_or_name)}")

    def flush(self) -> None:
        """Clear the cache"""
        self._entries.flush()
        self._file_entries.flush()

    def get_all_textures(self) -> set["Texture"]:
        """Get all textures in the cache"""
        return set(self._entries._entries.values())

    def __len__(self) -> int:
        """Count the number of unique textures"""
        return len(self._entries)

    def __contains__(self, texture: "Texture") -> bool:
        """Check if a texture is in the cache"""
        return texture in self.get_all_textures()

    def __iter__(self):
        """Iterate over all unique textures"""
        return iter(self.get_all_textures())

    def __getitem__(self, name: str) -> Texture | None:
        """Get a texture from the cache by cache name"""
        return self.get(name)

    def __setitem__(self, name: str, texture: "Texture") -> None:
        """Add a texture to the cache by cache name"""
        self.put(texture)

    def __delitem__(self, name: str) -> None:
        """Delete a texture from the cache by cache name"""
        self.delete(name, raise_if_not_exist=False)
