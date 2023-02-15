from typing import Any
from PIL.Image import Image
from arcade import PointList


class HitBoxAlgorithm:
    """
    Base class for hit box algorithms. Hit box algorithms are used to calculate the
    points that make up a hit box for a sprite.
    """
    #: The name of the algorithm
    name = "base"
    #: Should points for this algorithm be cached?
    cache = True

    @property
    def param_str(self) -> str:
        """
        Return a string representation of the parameters used to create this algorithm.

        This is used in caching.
        """
        return ""

    def calculate(self, image: Image, **kwargs) -> PointList:
        raise NotImplementedError

    def __call__(self, *args: Any, **kwds: Any) -> "HitBoxAlgorithm":
        return self.__class__(*args, **kwds)
