from typing import Tuple

import pyglet

from arcade.context import ArcadeContext
from arcade.gl.context import Context, Info

from arcade.gl import enums

import pyglet.graphics.api
from pyglet.graphics.api.webgl.webgl_js import WebGL2RenderingContext


class WebGLContext(Context):
    gl_api: str = "webgl"

    def __init__(
            self, window: pyglet.window.Window, gl_api: str = "webgl"
    ):
        super().__init__(window)

        if gl_api != "webgl":
            raise ValueError("Tried to create a WebGLContext with an incompatible api selected.")
        
        self.gl_api = gl_api
        self._gl: WebGL2RenderingContext = pyglet.graphics.api.core.current_context.gl

        self._gl.enable(enums.SCISSOR_TEST)

    @Context.extensions.getter
    def extensions(self) -> set[str]:
        return self.window.context.get_info().extensions  # type: ignore

    @property
    def error(self) -> str | None:
        err = self._gl.getError()
        if err == enums.NO_ERROR:
            return None
        
        return self._errors.get(err, "UNKNOWN_ERROR")
    
    def enable(self, *flags, int):
        self._flags.update(flags)

        for flag in flags:
            self._gl.enable(flag)

    def enable_only(self, *args: int):
        self._flags = set(args)

        if self.BLEND in self._flags:
            self._gl.enable(self.BLEND)
        else:
            self._gl.disable(self.BLEND)

        if self.DEPTH_TEST in self._flags:
            self._gl.enable(self.DEPTH_TEST)
        else:
            self._gl.disable(self.DEPTH_TEST)

        if self.CULL_FACE in self._flags:
            self._gl.enable(self.CULL_FACE)
        else:
            self._gl.disable(self.CULL_FACE)

    def disable(self, *args):
        self._flags -= set(args)

        for flag in args:
            self._gl.disable(flag)

    @Context.blend_func.setter
    def blend_func(self, value: Tuple[int, int] | Tuple[int, int, int, int]):
        self._blend_func = value
        if len(value) == 2:
            self._gl.blendFunc(*value)
        elif len(value) == 4:
            self._gl.blendFuncSeparate(*value)
        else:
            ValueError("blend_func takes a tuple of 2 or 4 values")

    @property
    def front_face(self) -> str:
        value = self._gl.getParameter(enums.FRONT_FACE)
        return "cw" if value == enums.CW else "ccw"
    
    @front_face.setter
    def front_face(self, value: str):
        if value not in ["cw", "ccw"]:
            raise ValueError("front_face must be 'cw' or 'ccw'")
        self._gl.frontFace(enums.CW if value == "cw" else enums.CCW)

    @property
    def cull_face(self) -> str:
        value = self._gl.getParameter(enums.CULL_FACE_MODE)
        return self._cull_face_options_reverse[value]
    
    @cull_face.setter
    def cull_face(self, value):
        if value not in self._cull_face_options:
            raise ValueError("cull_face must be", list(self._cull_face_options.keys()))

        self._gl.cullFace(self._cull_face_options[value])

    @Context.wireframe.setter
    def wireframe(self, value: bool):
        raise NotImplementedError("wireframe is not supported with WebGL")

    @property
    def patch_vertices(self) -> int:
        raise NotImplementedError("patch_vertices is not supported with WebGL")

    @patch_vertices.setter
    def patch_vertices(self, value: int):
        raise NotImplementedError("patch_vertices is not supported with WebGL")

    @Context.point_size.setter
    def point_size(self, value: float):
        raise NotImplementedError("point_size is not supported with WebGL")
    
    @Context.primitive_restart_index.setter
    def primitive_restart_index(self, value: int):
        raise NotImplementedError("primitive_restart_index is not supported with WebGL")

    def finish(self) -> None:
        self._gl.finish()

    def flush(self) -> None:
        self._gl.flush()

    def _create_default_framebuffer(self):
        raise NotImplementedError("Not done yet")


class WebGLArcadeContext(ArcadeContext, WebGLContext):
    def __init__(self, *args, **kwargs):
        WebGLContext.__init__(self, *args, **kwargs)
        ArcadeContext.__init__(self, *args, **kwargs)


class WebGLInfo(Info):
    def __init__(self, ctx):
        super().__init__(ctx)