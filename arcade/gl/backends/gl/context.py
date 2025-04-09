from typing import List, Dict, Iterable, Sequence, Tuple

from arcade.gl.context import Context
from arcade.context import ArcadeContext

import pyglet
from pyglet import gl

from arcade.types import BufferProtocol

from .types import PyGLenum

from .buffer import GLBuffer
from .compute_shader import GLComputeShader
from .framebuffer import GLFramebuffer, GLDefaultFrameBuffer
from .glsl import ShaderSource
from .types import BufferDescription
from .program import GLProgram
from .sampler import GLSampler
from .texture import GLTexture2D
from .vertex_array import GLGeometry


class GLContext(Context):
    def __init__(self, window: pyglet.window.Window, gc_mode: str = "context_gc", gl_api: str = "gl"):
        super().__init__(window, gc_mode, gl_api)

    def _create_default_framebuffer(self) -> GLDefaultFrameBuffer:
        return GLDefaultFrameBuffer(self)

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
        source_vs = ShaderSource(self, vertex_shader, common, gl.GL_VERTEX_SHADER)
        source_fs = (
            ShaderSource(self, fragment_shader, common, gl.GL_FRAGMENT_SHADER)
            if fragment_shader
            else None
        )
        source_geo = (
            ShaderSource(self, geometry_shader, common, gl.GL_GEOMETRY_SHADER)
            if geometry_shader
            else None
        )
        source_tc = (
            ShaderSource(self, tess_control_shader, common, gl.GL_TESS_CONTROL_SHADER)
            if tess_control_shader
            else None
        )
        source_te = (
            ShaderSource(self, tess_evaluation_shader, common, gl.GL_TESS_EVALUATION_SHADER)
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

    def compute_shader(self, *, source: str, common: Iterable[str] = ()) -> GLComputeShader:
        src = ShaderSource(self, source, common, pyglet.gl.GL_COMPUTE_SHADER)
        return GLComputeShader(self, src.get_source())

    def texture(
        self,
        size: Tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        wrap_x: PyGLenum | None = None,
        wrap_y: PyGLenum | None = None,
        filter: Tuple[PyGLenum, PyGLenum] | None = None,
        samples: int = 0,
        immutable: bool = False,
        internal_format: PyGLenum | None = None,
        compressed: bool = False,
        compressed_data: bool = False,
    ) -> GLTexture2D:
        compressed = compressed or compressed_data

        return GLTexture2D(
            self,
            size,
            components=components,
            data=data,
            dtype=dtype,
            wrap_x=wrap_x,
            wrap_y=wrap_y,
            filter=filter,
            samples=samples,
            immutable=immutable,
            internal_format=internal_format,
            compressed=compressed,
            compressed_data=compressed_data,
        )

    def depth_texture(
            self, size: Tuple[int, int], *, data: BufferProtocol | None = None
    ) -> GLTexture2D:
        return GLTexture2D(self, size, data=data, depth=True)

    def framebuffer(
        self,
        *,
        color_attachments: GLTexture2D | List[GLTexture2D] | None = None,
        depth_attachment: GLTexture2D | None = None,
    ) -> GLFramebuffer:
        return GLFramebuffer(
            self, color_attachments=color_attachments or [], depth_attachment=depth_attachment
        )

    def copy_framebuffer(
        self,
        src: GLFramebuffer,
        dst: GLFramebuffer,
        src_attachment_index: int = 0,
        depth: bool = True,
    ):
        # Set source and dest framebuffer
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, src.glo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, dst.glo)

        # TODO: We can support blitting multiple layers here
        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0 + src_attachment_index)
        if dst.is_default:
            gl.glDrawBuffer(gl.GL_BACK)
        else:
            gl.glDrawBuffer(gl.GL_COLOR_ATTACHMENT0)

        # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, src._glo)
        gl.glBlitFramebuffer(
            0,
            0,
            src.width,
            src.height,  # Make source and dest size the same
            0,
            0,
            src.width,
            src.height,
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT,
            gl.GL_NEAREST,
        )

        # Reset states. We can also apply previous states here
        gl.glReadBuffer(gl.GL_COLOR_ATTACHMENT0)

    def sampler(self, texture: GLTexture2D) -> GLSampler:
        """
        Create a sampler object for a texture.

        Args:
            texture:
                The texture to create a sampler for
        """
        return GLSampler(self, texture)

class GLArcadeContext(ArcadeContext, GLContext):
    def __init__(self, *args, **kwargs):
        GLContext.__init__(self, *args, **kwargs)
        ArcadeContext.__init__(self, *args, **kwargs)