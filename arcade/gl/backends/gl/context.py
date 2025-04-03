from arcade.gl.context import Context
from arcade.context import ArcadeContext


import pyglet

from arcade.types import BufferProtocol

from .buffer import GLBuffer

class GLContext(Context):
    def __init__(self, window: pyglet.window.Window, gc_mode: str = "context_gc", gl_api: str = "gl"):
        super().__init__(window, gc_mode, gl_api)

    def buffer(self, *, data: BufferProtocol | None = None, reserve: int = 0, usage: str = "static") -> GLBuffer:
        return GLBuffer(self, data, reserve=reserve, usage=usage)


class GLArcadeContext(ArcadeContext, GLContext):
    def __init__(self, *args, **kwargs):
        GLContext.__init__(self, *args, **kwargs)
        ArcadeContext.__init__(self, *args, **kwargs)