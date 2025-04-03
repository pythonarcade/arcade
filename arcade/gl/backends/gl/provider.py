from arcade.gl.provider import BaseProvider

from .context import GLContext, GLArcadeContext

class Provider(BaseProvider):
    def create_context(self, *args, **kwargs):
        return GLContext(*args, **kwargs)

    def create_arcade_context(self, *args, **kwargs):
        return GLArcadeContext(*args, **kwargs)