from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from pyglet import gl

from arcade.gl.query import Query

if TYPE_CHECKING:
    from arcade.gl import Context


class OpenGLQuery(Query):
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
        "_glo_samples_passed",
        "_glo_time_elapsed",
        "_glo_primitives_generated",
    )

    def __init__(self, ctx: Context, samples=True, time=True, primitives=True):
        super().__init__(ctx, samples, time, primitives)

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

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, OpenGLQuery.delete_glo, self._ctx, glos)

    def __enter__(self):
        if self._ctx.gl_api == "opengl":
            if self._samples_enabled:
                gl.glBeginQuery(gl.GL_SAMPLES_PASSED, self._glo_samples_passed)
            if self._time_enabled:
                gl.glBeginQuery(gl.GL_TIME_ELAPSED, self._glo_time_elapsed)
        if self._primitives_enabled:
            gl.glBeginQuery(gl.GL_PRIMITIVES_GENERATED, self._glo_primitives_generated)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._ctx.gl_api == "opengl":
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
        OpenGLQuery.delete_glo(
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
