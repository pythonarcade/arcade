from arcade.gl.provider import BaseProvider

from .context import WebGLArcadeContext, WebGLContext, WebGLInfo


class Provider(BaseProvider):
    def create_context(self, *args, **kwargs):
        return WebGLContext(*args, **kwargs)

    def create_info(self, ctx):
        return WebGLInfo(ctx)  # type: ignore

    def create_arcade_context(self, *args, **kwargs):
        return WebGLArcadeContext(*args, **kwargs)
