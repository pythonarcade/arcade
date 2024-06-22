import logging
from pathlib import Path
from typing import Union, Optional, Tuple

import PIL.Image
import PIL.ImageOps
import PIL.ImageDraw

import arcade
from arcade import hitbox
from arcade.texture import ImageData
from .texture import Texture
from arcade.cache import (
    TextureCache,
    ImageDataCache,
    HitBoxCache,
)

LOG = logging.getLogger(__name__)


class TextureCacheManager:
    """
    A simple manager wrapping texture, image data and hit box caches
    with convenience methods for loading textures and sprite sheets.
    """
    def __init__(self):
        self._sprite_sheets = {}
        self._hit_box_cache = HitBoxCache()
        self._image_data_cache = ImageDataCache()
        self._texture_cache = TextureCache()

    @property
    def hit_box_cache(self) -> HitBoxCache:
        """Cache for hit boxes."""
        return self._hit_box_cache

    @property
    def image_data_cache(self) -> ImageDataCache:
        """Cache for image data."""
        return self._image_data_cache

    @property
    def texture_cache(self) -> TextureCache:
        """Cache for textures."""
        return self._texture_cache

    def _get_real_path(self, path: Union[str, Path]) -> Path:
        """Resolve the path to the file."""
        if isinstance(path, str):
            return arcade.resources.resolve(path)
        elif isinstance(path, Path):
            return path
        else:
            raise TypeError(f"Invalid path type: {type(path)} for {path}")

    def load_image(
        self,
        path: Union[str, Path],
        hash: Optional[str] = None,
        mode="RGBA",
    ) -> ImageData:
        """
        Loads a complete image from disk.

        :param path: Path of the file to load.
        :param hash: Optional override for image hash
        :param cache: If ``True``, the image will be cached. If ``False``, the
            image will not be cached or returned from the cache.
        :param mode: The mode to use for the image. Default is "RGBA".
        """
        real_path = self._get_real_path(path)
        name = Texture.create_image_cache_name(str(real_path))
        im_data = self._image_data_cache.get(name)
        if im_data:
            return im_data
        image = PIL.Image.open(real_path).convert(mode)
        im_data = ImageData(image, hash=hash)
        self._image_data_cache.put(name, im_data)
        return im_data

    def flush(
        self,
        sprite_sheets: bool = True,
        textures: bool = True,
        image_data: bool = True,
        hit_boxes: bool = False,
    ):
        """
        Remove contents from the texture manager.

        :param sprite_sheets: If ``True``, sprite sheets will be flushed.
        :param textures: If ``True``, textures will be flushed.
        :param image_data: If ``True``, image data will be flushed.
        :param hit_boxes: If ``True``, hit boxes will be flushed.
        """
        if sprite_sheets:
            self._sprite_sheets.clear()
        if textures:
            self._texture_cache.flush()
        if image_data:
            self._image_data_cache.flush()
        if hit_boxes:
            self._hit_box_cache.flush()

    def load_texture(
        self,
        file_path: Union[str, Path],
        *,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        hit_box_algorithm: Optional[hitbox.HitBoxAlgorithm] = None,
    ) -> Texture:
        """
        Load an image from disk and create a texture.

        The ``x``, ``y``, ``width``, and ``height`` parameters are used to
        specify a sub-rectangle of the image to load. If not specified, the
        entire image is loaded.

        :param file_name: Name of the file to that holds the texture.
        :param x: X coordinate of the texture in the image.
        :param y: Y coordinate of the texture in the image.
        :param width: Width of the texture in the image.
        :param height: Height of the texture in the image.
        :param hit_box_algorithm:
        """
        LOG.info("load_texture: %s ", file_path)
        real_path = self._get_real_path(file_path)
        crop = (x, y, width, height)
        return self._load_or_get_texture(
            real_path,
            hit_box_algorithm=hit_box_algorithm,
            crop=crop,
        )

    def _load_tilemap_texture(
        self,
        file_path: Path,
        *,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        hit_box_algorithm: Optional[hitbox.HitBoxAlgorithm] = None,
    ) -> Texture:
        """
        Load an image from disk and create a texture.

        The ``x``, ``y``, ``width``, and ``height`` parameters are used to
        specify a sub-rectangle of the image to load. If not specified, the
        entire image is loaded.

        :param file_name: Name of the file to that holds the texture.
        :param x: X coordinate of the texture in the image.
        :param y: Y coordinate of the texture in the image.
        :param width: Width of the texture in the image.
        :param height: Height of the texture in the image.
        :param hit_box_algorithm:
        :returns: New :class:`Texture` object.
        :raises: ValueError
        """
        crop = (x, y, width, height)
        return self._load_or_get_texture(
            file_path,
            hit_box_algorithm=hit_box_algorithm,
            crop=crop,
        )

    def _load_or_get_texture(
        self,
        file_path: Path,
        hit_box_algorithm: Optional[hitbox.HitBoxAlgorithm] = None,
        crop: Tuple[int, int, int, int] = (0, 0, 0, 0),
        hash: Optional[str] = None,
    ) -> Texture:
        """Load a texture, or return a cached version if it's already loaded."""
        hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
        image_data: Optional[ImageData] = None
        texture = None

        # Load the image data from disk or get from cache
        image_data, cached = self._load_or_get_image(file_path, hash=hash)
        # If the image was fetched from cache we might have cached texture
        if cached:
            texture = self._texture_cache.get_with_config(image_data.hash, hit_box_algorithm)
        # If we still don't have a texture, create it
        if texture is None:
            texture = Texture(image_data, hit_box_algorithm=hit_box_algorithm)
            texture.file_path = file_path
            texture.crop_values = crop
            self._texture_cache.put(texture, file_path=file_path)

        # If we have crop values we need to dig deeper looking for cached versions
        if crop != (0, 0, 0, 0):
            image_data = self._image_data_cache.get(Texture.create_image_cache_name(file_path, crop))
            # If we don't have and cached image data we can crop from the base texture
            if image_data is None:
                texture = texture.crop(*crop)
                self._texture_cache.put(texture)
                self._image_data_cache.put(Texture.create_image_cache_name(file_path, crop), texture.image_data)
            else:
                # We might have a texture for this image data
                texture = self._texture_cache.get_with_config(image_data.hash, hit_box_algorithm)
                if texture is None:
                    texture = Texture(image_data, hit_box_algorithm=hit_box_algorithm)
                    texture.file_path = file_path
                    texture.crop_values = crop
                    self._texture_cache.put(texture, file_path=file_path)

        return texture

    def _load_or_get_image(
        self,
        file_path: Path,
        hash: Optional[str] = None,
        mode: str = "RGBA",
    ) -> Tuple[ImageData, bool]:
        """
        Load an image, or return a cached version

        :param file_path: Path to image
        :param hash: Hash of the image
        :param mode: The image mode to use (RGBA, RGB, etc.)
        :return: Tuple of image data and a boolean indicating if the image
                was fetched from cache
        """
        file_path_str = str(file_path)
        cached = True

        # Do we have cached image data for this file?
        image_data = self._image_data_cache.get(
            Texture.create_image_cache_name(file_path_str)
        )
        if not image_data:
            cached = False
            im = PIL.Image.open(file_path).convert(mode)
            image_data = ImageData(im, hash)
            self._image_data_cache.put(
                Texture.create_image_cache_name(file_path_str),
                image_data,
            )

        return image_data, cached
