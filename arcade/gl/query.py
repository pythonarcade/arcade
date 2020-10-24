from typing import TYPE_CHECKING
from ctypes import byref, pointer
import weakref

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
    """

    __slots__ = (
        "_ctx",
        "_glo_samples_passed",
        "_glo_any_samples_passed",
        "_glo_time_elapsed",
        "_glo_primitives_generated",
        "__weakref__",
    )

    def __init__(self, ctx: "Context"):
        # TODO: Support querying a subset of these queries (faster)
        # TODO: Evalute of this query should be included
        # gl.GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN
        # gl.GL_ANY_SAMPLES_PASSED

        self._ctx = ctx

        self._glo_samples_passed = glo_samples_passed = gl.GLuint()
        gl.glGenQueries(1, self._glo_samples_passed)

        self._glo_time_elapsed = glo_time_elapsed = gl.GLuint()
        gl.glGenQueries(1, self._glo_time_elapsed)

        self._glo_primitives_generated = glo_time_elapsed = gl.GLuint()
        gl.glGenQueries(1, self._glo_primitives_generated)

        glos = [glo_samples_passed, glo_time_elapsed, glo_time_elapsed]
        weakref.finalize(self, Query.release, self._ctx, glos)

    @property
    def ctx(self) -> "Context":
        """
        The context this query object belongs to

        :type: :py:class:`arcade.gl.Context`
        """
        return self._ctx

    @property
    def samples_passed(self) -> int:
        """
        How many samples was written. These are per component (RGBA)
        
        :type: int
        """
        value = gl.GLint()
        gl.glGetQueryObjectiv(self._glo_samples_passed, gl.GL_QUERY_RESULT, value)
        return value.value

    @property
    def time_elapsed(self) -> int:
        """
        The time elapsed in nanoseconds
        
        :type: int
        """
        value = gl.GLint()
        gl.glGetQueryObjectiv(self._glo_time_elapsed, gl.GL_QUERY_RESULT, value)
        return value.value

    @property
    def primitives_generated(self) -> int:
        """
        How many primitives a vertex or geometry shader processed

        :type: int
        """
        value = gl.GLint()
        gl.glGetQueryObjectiv(self._glo_primitives_generated, gl.GL_QUERY_RESULT, value)
        return value.value

    def __enter__(self):
        gl.glBeginQuery(gl.GL_SAMPLES_PASSED, self._glo_samples_passed)
        gl.glBeginQuery(gl.GL_TIME_ELAPSED, self._glo_time_elapsed)
        gl.glBeginQuery(gl.GL_PRIMITIVES_GENERATED, self._glo_primitives_generated)

    def __exit__(self, exc_type, exc_val, exc_tb):
        gl.glEndQuery(gl.GL_SAMPLES_PASSED)
        gl.glEndQuery(gl.GL_TIME_ELAPSED)
        gl.glEndQuery(gl.GL_PRIMITIVES_GENERATED)

    @staticmethod
    def release(ctx, glos) -> None:
        """
        Delete this query object. This is automatically called
        when the object is garbage collected.
        """
        if gl.current_context is None:
            return

        for glo in glos:
            gl.glDeleteQueries(1, glo)
