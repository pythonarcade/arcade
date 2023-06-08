from PIL.Image import Image
from arcade.types import PointList
from .base import HitBoxAlgorithm


class BoundingHitBoxAlgorithm(HitBoxAlgorithm):
    """
    A simple hit box algorithm that returns a hit box around the entire image.
    """
    name = "bounding_box"
    cache = False

    def calculate(self, image: Image, **kwargs) -> PointList:
        """
        Given an RGBA image, this returns points that make up a hit box around it
        without any attempt to trim out transparent pixels.

        :param Image image: Image get hit box from.

        :Returns: List of points
        """
        return self.create_bounding_box(image)
