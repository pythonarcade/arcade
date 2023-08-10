from __future__ import annotations

from math import trunc
from typing import (
    List,
    Set,
    Dict,
    Generic,
)
from arcade.sprite.base import BasicSprite
from arcade.types import Point, IPoint, Rect
from arcade.sprite import SpriteType


class SpatialHash(Generic[SpriteType]):
    """
    Structure for fast collision checking with sprites.

    See: https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/

    :param int cell_size: Size (width and height) of the cells in the spatial hash
    """
    def __init__(self, cell_size: int) -> None:
        # Sanity check the cell size
        if cell_size <= 0:
            raise ValueError("cell_size must be greater than 0")
        if not isinstance(cell_size, int):
            raise ValueError("cell_size must be an integer")

        self.cell_size = cell_size
        # Buckets of sprites per cell
        self.contents: Dict[IPoint, Set[SpriteType]] = {}
        # All the buckets a sprite is in.
        # This is used to remove a sprite from the spatial hash.
        self.buckets_for_sprite: Dict[SpriteType, List[Set[SpriteType]]] = {}

    def hash(self, point: IPoint) -> IPoint:
        """Convert world coordinates to cell coordinates"""
        return (
            point[0] // self.cell_size,
            point[1] // self.cell_size,
        )

    def reset(self):
        """
        Clear all the sprites from the spatial hash.
        """
        self.contents.clear()
        self.buckets_for_sprite.clear()

    def add(self, sprite: SpriteType) -> None:
        """
        Add a sprite to the spatial hash.

        :param Sprite sprite: The sprite to add
        """
        min_point = trunc(sprite.left), trunc(sprite.bottom)
        max_point = trunc(sprite.right), trunc(sprite.top)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        buckets: List[Set[SpriteType]] = []

        # Iterate over the rectangular region adding the sprite to each cell
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # Add sprite to the bucket
                bucket = self.contents.setdefault((i, j), set())
                bucket.add(sprite)
                # Collect all the buckets we added to
                buckets.append(bucket)

        # Keep track of which buckets the sprite is in
        self.buckets_for_sprite[sprite] = buckets

    def move(self, sprite: SpriteType) -> None:
        """
        Shortcut to remove and re-add a sprite.

        :param Sprite sprite: The sprite to move
        """
        self.remove(sprite)
        self.add(sprite)

    def remove(self, sprite: SpriteType) -> None:
        """
        Remove a Sprite.

        :param Sprite sprite: The sprite to remove
        """
        # Remove the sprite from all the buckets it is in
        for bucket in self.buckets_for_sprite[sprite]:
            bucket.remove(sprite)

        # Delete the sprite from the bucket tracker
        del self.buckets_for_sprite[sprite]

    def get_sprites_near_sprite(self, sprite: BasicSprite) -> Set[SpriteType]:
        """
        Get all the sprites that are in the same buckets as the given sprite.

        :param Sprite sprite: The sprite to check
        :return: A set of close-by sprites
        :rtype: Set
        """
        min_point = trunc(sprite.left), trunc(sprite.bottom)
        max_point = trunc(sprite.right), trunc(sprite.top)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        close_by_sprites: Set[SpriteType] = set()

        # Iterate over the all the covered cells and collect the sprites
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = self.contents.setdefault((i, j), set())
                close_by_sprites.update(bucket)

        return close_by_sprites

    def get_sprites_near_point(self, point: Point) -> Set[SpriteType]:
        """
        Return sprites in the same bucket as the given point.

        :param Point point: The point to check

        :return: A set of close-by sprites
        :rtype: Set
        """
        hash_point = self.hash((trunc(point[0]), trunc(point[1])))
        # Return a copy of the set.
        return set(self.contents.setdefault(hash_point, set()))

    def get_sprites_near_rect(self, rect: Rect) -> Set[SpriteType]:
        """
        Return sprites in the same buckets as the given rectangle.

        :param Rect rect: The rectangle to check (left, right, bottom, top)
        :return: A set of sprites in the rectangle
        :rtype: Set
        """
        left, right, bottom, top = rect
        min_point = trunc(left), trunc(bottom)
        max_point = trunc(right), trunc(top)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        close_by_sprites: Set[SpriteType] = set()

        # Iterate over the all the covered cells and collect the sprites
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = self.contents.setdefault((i, j), set())
                close_by_sprites.update(bucket)

        return close_by_sprites

    @property
    def count(self) -> int:
        """Return the number of sprites in the spatial hash"""
        # NOTE: We should really implement __len__ but this means
        # changing the truthiness of the class instance.
        # if spatial_hash will be False if it is empty.
        # For backwards compatibility, we'll keep it as a property.
        return len(self.buckets_for_sprite)
