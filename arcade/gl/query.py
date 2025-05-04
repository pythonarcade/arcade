from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.gl import Context


class Query(ABC):
    """
    A query object to perform low level measurements of OpenGL rendering calls.

    The best way to create a program instance is through :py:meth:`arcade.gl.Context.query`

    Example usage::

        query = ctx.query()
        with query:
            geometry.render(..)

        print('samples_passed:', query.samples_passed)
        print('time_elapsed:', query.time_elapsed)
        print('primitives_generated:', query.primitives_generated)

    Args:
        ctx:
            The context this query object belongs to
        samples:
            Enable counting written samples
        time:
            Enable measuring time elapsed
        primitives:
            Enable counting primitives
    """

    __slots__ = (
        "_ctx",
        "__weakref__",
        "_samples_enabled",
        "_time_enabled",
        "_primitives_enabled",
        "_samples",
        "_time",
        "_primitives",
    )

    def __init__(self, ctx: Context, samples=True, time=True, primitives=True):
        # TODO: Support querying a subset of these queries (faster)
        # TODO: Evaluate of this query should be included
        # gl.GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN
        # gl.GL_ANY_SAMPLES_PASSED
        self._ctx = ctx

        self._samples_enabled = samples
        self._time_enabled = time
        self._primitives_enabled = primitives

        self._samples = 0
        self._time = 0
        self._primitives = 0

        self.ctx.stats.incr("query")

    def __del__(self):
        if self._ctx.gc_mode == "context_gc":
            self._ctx.objects.append(self)

    @property
    def ctx(self) -> Context:
        """The context this query object belongs to"""
        return self._ctx

    @property
    def samples_passed(self) -> int:
        """
        How many samples was written. These are per component (RGBA)

        If one RGBA pixel is written, this will be 4.
        """
        return self._samples

    @property
    def time_elapsed(self) -> int:
        """The time elapsed in nanoseconds"""
        return self._time

    @property
    def primitives_generated(self) -> int:
        """
        How many primitives a vertex or geometry shader processed.

        When using a geometry shader this only counts
        the primitives actually emitted.
        """
        return self._primitives

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")
