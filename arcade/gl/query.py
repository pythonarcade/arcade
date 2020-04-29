from pyglet import gl


class Query:

    __slots__ = '__weakref__'

    def __init__(self, samples=False, any_samples=False, time=False, primitives=False):
        gl.glGenQueries
        gl.GL_TIME_ELAPSED
        gl.GL_SAMPLES_PASSED
        gl.GL_ANY_SAMPLES_PASSED
        gl.GL_PRIMITIVES_GENERATED
        gl.GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN

    def __enter__(self):
        # TODO: Begin query
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: End query
        pass

    @staticmethod
    def release(ctx, glo):
        pass
