from typing import TYPE_CHECKING, Dict, Iterable, List, Sequence, Tuple

import pyglet
import pyglet.graphics.api

from arcade.context import ArcadeContext
from arcade.gl import enums
from arcade.gl.context import Context, Info
from arcade.gl.types import BufferDescription
from arcade.types import BufferProtocol

from .buffer import WebGLBuffer
from .framebuffer import WebGLDefaultFrameBuffer, WebGLFramebuffer
from .glsl import ShaderSource
from .program import WebGLProgram
from .query import WebGLQuery
from .sampler import WebGLSampler
from .texture import WebGLTexture2D
from .texture_array import WebGLTextureArray
from .vertex_array import WebGLGeometry, WebGLVertexArray  # noqa: F401

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGL2RenderingContext


class WebGLContext(Context):
    gl_api: str = "webgl"

    def __init__(
        self,
        window: pyglet.window.Window,
        gc_mode: str = "context_gc",
        gl_api: str = "webgl",  # type: ignore
    ):
        if gl_api != "webgl":
            raise ValueError("Tried to create a WebGLContext with an incompatible api selected.")

        self.gl_api = gl_api
        self._gl: WebGL2RenderingContext = pyglet.graphics.api.core.current_context.gl

        anistropy_ext = self._gl.getExtension("EXT_texture_filter_anisotropic")
        texture_float_linear_ext = self._gl.getExtension("OES_texture_float_linear")

        unsupported_extensions = []
        if not anistropy_ext:
            unsupported_extensions.append("EXT_texture_filter_anisotropic")
        if not texture_float_linear_ext:
            unsupported_extensions.append("OES_texture_float_linear")

        if unsupported_extensions:
            raise RuntimeError(
                f"Tried to create a WebGL context with missing extensions: {unsupported_extensions}"
            )

        super().__init__(window, gc_mode, gl_api)

        self._gl.enable(enums.SCISSOR_TEST)

        self._build_uniform_setters()

    def _build_uniform_setters(self):
        self._uniform_setters = {
            # Integers
            enums.INT: (int, self._gl.uniform1i, 1, 1),
            enums.INT_VEC2: (int, self._gl.uniform2iv, 2, 1),
            enums.INT_VEC3: (int, self._gl.uniform3iv, 3, 1),
            enums.INT_VEC4: (int, self._gl.uniform4iv, 4, 1),
            # Unsigned Integers
            enums.UNSIGNED_INT: (int, self._gl.uniform1ui, 1, 1),
            enums.UNSIGNED_INT_VEC2: (int, self._gl.uniform2ui, 2, 1),
            enums.UNSIGNED_INT_VEC3: (int, self._gl.uniform3ui, 3, 1),
            enums.UNSIGNED_INT_VEC4: (int, self._gl.uniform4ui, 4, 1),
            # Bools
            enums.BOOL: (bool, self._gl.uniform1i, 1, 1),
            enums.BOOL_VEC2: (bool, self._gl.uniform2iv, 2, 1),
            enums.BOOL_VEC3: (bool, self._gl.uniform3iv, 3, 1),
            enums.BOOL_VEC4: (bool, self._gl.uniform4iv, 4, 1),
            # Floats
            enums.FLOAT: (float, self._gl.uniform1f, 1, 1),
            enums.FLOAT_VEC2: (float, self._gl.uniform2fv, 2, 1),
            enums.FLOAT_VEC3: (float, self._gl.uniform3fv, 3, 1),
            enums.FLOAT_VEC4: (float, self._gl.uniform4fv, 4, 1),
            # Matrices
            enums.FLOAT_MAT2: (float, self._gl.uniformMatrix2fv, 4, 1),
            enums.FLOAT_MAT3: (float, self._gl.uniformMatrix3fv, 9, 1),
            enums.FLOAT_MAT4: (float, self._gl.uniformMatrix4fv, 16, 1),
            # 2D Samplers
            enums.SAMPLER_2D: (int, self._gl.uniform1i, 1, 1),
            enums.INT_SAMPLER_2D: (int, self._gl.uniform1i, 1, 1),
            enums.UNSIGNED_INT_SAMPLER_2D: (int, self._gl.uniform1i, 1, 1),
            # Array
            enums.SAMPLER_2D_ARRAY: (
                int,
                self._gl.uniform1iv,
                self._gl.uniform1iv,
                1,
                1,
            ),
        }

    @Context.extensions.getter
    def extensions(self) -> set[str]:
        return self.window.context.get_info().extensions  # type: ignore

    @property
    def error(self) -> str | None:
        err = self._gl.getError()
        if err == enums.NO_ERROR:
            return None

        return self._errors.get(err, "UNKNOWN_ERROR")

    def enable(self, *flags: int):
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

    def _create_default_framebuffer(self) -> WebGLDefaultFrameBuffer:
        return WebGLDefaultFrameBuffer(self)

    def buffer(
        self, *, data: BufferProtocol | None = None, reserve: int = 0, usage: str = "static"
    ) -> WebGLBuffer:
        return WebGLBuffer(self, data, reserve=reserve, usage=usage)

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
    ):
        if geometry_shader is not None:
            raise NotImplementedError("Geometry Shaders not supported with WebGL")

        if tess_control_shader is not None:
            raise NotImplementedError("Tessellation Shaders not supported with WebGL")

        if tess_evaluation_shader is not None:
            raise NotImplementedError("Tessellation Shaders not supported with WebGL")

        source_vs = ShaderSource(self, vertex_shader, common, enums.VERTEX_SHADER)
        source_fs = (
            ShaderSource(self, fragment_shader, common, enums.FRAGMENT_SHADER)
            if fragment_shader
            else None
        )

        out_attributes = list(varyings) if varyings is not None else []
        if not source_fs and not out_attributes:
            out_attributes = source_vs.out_attributes

        return WebGLProgram(
            self,
            vertex_shader=source_vs.get_source(defines=defines),
            fragment_shader=source_fs.get_source(defines=defines) if source_fs else None,
            geometry_shader=None,
            tess_control_shader=None,
            tess_evaluation_shader=None,
            varyings=out_attributes,
            varyings_capture_mode=varyings_capture_mode,
        )

    def geometry(
        self,
        content: Sequence[BufferDescription] | None = None,
        index_buffer: WebGLBuffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ) -> WebGLGeometry:
        return WebGLGeometry(
            self,
            content,
            index_buffer=index_buffer,
            mode=mode,
            index_element_size=index_element_size,
        )

    def compute_shader(self, *, source: str, common: Iterable[str] = ()) -> None:
        raise NotImplementedError("compute_shader is not supported with WebGL")

    def texture(
        self,
        size: Tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        wrap_x: int | None = None,
        wrap_y: int | None = None,
        filter: Tuple[int, int] | None = None,
        samples: int = 0,
        immutable: bool = False,
        internal_format: int | None = None,
        compressed: bool = False,
        compressed_data: bool = False,
    ) -> WebGLTexture2D:
        return WebGLTexture2D(
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
    ) -> WebGLTexture2D:
        return WebGLTexture2D(self, size, data=data, depth=True)

    def framebuffer(
        self,
        *,
        color_attachments: WebGLTexture2D | List[WebGLTexture2D] | None = None,
        depth_attachment: WebGLTexture2D | None = None,
    ) -> WebGLFramebuffer:
        return WebGLFramebuffer(
            self, color_attachments=color_attachments or [], depth_attachment=depth_attachment
        )

    def copy_framebuffer(
        self,
        src: WebGLFramebuffer,
        dst: WebGLFramebuffer,
        src_attachment_index: int = 0,
        depth: bool = True,
    ):
        self._gl.bindFramebuffer(enums.READ_FRAMEBUFFER, src.glo)
        self._gl.bindFramebuffer(enums.DRAW_FRAMEBUFFER, dst.glo)

        self._gl.readBuffer(enums.COLOR_ATTACHMENT0 + src_attachment_index)
        if dst.is_default:
            self._gl.drawBuffers([enums.BACK])
        else:
            self._gl.drawBuffers([enums.COLOR_ATTACHMENT0])

        self._gl.blitFramebuffer(
            0,
            0,
            src.width,
            src.height,
            0,
            0,
            src.width,
            src.height,
            enums.COLOR_BUFFER_BIT | enums.DEPTH_BUFFER_BIT,
            enums.NEAREST,
        )

        self._gl.readBuffer(enums.COLOR_ATTACHMENT0)

    def sampler(self, texture: WebGLTexture2D):
        return WebGLSampler(self, texture)

    def texture_array(
        self,
        size: Tuple[int, int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        wrap_x: int | None = None,
        wrap_y: int | None = None,
        filter: Tuple[int, int] | None = None,
    ) -> WebGLTextureArray:
        return WebGLTextureArray(
            self,
            size,
            components=components,
            dtype=dtype,
            data=data,
            wrap_x=wrap_x,
            wrap_y=wrap_y,
            filter=filter,
        )

    def query(self, *, samples=True, time=False, primitives=True):
        return WebGLQuery(self, samples=samples, time=time, primitives=primitives)


class WebGLArcadeContext(ArcadeContext, WebGLContext):
    def __init__(self, *args, **kwargs):
        WebGLContext.__init__(self, *args, **kwargs)
        ArcadeContext.__init__(self, *args, **kwargs)

    def bind_window_block(self):
        self._gl.bindBufferRange(
            enums.UNIFORM_BUFFER,
            0,
            self._window_block.buffer.id,
            0,
            128,
        )


class WebGLInfo(Info):
    def __init__(self, ctx: WebGLContext):
        super().__init__(ctx)
        self._ctx = ctx

    def get_int_tuple(self, enum, length: int):
        # TODO: this might not work
        values = self._ctx._gl.getParameter(enum)
        return tuple(values)

    def get(self, enum, default=0):
        value = self._ctx._gl.getParameter(enum)
        return value or default

    def get_float(self, enum, default=0.0):
        return self.get(enum, default)  # type: ignore

    def get_str(self, enum):
        return self.get(enum)
