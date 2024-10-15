from __future__ import annotations

from PIL.Image import Image

from arcade.types import Point2List

from arcade.hitbox.base import HitBoxAlgorithm

from .dud import DudImplimentationError


class PymunkHitBoxAlgorithm(HitBoxAlgorithm):
    """
    Hit box point algorithm that uses pymunk to calculate the points.

    This is a more accurate algorithm generating more points. The
    point count can be controlled with the ``detail`` parameter.
    """

    #: The default detail when creating a new instance.
    default_detail = 4.5

    def __init__(self, *, detail: float | None = None):
        super().__init__()

    def __call__(self, *, detail: float | None = None) -> "PymunkHitBoxAlgorithm":
        """Create a new instance with new default values"""
        raise DudImplimentationError

    def calculate(self, image: Image, detail: float | None = None, **kwargs) -> Point2List:
        """
        Given an RGBA image, this returns points that make up a hit box around it.

        Args:
            image: Image get hit box from.
            detail: How detailed to make the hit box. There's a
                trade-off in number of points vs. accuracy.
        """
        raise DudImplimentationError

    def to_points_list(self, image: Image, line_set) -> Point2List:
        """
        Convert a line set to a list of points.

        Coordinates are offset so ``(0,0)`` is the center of the image.

        Args:
            image: Image to trace.
            line_set: Line set to convert.
        """
        raise DudImplimentationError

    def trace_image(self, image: Image):
        """
        Trace the image and return a :py:class:~collections.abc.Sequence` of line sets.

        .. important:: The image :py:attr:`~PIL.Image.Image.mode` must be ``"RGBA"``!

                       * This method raises a :py:class:`TypeError` when it isn't
                       * Use :py:meth:`convert("RGBA") <PIL.Image.Image.convert>` to
                         convert

        The returned object will be a :py:mod:`pymunk`
        :py:class:`~pymunk.autogeometry.PolylineSet`. Each
        :py:class:`list` inside it will contain points as
        :py:class:`pymunk.vec2d.Vec2d` instances. These lists
        may represent:

        * the outline of the image's contents
        * the holes in the image

        When this method returns more than one line set,
        it's important to pick the one which covers the largest
        portion of the image.

        Args:
            image: A :py:class:`PIL.Image.Image` to trace.

        Returns:
            A :py:mod:`pymunk` object which is a :py:class:`~collections.abc.Sequence`
            of :py:class:`~pymunk.autogeometry.PolylineSet` of line sets.
        """
        raise DudImplimentationError

    def select_largest_line_set(self, line_sets):
        """
        Given a list of line sets, return the one that covers the most of the image.

        Args:
            line_sets: List of line sets.
        """
        raise DudImplimentationError
