from ctypes import byref, pointer
import weakref

from pyglet import gl


class Query:

    __slots__ = (
        'ctx',
        '_glo_samples_passed', '_glo_any_samples_passed', '_glo_time_elapsed', '_glo_primitives_generated',
        '__weakref__')

    def __init__(self, ctx):
        # TODO: Support querying a subset of these queries (faster)
        # TODO: Evalute of this query should be included
        # gl.GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN
        # gl.GL_ANY_SAMPLES_PASSED

        self.ctx = ctx

        self._glo_samples_passed = glo_samples_passed = gl.GLuint()
        gl.glGenQueries(1, self._glo_samples_passed)

        self._glo_time_elapsed = glo_time_elapsed = gl.GLuint()
        gl.glGenQueries(1, self._glo_time_elapsed)

        self._glo_primitives_generated = glo_time_elapsed = gl.GLuint()
        gl.glGenQueries(1, self._glo_primitives_generated)

        glos = [glo_samples_passed, glo_time_elapsed, glo_time_elapsed]
        weakref.finalize(self, Query.release, self.ctx, glos)

    @property
    def samples_passed(self) -> int:
        """How many samples was written. These are per component (RGBA)"""
        value = gl.GLint()
        gl.glGetQueryObjectiv(self._glo_samples_passed, gl.GL_QUERY_RESULT, value)
        return value.value

    @property
    def time_elapsed(self) -> int:
        """The time elapsed in nanoseconds."""
        value = gl.GLint()
        gl.glGetQueryObjectiv(self._glo_time_elapsed, gl.GL_QUERY_RESULT, value)
        return value.value

    @property
    def primitives_generated(self) -> int:
        """How many primitives a vertex shader or geometry shader generated"""
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
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        for glo in glos:
            gl.glDeleteQueries(1, glo)
