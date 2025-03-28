from PIL.Image import Image

from arcade.types import Point2List

from .base import HitBoxAlgorithm


class BoundingHitBoxAlgorithm(HitBoxAlgorithm):
    """
    A simple hit box algorithm that returns a hit box around the entire image.
    """

    cache = False

    def calculate(self, image: Image, **kwargs) -> Point2List:
        """
        Given an RGBA image, this returns points that make up a hit box around it
        without any attempt to trim out transparent pixels.

        Args:
            image: Image get hit box from.
        """
        return self.create_bounding_box(image)
