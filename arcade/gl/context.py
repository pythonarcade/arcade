from ctypes import c_int, c_char_p, cast, c_float
import sys
import logging
import weakref
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union, Sequence, Set

import pyglet
from pyglet.window import Window
from pyglet import gl

from .buffer import Buffer
from .program import Program
from .vertex_array import Geometry, VertexArray
from .framebuffer import Framebuffer, DefaultFrameBuffer
from typing import Optional
from .texture import Texture
from .query import Query
from .glsl import ShaderSource
from .types import BufferDescription

LOG = logging.getLogger(__name__)


class Context:
    """
    Represents an OpenGL context. This context belongs to a ``pyglet.Window``
    normally accessed through ``window.ctx``.

    The Context class contains methods for creating resources,
    global states and commonly used enums. All enums also exist
    in the ``gl`` module. (``ctx.BLEND`` or ``arcade.gl.BLEND``).
    """

    #: The active context
    active: Optional["Context"] = None

    # --- Store the most commonly used OpenGL constants
    # Texture
    #: Texture interpolation: Nearest pixel
    NEAREST = 0x2600
    #: Texture interpolation: Linear interpolate
    LINEAR = 0x2601
    #: Texture interpolation: Minification filter for mipmaps
    NEAREST_MIPMAP_NEAREST = 0x2700
    #: Texture interpolation: Minification filter for mipmaps
    LINEAR_MIPMAP_NEAREST = 0x2701
    #: Texture interpolation: Minification filter for mipmaps
    NEAREST_MIPMAP_LINEAR = 0x2702
    #: Texture interpolation: Minification filter for mipmaps
    LINEAR_MIPMAP_LINEAR = 0x2703

    #: Texture wrap mode: Repeat
    REPEAT = gl.GL_REPEAT
    # Texture wrap mode: Clamp to border pixel
    CLAMP_TO_EDGE = gl.GL_CLAMP_TO_EDGE
    # Texture wrap mode: Clamp to border color
    CLAMP_TO_BORDER = gl.GL_CLAMP_TO_BORDER
    # Texture wrap mode: Repeat mirrored
    MIRRORED_REPEAT = gl.GL_MIRRORED_REPEAT

    # Flags
    #: Context flag: Blending
    BLEND = gl.GL_BLEND
    #: Context flag: Depth testing
    DEPTH_TEST = gl.GL_DEPTH_TEST
    #: Context flag: Face culling
    CULL_FACE = gl.GL_CULL_FACE
    #: Context flag: Enable ``gl_PointSize`` in shaders.
    PROGRAM_POINT_SIZE = gl.GL_PROGRAM_POINT_SIZE

    # Blend functions
    #: Blend function
    ZERO = 0x0000
    #: Blend function
    ONE = 0x0001
    #: Blend function
    SRC_COLOR = 0x0300
    #: Blend function
    ONE_MINUS_SRC_COLOR = 0x0301
    #: Blend function
    SRC_ALPHA = 0x0302
    #: Blend function
    ONE_MINUS_SRC_ALPHA = 0x0303
    #: Blend function
    DST_ALPHA = 0x0304
    #: Blend function
    ONE_MINUS_DST_ALPHA = 0x0305
    #: Blend function
    DST_COLOR = 0x0306
    #: Blend function
    ONE_MINUS_DST_COLOR = 0x0307

    # Blend equations
    #: source + destination
    FUNC_ADD = 0x8006
    #: Blend equations: source - destination
    FUNC_SUBTRACT = 0x800A
    #: Blend equations: destination - source
    FUNC_REVERSE_SUBTRACT = 0x800B
    #: Blend equations: Minimum of source and destination
    MIN = 0x8007
    #: Blend equations: Maximum of source and destination
    MAX = 0x8008

    # Blend mode shortcuts
    #: Blend mode shortcut for default blend mode: ``SRC_ALPHA, ONE_MINUS_SRC_ALPHA``
    BLEND_DEFAULT = 0x0302, 0x0303
    #: Blend mode shortcut for additive blending: ``ONE, ONE``
    BLEND_ADDITIVE = 0x0001, 0x0001
    #: Blend mode shortcut for premultipled alpha: ``SRC_ALPHA, ONE``
    BLEND_PREMULTIPLIED_ALPHA = 0x0302, 0x0001

    # VertexArray: Primitives
    #: Primitive mode
    POINTS = gl.GL_POINTS  # 0
    #: Primitive mode
    LINES = gl.GL_LINES  # 1
    #: Primitive mode
    LINE_STRIP = gl.GL_LINE_STRIP  # 3
    #: Primitive mode
    TRIANGLES = gl.GL_TRIANGLES  # 4
    #: Primitive mode
    TRIANGLE_STRIP = gl.GL_TRIANGLE_STRIP  # 5
    #: Primitive mode
    TRIANGLE_FAN = gl.GL_TRIANGLE_FAN  # 6
    #: Primitive mode
    LINES_ADJACENCY = gl.GL_LINES_ADJACENCY  # 10
    #: Primitive mode
    LINE_STRIP_ADJACENCY = gl.GL_LINE_STRIP_ADJACENCY  # 11
    #: Primitive mode
    TRIANGLES_ADJACENCY = gl.GL_TRIANGLES_ADJACENCY  # 12
    #: Primitive mode
    TRIANGLE_STRIP_ADJACENCY = gl.GL_TRIANGLE_STRIP_ADJACENCY  # 13
    #: Patch mode (tessellation)
    PATCHES = gl.GL_PATCHES

    # The most common error enums
    _errors = {
        gl.GL_INVALID_ENUM: "GL_INVALID_ENUM",
        gl.GL_INVALID_VALUE: "GL_INVALID_VALUE",
        gl.GL_INVALID_OPERATION: "GL_INVALID_OPERATION",
        gl.GL_INVALID_FRAMEBUFFER_OPERATION: "GL_INVALID_FRAMEBUFFER_OPERATION",
        gl.GL_OUT_OF_MEMORY: "GL_OUT_OF_MEMORY",
        gl.GL_STACK_UNDERFLOW: "GL_STACK_UNDERFLOW",
        gl.GL_STACK_OVERFLOW: "GL_STACK_OVERFLOW",
    }

    def __init__(self, window: pyglet.window.Window):
        self._window_ref = weakref.ref(window)
        self.limits = Limits(self)
        self._gl_version = (self.limits.MAJOR_VERSION, self.limits.MINOR_VERSION)
        Context.activate(self)

        # Detect the default framebuffer
        self._screen = DefaultFrameBuffer(self)
        # Tracking active program
        self.active_program: Optional[Program] = None
        # Tracking active framebuffer. On context creation the window is the default render target
        self.active_framebuffer: Framebuffer = self._screen
        self.stats: ContextStats = ContextStats(warn_threshold=1000)

        # Hardcoded states
        # This should always be enabled
        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP_SEAMLESS)
        # Set primitive restart index to -1 by default
        gl.glEnable(gl.GL_PRIMITIVE_RESTART)
        self._primitive_restart_index = -1
        self.primitive_restart_index = self._primitive_restart_index

        # We enable scissor testing by default.
        # This is always set to the same value as the viewport
        # to avoid background color affecting areas outside the viewport
        gl.glEnable(gl.GL_SCISSOR_TEST)

        # States
        self._blend_func = self.BLEND_DEFAULT
        self._point_size = 1.0
        self._flags: Set[int] = set()

    @property
    def window(self) -> Window:
        """
        The window this context belongs to.
        
        :type: ``pyglet.Window``
        """
        return self._window_ref()

    @property
    def screen(self) -> Framebuffer:
        """
        The framebuffer for the window.
        
        :type: :py:class:`~arcade.Framebuffer`
        """
        return self._screen

    @property
    def fbo(self) -> Framebuffer:
        """
        Get the currently active framebuffer.
        This property is read-only

        :type: :py:class:`arcade.gl.Framebuffer`
        """
        return self.active_framebuffer

    @property
    def gl_version(self) -> Tuple[int, int]:
        """
        The OpenGL version as a 2 component tuple

        :type: tuple (major, minor) version
        """
        return self._gl_version

    @property
    def error(self) -> Union[str, None]:
        """Check OpenGL error

        Returns a string representation of the occurring error
        or ``None`` of no errors has occurred.

        Example::

            err = ctx.error
            if err:
                raise RuntimeError("OpenGL error: {err}")

        :type: str
        """
        err = gl.glGetError()
        if err == gl.GL_NO_ERROR:
            return None

        return self._errors.get(err, "GL_UNKNOWN_ERROR")

    @classmethod
    def activate(cls, ctx: "Context"):
        """Mark a context as the currently active one"""
        cls.active = ctx

    def enable(self, *args):
        """
        Enables one or more context flags::

            # Single flag
            ctx.enable(ctx.BLEND)
            # Multiple flags
            ctx.enable(ctx.DEPTH_TEST, ctx.CULL_FACE)
        """
        self._flags.update(args)

        for flag in args:
            gl.glEnable(flag)

    def enable_only(self, *args):
        """
        Enable only some flags. This will disable all other flags.
        This is a simple way to ensure that context flag states
        are not lingering from other sections of your code base::

            # Ensure all flags are disabled (enable no flags)
            ctx.enable_only()
            # Make sure only blending is enabled
            ctx.enable_only(ctx.BLEND)
            # Make sure only depth test and culling is enabled
            ctx.enable_only(ctx.DEPTH_TEST, ctx.CULL_FACE)        
        """
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

        if self.PROGRAM_POINT_SIZE in self._flags:
            gl.glEnable(self.PROGRAM_POINT_SIZE)
        else:
            gl.glDisable(self.PROGRAM_POINT_SIZE)

    def disable(self, *args):
        """
        Disable one or more context flags::

            # Single flag
            ctx.disable(ctx.BLEND)
            # Multiple flags
            ctx.disable(ctx.DEPTH_TEST, ctx.CULL_FACE)
        """
        self._flags -= set(args)

        for flag in args:
            gl.glDisable(flag)

    def is_enabled(self, flag) -> bool:
        """
        Check if a context flag is enabled

        :type: bool
        """
        return flag in self._flags

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """
        Get or set the viewport for the currently active framebuffer.
        The viewport simply describes what pixels of the screen
        OpenGL should render to. Normally it would be the size of
        the window's framebuffer::

            # 4:3 screen
            ctx.viewport = 0, 0, 800, 600
            # 1080p
            ctx.viewport = 0, 0, 1920, 1080
            # Using the current framebuffer size
            ctx.viewport = 0, 0, *ctx.screen.size

        :type: tuple (x, y, width, height)
        """
        return self.active_framebuffer.viewport

    @viewport.setter
    def viewport(self, value: Tuple[int, int, int, int]):
        self.active_framebuffer.viewport = value

    @property
    def blend_func(self) -> Tuple[int, int]:
        """
        Get or the blend function::

            ctx.blend_func = ctx.ONE, ctx.ONE

        :type: tuple (src, dst)
        """
        return self._blend_func

    @blend_func.setter
    def blend_func(self, value: Tuple[int, int]):
        self._blend_func = value
        gl.glBlendFunc(value[0], value[1])

    # def blend_equation(self)
    # def front_face(self)
    # def cull_face(self)

    @property
    def patch_vertices(self) -> int:
        """
        Get or set number of vertices that will be used to make up a single patch primitive.
        Patch primitives are consumed by the tessellation control shader (if present) and subsequently used for tessellation.

        :type: int
        """
        value = c_int()
        gl.glGetIntegerv(gl.GL_PATCH_VERTICES, value)
        return value.value

    @patch_vertices.setter
    def patch_vertices(self, value: int):
        if not isinstance(value, int):
            raise TypeError("patch_vertices must be an integer")

        gl.glPatchParameteri(gl.GL_PATCH_VERTICES, value)

    @property
    def point_size(self) -> float:
        """float: Get or set the point size."""
        return self._point_size

    @point_size.setter
    def point_size(self, value: float):
        gl.glPointSize(self._point_size)
        self._point_size = value

    @property
    def primitive_restart_index(self) -> int:
        """Get or set the primitive restart index. Default is -1"""
        return self._primitive_restart_index

    @primitive_restart_index.setter
    def primitive_restart_index(self, value: int):
        self._primitive_restart_index = value
        gl.glPrimitiveRestartIndex(value)

    def finish(self) -> None:
        """Wait until all OpenGL rendering commands are completed"""
        gl.glFinish()

    # --- Resource methods ---

    def buffer(
        self, *, data: Optional[Any] = None, reserve: int = 0, usage: str = "static"
    ) -> Buffer:
        """Create a new OpenGL Buffer object.

        :param Any data: The buffer data, This can be ``bytes`` or an object supporting the buffer protocol.
        :param int reserve: The number of bytes reserve
        :param str usage: Buffer usage. 'static', 'dynamic' or 'stream'
        :rtype: :py:class:`~arcade.gl.Buffer`
        """
        # create_with_size
        return Buffer(self, data, reserve=reserve, usage=usage)

    def framebuffer(
        self,
        *,
        color_attachments: Union[Texture, List[Texture]] = None,
        depth_attachment: Texture = None
    ) -> Framebuffer:
        """Create a Framebuffer.

        :param List[arcade.gl.Texture] color_attachments: List of textures we want to render into
        :param arcade.gl.Texture depth_attachment: Depth texture
        :rtype: :py:class:`~arcade.gl.Framebuffer`
        """
        return Framebuffer(
            self, color_attachments=color_attachments, depth_attachment=depth_attachment
        )

    def texture(
        self,
        size: Tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: Any = None,
        wrap_x: gl.GLenum = None,
        wrap_y: gl.GLenum = None,
        filter: Tuple[gl.GLenum, gl.GLenum] = None
    ) -> Texture:
        """Create a 2D Texture.

        Wrap modes: ``GL_REPEAT``, ``GL_MIRRORED_REPEAT``, ``GL_CLAMP_TO_EDGE``, ``GL_CLAMP_TO_BORDER``

        Minifying filters: ``GL_NEAREST``, ``GL_LINEAR``, ``GL_NEAREST_MIPMAP_NEAREST``, ``GL_LINEAR_MIPMAP_NEAREST``
        ``GL_NEAREST_MIPMAP_LINEAR``, ``GL_LINEAR_MIPMAP_LINEAR``

        Magnifying filters: ``GL_NEAREST``, ``GL_LINEAR``

        :param Tuple[int, int] size: The size of the texture
        :param int components: Number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
        :param str dtype: The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
        :param Any data: The texture data (optional). Can be bytes or an object supporting the buffer protocol.
        :param GLenum wrap_x: How the texture wraps in x direction
        :param GLenum wrap_y: How the texture wraps in y direction
        :param Tuple[GLenum,GLenum] filter: Minification and magnification filter
        """
        return Texture(
            self,
            size,
            components=components,
            data=data,
            dtype=dtype,
            wrap_x=wrap_x,
            wrap_y=wrap_y,
            filter=filter,
        )

    def depth_texture(self, size: Tuple[int, int], *, data=None) -> Texture:
        """Create a 2D depth texture

        :param Tuple[int, int] size: The size of the texture
        :param Any data: The texture data (optional). Can be bytes or an object supporting the buffer protocol.
        """
        return Texture(self, size, data=data, depth=True)

    def geometry(
        self,
        content: Optional[Sequence[BufferDescription]] = None,
        index_buffer: Buffer = None,
        mode: int = None,
        index_element_size: int = 4,
    ):
        """
        Create a Geomtry instance.

        :param list content: List of :py:class:`~arcade.gl.BufferDescription` (optional)
        :param Buffer index_buffer: Index/element buffer (optional)
        :param int mode: The default draw mode (optional)
        :param int mode: The default draw mode (optional)
        :param int index_element_size: Byte size of the index buffer type. Can be 1, 2 or 4 (8, 16 or 32 bit unsigned integer)
        """
        return Geometry(self, content, index_buffer=index_buffer, mode=mode, index_element_size=index_element_size)

    def program(
        self,
        *,
        vertex_shader: str,
        fragment_shader: str = None,
        geometry_shader: str = None,
        tess_control_shader: str = None,
        tess_evaluation_shader: str = None,
        defines: Dict[str, str] = None
    ) -> Program:
        """Create a :py:class:`~arcade.gl.Program` given the vertex, fragment and geometry shader.

        :param str vertex_shader: vertex shader source
        :param str fragment_shader: fragment shader source (optional)
        :param str geometry_shader: geometry shader source (optional)
        :param str tess_control_shader: tessellation control shader source (optional)
        :param str tess_evaluation_shader: tessellation evaluation shader source (optional)
        :param dict defines: Substitute #defines values in the source (optional)
        :rtype: :py:class:`~arcade.gl.Program`
        """
        source_vs = ShaderSource(vertex_shader, gl.GL_VERTEX_SHADER)
        source_fs = (
            ShaderSource(fragment_shader, gl.GL_FRAGMENT_SHADER)
            if fragment_shader
            else None
        )
        source_geo = (
            ShaderSource(geometry_shader, gl.GL_GEOMETRY_SHADER)
            if geometry_shader
            else None
        )
        source_tc = (
            ShaderSource(tess_control_shader, gl.GL_TESS_CONTROL_SHADER)
            if tess_control_shader
            else None
        )
        source_te = (
            ShaderSource(tess_evaluation_shader, gl.GL_TESS_EVALUATION_SHADER)
            if tess_evaluation_shader
            else None
        )

        # If we don't have a fragment shader we are doing transform feedback.
        # When a geometry shader is present the out attributes will be located there
        out_attributes = []  # type: List[str]
        if not source_fs:
            if source_geo:
                out_attributes = source_geo.out_attributes
            else:
                out_attributes = source_vs.out_attributes

        return Program(
            self,
            vertex_shader=source_vs.get_source(defines=defines),
            fragment_shader=source_fs.get_source(defines=defines)
            if source_fs
            else None,
            geometry_shader=source_geo.get_source(defines=defines)
            if source_geo
            else None,
            tess_control_shader=source_tc.get_source(defines=defines)
            if source_tc
            else None,
            tess_evaluation_shader=source_te.get_source(defines=defines)
            if source_te
            else None,
            out_attributes=out_attributes,
        )

    def query(self):
        """
        Create a query object for measuring rendering calls in opengl.

        :rtype: :py:class:`~arcade.gl.Query`
        """
        return Query(self)


class ContextStats:
    def __init__(self, warn_threshold=100):
        self.warn_threshold = warn_threshold
        # (created, freed)
        self.texture = (0, 0)
        self.framebuffer = (0, 0)
        self.buffer = (0, 0)
        self.program = (0, 0)
        self.vertex_array = (0, 0)
        self.geometry = (0, 0)

    def incr(self, key):
        created, freed = getattr(self, key)
        setattr(self, key, (created + 1, freed))
        if created % self.warn_threshold == 0 and created > 0:
            LOG.debug(
                "%s allocations passed threshold (%s) [created = %s] [freed = %s] [active = %s]",
                key,
                self.warn_threshold,
                created,
                freed,
                created - freed,
            )

    def decr(self, key):
        created, freed = getattr(self, key)
        setattr(self, key, (created, freed + 1))


class Limits:
    """OpenGL Limitations"""

    def __init__(self, ctx):
        self._ctx = ctx
        #: Minor version number of the OpenGL API supported by the current context
        self.MINOR_VERSION = self.get(gl.GL_MINOR_VERSION)
        #: Major version number of the OpenGL API supported by the current context.
        self.MAJOR_VERSION = self.get(gl.GL_MAJOR_VERSION)
        self.VENDOR = self.get_str(gl.GL_VENDOR)
        self.RENDERER = self.get_str(gl.GL_RENDERER)
        #: Value indicating the number of sample buffers associated with the framebuffer
        self.SAMPLE_BUFFERS = self.get(gl.GL_SAMPLE_BUFFERS)
        #: An estimate of the number of bits of subpixel resolution
        #: that are used to position rasterized geometry in window coordinates
        self.SUBPIXEL_BITS = self.get(gl.GL_SUBPIXEL_BITS)
        #: A mask value indicating what context profile is used (core, compat etc.)
        self.CONTEXT_PROFILE_MASK = self.get(gl.GL_CONTEXT_PROFILE_MASK)
        #: Minimum required alignment for uniform buffer sizes and offset
        self.UNIFORM_BUFFER_OFFSET_ALIGNMENT = self.get(
            gl.GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT
        )
        #: Value indicates the maximum number of layers allowed in an array texture, and must be at least 256
        self.MAX_ARRAY_TEXTURE_LAYERS = self.get(gl.GL_MAX_ARRAY_TEXTURE_LAYERS)
        #: A rough estimate of the largest 3D texture that the GL can handle. The value must be at least 64
        self.MAX_3D_TEXTURE_SIZE = self.get(gl.GL_MAX_3D_TEXTURE_SIZE)
        #: Maximum number of color attachments in a framebuffer
        self.MAX_COLOR_ATTACHMENTS = self.get(gl.GL_MAX_COLOR_ATTACHMENTS)
        #: Maximum number of samples in a color multisample texture
        self.MAX_COLOR_TEXTURE_SAMPLES = self.get(gl.GL_MAX_COLOR_TEXTURE_SAMPLES)
        #: the number of words for fragment shader uniform variables in all uniform blocks
        self.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS
        )
        #: Number of words for geometry shader uniform variables in all uniform blocks
        self.MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS
        )
        #: Maximum supported texture image units that can be used to access texture maps from the vertex shader
        self.MAX_COMBINED_TEXTURE_IMAGE_UNITS = self.get(
            gl.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS
        )
        #: Maximum number of uniform blocks per program
        self.MAX_COMBINED_UNIFORM_BLOCKS = self.get(gl.GL_MAX_COMBINED_UNIFORM_BLOCKS)
        #: Number of words for vertex shader uniform variables in all uniform blocks
        self.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS
        )
        #: A rough estimate of the largest cube-map texture that the GL can handle
        self.MAX_CUBE_MAP_TEXTURE_SIZE = self.get(gl.GL_MAX_CUBE_MAP_TEXTURE_SIZE)
        #: Maximum number of samples in a multisample depth or depth-stencil texture
        self.MAX_DEPTH_TEXTURE_SAMPLES = self.get(gl.GL_MAX_DEPTH_TEXTURE_SAMPLES)
        #: Maximum number of simultaneous outputs that may be written in a fragment shader
        self.MAX_DRAW_BUFFERS = self.get(gl.GL_MAX_DRAW_BUFFERS)
        #: Maximum number of active draw buffers when using dual-source blending
        self.MAX_DUAL_SOURCE_DRAW_BUFFERS = self.get(gl.GL_MAX_DUAL_SOURCE_DRAW_BUFFERS)
        #: Recommended maximum number of vertex array indices
        self.MAX_ELEMENTS_INDICES = self.get(gl.GL_MAX_ELEMENTS_INDICES)
        #: Recommended maximum number of vertex array vertices
        self.MAX_ELEMENTS_VERTICES = self.get(gl.GL_MAX_ELEMENTS_VERTICES)
        #: Maximum number of components of the inputs read by the fragment shader
        self.MAX_FRAGMENT_INPUT_COMPONENTS = self.get(
            gl.GL_MAX_FRAGMENT_INPUT_COMPONENTS
        )
        #: Maximum number of individual floating-point, integer, or boolean values that can be
        #: held in uniform variable storage for a fragment shader
        self.MAX_FRAGMENT_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_FRAGMENT_UNIFORM_COMPONENTS
        )
        #: maximum number of individual 4-vectors of floating-point, integer,
        #: or boolean values that can be held in uniform variable storage for a fragment shader
        self.MAX_FRAGMENT_UNIFORM_VECTORS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_VECTORS)
        #: Maximum number of uniform blocks per fragment shader.
        self.MAX_FRAGMENT_UNIFORM_BLOCKS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_BLOCKS)
        #: Maximum number of components of inputs read by a geometry shader
        self.MAX_GEOMETRY_INPUT_COMPONENTS = self.get(
            gl.GL_MAX_GEOMETRY_INPUT_COMPONENTS
        )
        #: Maximum number of components of outputs written by a geometry shader
        self.MAX_GEOMETRY_OUTPUT_COMPONENTS = self.get(
            gl.GL_MAX_GEOMETRY_OUTPUT_COMPONENTS
        )
        #: Maximum supported texture image units that can be used to access texture maps from the geometry shader
        self.MAX_GEOMETRY_TEXTURE_IMAGE_UNITS = self.get(
            gl.GL_MAX_GEOMETRY_TEXTURE_IMAGE_UNITS
        )
        #: Maximum number of uniform blocks per geometry shader
        self.MAX_GEOMETRY_UNIFORM_BLOCKS = self.get(gl.GL_MAX_GEOMETRY_UNIFORM_BLOCKS)
        #: Maximum number of individual floating-point, integer, or boolean values that can
        #: be held in uniform variable storage for a geometry shader
        self.MAX_GEOMETRY_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_GEOMETRY_UNIFORM_COMPONENTS
        )
        #: Maximum number of samples supported in integer format multisample buffers
        self.MAX_INTEGER_SAMPLES = self.get(gl.GL_MAX_INTEGER_SAMPLES)
        #: Maximum samples for a framebuffer
        self.MAX_SAMPLES = self.get(gl.GL_MAX_SAMPLES)
        #: A rough estimate of the largest rectangular texture that the GL can handle
        self.MAX_RECTANGLE_TEXTURE_SIZE = self.get(gl.GL_MAX_RECTANGLE_TEXTURE_SIZE)
        #: Maximum supported size for renderbuffers
        self.MAX_RENDERBUFFER_SIZE = self.get(gl.GL_MAX_RENDERBUFFER_SIZE)
        #: Maximum number of sample mask words
        self.MAX_SAMPLE_MASK_WORDS = self.get(gl.GL_MAX_SAMPLE_MASK_WORDS)
        #: Maximum number of texels allowed in the texel array of a texture buffer object
        self.MAX_TEXTURE_BUFFER_SIZE = self.get(gl.GL_MAX_TEXTURE_BUFFER_SIZE)
        #: Maximum number of uniform buffer binding points on the context
        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        #: Maximum number of uniform buffer binding points on the context
        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        #: The value gives a rough estimate of the largest texture that the GL can handle
        self.MAX_TEXTURE_SIZE = self.get(gl.GL_MAX_TEXTURE_SIZE)
        #: Maximum number of uniform buffer binding points on the context
        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        #: Maximum size in basic machine units of a uniform block
        self.MAX_UNIFORM_BLOCK_SIZE = self.get(gl.GL_MAX_UNIFORM_BLOCK_SIZE)
        #: The number 4-vectors for varying variables
        self.MAX_VARYING_VECTORS = self.get(gl.GL_MAX_VARYING_VECTORS)
        #: Maximum number of 4-component generic vertex attributes accessible to a vertex shader.
        self.MAX_VERTEX_ATTRIBS = self.get(gl.GL_MAX_VERTEX_ATTRIBS)
        #: Maximum supported texture image units that can be used to access texture maps from the vertex shader.
        self.MAX_VERTEX_TEXTURE_IMAGE_UNITS = self.get(
            gl.GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS
        )
        #: Maximum number of individual floating-point, integer, or boolean values that
        #: can be held in uniform variable storage for a vertex shader
        self.MAX_VERTEX_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_VERTEX_UNIFORM_COMPONENTS
        )
        #: Maximum number of 4-vectors that may be held in uniform variable storage for the vertex shader
        self.MAX_VERTEX_UNIFORM_VECTORS = self.get(gl.GL_MAX_VERTEX_UNIFORM_VECTORS)
        #: Maximum number of components of output written by a vertex shader
        self.MAX_VERTEX_OUTPUT_COMPONENTS = self.get(gl.GL_MAX_VERTEX_OUTPUT_COMPONENTS)
        #: Maximum number of uniform blocks per vertex shader.
        self.MAX_VERTEX_UNIFORM_BLOCKS = self.get(gl.GL_MAX_VERTEX_UNIFORM_BLOCKS)
        # self.MAX_VERTEX_ATTRIB_RELATIVE_OFFSET = self.get(gl.GL_MAX_VERTEX_ATTRIB_RELATIVE_OFFSET)
        # self.MAX_VERTEX_ATTRIB_BINDINGS = self.get(gl.GL_MAX_VERTEX_ATTRIB_BINDINGS)
        self.MAX_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_TEXTURE_IMAGE_UNITS)
        # TODO: Missing in pyglet
        # self.MAX_TEXTURE_MAX_ANISOTROPY = self.get_float(gl.GL_MAX_TEXTURE_MAX_ANISOTROPY)

        err = self._ctx.error
        if err:
            from warnings import warn

            warn("Error happened while querying of limits. Moving on ..")

    def get(self, enum: gl.GLenum) -> int:
        """Get an integer limit"""
        value = c_int()
        gl.glGetIntegerv(enum, value)
        return value.value

    def get_float(self, enum) -> float:
        """Get a float limit"""
        value = c_float()
        gl.glGetFloatv(enum, value)
        return value.value

    def get_str(self, enum: gl.GLenum) -> str:
        """Get a string limit"""
        return cast(gl.glGetString(enum), c_char_p).value.decode()  # type: ignore
