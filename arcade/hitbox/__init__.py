from PIL.Image import Image
from arcade.types import PointList
from .base import HitBoxAlgorithm
from .bounding_box import BoundingHitBoxAlgorithm
from .simple import SimpleHitBoxAlgorithm
from .pymunk import PymunkHitBoxAlgorithm

#: The simple hit box algorithm.
algo_simple = SimpleHitBoxAlgorithm()
#: The detailed hit box algorithm.
algo_detailed = PymunkHitBoxAlgorithm()
#: The bounding box hit box algorithm.
algo_bounding_box = BoundingHitBoxAlgorithm()
#: The default hit box algorithm.
algo_default = algo_simple


# Temporary functions for backwards compatibility
def calculate_hit_box_points_simple(image: Image, *args) -> PointList:
    """
    Given an RGBA image, this returns points that make up a hit box around it. Attempts
    to trim out transparent pixels.

    :param Image image: Image get hit box from.

    :Returns: List of points
    """
    return algo_simple.calculate(image)


def calculate_hit_box_points_detailed(
    image: Image,
    hit_box_detail: float = 4.5,
) -> PointList:
    """
    Given an RGBA image, this returns points that make up a hit box around it. Attempts
    to trim out transparent pixels.

    :param Image image: Image get hit box from.
    :param int hit_box_detail: How detailed to make the hit box. There's a
                               trade-off in number of points vs. accuracy.

    :Returns: List of points
    """
    return algo_detailed.calculate(image, detail=hit_box_detail)


__all__ = [
    "HitBoxAlgorithm",
    "SimpleHitBoxAlgorithm",
    "PymunkHitBoxAlgorithm",
    "BoundingHitBoxAlgorithm",
    "algo_simple",
    "algo_detailed",
    "algo_bounding_box",
    "algo_default",
    "calculate_hit_box_points_simple",
    "calculate_hit_box_points_detailed",
]
