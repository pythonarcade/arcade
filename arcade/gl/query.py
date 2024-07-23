from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from pyglet import gl

if TYPE_CHECKING:
    from arcade.gl import Context


class Query:
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
        "_glo_samples_passed",
        "_glo_time_elapsed",
        "_glo_primitives_generated",
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

        glos = []

        self._glo_samples_passed = glo_samples_passed = gl.GLuint()
        if self._samples_enabled:
            gl.glGenQueries(1, self._glo_samples_passed)
            glos.append(glo_samples_passed)

        self._glo_time_elapsed = glo_time_elapsed = gl.GLuint()
        if self._time_enabled:
            gl.glGenQueries(1, self._glo_time_elapsed)
            glos.append(glo_time_elapsed)

        self._glo_primitives_generated = glo_primitives_generated = gl.GLuint()
        if self._primitives_enabled:
            gl.glGenQueries(1, self._glo_primitives_generated)
            glos.append(glo_primitives_generated)

        self.ctx.stats.incr("query")

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, Query.delete_glo, self._ctx, glos)

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

    def __enter__(self):
        if self._ctx.gl_api == "gl":
            if self._samples_enabled:
                gl.glBeginQuery(gl.GL_SAMPLES_PASSED, self._glo_samples_passed)
            if self._time_enabled:
                gl.glBeginQuery(gl.GL_TIME_ELAPSED, self._glo_time_elapsed)
        if self._primitives_enabled:
            gl.glBeginQuery(gl.GL_PRIMITIVES_GENERATED, self._glo_primitives_generated)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._ctx.gl_api == "gl":
            if self._samples_enabled:
                gl.glEndQuery(gl.GL_SAMPLES_PASSED)
                value = gl.GLint()
                gl.glGetQueryObjectiv(self._glo_samples_passed, gl.GL_QUERY_RESULT, value)
                self._samples = value.value

            if self._time_enabled:
                gl.glEndQuery(gl.GL_TIME_ELAPSED)
                value = gl.GLint()
                gl.glGetQueryObjectiv(self._glo_time_elapsed, gl.GL_QUERY_RESULT, value)
                self._time = value.value

        if self._primitives_enabled:
            gl.glEndQuery(gl.GL_PRIMITIVES_GENERATED)
            value = gl.GLint()
            gl.glGetQueryObjectiv(self._glo_primitives_generated, gl.GL_QUERY_RESULT, value)
            self._primitives = value.value

    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        Query.delete_glo(
            self._ctx,
            [
                self._glo_samples_passed,
                self._glo_time_elapsed,
                self._glo_primitives_generated,
            ],
        )

    @staticmethod
    def delete_glo(ctx, glos) -> None:
        """
        Delete this query object.

        This is automatically called when the object is garbage collected.
        """
        if gl.current_context is None:
            return

        for glo in glos:
            gl.glDeleteQueries(1, glo)

        ctx.stats.decr("query")
