from arcade.gl.provider import BaseProvider

from .context import OpenGLArcadeContext, OpenGLContext, OpenGLInfo


class Provider(BaseProvider):
    def create_context(self, *args, **kwargs):
        return OpenGLContext(*args, **kwargs)

    def create_info(self, ctx):
        return OpenGLInfo(ctx)

    def create_arcade_context(self, *args, **kwargs):
        return OpenGLArcadeContext(*args, **kwargs)
