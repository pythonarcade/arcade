from __future__ import annotations

from PIL.Image import Image
from arcade.types import PointList
from .base import HitBoxAlgorithm


class BoundingHitBoxAlgorithm(HitBoxAlgorithm):
    """
    A simple hit box algorithm that returns a hit box around the entire image.
    """
    cache = False

    def calculate(self, image: Image, **kwargs) -> PointList:
        """
        Given an RGBA image, this returns points that make up a hit box around it
        without any attempt to trim out transparent pixels.

        :param Image image: Image get hit box from.

        :Returns: List of points
        """
        size = image.size
        return (
            (-size[0] / 2, -size[1] / 2),
            (size[0] / 2, -size[1] / 2),
            (size[0] / 2, size[1] / 2),
            (-size[0] / 2, size[1] / 2),
        )
