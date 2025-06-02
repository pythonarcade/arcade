from ctypes import c_char_p, c_float, c_int, cast
from typing import Dict, Iterable, List, Sequence, Tuple

import pyglet
from pyglet import gl

from arcade.context import ArcadeContext
from arcade.gl import enums
from arcade.gl.context import Context, Info
from arcade.gl.types import BufferDescription, PyGLenum
from arcade.types import BufferProtocol

from .buffer import OpenGLBuffer
from .compute_shader import OpenGLComputeShader
from .framebuffer import OpenGLDefaultFrameBuffer, OpenGLFramebuffer
from .glsl import ShaderSource
from .program import OpenGLProgram
from .query import OpenGLQuery
from .sampler import OpenGLSampler
from .texture import OpenGLTexture2D
from .texture_array import OpenGLTextureArray
from .vertex_array import OpenGLGeometry


class OpenGLContext(Context):
    #: The OpenGL api. Usually "opengl" or "opengles".
    gl_api: str = "opengl"

    _valid_apis = ("opengl", "opengles")

    def __init__(
        self, window: pyglet.window.Window, gc_mode: str = "context_gc", gl_api: str = "opengl"
    ):
        super().__init__(window, gc_mode)

        if gl_api not in self._valid_apis:
            if gl_api == "webgl":
                raise ValueError(
                    "Tried to create a OpenGLContext with WebGL api selected. "
                    + f"Valid options for this backend are: {self._valid_apis}"
                )
            raise ValueError(f"Invalid gl_api. Options are: {self._valid_apis}")
        self.gl_api = gl_api

        self._gl_version = (self._info.MAJOR_VERSION, self._info.MINOR_VERSION)

        # Hardcoded states
        # This should always be enabled
        # gl.glEnable(gl.GL_TEXTURE_CUBE_MAP_SEAMLESS)
        # Set primitive restart index to -1 by default
        if self.gl_api == "opengles":
            gl.glEnable(gl.GL_PRIMITIVE_RESTART_FIXED_INDEX)
        else:
            gl.glEnable(gl.GL_PRIMITIVE_RESTART)

        # Detect support for glProgramUniform.
        # Assumed to be supported in gles
        self._ext_separate_shader_objects_enabled = True
        if self.gl_api == "opengl":
            have_ext = gl.gl_info.have_extension("GL_ARB_separate_shader_objects")
            self._ext_separate_shader_objects_enabled = self.gl_version >= (4, 1) or have_ext

        # We enable scissor testing by default.
        # This is always set to the same value as the viewport
        # to avoid background color affecting areas outside the viewport
        gl.glEnable(gl.GL_SCISSOR_TEST)

    @property
    def gl_version(self) -> Tuple[int, int]:
        """
        The OpenGL major and minor version as a tuple.

        This is the reported OpenGL version from
        drivers and might be a higher version than
        you requested.
        """
        return self._gl_version

    @Context.extensions.getter
    def extensions(self) -> set[str]:
        return gl.gl_info.get_extensions()

    @property
    def error(self) -> str | None:
        """Check OpenGL error

        Returns a string representation of the occurring error
        or ``None`` of no errors has occurred.

        Example::

            err = ctx.error
            if err:
                raise RuntimeError("OpenGL error: {err}")
        """
        err = gl.glGetError()
        if err == enums.NO_ERROR:
            return None

        return self._errors.get(err, "UNKNOWN_ERROR")

    def enable(self, *flags: int):
        self._flags.update(flags)

        for flag in flags:
            gl.glEnable(flag)

    def enable_only(self, *args: int):
        self._flags = set(args)

        if self.BLEND in self._flags:
            gl.glEnable(self.BLEND)
        else:
            gl.glDisable(self.BLEND)

        if self.DEPTH_TEST in self._flags:
            gl.glEnable(self.DEPTH_TEST)
        else:
            gl.glDisable(self.DEPTH_TEST)

        if self.CULL_FACE in self._flags:
            gl.glEnable(self.CULL_FACE)
        else:
            gl.glDisable(self.CULL_FACE)

        if self.gl_api == "opengl":
            if gl.GL_PROGRAM_POINT_SIZE in self._flags:
                gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
            else:
                gl.glDisable(gl.GL_PROGRAM_POINT_SIZE)

    def disable(self, *args):
        self._flags -= set(args)

        for flag in args:
            gl.glDisable(flag)

    @Context.blend_func.setter
    def blend_func(self, value: Tuple[int, int] | Tuple[int, int, int, int]):
        self._blend_func = value
        if len(value) == 2:
            gl.glBlendFunc(*value)
        elif len(value) == 4:
            gl.glBlendFuncSeparate(*value)
        else:
            raise ValueError(f"blend_func takes a tuple of 2 or 4 values, got {len(value)}")

    @property
    def front_face(self) -> str:
        value = c_int()
        gl.glGetIntegerv(gl.GL_FRONT_FACE, value)
        return "cw" if value.value == gl.GL_CW else "ccw"

    @front_face.setter
    def front_face(self, value: str):
        if value not in ["cw", "ccw"]:
            raise ValueError("front_face must be 'cw' or 'ccw'")
        gl.glFrontFace(gl.GL_CW if value == "cw" else gl.GL_CCW)

    @property
    def cull_face(self) -> str:
        value = c_int()
        gl.glGetIntegerv(gl.GL_CULL_FACE_MODE, value)
        return self._cull_face_options_reverse[value.value]

    @cull_face.setter
    def cull_face(self, value):
        if value not in self._cull_face_options:
            raise ValueError("cull_face must be", list(self._cull_face_options.keys()))

        gl.glCullFace(self._cull_face_options[value])

    @Context.wireframe.setter
    def wireframe(self, value: bool):
        self._wireframe = value
        if value:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    @property
    def patch_vertices(self) -> int:
        value = c_int()
        gl.glGetIntegerv(gl.GL_PATCH_VERTICES, value)
        return value.value

    @patch_vertices.setter
    def patch_vertices(self, value: int):
        if not isinstance(value, int):
            raise TypeError("patch_vertices must be an integer")

        gl.glPatchParameteri(gl.GL_PATCH_VERTICES, value)

    @Context.point_size.setter
    def point_size(self, value: float):
        if self.gl_api == "opengl":
            gl.glPointSize(self._point_size)
        self._point_size = value

    @Context.primitive_restart_index.setter
    def primitive_restart_index(self, value: int):
        self._primitive_restart_index = value
        if self.gl_api == "opengl":
            gl.glPrimitiveRestartIndex(value)

    def finish(self) -> None:
        gl.glFinish()

    def flush(self) -> None:
        gl.glFlush()

    def _create_default_framebuffer(self) -> OpenGLDefaultFrameBuffer:
        return OpenGLDefaultFrameBuffer(self)

    def buffer(
        self, *, data: BufferProtocol | None = None, reserve: int = 0, usage: str = "static"
    ) -> OpenGLBuffer:
        return OpenGLBuffer(self, data, reserve=reserve, usage=usage)

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
    ) -> OpenGLProgram:
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

        return OpenGLProgram(
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
        index_buffer: OpenGLBuffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ):
        return OpenGLGeometry(
            self,
            content,
            index_buffer=index_buffer,
            mode=mode,
            index_element_size=index_element_size,
        )

    def compute_shader(self, *, source: str, common: Iterable[str] = ()) -> OpenGLComputeShader:
        src = ShaderSource(self, source, common, pyglet.gl.GL_COMPUTE_SHADER)
        return OpenGLComputeShader(self, src.get_source())

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
    ) -> OpenGLTexture2D:
        compressed = compressed or compressed_data

        return OpenGLTexture2D(
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
    ) -> OpenGLTexture2D:
        return OpenGLTexture2D(self, size, data=data, depth=True)

    def framebuffer(
        self,
        *,
        color_attachments: OpenGLTexture2D | List[OpenGLTexture2D] | None = None,
        depth_attachment: OpenGLTexture2D | None = None,
    ) -> OpenGLFramebuffer:
        return OpenGLFramebuffer(
            self, color_attachments=color_attachments or [], depth_attachment=depth_attachment
        )

    def copy_framebuffer(
        self,
        src: OpenGLFramebuffer,
        dst: OpenGLFramebuffer,
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

    def sampler(self, texture: OpenGLTexture2D) -> OpenGLSampler:
        """
        Create a sampler object for a texture.

        Args:
            texture:
                The texture to create a sampler for
        """
        return OpenGLSampler(self, texture)

    def texture_array(
        self,
        size: Tuple[int, int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        wrap_x: PyGLenum | None = None,
        wrap_y: PyGLenum | None = None,
        filter: Tuple[PyGLenum, PyGLenum] | None = None,
    ) -> OpenGLTextureArray:
        return OpenGLTextureArray(
            self,
            size,
            components=components,
            dtype=dtype,
            data=data,
            wrap_x=wrap_x,
            wrap_y=wrap_y,
            filter=filter,
        )

    def query(self, *, samples=True, time=True, primitives=True) -> OpenGLQuery:
        return OpenGLQuery(self, samples=samples, time=time, primitives=primitives)


class OpenGLArcadeContext(ArcadeContext, OpenGLContext):
    def __init__(self, *args, **kwargs):
        OpenGLContext.__init__(self, *args, **kwargs)
        ArcadeContext.__init__(self, *args, **kwargs)


class OpenGLInfo(Info):
    """OpenGL info and capabilities"""

    def __init__(self, ctx):
        super().__init__(ctx)

        self.MINOR_VERSION = self.get(gl.GL_MINOR_VERSION)
        """Minor version number of the OpenGL API supported by the current context"""

        self.MAJOR_VERSION = self.get(gl.GL_MAJOR_VERSION)
        """Major version number of the OpenGL API supported by the current context."""

        self.MAX_COLOR_TEXTURE_SAMPLES = self.get(gl.GL_MAX_COLOR_TEXTURE_SAMPLES)
        """Maximum number of samples in a color multisample texture"""

        self.MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS
        )
        """Number of words for geometry shader uniform variables in all uniform blocks"""

        self.MAX_DEPTH_TEXTURE_SAMPLES = self.get(gl.GL_MAX_DEPTH_TEXTURE_SAMPLES)
        """Maximum number of samples in a multisample depth or depth-stencil texture"""

        self.MAX_GEOMETRY_INPUT_COMPONENTS = self.get(gl.GL_MAX_GEOMETRY_INPUT_COMPONENTS)
        """Maximum number of components of inputs read by a geometry shader"""

        self.MAX_GEOMETRY_OUTPUT_COMPONENTS = self.get(gl.GL_MAX_GEOMETRY_OUTPUT_COMPONENTS)
        """Maximum number of components of outputs written by a geometry shader"""

        self.MAX_GEOMETRY_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_GEOMETRY_TEXTURE_IMAGE_UNITS)
        """
        Maximum supported texture image units that can be used to access texture
        maps from the geometry shader
        """

        self.MAX_GEOMETRY_UNIFORM_BLOCKS = self.get(gl.GL_MAX_GEOMETRY_UNIFORM_BLOCKS)
        """Maximum number of uniform blocks per geometry shader"""

        self.MAX_GEOMETRY_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_GEOMETRY_UNIFORM_COMPONENTS)
        """
        Maximum number of individual floating-point, integer, or boolean values that can
        be held in uniform variable storage for a geometry shader
        """

        self.MAX_INTEGER_SAMPLES = self.get(gl.GL_MAX_INTEGER_SAMPLES)
        """Maximum number of samples supported in integer format multisample buffers"""

        self.MAX_SAMPLE_MASK_WORDS = self.get(gl.GL_MAX_SAMPLE_MASK_WORDS)
        """Maximum number of sample mask words"""

        self.POINT_SIZE_RANGE = self.get_int_tuple(gl.GL_POINT_SIZE_RANGE, 2)
        """The minimum and maximum point size"""

        # This error checking doesn't actually need any implementation specific details
        # However we need to do it here instead of the common class to catch all possible
        # errors because of implementation specific gets.
        err = self._ctx.error
        if err:
            from warnings import warn

            warn(f"Error happened while querying of limits. {err}")

    def get_int_tuple(self, enum, length: int):
        """
        Get an enum as an int tuple

        Args:
            enum: The enum to query
            length: The length of the tuple
        """
        try:
            values = (c_int * length)()
            gl.glGetIntegerv(enum, values)
            return tuple(values)
        except pyglet.gl.lib.GLException:
            return tuple([0] * length)

    def get(self, enum, default=0) -> int:
        """
        Get an integer limit.

        Args:
            enum: The enum to query
            default: The default value if the query fails
        """
        try:
            value = c_int()
            gl.glGetIntegerv(enum, value)
            return value.value
        except pyglet.gl.lib.GLException:
            return default

    def get_float(self, enum, default=0.0) -> float:
        """
        Get a float limit

        Args:
            enum: The enum to query
            default: The default value if the query fails
        """
        try:
            value = c_float()
            gl.glGetFloatv(enum, value)
            return value.value
        except pyglet.gl.lib.GLException:
            return default

    def get_str(self, enum) -> str:
        """
        Get a string limit.

        Args:
            enum: The enum to query
        """
        try:
            return cast(gl.glGetString(enum), c_char_p).value.decode()  # type: ignore
        except pyglet.gl.lib.GLException:
            return "Unknown"
