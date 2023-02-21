from typing import (
    List,
    Set,
    Dict,
    TYPE_CHECKING
)
from arcade.types import IPoint

if TYPE_CHECKING:
    from arcade import Sprite


class SpatialHash:
    """
    Structure for fast collision checking with sprites.

    See: https://www.gamedev.net/articles/programming/general-and-gameplay-programming/spatial-hashing-r2697/

    :param int cell_size: Size (width and height) of the cells in the spatial hash
    """
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        # Buckets of sprites per cell
        self.contents: Dict[IPoint, Set["Sprite"]] = {}
        # All the buckets a sprite is in.
        # This is used to remove a sprite from the spatial hash.
        self.buckets_for_sprite: Dict["Sprite", List[Set["Sprite"]]] = {}

    def _hash(self, point: IPoint) -> IPoint:
        """Convert world coordinates to cell coordinates"""
        return (
            point[0] // self.cell_size,
            point[1] // self.cell_size,
        )

    def reset(self):
        """Clear the spatial hash"""
        self.contents.clear()
        self.buckets_for_sprite.clear()

    def insert_object_for_box(self, sprite: "Sprite"):
        """
        Insert a sprite.
        """
        # Get the corners
        min_x = int(sprite.left)
        max_x = int(sprite.right)
        min_y = int(sprite.bottom)
        max_y = int(sprite.top)

        # print(f"New - Center: ({new_object.center_x}, {new_object.center_y}), Angle: {new_object.angle}, "
        #       f"Left: {new_object.left}, Right {new_object.right}")

        min_point = min_x, min_y
        max_point = max_x, max_y

        # print(f"Add 1: {min_point} {max_point}")

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print(f"Add 2: {min_point} {max_point}")
        # print("Add: ", min_point, max_point)

        buckets: List[Set["Sprite"]] = []

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

    def move(self, sprite: "Sprite"):
        """Update the sprite's position in the spatial hash."""
        # Calculate the new buckets
        # Compare to the old buckets
        # Update state
        pass

    def remove_object(self, sprite: "Sprite"):
        """
        Remove a Sprite.

        :param Sprite sprite: The sprite to remove
        """
        # Remove the sprite from all the buckets it is in
        for bucket in self.buckets_for_sprite[sprite]:
            bucket.remove(sprite)

        # Delete the sprite from the bucket tracker
        del self.buckets_for_sprite[sprite]

    def get_objects_for_box(self, sprite: "Sprite") -> Set["Sprite"]:
        """
        Returns colliding Sprites.

        :param Sprite check_object: Sprite we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List
        """
        # Get the corners
        min_x = int(sprite.left)
        max_x = int(sprite.right)
        min_y = int(sprite.bottom)
        max_y = int(sprite.top)

        min_point = min_x, min_y
        max_point = max_x, max_y

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)
        close_by_sprites: Set["Sprite"] = set()

        # Iterate over the all the covered cells and collect the sprites
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = self.contents.setdefault((i, j), set())
                close_by_sprites.update(bucket)

        return close_by_sprites

    def get_objects_for_point(self, point: IPoint) -> Set["Sprite"]:
        """
        Returns Sprites at or close to a point.

        :param IPoint point: Point we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List
        """
        hash_point = self._hash(point)
        close_by_sprites: Set["Sprite"] = set()

        new_items = self.contents.setdefault(hash_point, set())
        close_by_sprites.update(new_items)

        return close_by_sprites

    @property
    def count(self) -> int:
        """Return the number of sprites in the spatial hash"""
        # NOTE: We should really implement __len__ but this means
        # changing the truthiness of the class instance.
        # if spatial_hash will be False if it is empty.
        # For backwards compatibility, we'll keep it as a property.
        return len(self.buckets_for_sprite)
