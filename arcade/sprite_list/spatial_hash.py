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
    comments of :py:class:`~arcade.SpriteList`.
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

        .. tip:: Use the helper functions in ``arcade.types.rect`` to create
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
    :py:attr:`cell_size`.

    Moving a sprite only marks it as moved. The next query, such as a
    collision check, puts the moved sprites in their new squares, skipping
    any still in the same squares. So a sprite that moves several times in
    a frame is updated once, and moving sprites costs nothing until
    something checks for collisions. Moving many sprites still adds up and
    can slow down a game.

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
        self._contents: dict[IPoint, set[SpriteType]] = {}
        # All the buckets a sprite is in.
        # This is used to remove a sprite from the spatial hash.
        self._buckets_for_sprite: dict[SpriteType, list[set[SpriteType]]] = {}
        # The min and max cells each sprite was added to, to skip moves
        # that stay in the same cells
        self._cells_for_sprite: dict[SpriteType, tuple[IPoint, IPoint]] = {}
        # Sprites that moved since the last query
        self._moved: set[SpriteType] = set()

    @property
    def contents(self) -> dict[IPoint, set[SpriteType]]:
        """The sprites in each cell, keyed by cell coordinates."""
        self._update_moved()
        return self._contents

    @property
    def buckets_for_sprite(self) -> dict[SpriteType, list[set[SpriteType]]]:
        """The cell buckets each sprite is in."""
        self._update_moved()
        return self._buckets_for_sprite

    def _update_moved(self) -> None:
        """Put sprites that moved since the last query in their new cells."""
        if not self._moved:
            return
        moved = self._moved
        self._moved = set()
        cells_for_sprite = self._cells_for_sprite
        for sprite in moved:
            cells = cells_for_sprite.get(sprite)
            # Skip sprites removed since, and moves within the same cells
            if cells is not None and self._get_cell_bounds(sprite) != cells:
                self.remove(sprite)
                self.add(sprite)

    def hash(self, point: IPoint) -> IPoint:
        """Convert world coordinates to cell coordinates"""
        return (
            point[0] // self.cell_size,
            point[1] // self.cell_size,
        )

    def reset(self):
        """Clear all the sprites from the spatial hash."""
        self._contents.clear()
        self._buckets_for_sprite.clear()
        self._cells_for_sprite.clear()
        self._moved.clear()

    def _get_cell_bounds(self, sprite: BasicSprite) -> tuple[IPoint, IPoint]:
        """Get the min and max cells covered by a sprite's hit box."""
        # The hit box caches its bounds, so collision checks can reuse them
        left, right, bottom, top = sprite.hit_box.get_adjusted_bounds()
        min_point = self.hash((trunc(left), trunc(bottom)))
        max_point = self.hash((trunc(right), trunc(top)))
        return min_point, max_point

    def add(self, sprite: SpriteType) -> None:
        """
        Add a sprite to the spatial hash.

        Args:
            sprite: The sprite to add
        """
        min_point, max_point = cells = self._get_cell_bounds(sprite)
        buckets: list[set[SpriteType]] = []
        contents = self._contents

        # Iterate over the rectangular region adding the sprite to each cell
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # Add sprite to the bucket
                bucket = contents.setdefault((i, j), set())
                bucket.add(sprite)
                # Collect all the buckets we added to
                buckets.append(bucket)

        # Keep track of which buckets the sprite is in
        self._buckets_for_sprite[sprite] = buckets
        self._cells_for_sprite[sprite] = cells

    def move(self, sprite: SpriteType) -> None:
        """
        Mark a sprite as moved.

        It's put in its new cells at the next query, if they changed.

        Args:
            sprite: The sprite to move
        """
        self._moved.add(sprite)

    def remove(self, sprite: SpriteType) -> None:
        """
        Remove a Sprite.

        Args:
            sprite: The sprite to remove
        """
        # Remove the sprite from all the buckets it is in
        for bucket in self._buckets_for_sprite[sprite]:
            bucket.remove(sprite)

        # Delete the sprite from the bucket tracker
        del self._buckets_for_sprite[sprite]
        del self._cells_for_sprite[sprite]
        self._moved.discard(sprite)

    # NOTE: The query methods below use contents.get() rather than
    # setdefault() so that looking at an empty cell doesn't create a bucket
    # for it. Otherwise the dict grows with every cell ever queried.

    def get_sprites_near_sprite(self, sprite: BasicSprite) -> set[SpriteType]:
        self._update_moved()
        min_point, max_point = self._get_cell_bounds(sprite)
        close_by_sprites: set[SpriteType] = set()
        contents = self._contents

        # Iterate over the all the covered cells and collect the sprites
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = contents.get((i, j))
                if bucket:
                    close_by_sprites.update(bucket)

        return close_by_sprites

    def get_sprites_near_point(self, point: Point) -> set[SpriteType]:
        self._update_moved()
        hash_point = self.hash((trunc(point[0]), trunc(point[1])))
        # Return a copy of the set.
        return set(self._contents.get(hash_point, ()))

    def get_sprites_near_rect(self, rect: Rect) -> set[SpriteType]:
        left, right, bottom, top = rect.lrbt
        min_point = trunc(left), trunc(bottom)
        max_point = trunc(right), trunc(top)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        close_by_sprites: set[SpriteType] = set()
        self._update_moved()
        contents = self._contents

        # Iterate over the all the covered cells and collect the sprites
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = contents.get((i, j))
                if bucket:
                    close_by_sprites.update(bucket)

        return close_by_sprites

    @property
    def count(self) -> int:
        """Return the number of sprites in the spatial hash"""
        # NOTE: We should really implement __len__ but this means
        # changing the truthiness of the class instance.
        # if spatial_hash will be False if it is empty.
        # For backwards compatibility, we'll keep it as a property.
        return len(self._buckets_for_sprite)
