from typing import Dict
from PIL.Image import Image
from arcade import PointList
from .base import HitBoxAlgorithm
from .bounding_box import BoundingHitBoxAlgorithm
from .simple import SimpleHitBoxAlgorithm
from .pymunk import PymunkHitBoxAlgorithm

#: Registry for hit box algorithms.
algorithms: Dict[str, HitBoxAlgorithm] = {}
#: The default hit box algorithm.
default: HitBoxAlgorithm = SimpleHitBoxAlgorithm()
#: The detailed hit box algorithm.
detailed = PymunkHitBoxAlgorithm()
#: The simple hit box algorithm.
simple = SimpleHitBoxAlgorithm()
#: The bounding box hit box algorithm.
bounding_box = BoundingHitBoxAlgorithm()


def get_algorithm(name: str) -> HitBoxAlgorithm:
    """
    Returns a hit box algorithm by name.

    :param str name: Name of the algorithm.

    :Returns: Hit box algorithm
    """
    try:
        return algorithms[name.lower()]
    except KeyError:
        raise ValueError(f"Unknown hit box algorithm '{name}'")


def register_algorithm(algorithm: HitBoxAlgorithm):
    """
    Registers a hit box algorithm.

    :param HitBoxAlgorithm algorithm: Algorithm to register.
    """
    algorithms[algorithm.name.lower()] = algorithm


# Register algorithms
register_algorithm(BoundingHitBoxAlgorithm())
register_algorithm(SimpleHitBoxAlgorithm())
register_algorithm(PymunkHitBoxAlgorithm())


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
    return get_algorithm("pymunk").calculate(image, hit_box_detail=hit_box_detail)
