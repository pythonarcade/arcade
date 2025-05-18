import pyglet

from arcade.context import ArcadeContext
from arcade.gl.context import Context, Info


class WebGLContext(Context):
    gl_api: str = "webgl"

    def __init__(
            self, window: pyglet.window.Window, gl_api: str = "webgl"
    ):
        super().__init__(window)

        if gl_api != "webgl":
            raise ValueError("Tried to create a WebGLContext with an incompatible api selected.")
        
        self.gl_api = gl_api


class WebGLArcadeContext(ArcadeContext, WebGLContext):
    def __init__(self, *args, **kwargs):
        WebGLContext.__init__(self, *args, **kwargs)
        ArcadeContext.__init__(self, *args, **kwargs)


class WebGLInfo(Info):
    def __init__(self, ctx):
        super().__init__(ctx)