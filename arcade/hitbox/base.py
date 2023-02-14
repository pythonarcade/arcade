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

    def create_param_str(self, **kwargs) -> str:
        """
        Convert all the parameters for this algorithm into a string.
        This is used for texture and hit box caching. It's important
        that the parameter order is consistent.
        """
        return ""

    def calculate(self, image: Image, **kwargs) -> PointList:
        raise NotImplementedError

    def __call__(self, *args: Any, **kwds: Any) -> "HitBoxAlgorithm":
        return self.__class__(*args, **kwds)
