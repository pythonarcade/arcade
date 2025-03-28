from pathlib import Path

import PIL.Image
import PIL.ImageDraw
import PIL.ImageOps

import arcade
from arcade import hitbox
from arcade.cache import (
    HitBoxCache,
    ImageDataCache,
    TextureCache,
)
from arcade.texture import ImageData, SpriteSheet
from arcade.types.rect import Rect

from .texture import Texture


class TextureCacheManager:
    """
    A simple manager wrapping texture, image data and hit box caches
    with convenient methods for loading textures and sprite sheets.

    Args:
        hit_box_cache:
            Optional hit box cache to use. If not specified, a new cache will be created.
        image_data_cache:
            Optional image data cache to use. If not specified, a new cache will be created.
        texture_cache:
            Optional texture cache to use. If not specified, a new cache will be created
    """

    def __init__(
        self,
        hit_box_cache: HitBoxCache | None = None,
        image_data_cache: ImageDataCache | None = None,
        texture_cache: TextureCache | None = None,
    ):
        self._sprite_sheets: dict[str, SpriteSheet] = {}
        self._hit_box_cache = hit_box_cache or HitBoxCache()
        self._image_data_cache = image_data_cache or ImageDataCache()
        self._texture_cache = texture_cache or TextureCache()

    @property
    def hit_box_cache(self) -> HitBoxCache:
        """Get or set the current hit box cache."""
        return self._hit_box_cache

    @hit_box_cache.setter
    def hit_box_cache(self, value: HitBoxCache):
        self._hit_box_cache = value

    @property
    def image_data_cache(self) -> ImageDataCache:
        """Cache for image data."""
        return self._image_data_cache

    @property
    def texture_cache(self) -> TextureCache:
        """Cache for textures."""
        return self._texture_cache

    def flush(
        self,
        sprite_sheets: bool = True,
        textures: bool = True,
        image_data: bool = True,
        hit_boxes: bool = False,
    ):
        """
        Remove contents from the texture manager.

        Args:
            sprite_sheets:
                If ``True``, sprite sheets will be flushed.
            textures:
                If ``True``, textures will be flushed.
            image_data:
                If ``True``, image data will be flushed.
            hit_boxes:
                If ``True``, hit boxes will be flushed.
        """
        if sprite_sheets:
            self._sprite_sheets.clear()
        if textures:
            self._texture_cache.flush()
        if image_data:
            self._image_data_cache.flush()
        if hit_boxes:
            self._hit_box_cache.flush()

    def _get_real_path(self, path: str | Path) -> Path:
        """
        Resolve the path to the file.

        Args:
            path: Path to the file
        """
        if isinstance(path, str):
            return arcade.resources.resolve(path)
        elif isinstance(path, Path):
            return path
        else:
            raise TypeError(f"Invalid path type: {type(path)} for {path}")

    def load_or_get_spritesheet(self, path: str | Path) -> SpriteSheet:
        """
        Load a sprite sheet from disk, or return a cached version.

        Note that any texture sliced from the sprite sheet will be cached.
        if this is not the desirable behavior, use :meth:`load_or_get_spritesheet_texture`.

        Args:
            path: Path to the sprite sheet image
        """
        real_path = self._get_real_path(path)
        real_path_str = str(real_path)

        sprite_sheet = self._sprite_sheets.get(real_path_str)
        if sprite_sheet is None:
            sprite_sheet = arcade.SpriteSheet(real_path)
            self._sprite_sheets[real_path_str] = sprite_sheet

        return sprite_sheet

    def load_or_get_spritesheet_texture(
        self,
        path: str | Path,
        rect: Rect,
        hit_box_algorithm: hitbox.HitBoxAlgorithm | None = None,
    ) -> Texture:
        """
        Slice out a texture slice from a sprite sheet.

        * If the spritesheet is not already loaded, it will be loaded and cached.
        * If the sliced texture is already cached, it will be returned instead.

        Args:
            path:
                Path to the sprite sheet image
            rect:
                Slice of the texture in the sprite sheet.
            hit_box_algorithm:
                Hit box algorithm to use. If not specified, the global default will be used.
        """
        real_path = self._get_real_path(path)
        texture = self._texture_cache.get_texture_by_filepath(real_path, crop=rect.lbwh_int)
        if texture:
            return texture

        # check if sprite sheet is cached and load if not
        sprite_sheet = self.load_or_get_spritesheet(real_path)

        # slice out the texture and cache + return
        texture = sprite_sheet.get_texture(rect, hit_box_algorithm=hit_box_algorithm)
        self._texture_cache.put(texture)
        if texture.image_cache_name:
            self._image_data_cache.put(texture.image_cache_name, texture.image_data)

        # Add to image data cache
        self._image_data_cache.put(
            Texture.create_image_cache_name(real_path, rect.lbwh_int),
            texture.image_data,
        )

        return texture

    def load_or_get_image(
        self,
        path: str | Path,
        hash: str | None = None,
        mode="RGBA",
    ) -> ImageData:
        """
        Loads a complete image from disk or return a cached version.

        Args:
            path:
                Path of the file to load.
            hash:
                Optional override for image hash
            mode:
                The mode to use for the image. Default is "RGBA".
        """
        real_path = self._get_real_path(path)
        name = Texture.create_image_cache_name(real_path)
        im_data = self._image_data_cache.get(name)
        if im_data:
            return im_data
        image = PIL.Image.open(real_path).convert(mode)
        im_data = ImageData(image, hash=hash)
        self._image_data_cache.put(name, im_data)
        return im_data

    def load_or_get_texture(
        self,
        file_path: str | Path,
        *,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        hit_box_algorithm: hitbox.HitBoxAlgorithm | None = None,
    ) -> Texture:
        """
        Load an image from disk and create a texture. If the image is already
        loaded, return the cached version.

        The ``x``, ``y``, ``width``, and ``height`` parameters are used to
        specify a sub-rectangle of the image to load. If not specified, the
        entire image is loaded.

        Args:
            file_path:
                Path to the image file.
            x:
                X coordinate of the texture in the image.
            y:
                Y coordinate of the texture in the image.
            width:
                Width of the texture in the image.
            height:
                Height of the texture in the image.
            hit_box_algorithm:
                The hit box algorithm to use for this texture. If not specified,
                the global default will be used.
        """
        real_path = self._get_real_path(file_path)

        return self._load_or_get_texture(
            real_path,
            hit_box_algorithm=hit_box_algorithm,
            crop=(x, y, width, height),
        )

    def _load_or_get_texture(
        self,
        file_path: Path,
        hit_box_algorithm: hitbox.HitBoxAlgorithm | None = None,
        crop: tuple[int, int, int, int] = (0, 0, 0, 0),
        hash: str | None = None,
    ) -> Texture:
        """Load a texture, or return a cached version if it's already loaded."""
        hit_box_algorithm = hit_box_algorithm or hitbox.algo_default
        image_data: ImageData | None = None
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
            self._texture_cache.put(texture)

        # If we have crop values we need to dig deeper looking for cached versions
        if crop != (0, 0, 0, 0):
            image_data = self._image_data_cache.get(
                Texture.create_image_cache_name(file_path, crop)
            )
            # If we don't have and cached image data we can crop from the base texture
            if image_data is None:
                texture = texture.crop(*crop)
                self._texture_cache.put(texture)
                self._image_data_cache.put(
                    Texture.create_image_cache_name(file_path, crop), texture.image_data
                )
            else:
                # We might have a texture for this image data
                texture = self._texture_cache.get_with_config(image_data.hash, hit_box_algorithm)
                if texture is None:
                    texture = Texture(image_data, hit_box_algorithm=hit_box_algorithm)
                    texture.file_path = file_path
                    texture.crop_values = crop
                    self._texture_cache.put(texture)

        return texture

    def _load_or_get_image(
        self,
        file_path: Path,
        hash: str | None = None,
        mode: str = "RGBA",
    ) -> tuple[ImageData, bool]:
        """
        Load an image, or return a cached version

        Args:
            file_path:
                Path to image
            hash:
                Hash of the image
            mode:
                The image mode to use (RGBA, RGB, etc.)

        Returns:
            Tuple of image data and a boolean indicating if the
            image was fetched from cache
        """
        file_path_str = str(file_path)
        cached = True

        # Do we have cached image data for this file?
        image_data = self._image_data_cache.get(Texture.create_image_cache_name(file_path_str))
        if not image_data:
            cached = False
            im = PIL.Image.open(file_path).convert(mode)
            image_data = ImageData(im, hash)
            self._image_data_cache.put(
                Texture.create_image_cache_name(file_path_str),
                image_data,
            )

        return image_data, cached
