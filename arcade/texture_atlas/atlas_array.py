"""
THIS IS WORK IN PROGRESS. DO NOT USE.
"""

from typing import (
    TYPE_CHECKING,
    Tuple,
)

from .base import TextureAtlasBase

if TYPE_CHECKING:
    from arcade import ArcadeContext


class TextureArrayAtlas(TextureAtlasBase):
    """
    A texture atlas that stores textures in a texture array.

    Args:
        ctx (ArcadeContext): The Arcade context.
        size (Tuple[int, int]): The texture size in pixels per layer
        layers (int): The number of layers (number of textures to store)
    """

    def __init__(self, ctx: ArcadeContext | None, size: Tuple[int, int], layers: int):
        super().__init__(ctx)
        self._size = size
        self._layers = layers

    @property
    def size(self) -> Tuple[int, int]:
        """The texture size in pixels per layer."""
        return self._size

    @property
    def layers(self) -> int:
        """The number of layers (number of textures to store)."""
        return self._layers
