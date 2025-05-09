from abc import abstractmethod
from collections.abc import Set
from math import trunc
from typing import Protocol

from arcade.sprite import SpriteType, SpriteType_co
from arcade.sprite.base import BasicSprite
from arcade.types import IPoint, Point
from arcade.types.rect import Rect


class ReadOnlySpatialHash(Protocol[SpriteType_co]):
    """A read-only view of a :py:class:`.SpatialHash` which helps preserve safety.

    This works like the read-only views of Python's built-in :py:class:`dict`
    and other types. As an every-day user, it means that the underlying
    `SpatialHash` may contain subclasses of the annotated type, but not
    superclasses.

    This ensures predicable behavior via type safety in cases where:

    #. A spatial hash is annotated with a specific type
    #. It is then manipulated outside the original context with a broader type

    Advanced users who want more information on the specifics should see the
    comments of :py:class:`~arcade.sprite_list.SpriteList`.
    """

    @abstractmethod
    def get_sprites_near_sprite(self, sprite: BasicSprite) -> Set[SpriteType_co]:
        """
        Get all the sprites that are in the same buckets as the given sprite.

        Args:
            sprite: The sprite to check
        """
        ...

    @abstractmethod
    def get_sprites_near_point(self, point: Point) -> Set[SpriteType_co]:
        """
        Return sprites in the same bucket as the given point.

        Args:
            point: The point to check
        """
        ...

    @abstractmethod
    def get_sprites_near_rect(self, rect: Rect) -> Set[SpriteType_co]:
        """
        Return sprites in the same buckets as the given rectangle.

        .. tip:: Use :py:mod:`arcade.types.rect`'s helper functions to create
          rectangle objects!

        Args:
            rect:
                The rectangle to check as a :py:class:`~arcade.types.rect.Rect`
                object.
        """
        ...


class SpatialHash(ReadOnlySpatialHash[SpriteType]):
    """A data structure best for collision checks with non-moving sprites.

    It subdivides space into a grid of squares, each with sides of length
    :py:attr:`cell_size`. Moving a sprite from one place to another is the
    same as removing and adding it. Although moving a few can be okay, it
    can quickly add up and slow down a game.

    Args:
        cell_size:
            The width and height of each square in the grid.
    """

    def __init__(self, cell_size: int) -> None:
        # Sanity check the cell size
        if not isinstance(cell_size, int):
            raise TypeError("cell_size must be an int (integer)")
        if cell_size <= 0:
            raise ValueError("cell_size must be greater than 0")

        self.cell_size: int = cell_size
        """How big each grid cell is on each side.

        .. warning:: Do not change this after creation!

        Since each cell is a square, they're used as both the
        width and height.
        """
        # Buckets of sprites per cell
        self.contents: dict[IPoint, set[SpriteType]] = {}
        # All the buckets a sprite is in.
        # This is used to remove a sprite from the spatial hash.
        self.buckets_for_sprite: dict[SpriteType, list[set[SpriteType]]] = {}

    def hash(self, point: IPoint) -> IPoint:
        """Convert world coordinates to cell coordinates"""
        return (
            point[0] // self.cell_size,
            point[1] // self.cell_size,
        )

    def reset(self):
        """Clear all the sprites from the spatial hash."""
        self.contents.clear()
        self.buckets_for_sprite.clear()

    def add(self, sprite: SpriteType) -> None:
        """
        Add a sprite to the spatial hash.

        Args:
            sprite: The sprite to add
        """
        min_point = trunc(sprite.left), trunc(sprite.bottom)
        max_point = trunc(sprite.right), trunc(sprite.top)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        buckets: list[set[SpriteType]] = []

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

        Args:
            sprite: The sprite to move
        """
        self.remove(sprite)
        self.add(sprite)

    def remove(self, sprite: SpriteType) -> None:
        """
        Remove a Sprite.

        Args:
            sprite: The sprite to remove
        """
        # Remove the sprite from all the buckets it is in
        for bucket in self.buckets_for_sprite[sprite]:
            bucket.remove(sprite)

        # Delete the sprite from the bucket tracker
        del self.buckets_for_sprite[sprite]

    def get_sprites_near_sprite(self, sprite: BasicSprite) -> set[SpriteType]:
        min_point = trunc(sprite.left), trunc(sprite.bottom)
        max_point = trunc(sprite.right), trunc(sprite.top)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        close_by_sprites: set[SpriteType] = set()

        # Iterate over the all the covered cells and collect the sprites
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = self.contents.setdefault((i, j), set())
                close_by_sprites.update(bucket)

        return close_by_sprites

    def get_sprites_near_point(self, point: Point) -> set[SpriteType]:
        hash_point = self.hash((trunc(point[0]), trunc(point[1])))
        # Return a copy of the set.
        return set(self.contents.setdefault(hash_point, set()))

    def get_sprites_near_rect(self, rect: Rect) -> set[SpriteType]:
        left, right, bottom, top = rect.lrbt
        min_point = trunc(left), trunc(bottom)
        max_point = trunc(right), trunc(top)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        close_by_sprites: set[SpriteType] = set()

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
