from typing import Dict, Type
from PIL.Image import Image
from arcade import PointList
from .base import HitBoxAlgorithm
from .bounding import BoundingHitBoxAlgorithm
from .simple import SimpleHitBoxAlgorithm
from .detailed import DetailedHitBoxAlgorithm

#: Registry for hit box algorithms.
algorithms: Dict[str, Type[HitBoxAlgorithm]] = {}
#: The default hit box algorithm.
default_algorithm: Type[HitBoxAlgorithm] = SimpleHitBoxAlgorithm


def get_algorithm(name: str) -> Type[HitBoxAlgorithm]:
    """
    Returns a hit box algorithm by name.

    :param str name: Name of the algorithm.

    :Returns: Hit box algorithm
    """
    try:
        return algorithms[name.lower()]
    except KeyError:
        raise ValueError(f"Unknown hit box algorithm '{name}'")


def register_algorithm(algorithm: Type[HitBoxAlgorithm]):
    """
    Registers a hit box algorithm.

    :param HitBoxAlgorithm algorithm: Algorithm to register.
    """
    algorithms[algorithm.name.lower()] = algorithm


# Register algorithms
register_algorithm(BoundingHitBoxAlgorithm)
register_algorithm(SimpleHitBoxAlgorithm)
register_algorithm(DetailedHitBoxAlgorithm)


# Temporary functions for backwards compatibility
def calculate_hit_box_points_simple(image: Image, *args) -> PointList:
    """
    Given an RGBA image, this returns points that make up a hit box around it. Attempts
    to trim out transparent pixels.

    :param Image image: Image get hit box from.

    :Returns: List of points
    """
    return get_algorithm("simple").calculate(image)


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
    return get_algorithm("detailed").calculate(image, hit_box_detail=hit_box_detail)
