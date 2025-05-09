from __future__ import annotations

import logging
import weakref
from collections import deque
from contextlib import contextmanager
from ctypes import c_char_p, c_float, c_int, cast
from typing import (
    Any,
    Deque,
    Dict,
    Iterable,
    List,
    Literal,
    Sequence,
    Set,
    Tuple,
    overload,
)

import pyglet
import pyglet.gl.lib
from pyglet import gl
from pyglet.window import Window

from ..types import BufferProtocol
from .buffer import Buffer
from .compute_shader import ComputeShader
from .framebuffer import DefaultFrameBuffer, Framebuffer
from .glsl import ShaderSource
from .program import Program
from .query import Query
from .sampler import Sampler
from .texture import Texture2D
from .texture_array import TextureArray
from .types import BufferDescription, GLenumLike, PyGLenum
from .vertex_array import Geometry

LOG = logging.getLogger(__name__)


class Context:
    """
    Represents an OpenGL context. This context belongs to a pyglet window.
    normally accessed through ``window.ctx``.

    The Context class contains methods for creating resources,
    global states and commonly used enums. All enums also exist
    in the ``gl`` module. (``ctx.BLEND`` or ``arcade.gl.BLEND``).

    Args:
        window: The pyglet window this context belongs to
        gc_mode: The garbage collection mode. Default is "context_gc"
        gl_api: The OpenGL api. Default is "gl"
    """

    active: Context | None = None
    """The active context"""

    #: The OpenGL api. Usually "gl" or "gles".
    gl_api: str = "gl"

    # --- Store the most commonly used OpenGL constants
    # Texture

    NEAREST = 0x2600
    """Texture interpolation - Nearest pixel"""

    LINEAR = 0x2601
    """Texture interpolation - Linear interpolate"""

    NEAREST_MIPMAP_NEAREST = 0x2700
    """Texture interpolation - Minification filter for mipmaps"""

    LINEAR_MIPMAP_NEAREST = 0x2701
    """Texture interpolation - Minification filter for mipmaps"""

    NEAREST_MIPMAP_LINEAR = 0x2702
    """Texture interpolation - Minification filter for mipmaps"""

    LINEAR_MIPMAP_LINEAR = 0x2703
    """Texture interpolation - Minification filter for mipmaps"""

    REPEAT = gl.GL_REPEAT
    """Texture wrap mode - Repeat"""

    CLAMP_TO_EDGE = gl.GL_CLAMP_TO_EDGE
    """Texture wrap mode - Clamp to border pixel"""

    CLAMP_TO_BORDER = gl.GL_CLAMP_TO_BORDER
    """Texture wrap mode - Clamp to border color"""

    MIRRORED_REPEAT = gl.GL_MIRRORED_REPEAT
    """Texture wrap mode - Repeat mirrored"""

    # Flags

    BLEND = gl.GL_BLEND
    """Context flag - Blending"""

    DEPTH_TEST = gl.GL_DEPTH_TEST
    """Context flag - Depth testing"""

    CULL_FACE = gl.GL_CULL_FACE
    """Context flag - Face culling"""

    PROGRAM_POINT_SIZE = gl.GL_PROGRAM_POINT_SIZE
    """
    Context flag - Enables ``gl_PointSize`` in vertex or geometry shaders.

    When enabled we can write to ``gl_PointSize`` in the vertex shader to specify the point size
    for each individual point.

    If this value is not set in the shader the behavior is undefined. This means the points may
    or may not appear depending if the drivers enforce some default value for ``gl_PointSize``.

    When disabled :py:attr:`point_size` is used.
    """

    # Blend functions
    ZERO = 0x0000
    """Blend function"""

    ONE = 0x0001
    """Blend function"""

    SRC_COLOR = 0x0300
    """Blend function"""

    ONE_MINUS_SRC_COLOR = 0x0301
    """Blend function"""

    SRC_ALPHA = 0x0302
    """Blend function"""

    ONE_MINUS_SRC_ALPHA = 0x0303
    """Blend function"""

    DST_ALPHA = 0x0304
    """Blend function"""

    ONE_MINUS_DST_ALPHA = 0x0305
    """Blend function"""

    DST_COLOR = 0x0306
    """Blend function"""

    ONE_MINUS_DST_COLOR = 0x0307
    """Blend function"""

    # Blend equations
    FUNC_ADD = 0x8006
    """Blend equation - source + destination"""

    FUNC_SUBTRACT = 0x800A
    """Blend equation - source - destination"""

    FUNC_REVERSE_SUBTRACT = 0x800B
    """Blend equation - destination - source"""

    MIN = 0x8007
    """Blend equation - Minimum of source and destination"""

    MAX = 0x8008
    """Blend equation - Maximum of source and destination"""

    # Blend mode shortcuts
    BLEND_DEFAULT = 0x0302, 0x0303
    """Blend mode shortcut for default blend mode - ``SRC_ALPHA, ONE_MINUS_SRC_ALPHA``"""

    BLEND_ADDITIVE = 0x0001, 0x0001
    """Blend mode shortcut for additive blending - ``ONE, ONE``"""

    BLEND_PREMULTIPLIED_ALPHA = 0x0302, 0x0001
    """Blend mode shortcut for pre-multiplied alpha - ``SRC_ALPHA, ONE``"""

    # VertexArray: Primitives
    POINTS = gl.GL_POINTS  # 0
    """Primitive mode - points"""

    LINES = gl.GL_LINES  # 1
    """Primitive mode - lines"""

    LINE_LOOP = gl.GL_LINE_LOOP  # 2
    """Primitive mode - line loop"""

    LINE_STRIP = gl.GL_LINE_STRIP  # 3
    """Primitive mode - line strip"""

    TRIANGLES = gl.GL_TRIANGLES  # 4
    """Primitive mode - triangles"""

    TRIANGLE_STRIP = gl.GL_TRIANGLE_STRIP  # 5
    """Primitive mode - triangle strip"""

    TRIANGLE_FAN = gl.GL_TRIANGLE_FAN  # 6
    """Primitive mode - triangle fan"""

    LINES_ADJACENCY = gl.GL_LINES_ADJACENCY  # 10
    """Primitive mode - lines with adjacency"""

    LINE_STRIP_ADJACENCY = gl.GL_LINE_STRIP_ADJACENCY  # 11
    """Primitive mode - line strip with adjacency"""

    TRIANGLES_ADJACENCY = gl.GL_TRIANGLES_ADJACENCY  # 12
    """Primitive mode - triangles with adjacency"""

    TRIANGLE_STRIP_ADJACENCY = gl.GL_TRIANGLE_STRIP_ADJACENCY  # 13
    """Primitive mode - triangle strip with adjacency"""

    PATCHES = gl.GL_PATCHES
    """Primitive mode - Patch (tessellation)"""

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
    _valid_apis = ("gl", "gles")

    def __init__(
        self,
        window: pyglet.window.Window,  # type: ignore
        gc_mode: str = "context_gc",
        gl_api: str = "gl",
    ):
        self._window_ref = weakref.ref(window)
        if gl_api not in self._valid_apis:
            raise ValueError(f"Invalid gl_api. Options are: {self._valid_apis}")
        self.gl_api = gl_api
        self._info = GLInfo(self)
        self._gl_version = (self._info.MAJOR_VERSION, self._info.MINOR_VERSION)
        Context.activate(self)
        # Texture unit we use when doing operations on textures to avoid
        # affecting currently bound textures in the first units
        self.default_texture_unit: int = self._info.MAX_TEXTURE_IMAGE_UNITS - 1

        # Detect the default framebuffer
        self._screen = DefaultFrameBuffer(self)
        # Tracking active program
        self.active_program: Program | ComputeShader | None = None
        # Tracking active framebuffer. On context creation the window is the default render target
        self.active_framebuffer: Framebuffer = self._screen
        self._stats: ContextStats = ContextStats(warn_threshold=1000)

        # Hardcoded states
        # This should always be enabled
        # gl.glEnable(gl.GL_TEXTURE_CUBE_MAP_SEAMLESS)
        # Set primitive restart index to -1 by default
        if self.gl_api == "gles":
            gl.glEnable(gl.GL_PRIMITIVE_RESTART_FIXED_INDEX)
        else:
            gl.glEnable(gl.GL_PRIMITIVE_RESTART)

        self._primitive_restart_index = -1
        self.primitive_restart_index = self._primitive_restart_index

        # Detect support for glProgramUniform.
        # Assumed to be supported in gles
        self._ext_separate_shader_objects_enabled = True
        if self.gl_api == "gl":
            have_ext = gl.gl_info.have_extension("GL_ARB_separate_shader_objects")
            self._ext_separate_shader_objects_enabled = self.gl_version >= (4, 1) or have_ext

        # We enable scissor testing by default.
        # This is always set to the same value as the viewport
        # to avoid background color affecting areas outside the viewport
        gl.glEnable(gl.GL_SCISSOR_TEST)

        # States
        self._blend_func: Tuple[int, int] | Tuple[int, int, int, int] = self.BLEND_DEFAULT
        self._point_size = 1.0
        self._flags: Set[int] = set()
        self._wireframe = False
        # Options for cull_face
        self._cull_face_options = {
            "front": gl.GL_FRONT,
            "back": gl.GL_BACK,
            "front_and_back": gl.GL_FRONT_AND_BACK,
        }
        self._cull_face_options_reverse = {
            gl.GL_FRONT: "front",
            gl.GL_BACK: "back",
            gl.GL_FRONT_AND_BACK: "front_and_back",
        }

        # Context GC as default. We need to call Context.gc() to free opengl resources
        self._gc_mode = "context_gc"
        self.gc_mode = gc_mode
        #: Collected objects to gc when gc_mode is "context_gc".
        #: This can be used during debugging.
        self.objects: Deque[Any] = deque()

    @property
    def info(self) -> GLInfo:
        """
        Get the info object for this context containing information
        about hardware/driver limits and other information.

        Example::

            >> ctx.info.MAX_TEXTURE_SIZE
            (16384, 16384)
            >> ctx.info.VENDOR
            NVIDIA Corporation
            >> ctx.info.RENDERER
            NVIDIA GeForce RTX 2080 SUPER/PCIe/SSE2
        """
        return self._info

    @property
    def extensions(self) -> set[str]:
        """
        Get a set of supported OpenGL extensions strings for this context.

        This can be used to check if a specific extension is supported::

            # Check if bindless textures are supported
            "GL_ARB_bindless_texture" in ctx.extensions
            # Check for multiple extensions
            expected_extensions = {"GL_ARB_bindless_texture", "GL_ARB_get_program_binary"}
            ctx.extensions & expected_extensions == expected_extensions
        """
        return gl.gl_info.get_extensions()

    @property
    def stats(self) -> ContextStats:
        """
        Get the stats instance containing runtime information
        about creation and destruction of OpenGL objects.

        This can be useful for debugging and profiling.
        Creating and throwing away OpenGL objects can be detrimental
        to performance.

        Example::

            # Show the created and freed resource count
            >> ctx.stats.texture
            (100, 10)
            >> ctx.framebuffer
            (1, 0)
            >> ctx.buffer
            (10, 0)
        """
        return self._stats

    @property
    def window(self) -> Window:
        """The window this context belongs to (read only)."""
        window_ref = self._window_ref()
        if window_ref is None:
            raise Exception("Window not available, lost reference.")
        return window_ref

    @property
    def screen(self) -> Framebuffer:
        """The framebuffer for the window (read only)"""
        return self._screen

    @property
    def fbo(self) -> Framebuffer:
        """
        Get the currently active framebuffer (read only).
        """
        return self.active_framebuffer

    @property
    def gl_version(self) -> Tuple[int, int]:
        """
        The OpenGL major and minor version as a tuple.

        This is the reported OpenGL version from
        drivers and might be a higher version than
        you requested.
        """
        return self._gl_version

    def gc(self) -> int:
        """
        Run garbage collection of OpenGL objects for this context.
        This is only needed when ``gc_mode`` is ``context_gc``.

        Returns:
            The number of resources destroyed
        """
        # Loop the array until all objects are gone.
        # Deleting one object might add new ones so we need
        # to loop until the deque is empty
        num_objects = 0

        while len(self.objects):
            obj = self.objects.popleft()
            obj.delete()
            num_objects += 1

        return num_objects

    @property
    def gc_mode(self) -> str:
        """
        Set the garbage collection mode for OpenGL resources.
        Supported modes are::

            # Default:
            # Defer garbage collection until ctx.gc() is called
            # This can be useful to enforce the main thread to
            # run garbage collection of opengl resources
            ctx.gc_mode = "context_gc"

            # Auto collect is similar to python garbage collection.
            # This is a risky mode. Know what you are doing before using this.
            ctx.gc_mode = "auto"
        """
        return self._gc_mode

    @gc_mode.setter
    def gc_mode(self, value: str):
        modes = ["auto", "context_gc"]
        if value not in modes:
            raise ValueError("Unsupported gc_mode. Supported modes are:", modes)
        self._gc_mode = value

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
        if err == gl.GL_NO_ERROR:
            return None

        return self._errors.get(err, "GL_UNKNOWN_ERROR")

    @classmethod
    def activate(cls, ctx: Context):
        """
        Mark a context as the currently active one.

        .. Warning:: Never call this unless you know exactly what you are doing.

        Args:
            ctx: The context to activate
        """
        cls.active = ctx

    def enable(self, *flags: int):
        """
        Enables one or more context flags::

            # Single flag
            ctx.enable(ctx.BLEND)
            # Multiple flags
            ctx.enable(ctx.DEPTH_TEST, ctx.CULL_FACE)

        Args:
            *flags: The flags to enable
        """
        self._flags.update(flags)

        for flag in flags:
            gl.glEnable(flag)

    def enable_only(self, *args: int):
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

        Args:
            *args: The flags to enable
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

        if self.gl_api == "gl":
            if self.PROGRAM_POINT_SIZE in self._flags:
                gl.glEnable(self.PROGRAM_POINT_SIZE)
            else:
                gl.glDisable(self.PROGRAM_POINT_SIZE)

    @contextmanager
    def enabled(self, *flags):
        """
        Temporarily change enabled flags.

        Flags that was enabled initially will stay enabled.
        Only new enabled flags will be reversed when exiting
        the context.

        Example::

            with ctx.enabled(ctx.BLEND, ctx.CULL_FACE):
                # Render something
        """
        flags = set(flags)
        new_flags = flags - self._flags

        self.enable(*flags)
        try:
            yield
        finally:
            self.disable(*new_flags)

    @contextmanager
    def enabled_only(self, *flags):
        """
        Temporarily change enabled flags.

        Only the supplied flags with be enabled in in the context. When exiting
        the context the old flags will be restored.

        Example::

            with ctx.enabled_only(ctx.BLEND, ctx.CULL_FACE):
                # Render something
        """
        old_flags = self._flags
        self.enable_only(*flags)
        try:
            yield
        finally:
            self.enable_only(*old_flags)

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
        Check if a context flag is enabled.

        .. Warning::

            This only tracks states set through this context instance.
            It does not query the actual OpenGL state. If you change context
            flags by calling ``glEnable`` or ``glDisable`` directly you
            are on your own.
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
        """
        return self.active_framebuffer.viewport

    @viewport.setter
    def viewport(self, value: Tuple[int, int, int, int]):
        self.active_framebuffer.viewport = value

    @property
    def scissor(self) -> Tuple[int, int, int, int] | None:
        """
        Get or set the scissor box for the active framebuffer.
        This is a shortcut for :py:meth:`~arcade.gl.Framebuffer.scissor`.

        By default the scissor box is disabled and has no effect
        and will have an initial value of ``None``. The scissor
        box is enabled when setting a value and disabled when
        set to ``None``.

        Example::

            # Set and enable scissor box only drawing
            # in a 100 x 100 pixel lower left area
            ctx.scissor = 0, 0, 100, 100
            # Disable scissoring
            ctx.scissor = None
        """
        return self.fbo.scissor

    @scissor.setter
    def scissor(self, value):
        self.fbo.scissor = value

    @property
    def blend_func(self) -> Tuple[int, int] | Tuple[int, int, int, int]:
        """
        Get or set the blend function.
        This is tuple specifying how the color and
        alpha blending factors are computed for the source
        and destination pixel.

        When using a two component tuple you specify the
        blend function for the source and the destination.

        When using a four component tuple you specify the
        blend function for the source color, source alpha
        destination color and destination alpha. (separate blend
        functions for color and alpha)

        Supported blend functions are::

            ZERO
            ONE
            SRC_COLOR
            ONE_MINUS_SRC_COLOR
            DST_COLOR
            ONE_MINUS_DST_COLOR
            SRC_ALPHA
            ONE_MINUS_SRC_ALPHA
            DST_ALPHA
            ONE_MINUS_DST_ALPHA

            # Shortcuts
            DEFAULT_BLENDING     # (SRC_ALPHA, ONE_MINUS_SRC_ALPHA)
            ADDITIVE_BLENDING    # (ONE, ONE)
            PREMULTIPLIED_ALPHA  # (SRC_ALPHA, ONE)

        These enums can be accessed in the ``arcade.gl``
        module or simply as attributes of the context object.
        The raw enums from ``pyglet.gl`` can also be used.

        Example::

            # Using constants from the context object
            ctx.blend_func = ctx.ONE, ctx.ONE
            # from the gl module
            from arcade import gl
            ctx.blend_func = gl.ONE, gl.ONE
        """
        return self._blend_func

    @blend_func.setter
    def blend_func(self, value: Tuple[int, int] | Tuple[int, int, int, int]):
        self._blend_func = value
        if len(value) == 2:
            gl.glBlendFunc(*value)
        elif len(value) == 4:
            gl.glBlendFuncSeparate(*value)
        else:
            ValueError("blend_func takes a tuple of 2 or 4 values")

    # def blend_equation(self)
    # Default is FUNC_ADD

    @property
    def front_face(self) -> str:
        """
        Configure front face winding order of triangles.

        By default the counter-clockwise winding side is the front face.
        This can be set set to clockwise or counter-clockwise::

            ctx.front_face = "cw"
            ctx.front_face = "ccw"
        """
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
        """
        The face side to cull when face culling is enabled.

        By default the back face is culled. This can be set to
        front, back or front_and_back::

            ctx.cull_face = "front"
            ctx.cull_face = "back"
            ctx.cull_face = "front_and_back"
        """
        value = c_int()
        gl.glGetIntegerv(gl.GL_CULL_FACE_MODE, value)
        return self._cull_face_options_reverse[value.value]

    @cull_face.setter
    def cull_face(self, value):
        if value not in self._cull_face_options:
            raise ValueError("cull_face must be", list(self._cull_face_options.keys()))

        gl.glCullFace(self._cull_face_options[value])

    @property
    def wireframe(self) -> bool:
        """
        Get or set the wireframe mode.

        When enabled all primitives will be rendered as lines
        by changing the polygon mode.
        """
        return self._wireframe

    @wireframe.setter
    def wireframe(self, value: bool):
        self._wireframe = value
        if value:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        else:
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    @property
    def patch_vertices(self) -> int:
        """
        Get or set number of vertices that will be used to make up a single patch primitive.

        Patch primitives are consumed by the tessellation control shader (if present)
        and subsequently used for tessellation.
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
        """
        Set or get the point size. Default is `1.0`.

        Point size changes the pixel size of rendered points. The min and max values
        are limited by :py:attr:`~arcade.gl.context.Limits.POINT_SIZE_RANGE`.
        This value usually at least ``(1, 100)``, but this depends on the drivers/vendors.

        If variable point size is needed you can enable
        :py:attr:`~arcade.gl.Context.PROGRAM_POINT_SIZE` and write to ``gl_PointSize``
        in the vertex or geometry shader.

        .. Note::

            Using a geometry shader to create triangle strips from points is often a safer
            way to render large points since you don't have have any size restrictions
            and it offers more flexibility.
        """
        return self._point_size

    @point_size.setter
    def point_size(self, value: float):
        if self.gl_api == "gl":
            gl.glPointSize(self._point_size)
        self._point_size = value

    @property
    def primitive_restart_index(self) -> int:
        """
        Get or set the primitive restart index. Default is ``-1``.

        The primitive restart index can be used in index buffers
        to restart a primitive. This is for example useful when you
        use triangle strips or line strips and want to start on
        a new strip in the same buffer / draw call.
        """
        return self._primitive_restart_index

    @primitive_restart_index.setter
    def primitive_restart_index(self, value: int):
        self._primitive_restart_index = value
        if self.gl_api == "gl":
            gl.glPrimitiveRestartIndex(value)

    def finish(self) -> None:
        """
        Wait until all OpenGL rendering commands are completed.

        This function will actually stall until all work is done
        and may have severe performance implications.
        """
        gl.glFinish()

    def flush(self) -> None:
        """
        Flush the OpenGL command buffer.

        This will send all queued commands to the GPU but will not wait
        until they are completed. This is useful when you want to
        ensure that all commands are sent to the GPU before doing
        something else.
        """
        gl.glFlush()

    # Various utility methods

    def copy_framebuffer(
        self,
        src: Framebuffer,
        dst: Framebuffer,
        src_attachment_index: int = 0,
        depth: bool = True,
    ):
        """
        Copies/blits a framebuffer to another one.
        We can select one color attachment to copy plus
        an optional depth attachment.

        This operation has many restrictions to ensure it works across
        different platforms and drivers:

        * The source and destination framebuffer must be the same size
        * The formats of the attachments must be the same
        * Only the source framebuffer can be multisampled
        * Framebuffers cannot have integer attachments

        Args:
            src:
                The framebuffer to copy from
            dst:
                The framebuffer we copy to
            src_attachment_index:
                The color attachment to copy from
            depth:
                Also copy depth attachment if present
        """
        # Set source and dest framebuffer
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, src._glo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, dst._glo)

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

    # --- Resource methods ---

    def buffer(
        self, *, data: BufferProtocol | None = None, reserve: int = 0, usage: str = "static"
    ) -> Buffer:
        """
        Create an OpenGL Buffer object. The buffer will contain all zero-bytes if
        no data is supplied.

        Examples::

            # Create 1024 byte buffer
            ctx.buffer(reserve=1024)
            # Create a buffer with 1000 float values using python's array.array
            from array import array
            ctx.buffer(data=array('f', [i for in in range(1000)])
            # Create a buffer with 1000 random 32 bit floats using numpy
            self.ctx.buffer(data=np.random.random(1000).astype("f4"))

        The ``data`` parameter can be anything that implements the
        `Buffer Protocol <https://docs.python.org/3/c-api/buffer.html>`_.

        This includes ``bytes``, ``bytearray``, ``array.array``, and
        more. You may need to use typing workarounds for non-builtin
        types. See :ref:`prog-guide-gl-buffer-protocol-typing` for more
        information.

        The ``usage`` parameter enables the GL implementation to make more intelligent
        decisions that may impact buffer object performance. It does not add any restrictions.
        If in doubt, skip this parameter and revisit when optimizing. The result
        are likely to be different between vendors/drivers or may not have any effect.
        Always use the default static usage for buffers that don't change.

        The available values mean the following::

            stream
                The data contents will be modified once and used at most a few times.
            static
                The data contents will be modified once and used many times.
            dynamic
                The data contents will be modified repeatedly and used many times.

        Args:
            data:
                The buffer data. This can be a ``bytes`` instance or any
                any other object supporting the buffer protocol.
            reserve:
                The number of bytes to reserve
            usage:
                Buffer usage. 'static', 'dynamic' or 'stream'
        """
        return Buffer(self, data, reserve=reserve, usage=usage)

    def framebuffer(
        self,
        *,
        color_attachments: Texture2D | List[Texture2D] | None = None,
        depth_attachment: Texture2D | None = None,
    ) -> Framebuffer:
        """Create a Framebuffer.

        Args:
            color_attachments:
                List of textures we want to render into
            depth_attachment:
                Depth texture
        """
        return Framebuffer(
            self, color_attachments=color_attachments or [], depth_attachment=depth_attachment
        )

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
    ) -> Texture2D:
        """
        Create a 2D Texture.

        Example::

            # Create a 1024 x 1024 RGBA texture
            image = PIL.Image.open("my_texture.png")
            ctx.texture(size=(1024, 1024), components=4, data=image.tobytes())

            # Create and compress a texture. The compression format is set by the internal_format
            image = PIL.Image.open("my_texture.png")
            ctx.texture(
                size=(1024, 1024),
                components=4,
                compressed=True,
                internal_format=gl.GL_COMPRESSED_RGBA_S3TC_DXT1_EXT,
                data=image.tobytes(),
            )

            # Create a compressed texture from raw compressed data. This is an extremely
            # fast way to load a large number of textures.
            image_bytes = "<raw compressed data from some source>"
            ctx.texture(
                size=(1024, 1024),
                components=4,
                internal_format=gl.GL_COMPRESSED_RGBA_S3TC_DXT1_EXT,
                compressed_data=True,
                data=image_bytes,
            )

        Wrap modes: ``GL_REPEAT``, ``GL_MIRRORED_REPEAT``, ``GL_CLAMP_TO_EDGE``,
        ``GL_CLAMP_TO_BORDER``

        Minifying filters: ``GL_NEAREST``, ``GL_LINEAR``, ``GL_NEAREST_MIPMAP_NEAREST``,
        ``GL_LINEAR_MIPMAP_NEAREST`` ``GL_NEAREST_MIPMAP_LINEAR``, ``GL_LINEAR_MIPMAP_LINEAR``

        Magnifying filters: ``GL_NEAREST``, ``GL_LINEAR``

        Args:
            size:
                The size of the texture
            components:
                Number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
            dtype:
                The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
            data:
                The texture data. Can be ``bytes``
                or any object supporting the buffer protocol.
            wrap_x:
                How the texture wraps in x direction
            wrap_y:
                How the texture wraps in y direction
            filter:
                Minification and magnification filter
            samples:
                Creates a multisampled texture for values > 0
            immutable:
                Make the storage (not the contents) immutable. This can sometimes be
                required when using textures with compute shaders.
            internal_format:
                The internal format of the texture. This can be used to
                enable sRGB or texture compression.
            compressed:
                Set to True if you want the texture to be compressed.
                This assumes you have set a internal_format to a compressed format.
            compressed_data:
                Set to True if you are passing in raw compressed pixel data.
                This implies ``compressed=True``.
        """
        compressed = compressed or compressed_data

        return Texture2D(
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
    ) -> TextureArray:
        """
        Create a 2D Texture Array.

        This is a 2D texture with multiple layers. This is useful for
        storing multiple textures in a single texture object. This can
        be used for texture atlases or storing multiple frames of an
        animation in a single texture or equally sized tile textures.

        Note that ``size`` is a 3-tuple where the last value is the number  of layers.

        See :py:meth:`~arcade.gl.Context.texture` for arguments.
        """
        return TextureArray(
            self,
            size,
            components=components,
            dtype=dtype,
            data=data,
            wrap_x=wrap_x,
            wrap_y=wrap_y,
            filter=filter,
        )

    def depth_texture(
        self, size: Tuple[int, int], *, data: BufferProtocol | None = None
    ) -> Texture2D:
        """
        Create a 2D depth texture. Can be used as a depth attachment
        in a :py:class:`~arcade.gl.Framebuffer`.

        Args:
            size:
                The size of the texture
            data:
                The texture data. Can be``bytes`` or any object
                supporting the buffer protocol.
        """
        return Texture2D(self, size, data=data, depth=True)

    def sampler(self, texture: Texture2D) -> Sampler:
        """
        Create a sampler object for a texture.

        Args:
            texture:
                The texture to create a sampler for
        """
        return Sampler(self, texture)

    def geometry(
        self,
        content: Sequence[BufferDescription] | None = None,
        index_buffer: Buffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ):
        """
        Create a Geometry instance. This is Arcade's version of a vertex array adding
        a lot of convenience for the user. Geometry objects are fairly light. They are
        mainly responsible for automatically map buffer inputs to your shader(s)
        and provide various methods for rendering or processing this geometry,

        The same geometry can be rendered with different
        programs as long as your shader is using one or more of the input attribute.
        This means geometry with positions and colors can be rendered with a program
        only using the positions. We will automatically map what is necessary and
        cache these mappings internally for performance.

        In short, the geometry object is a light object that describes what buffers
        contains and automatically negotiate with shaders/programs. This is a very
        complex field in OpenGL so the Geometry object provides substantial time
        savings and greatly reduces the complexity of your code.

        Geometry also provide rendering methods supporting the following:

        * Rendering geometry with and without index buffer
        * Rendering your geometry using instancing. Per instance buffers can be provided
          or the current instance can be looked up using ``gl_InstanceID`` in shaders.
        * Running transform feedback shaders that writes to buffers instead the screen.
          This can write to one or multiple buffer.
        * Render your geometry with indirect rendering. This means packing
          multiple meshes into the same buffer(s) and batch drawing them.

        Examples::

            # Single buffer geometry with a vec2 vertex position attribute
            ctx.geometry([BufferDescription(buffer, '2f', ["in_vert"])], mode=ctx.TRIANGLES)

            # Single interleaved buffer with two attributes. A vec2 position and vec2 velocity
            ctx.geometry([
                    BufferDescription(buffer, '2f 2f', ["in_vert", "in_velocity"])
                ],
                mode=ctx.POINTS,
            )

            # Geometry with index buffer
            ctx.geometry(
                [BufferDescription(buffer, '2f', ["in_vert"])],
                index_buffer=ibo,
                mode=ctx.TRIANGLES,
            )

            # Separate buffers
            ctx.geometry([
                    BufferDescription(buffer_pos, '2f', ["in_vert"])
                    BufferDescription(buffer_vel, '2f', ["in_velocity"])
                ],
                mode=ctx.POINTS,
            )

            # Providing per-instance data for instancing
            ctx.geometry([
                    BufferDescription(buffer_pos, '2f', ["in_vert"])
                    BufferDescription(buffer_instance_pos, '2f', ["in_offset"], instanced=True)
                ],
                mode=ctx.POINTS,
            )

        Args:
            content:
                List of :py:class:`~arcade.gl.BufferDescription`
            index_buffer:
                Index/element buffer
            mode:
                The default draw mode
            mode:
                The default draw mode
            index_element_size:
                Byte size of a single index/element in the index buffer.
                In other words, the index buffer can be 1, 2 or 4 byte integers.
                Can be 1, 2 or 4 (8, 16 or 32 bit unsigned integer)
        """
        return Geometry(
            self,
            content,
            index_buffer=index_buffer,
            mode=mode,
            index_element_size=index_element_size,
        )

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
    ) -> Program:
        """
        Create a :py:class:`~arcade.gl.Program` given shader sources
        and other settings.

        Args:
            vertex_shader:
                vertex shader source
            fragment_shader:
                fragment shader source
            geometry_shader:
                geometry shader source
            tess_control_shader:
                tessellation control shader source
            tess_evaluation_shader:
                tessellation evaluation shader source
            common:
                Common shader sources injected into all shaders
            defines:
                Substitute #defines values in the source
            varyings:
                The name of the out attributes in a transform shader.
                This is normally not necessary since we auto detect them,
                but some more complex out structures we can't detect.
            varyings_capture_mode:
                The capture mode for transforms.

                - ``"interleaved"`` means all out attribute will be written to a single buffer.
                - ``"separate"`` means each out attribute will be written separate buffers.

                Based on these settings the ``transform()`` method will accept a single
                buffer or a list of buffer.
        """
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

        return Program(
            self,
            vertex_shader=source_vs.get_source(defines=defines),
            fragment_shader=source_fs.get_source(defines=defines) if source_fs else None,
            geometry_shader=source_geo.get_source(defines=defines) if source_geo else None,
            tess_control_shader=source_tc.get_source(defines=defines) if source_tc else None,
            tess_evaluation_shader=source_te.get_source(defines=defines) if source_te else None,
            varyings=out_attributes,
            varyings_capture_mode=varyings_capture_mode,
        )

    def query(self, *, samples=True, time=True, primitives=True) -> Query:
        """
        Create a query object for measuring rendering calls in opengl.

        Args:
            samples: Collect written samples
            time: Measure rendering duration
            primitives: Collect the number of primitives emitted
        """
        return Query(self, samples=samples, time=time, primitives=primitives)

    def compute_shader(self, *, source: str, common: Iterable[str] = ()) -> ComputeShader:
        """
        Create a compute shader.

        Args:
            source:
                The glsl source
            common:
                Common / library source injected into compute shader
        """
        src = ShaderSource(self, source, common, gl.GL_COMPUTE_SHADER)
        return ComputeShader(self, src.get_source())


class ContextStats:
    """
    Runtime allocation statistics of OpenGL objects.
    """

    def __init__(self, warn_threshold=100):
        self.warn_threshold = warn_threshold

        self.texture = (0, 0)
        """Textures (created, freed)"""

        self.framebuffer = (0, 0)
        """Framebuffers (created, freed)"""

        self.buffer = (0, 0)
        """Buffers (created, freed)"""

        self.program = (0, 0)
        """Programs (created, freed)"""

        self.vertex_array = (0, 0)
        """Vertex Arrays (created, freed)"""

        self.geometry = (0, 0)
        """Geometry (created, freed)"""

        self.compute_shader = (0, 0)
        """Compute Shaders (created, freed)"""

        self.query = (0, 0)
        """Queries (created, freed)"""

    def incr(self, key: str) -> None:
        """
        Increments a counter.

        Args:
            key: The attribute name / counter to increment.
        """
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
        """
        Decrement a counter.

        Args:
            key: The attribute name / counter to decrement.
        """
        created, freed = getattr(self, key)
        setattr(self, key, (created, freed + 1))


class GLInfo:
    """OpenGL info and capabilities"""

    def __init__(self, ctx):
        self._ctx = ctx

        self.MINOR_VERSION = self.get(gl.GL_MINOR_VERSION)
        """Minor version number of the OpenGL API supported by the current context"""

        self.MAJOR_VERSION = self.get(gl.GL_MAJOR_VERSION)
        """Major version number of the OpenGL API supported by the current context."""

        self.VENDOR = self.get_str(gl.GL_VENDOR)
        """The vendor string. For example 'NVIDIA Corporation'"""

        self.RENDERER = self.get_str(gl.GL_RENDERER)
        """The renderer things. For example "NVIDIA GeForce RTX 2080 SUPER/PCIe/SSE2"""

        self.SAMPLE_BUFFERS = self.get(gl.GL_SAMPLE_BUFFERS)
        """Value indicating the number of sample buffers associated with the framebuffer"""

        self.SUBPIXEL_BITS = self.get(gl.GL_SUBPIXEL_BITS)
        """
        An estimate of the number of bits of subpixel resolution
        that are used to position rasterized geometry in window coordinates
        """

        self.UNIFORM_BUFFER_OFFSET_ALIGNMENT = self.get(gl.GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT)
        """Minimum required alignment for uniform buffer sizes and offset"""

        self.MAX_ARRAY_TEXTURE_LAYERS = self.get(gl.GL_MAX_ARRAY_TEXTURE_LAYERS)
        """
        Value indicates the maximum number of layers allowed in an array texture,
        and must be at least 256
        """

        self.MAX_3D_TEXTURE_SIZE = self.get(gl.GL_MAX_3D_TEXTURE_SIZE)
        """
        A rough estimate of the largest 3D texture that the GL can handle.
        The value must be at least 64
        """

        self.MAX_COLOR_ATTACHMENTS = self.get(gl.GL_MAX_COLOR_ATTACHMENTS)
        """Maximum number of color attachments in a framebuffer"""

        self.MAX_COLOR_TEXTURE_SAMPLES = self.get(gl.GL_MAX_COLOR_TEXTURE_SAMPLES)
        """Maximum number of samples in a color multisample texture"""

        self.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS
        )
        """the number of words for fragment shader uniform variables in all uniform blocks"""

        self.MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS
        )
        """Number of words for geometry shader uniform variables in all uniform blocks"""

        self.MAX_COMBINED_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS)
        """
        Maximum supported texture image units that can be used to access texture
        maps from the vertex shader
        """

        self.MAX_COMBINED_UNIFORM_BLOCKS = self.get(gl.GL_MAX_COMBINED_UNIFORM_BLOCKS)
        """Maximum number of uniform blocks per program"""

        self.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS = self.get(
            gl.GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS
        )
        """Number of words for vertex shader uniform variables in all uniform blocks"""

        self.MAX_CUBE_MAP_TEXTURE_SIZE = self.get(gl.GL_MAX_CUBE_MAP_TEXTURE_SIZE)
        """A rough estimate of the largest cube-map texture that the GL can handle"""

        self.MAX_DEPTH_TEXTURE_SAMPLES = self.get(gl.GL_MAX_DEPTH_TEXTURE_SAMPLES)
        """Maximum number of samples in a multisample depth or depth-stencil texture"""

        self.MAX_DRAW_BUFFERS = self.get(gl.GL_MAX_DRAW_BUFFERS)
        """Maximum number of simultaneous outputs that may be written in a fragment shader"""

        self.MAX_ELEMENTS_INDICES = self.get(gl.GL_MAX_ELEMENTS_INDICES)
        """Recommended maximum number of vertex array indices"""

        self.MAX_ELEMENTS_VERTICES = self.get(gl.GL_MAX_ELEMENTS_VERTICES)
        """Recommended maximum number of vertex array vertices"""

        self.MAX_FRAGMENT_INPUT_COMPONENTS = self.get(gl.GL_MAX_FRAGMENT_INPUT_COMPONENTS)
        """Maximum number of components of the inputs read by the fragment shader"""

        self.MAX_FRAGMENT_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_COMPONENTS)
        """
        Maximum number of individual floating-point, integer, or boolean values that can be
        held in uniform variable storage for a fragment shader
        """

        self.MAX_FRAGMENT_UNIFORM_VECTORS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_VECTORS)
        """
        Maximum number of individual 4-vectors of floating-point, integer,
        or boolean values that can be held in uniform variable storage for a fragment shader
        """

        self.MAX_FRAGMENT_UNIFORM_BLOCKS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_BLOCKS)
        """Maximum number of uniform blocks per fragment shader."""

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

        self.MAX_SAMPLES = self.get(gl.GL_MAX_SAMPLES)
        """Maximum samples for a framebuffer"""

        self.MAX_RENDERBUFFER_SIZE = self.get(gl.GL_MAX_RENDERBUFFER_SIZE)
        """Maximum supported size for renderbuffers"""

        self.MAX_SAMPLE_MASK_WORDS = self.get(gl.GL_MAX_SAMPLE_MASK_WORDS)
        """Maximum number of sample mask words"""

        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        """Maximum number of uniform buffer binding points on the context"""

        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        """Maximum number of uniform buffer binding points on the context"""

        self.MAX_TEXTURE_SIZE = self.get(gl.GL_MAX_TEXTURE_SIZE)
        """The value gives a rough estimate of the largest texture that the GL can handle"""

        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        """Maximum number of uniform buffer binding points on the context"""

        self.MAX_UNIFORM_BLOCK_SIZE = self.get(gl.GL_MAX_UNIFORM_BLOCK_SIZE)
        """Maximum size in basic machine units of a uniform block"""

        self.MAX_VARYING_VECTORS = self.get(gl.GL_MAX_VARYING_VECTORS)
        """The number 4-vectors for varying variables"""

        self.MAX_VERTEX_ATTRIBS = self.get(gl.GL_MAX_VERTEX_ATTRIBS)
        """Maximum number of 4-component generic vertex attributes accessible to a vertex shader."""

        self.MAX_VERTEX_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS)
        """
        Maximum supported texture image units that can be used to access texture
        maps from the vertex shader.
        """

        self.MAX_VERTEX_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_VERTEX_UNIFORM_COMPONENTS)
        """
        Maximum number of individual floating-point, integer, or boolean values that
        can be held in uniform variable storage for a vertex shader
        """

        self.MAX_VERTEX_UNIFORM_VECTORS = self.get(gl.GL_MAX_VERTEX_UNIFORM_VECTORS)
        """
        Maximum number of 4-vectors that may be held in uniform variable storage
        for the vertex shader
        """

        self.MAX_VERTEX_OUTPUT_COMPONENTS = self.get(gl.GL_MAX_VERTEX_OUTPUT_COMPONENTS)
        """Maximum number of components of output written by a vertex shader"""

        self.MAX_VERTEX_UNIFORM_BLOCKS = self.get(gl.GL_MAX_VERTEX_UNIFORM_BLOCKS)
        """Maximum number of uniform blocks per vertex shader."""

        # self.MAX_VERTEX_ATTRIB_RELATIVE_OFFSET = self.get(
        #     gl.GL_MAX_VERTEX_ATTRIB_RELATIVE_OFFSET
        # )
        # self.MAX_VERTEX_ATTRIB_BINDINGS = self.get(gl.GL_MAX_VERTEX_ATTRIB_BINDINGS)

        self.MAX_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_TEXTURE_IMAGE_UNITS)
        """Number of texture units"""

        self.MAX_TEXTURE_MAX_ANISOTROPY = self.get_float(gl.GL_MAX_TEXTURE_MAX_ANISOTROPY, 1.0)
        """The highest supported anisotropy value. Usually 8.0 or 16.0."""

        self.MAX_VIEWPORT_DIMS: Tuple[int, int] = self.get_int_tuple(gl.GL_MAX_VIEWPORT_DIMS, 2)
        """
        The maximum support window or framebuffer viewport.
        This is usually the same as the maximum texture size
        """

        self.MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS = self.get(
            gl.GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS
        )
        """
        How many buffers we can have as output when doing a transform(feedback).
        This is usually 4.
        """

        self.POINT_SIZE_RANGE = self.get_int_tuple(gl.GL_POINT_SIZE_RANGE, 2)
        """The minimum and maximum point size"""

        err = self._ctx.error
        if err:
            from warnings import warn

            warn("Error happened while querying of limits. Moving on ..")

    @overload
    def get_int_tuple(self, enum: GLenumLike, length: Literal[2]) -> Tuple[int, int]: ...

    @overload
    def get_int_tuple(self, enum: GLenumLike, length: int) -> Tuple[int, ...]: ...

    def get_int_tuple(self, enum: GLenumLike, length: int):
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

    def get(self, enum: GLenumLike, default=0) -> int:
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

    def get_float(self, enum: GLenumLike, default=0.0) -> float:
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

    def get_str(self, enum: GLenumLike) -> str:
        """
        Get a string limit.

        Args:
            enum: The enum to query
        """
        try:
            return cast(gl.glGetString(enum), c_char_p).value.decode()  # type: ignore
        except pyglet.gl.lib.GLException:
            return "Unknown"
