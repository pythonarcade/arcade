from __future__ import annotations

import logging
import weakref
from abc import ABC, abstractmethod
from collections import deque
from contextlib import contextmanager
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
from pyglet.window import Window

from ..types import BufferProtocol
from . import enums
from .buffer import Buffer
from .compute_shader import ComputeShader
from .framebuffer import DefaultFrameBuffer, Framebuffer
from .program import Program
from .provider import get_provider
from .query import Query
from .sampler import Sampler
from .texture import Texture2D
from .texture_array import TextureArray
from .vertex_array import Geometry

LOG = logging.getLogger(__name__)


class Context(ABC):
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

    # --- Store the most commonly used OpenGL constants
    # Texture

    NEAREST = enums.NEAREST
    """Texture interpolation - Nearest pixel"""

    LINEAR = enums.LINEAR
    """Texture interpolation - Linear interpolate"""

    NEAREST_MIPMAP_NEAREST = enums.NEAREST_MIPMAP_NEAREST
    """Texture interpolation - Minification filter for mipmaps"""

    LINEAR_MIPMAP_NEAREST = enums.LINEAR_MIPMAP_NEAREST
    """Texture interpolation - Minification filter for mipmaps"""

    NEAREST_MIPMAP_LINEAR = enums.NEAREST_MIPMAP_LINEAR
    """Texture interpolation - Minification filter for mipmaps"""

    LINEAR_MIPMAP_LINEAR = enums.LINEAR_MIPMAP_LINEAR
    """Texture interpolation - Minification filter for mipmaps"""

    REPEAT = enums.REPEAT
    """Texture wrap mode - Repeat"""

    CLAMP_TO_EDGE = enums.CLAMP_TO_EDGE
    """Texture wrap mode - Clamp to border pixel"""

    MIRRORED_REPEAT = enums.MIRRORED_REPEAT
    """Texture wrap mode - Repeat mirrored"""

    # Flags

    BLEND = enums.BLEND
    """Context flag - Blending"""

    DEPTH_TEST = enums.DEPTH_TEST
    """Context flag - Depth testing"""

    CULL_FACE = enums.CULL_FACE
    """Context flag - Face culling"""

    # Blend functions
    ZERO = enums.ZERO
    """Blend function"""

    ONE = enums.ONE
    """Blend function"""

    SRC_COLOR = enums.SRC_COLOR
    """Blend function"""

    ONE_MINUS_SRC_COLOR = enums.ONE_MINUS_SRC_COLOR
    """Blend function"""

    SRC_ALPHA = enums.SRC_ALPHA
    """Blend function"""

    ONE_MINUS_SRC_ALPHA = enums.ONE_MINUS_SRC_ALPHA
    """Blend function"""

    DST_ALPHA = enums.DST_ALPHA
    """Blend function"""

    ONE_MINUS_DST_ALPHA = enums.ONE_MINUS_DST_ALPHA
    """Blend function"""

    DST_COLOR = enums.DST_COLOR
    """Blend function"""

    ONE_MINUS_DST_COLOR = enums.ONE_MINUS_DST_COLOR
    """Blend function"""

    # Blend equations
    FUNC_ADD = enums.FUNC_ADD
    """Blend equation - source + destination"""

    FUNC_SUBTRACT = enums.FUNC_SUBTRACT
    """Blend equation - source - destination"""

    FUNC_REVERSE_SUBTRACT = enums.FUNC_REVERSE_SUBTRACT
    """Blend equation - destination - source"""

    MIN = enums.MIN
    """Blend equation - Minimum of source and destination"""

    MAX = enums.MAX
    """Blend equation - Maximum of source and destination"""

    # Blend mode shortcuts
    BLEND_DEFAULT = enums.BLEND_DEFAULT
    """Blend mode shortcut for default blend mode - ``SRC_ALPHA, ONE_MINUS_SRC_ALPHA``"""

    BLEND_ADDITIVE = enums.BLEND_ADDITIVE
    """Blend mode shortcut for additive blending - ``ONE, ONE``"""

    BLEND_PREMULTIPLIED_ALPHA = enums.BLEND_PREMULTIPLIED_ALPHA
    """Blend mode shortcut for pre-multiplied alpha - ``SRC_ALPHA, ONE``"""

    # VertexArray: Primitives
    POINTS = enums.POINTS  # 0
    """Primitive mode - points"""

    LINES = enums.LINES  # 1
    """Primitive mode - lines"""

    LINE_LOOP = enums.LINE_LOOP  # 2
    """Primitive mode - line loop"""

    LINE_STRIP = enums.LINE_STRIP  # 3
    """Primitive mode - line strip"""

    TRIANGLES = enums.TRIANGLES  # 4
    """Primitive mode - triangles"""

    TRIANGLE_STRIP = enums.TRIANGLE_STRIP  # 5
    """Primitive mode - triangle strip"""

    TRIANGLE_FAN = enums.TRIANGLE_FAN  # 6
    """Primitive mode - triangle fan"""

    ##### ADJACENCY VALUES ARE NOT SUPPORTED BY WEBGL
    ##### WE ARE LEAVING THESE VALUES IN THE COMMON IMPLEMENTATION
    ##### TO MAKE IMPLEMENTATION EASIER, BECAUSE WEBGL WILL FAIL
    ##### BEFORE USAGE OF THESE MATTERS

    LINES_ADJACENCY = enums.LINES_ADJACENCY  # 10
    """Primitive mode - lines with adjacency"""

    LINE_STRIP_ADJACENCY = enums.LINE_STRIP_ADJACENCY  # 11
    """Primitive mode - line strip with adjacency"""

    TRIANGLES_ADJACENCY = enums.TRIANGLES_ADJACENCY  # 12
    """Primitive mode - triangles with adjacency"""

    TRIANGLE_STRIP_ADJACENCY = enums.TRIANGLE_STRIP_ADJACENCY  # 13
    """Primitive mode - triangle strip with adjacency"""

    # The most common error enums
    _errors = {
        enums.INVALID_ENUM: "INVALID_ENUM",
        enums.INVALID_VALUE: "INVALID_VALUE",
        enums.INVALID_OPERATION: "INVALID_OPERATION",
        enums.INVALID_FRAMEBUFFER_OPERATION: "INVALID_FRAMEBUFFER_OPERATION",
        enums.OUT_OF_MEMORY: "OUT_OF_MEMORY",
    }

    def __init__(
        self,
        window: pyglet.window.Window,  # type: ignore
        gc_mode: str = "context_gc",
        gl_api: str = "gl",  # This is ignored here, but used in implementation classes
    ):
        self._window_ref = weakref.ref(window)
        self._info = get_provider().create_info(self)

        Context.activate(self)
        # Texture unit we use when doing operations on textures to avoid
        # affecting currently bound textures in the first units
        self.default_texture_unit: int = self._info.MAX_TEXTURE_IMAGE_UNITS - 1

        # Detect the default framebuffer
        self._screen = self._create_default_framebuffer()
        # Tracking active program
        self.active_program: Program | ComputeShader | None = None
        # Tracking active framebuffer. On context creation the window is the default render target
        self.active_framebuffer: Framebuffer = self._screen
        self._stats: ContextStats = ContextStats(warn_threshold=1000)

        self._primitive_restart_index = -1
        self.primitive_restart_index = self._primitive_restart_index

        # States
        self._blend_func: Tuple[int, int] | Tuple[int, int, int, int] = self.BLEND_DEFAULT
        self._point_size = 1.0
        self._flags: Set[int] = set()
        self._wireframe = False
        # Options for cull_face
        self._cull_face_options = {
            "front": enums.FRONT,
            "back": enums.BACK,
            "front_and_back": enums.FRONT_AND_BACK,
        }
        self._cull_face_options_reverse = {
            enums.FRONT: "front",
            enums.BACK: "back",
            enums.FRONT_AND_BACK: "front_and_back",
        }

        # Context GC as default. We need to call Context.gc() to free opengl resources
        self._gc_mode = "context_gc"
        self.gc_mode = gc_mode
        #: Collected objects to gc when gc_mode is "context_gc".
        #: This can be used during debugging.
        self.objects: Deque[Any] = deque()

    @abstractmethod
    def _create_default_framebuffer(self) -> DefaultFrameBuffer:
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    def info(self) -> Info:
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
    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def error(self) -> str | None:
        """Check OpenGL error

        Returns a string representation of the occurring error
        or ``None`` of no errors has occurred.

        Example::

            err = ctx.error
            if err:
                raise RuntimeError("OpenGL error: {err}")
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @classmethod
    def activate(cls, ctx: Context):
        """
        Mark a context as the currently active one.

        .. Warning:: Never call this unless you know exactly what you are doing.

        Args:
            ctx: The context to activate
        """
        cls.active = ctx

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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

    @abstractmethod
    def disable(self, *args):
        """
        Disable one or more context flags::

            # Single flag
            ctx.disable(ctx.BLEND)
            # Multiple flags
            ctx.disable(ctx.DEPTH_TEST, ctx.CULL_FACE)
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def blend_func(self, value: Tuple[int, int] | Tuple[int, int, int, int]):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    # def blend_equation(self)
    # Default is FUNC_ADD

    @property
    @abstractmethod
    def front_face(self) -> str:
        """
        Configure front face winding order of triangles.

        By default the counter-clockwise winding side is the front face.
        This can be set set to clockwise or counter-clockwise::

            ctx.front_face = "cw"
            ctx.front_face = "ccw"
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @front_face.setter
    @abstractmethod
    def front_face(self, value: str):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def cull_face(self) -> str:
        """
        The face side to cull when face culling is enabled.

        By default the back face is culled. This can be set to
        front, back or front_and_back::

            ctx.cull_face = "front"
            ctx.cull_face = "back"
            ctx.cull_face = "front_and_back"
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @cull_face.setter
    def cull_face(self, value):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    def wireframe(self) -> bool:
        """
        Get or set the wireframe mode.

        When enabled all primitives will be rendered as lines
        by changing the polygon mode.
        """
        return self._wireframe

    @wireframe.setter
    @abstractmethod
    def wireframe(self, value: bool):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def patch_vertices(self) -> int:
        """
        Get or set number of vertices that will be used to make up a single patch primitive.

        Patch primitives are consumed by the tessellation control shader (if present)
        and subsequently used for tessellation.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @patch_vertices.setter
    @abstractmethod
    def patch_vertices(self, value: int):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def point_size(self, value: float):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def primitive_restart_index(self, value: int):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def finish(self) -> None:
        """
        Wait until all OpenGL rendering commands are completed.

        This function will actually stall until all work is done
        and may have severe performance implications.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def flush(self) -> None:
        """
        Flush the OpenGL command buffer.

        This will send all queued commands to the GPU but will not wait
        until they are completed. This is useful when you want to
        ensure that all commands are sent to the GPU before doing
        something else.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    # Various utility methods

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    # --- Resource methods ---

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def texture(
        self,
        size: Tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        wrap_x=None,
        wrap_y=None,
        filter=None,
        samples: int = 0,
        immutable: bool = False,
        internal_format=None,
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def texture_array(
        self,
        size: Tuple[int, int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        wrap_x=None,
        wrap_y=None,
        filter=None,
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def sampler(self, texture: Texture2D) -> Sampler:
        """
        Create a sampler object for a texture.

        Args:
            texture:
                The texture to create a sampler for
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def geometry(
        self,
        content=None,
        index_buffer: Buffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ) -> Geometry:
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def query(self, *, samples=True, time=True, primitives=True) -> Query:
        """
        Create a query object for measuring rendering calls in opengl.

        Args:
            samples: Collect written samples
            time: Measure rendering duration
            primitives: Collect the number of primitives emitted
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def compute_shader(self, *, source: str, common: Iterable[str] = ()) -> ComputeShader:
        """
        Create a compute shader.

        Args:
            source:
                The glsl source
            common:
                Common / library source injected into compute shader
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")


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


class Info(ABC):
    """OpenGL info and capabilities"""

    def __init__(self, ctx):
        self._ctx = ctx

        self.VENDOR = self.get_str(enums.VENDOR)
        """The vendor string. For example 'NVIDIA Corporation'"""

        self.RENDERER = self.get_str(enums.RENDERER)
        """The renderer things. For example "NVIDIA GeForce RTX 2080 SUPER/PCIe/SSE2"""

        self.SAMPLE_BUFFERS = self.get(enums.SAMPLE_BUFFERS)
        """Value indicating the number of sample buffers associated with the framebuffer"""

        self.SUBPIXEL_BITS = self.get(enums.SUBPIXEL_BITS)
        """
        An estimate of the number of bits of subpixel resolution
        that are used to position rasterized geometry in window coordinates
        """

        self.UNIFORM_BUFFER_OFFSET_ALIGNMENT = self.get(enums.UNIFORM_BUFFER_OFFSET_ALIGNMENT)
        """Minimum required alignment for uniform buffer sizes and offset"""

        self.MAX_ARRAY_TEXTURE_LAYERS = self.get(enums.MAX_ARRAY_TEXTURE_LAYERS)
        """
        Value indicates the maximum number of layers allowed in an array texture,
        and must be at least 256
        """

        self.MAX_3D_TEXTURE_SIZE = self.get(enums.MAX_3D_TEXTURE_SIZE)
        """
        A rough estimate of the largest 3D texture that the GL can handle.
        The value must be at least 64
        """

        self.MAX_COLOR_ATTACHMENTS = self.get(enums.MAX_COLOR_ATTACHMENTS)
        """Maximum number of color attachments in a framebuffer"""

        self.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS = self.get(
            enums.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS
        )
        """Number of words for vertex shader uniform variables in all uniform blocks"""

        self.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS = self.get(
            enums.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS
        )
        """the number of words for fragment shader uniform variables in all uniform blocks"""

        self.MAX_COMBINED_TEXTURE_IMAGE_UNITS = self.get(enums.MAX_COMBINED_TEXTURE_IMAGE_UNITS)
        """
        Maximum supported texture image units that can be used to access texture
        maps from the vertex shader
        """

        self.MAX_COMBINED_UNIFORM_BLOCKS = self.get(enums.MAX_COMBINED_UNIFORM_BLOCKS)
        """Maximum number of uniform blocks per program"""

        self.MAX_CUBE_MAP_TEXTURE_SIZE = self.get(enums.MAX_CUBE_MAP_TEXTURE_SIZE)
        """A rough estimate of the largest cube-map texture that the GL can handle"""

        self.MAX_DRAW_BUFFERS = self.get(enums.MAX_DRAW_BUFFERS)
        """Maximum number of simultaneous outputs that may be written in a fragment shader"""

        self.MAX_ELEMENTS_VERTICES = self.get(enums.MAX_ELEMENTS_VERTICES)
        """Recommended maximum number of vertex array vertices"""

        self.MAX_ELEMENTS_INDICES = self.get(enums.MAX_ELEMENTS_INDICES)
        """Recommended maximum number of vertex array indices"""

        self.MAX_FRAGMENT_INPUT_COMPONENTS = self.get(enums.MAX_FRAGMENT_INPUT_COMPONENTS)
        """Maximum number of components of the inputs read by the fragment shader"""

        self.MAX_FRAGMENT_UNIFORM_COMPONENTS = self.get(enums.MAX_FRAGMENT_UNIFORM_COMPONENTS)
        """
        Maximum number of individual floating-point, integer, or boolean values that can be
        held in uniform variable storage for a fragment shader
        """

        self.MAX_FRAGMENT_UNIFORM_VECTORS = self.get(enums.MAX_FRAGMENT_UNIFORM_VECTORS)
        """
        Maximum number of individual 4-vectors of floating-point, integer,
        or boolean values that can be held in uniform variable storage for a fragment shader
        """

        self.MAX_FRAGMENT_UNIFORM_BLOCKS = self.get(enums.MAX_FRAGMENT_UNIFORM_BLOCKS)
        """Maximum number of uniform blocks per fragment shader."""

        self.MAX_SAMPLES = self.get(enums.MAX_SAMPLES)
        """Maximum samples for a framebuffer"""

        self.MAX_RENDERBUFFER_SIZE = self.get(enums.MAX_RENDERBUFFER_SIZE)
        """Maximum supported size for renderbuffers"""

        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(enums.MAX_UNIFORM_BUFFER_BINDINGS)
        """Maximum number of uniform buffer binding points on the context"""

        self.MAX_TEXTURE_SIZE = self.get(enums.MAX_TEXTURE_SIZE)
        """The value gives a rough estimate of the largest texture that the GL can handle"""

        self.MAX_UNIFORM_BLOCK_SIZE = self.get(enums.MAX_UNIFORM_BLOCK_SIZE)
        """Maximum size in basic machine units of a uniform block"""

        self.MAX_VARYING_VECTORS = self.get(enums.MAX_VARYING_VECTORS)
        """The number 4-vectors for varying variables"""

        self.MAX_VERTEX_ATTRIBS = self.get(enums.MAX_VERTEX_ATTRIBS)
        """Maximum number of 4-component generic vertex attributes accessible to a vertex shader."""

        self.MAX_VERTEX_TEXTURE_IMAGE_UNITS = self.get(enums.MAX_VERTEX_TEXTURE_IMAGE_UNITS)
        """
        Maximum supported texture image units that can be used to access texture
        maps from the vertex shader.
        """

        self.MAX_VERTEX_UNIFORM_COMPONENTS = self.get(enums.MAX_VERTEX_UNIFORM_COMPONENTS)
        """
        Maximum number of individual floating-point, integer, or boolean values that
        can be held in uniform variable storage for a vertex shader
        """

        self.MAX_VERTEX_UNIFORM_VECTORS = self.get(enums.MAX_VERTEX_UNIFORM_VECTORS)
        """
        Maximum number of 4-vectors that may be held in uniform variable storage
        for the vertex shader
        """

        self.MAX_VERTEX_OUTPUT_COMPONENTS = self.get(enums.MAX_VERTEX_OUTPUT_COMPONENTS)
        """Maximum number of components of output written by a vertex shader"""

        self.MAX_VERTEX_UNIFORM_BLOCKS = self.get(enums.MAX_VERTEX_UNIFORM_BLOCKS)
        """Maximum number of uniform blocks per vertex shader."""

        # self.MAX_VERTEX_ATTRIB_RELATIVE_OFFSET = self.get(
        #     gl.GL_MAX_VERTEX_ATTRIB_RELATIVE_OFFSET
        # )
        # self.MAX_VERTEX_ATTRIB_BINDINGS = self.get(gl.GL_MAX_VERTEX_ATTRIB_BINDINGS)

        self.MAX_TEXTURE_IMAGE_UNITS = self.get(enums.MAX_TEXTURE_IMAGE_UNITS)
        """Number of texture units"""

        self.MAX_TEXTURE_MAX_ANISOTROPY = self.get_float(enums.MAX_TEXTURE_MAX_ANISOTROPY, 1.0)
        """The highest supported anisotropy value. Usually 8.0 or 16.0."""

        self.MAX_VIEWPORT_DIMS: Tuple[int, int] = self.get_int_tuple(enums.MAX_VIEWPORT_DIMS, 2)
        """
        The maximum support window or framebuffer viewport.
        This is usually the same as the maximum texture size
        """

        self.MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS = self.get(
            enums.MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS
        )
        """
        How many buffers we can have as output when doing a transform(feedback).
        This is usually 4.
        """

    @overload
    def get_int_tuple(self, enum, length: Literal[2]) -> Tuple[int, int]: ...

    @overload
    def get_int_tuple(self, enum, length: int) -> Tuple[int, ...]: ...

    @abstractmethod
    def get_int_tuple(self, enum, length: int):
        """
        Get an enum as an int tuple

        Args:
            enum: The enum to query
            length: The length of the tuple
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def get(self, enum, default=0) -> int:
        """
        Get an integer limit.

        Args:
            enum: The enum to query
            default: The default value if the query fails
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def get_float(self, enum, default=0.0) -> float:
        """
        Get a float limit

        Args:
            enum: The enum to query
            default: The default value if the query fails
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def get_str(self, enum) -> str:
        """
        Get a string limit.

        Args:
            enum: The enum to query
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")
