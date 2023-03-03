from math import trunc
from typing import (
    List,
    Set,
    Dict,
    Generic,
    TypeVar,
)
from arcade.types import Point, IPoint, Rect
from arcade.sprite import SpriteType

class SpatialHashEntry(Generic[SpriteType], List[Set[SpriteType]]):
    """
    Describes the entry for a single sprite in the spatial hash.
    Stores a list of all buckets containing the sprite, but also supplemental
    fields that make updating the hash efficient.
    """
    __slots__ = ("_hash",)

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
        self.entries: Dict[SpriteType, SpatialHashEntry[SpriteType]] = {}

    def hash(self, point: IPoint) -> IPoint:
        """Convert world coordinates to cell coordinates"""
        return (
            point[0] // self.cell_size,
            point[1] // self.cell_size,
        )

    def _sprite_hash(self, sprite: SpriteType):
        x,y = sprite._position
        r = sprite._hit_box_max_dimension
        min_point = trunc(x - r), trunc(y - r)
        max_point = trunc(x + r), trunc(y + r)

        # hash the minimum and maximum points
        min_point, max_point = self.hash(min_point), self.hash(max_point)
        hash = (min_point, max_point)
        return hash
    
    def reset(self):
        """
        Clear all the sprites from the spatial hash.
        """
        self.contents.clear()
        self.entries.clear()

    def add(self, sprite: SpriteType, hash = None) -> None:
        """
        Add a sprite to the spatial hash.

        :param Sprite sprite: The sprite to add
        """
        if hash is None:
            hash = self._sprite_hash(sprite)

        min_point, max_point = hash

        buckets = SpatialHashEntry[SpriteType]()
        buckets._hash = hash

        # Iterate over the rectangular region adding the sprite to each cell
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # Add sprite to the bucket
                bucket = self.contents.setdefault((i, j), set())
                bucket.add(sprite)
                # Collect all the buckets we added to
                buckets.append(bucket)

        # Keep track of which buckets the sprite is in
        self.entries[sprite] = buckets

    def move(self, sprite: SpriteType) -> None:
        """
        Removes and re-adds a sprite, but only if the sprite's hash has changed.

        :param Sprite sprite: The sprite to move
        """
        hash = self._sprite_hash(sprite)
        buckets = self.entries[sprite]
        if buckets is not None and buckets._hash == hash:
            return
        self.remove(sprite, buckets)
        # TODO move these optimizations into `add`?  So you can `add` repeatedly
        # to keep a sprite updated in the hash?
        self.add(sprite, hash)

    def remove(self, sprite: SpriteType, buckets = None) -> None:
        """
        Remove a Sprite.

        :param Sprite sprite: The sprite to remove
        """
        if buckets is None:
            buckets = self.entries[sprite]
        # Remove the sprite from all the buckets it is in
        for bucket in buckets:
            bucket.remove(sprite)

        # Delete the sprite from the bucket tracker
        del self.entries[sprite]

    def get_sprites_near_sprite(self, sprite: SpriteType) -> Set[SpriteType]:
        """
        Get all the sprites that are in the same buckets as the given sprite.

        :param Sprite sprite: The sprite to check
        :return: A set of close-by sprites
        :rtype: Set
        """

        min_point, max_point = self._sprite_hash(sprite)

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
        return len(self.entries)
