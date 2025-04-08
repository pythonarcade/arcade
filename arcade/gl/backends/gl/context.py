from typing import List, Dict, Sequence

from arcade.gl.context import Context
from arcade.context import ArcadeContext

import pyglet

from arcade.types import BufferProtocol

from .buffer import GLBuffer
from .glsl import ShaderSource
from .types import BufferDescription
from .program import GLProgram
from .vertex_array import GLGeometry

class GLContext(Context):
    def __init__(self, window: pyglet.window.Window, gc_mode: str = "context_gc", gl_api: str = "gl"):
        super().__init__(window, gc_mode, gl_api)

    def buffer(self, *, data: BufferProtocol | None = None, reserve: int = 0, usage: str = "static") -> GLBuffer:
        return GLBuffer(self, data, reserve=reserve, usage=usage)

    def program(
            self,
            *,
            vertex_shader: str,
            fragment_shader: str | None = None,
            geometry_shader: str | None = None,
            tess_control_shader: str | None = None,
            tess_evaluation_shader: str | None = None,
            common: List[str] | None = None,
            defines: Dict[str, str] | None = None,
            varyings: Sequence[str] | None = None,
            varyings_capture_mode: str = "interleaved",
    ) -> GLProgram:
        source_vs = ShaderSource(self, vertex_shader, common, pyglet.gl.GL_VERTEX_SHADER)
        source_fs = (
            ShaderSource(self, fragment_shader, common, pyglet.gl.GL_FRAGMENT_SHADER)
            if fragment_shader
            else None
        )
        source_geo = (
            ShaderSource(self, geometry_shader, common, pyglet.gl.GL_GEOMETRY_SHADER)
            if geometry_shader
            else None
        )
        source_tc = (
            ShaderSource(self, tess_control_shader, common, pyglet.gl.GL_TESS_CONTROL_SHADER)
            if tess_control_shader
            else None
        )
        source_te = (
            ShaderSource(self, tess_evaluation_shader, common, pyglet.gl.GL_TESS_EVALUATION_SHADER)
            if tess_evaluation_shader
            else None
        )

        # If we don't have a fragment shader we are doing transform feedback.
        # When a geometry shader is present the out attributes will be located there
        out_attributes = list(varyings) if varyings is not None else []  # type: List[str]
        if not source_fs and not out_attributes:
            if source_geo:
                out_attributes = source_geo.out_attributes
            else:
                out_attributes = source_vs.out_attributes

        return GLProgram(
            self,
            vertex_shader=source_vs.get_source(defines=defines),
            fragment_shader=source_fs.get_source(defines=defines) if source_fs else None,
            geometry_shader=source_geo.get_source(defines=defines) if source_geo else None,
            tess_control_shader=source_tc.get_source(defines=defines) if source_tc else None,
            tess_evaluation_shader=source_te.get_source(defines=defines) if source_te else None,
            varyings=out_attributes,
            varyings_capture_mode=varyings_capture_mode,
        )

    def geometry(
        self,
        content: Sequence[BufferDescription] | None = None,
        index_buffer: GLBuffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ):
        return GLGeometry(
            self,
            content,
            index_buffer=index_buffer,
            mode=mode,
            index_element_size=index_element_size,
        )


class GLArcadeContext(ArcadeContext, GLContext):
    def __init__(self, *args, **kwargs):
        GLContext.__init__(self, *args, **kwargs)
        ArcadeContext.__init__(self, *args, **kwargs)