from PIL.Image import Image
from arcade import PointList


class HitBoxAlgorithm:
    """
    Base class for hit box algorithms. Hit box algorithms are used to calculate the
    points that make up a hit box for a sprite.
    """
    name = "base"

    @classmethod
    def calculate(cls, image: Image, **kwargs) -> PointList:
        raise NotImplementedError
