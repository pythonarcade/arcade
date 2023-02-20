from typing import (
    List,
    Set,
    Dict,
    Any,
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
        # Cells and their sprite contents
        self.contents: Dict[IPoint, List["Sprite"]] = {}
        # Sprites and their buckets
        self.buckets_for_sprite: Dict["Sprite", List[IPoint]] = {}

    def _hash(self, point: IPoint) -> IPoint:
        """Convert world coordinates to cell coordinates"""
        return (
            point[0] // self.cell_size,
            point[1] // self.cell_size,
        )

    def clear(self):
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

        min_point = (min_x, min_y)
        max_point = (max_x, max_y)

        # print(f"Add 1: {min_point} {max_point}")

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        # print(f"Add 2: {min_point} {max_point}")
        # print("Add: ", min_point, max_point)

        buckets: List[IPoint] = []

        # Iterate each intersection cell adding the sprites to the cells
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                bucket = (i, j)
                sprites_in_bucket = self.contents.setdefault(bucket, [])
                sprites_in_bucket.append(sprite)
                buckets.append(bucket)

        self.buckets_for_sprite[sprite] = buckets

    def remove_object(self, sprite: "Sprite"):
        """
        Remove a Sprite.

        :param Sprite sprite: The sprite to remove
        """
        for bucket in self.buckets_for_sprite[sprite]:
            bucket.remove(sprite)

    def get_objects_for_box(self, check_object: "Sprite") -> Set["Sprite"]:
        """
        Returns colliding Sprites.

        :param Sprite check_object: Sprite we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List
        """
        # Get the corners
        min_x = int(check_object.left)
        max_x = int(check_object.right)
        min_y = int(check_object.bottom)
        max_y = int(check_object.top)

        min_point = min_x, min_y
        max_point = max_x, max_y

        # hash the minimum and maximum points
        min_point, max_point = self._hash(min_point), self._hash(max_point)

        close_by_sprites: List["Sprite"] = []
        # iterate over the rectangular region
        for i in range(min_point[0], max_point[0] + 1):
            for j in range(min_point[1], max_point[1] + 1):
                # print(f"Checking {i}, {j}")
                # append to each intersecting cell
                new_items = self.contents.setdefault((i, j), [])
                # for item in new_items:
                #     print(f"Found {item.guid} in {i}, {j}")
                close_by_sprites.extend(new_items)

        return set(close_by_sprites)

    def get_objects_for_point(self, point: IPoint) -> List["Sprite"]:
        """
        Returns Sprites at or close to a point.

        :param IPoint point: Point we are checking to see if there are
            other sprites in the same box(es)

        :return: List of close-by sprites
        :rtype: List
        """
        hash_point = self._hash(point)

        close_by_sprites: List["Sprite"] = []
        new_items = self.contents.setdefault(hash_point, [])
        close_by_sprites.extend(new_items)

        return close_by_sprites

    def __len__(self) -> int:
        return len(self.buckets_for_sprite)
