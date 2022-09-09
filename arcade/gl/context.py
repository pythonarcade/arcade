from contextlib import contextmanager
from ctypes import c_int, c_char_p, cast, c_float
from collections import deque
import logging
import weakref
from typing import Any, Deque, Dict, List, Tuple, Union, Sequence, Set

import pyglet
from pyglet.window import Window
from pyglet import gl

from .buffer import Buffer
from .program import Program
from .vertex_array import Geometry
from .framebuffer import Framebuffer, DefaultFrameBuffer
from typing import Optional
from .texture import Texture
from .query import Query
from .glsl import ShaderSource
from .types import BufferDescription
from .compute_shader import ComputeShader

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
    #: Context flag: Enables ``gl_PointSize`` in vertex or geometry shaders.
    #:
    #: When enabled we can write to ``gl_PointSize`` in the vertex shader to specify the point size
    #: for each individual point.
    #:
    #: If this value is not set in the shader the behavior is undefined. This means the points may
    #: or may not appear depending if the drivers enforce some default value for ``gl_PointSize``.
    #:
    #: When disabled :py:attr:`Context.point_size` is used.
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
    LINE_LOOP = gl.GL_LINE_LOOP  # 2
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

    def __init__(self, window: pyglet.window.Window, gc_mode: str = "context_gc"):
        self._window_ref = weakref.ref(window)
        self._limits = Limits(self)
        self._gl_version = (self._limits.MAJOR_VERSION, self._limits.MINOR_VERSION)
        Context.activate(self)
        # Texture unit we use when doing operations on textures to avoid
        # affecting currently bound textures in the first units
        self.default_texture_unit: int = self._limits.MAX_TEXTURE_IMAGE_UNITS - 1

        # Detect the default framebuffer
        self._screen = DefaultFrameBuffer(self)
        # Tracking active program
        self.active_program: Optional[Program] = None
        # Tracking active framebuffer. On context creation the window is the default render target
        self.active_framebuffer: Framebuffer = self._screen
        self._stats: ContextStats = ContextStats(warn_threshold=1000)

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

        # Context GC as default. We need to call Context.gc() to free opengl resources
        self._gc_mode = "context_gc"
        self.gc_mode = gc_mode
        #: Collected objects to gc when gc_mode is "context_gc".
        #: This can be used during debugging.
        self.objects: Deque[Any] = deque()

    @property
    def info(self) -> "Limits":
        """
        Get the Limits object for this context containing information
        about hardware/driver limits and other context information.

        Example::

            >> ctx.info.MAX_TEXTURE_SIZE
            (16384, 16384)
            >> ctx.info.VENDOR
            NVIDIA Corporation
            >> ctx.info.RENDERER
            NVIDIA GeForce RTX 2080 SUPER/PCIe/SSE2
        """
        return self._limits

    @property
    def limits(self) -> "Limits":
        """
        Get the Limits object for this context containing information
        about hardware/driver limits and other context information.

        .. Warning::

            This an old alias for :py:attr:`~arcade.gl.Context.info`
            and is only around for backwards compatibility.

        Example::

            >> ctx.limits.MAX_TEXTURE_SIZE
            (16384, 16384)
            >> ctx.limits.VENDOR
            NVIDIA Corporation
            >> ctx.limits.RENDERER
            NVIDIA GeForce RTX 2080 SUPER/PCIe/SSE2
        """
        return self._limits

    @property
    def stats(self) -> "ContextStats":
        """
        Get the stats instance containing runtime information
        about creation and destruction of OpenGL objects.

        Example::

            >> ctx.limits.MAX_TEXTURE_SIZE
            (16384, 16384)
            >> ctx.limits.VENDOR
            NVIDIA Corporation
            >> ctx.limits.RENDERER
            NVIDIA GeForce RTX 2080 SUPER/PCIe/SSE2
        """
        return self._stats

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
        The OpenGL version as a 2 component tuple.
        This is the reported OpenGL version from
        drivers and might be a higher version than
        you requested.

        :type: tuple (major, minor) version
        """
        return self._gl_version

    def gc(self) -> int:
        """
        Run garbage collection of OpenGL objects for this context.
        This is only needed when ``gc_mode`` is ``context_gc``.

        :return: The number of resources destroyed
        :rtype: int
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
        """
        Mark a context as the currently active one.

        .. Warning:: Never call this unless you know exactly what you are doing.
        """
        cls.active = ctx

    def enable(self, *flags):
        """
        Enables one or more context flags::

            # Single flag
            ctx.enable(ctx.BLEND)
            # Multiple flags
            ctx.enable(ctx.DEPTH_TEST, ctx.CULL_FACE)
        """
        self._flags.update(flags)

        for flag in flags:
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

        Only the supplied flags with be enabled in
        in the context. When exiting the context
        the old flags will be restored.

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
    def scissor(self) -> Optional[Tuple[int, int, int, int]]:
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

        :type: tuple (x, y, width, height)
        """
        return self.fbo.scissor

    @scissor.setter
    def scissor(self, value):
        self.fbo.scissor = value

    @property
    def blend_func(self) -> Tuple[int, int]:
        """
        Get or set the blend function.
        This is tuple specifying how the red, green, blue, and
        alpha blending factors are computed for the source
        and  destination pixel.

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
            ctx.blend_func = gl.ONE, gl.One

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
        Patch primitives are consumed by the tessellation control shader (if present)
        and subsequently used for tessellation.

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
        """
        Set or get the point size. Default is `1.0`.

        Point size changes the pixel size of rendered points. The min and max values
        are limited by :py:attr:`~arcade.gl.Context.info.POINT_SIZE_RANGE`.
        This value usually at least ``(1, 100)``, but this depends on the drivers/vendors.

        If variable point size is needed you can enable :py:attr:`~arcade.gl.Context.PROGRAM_POINT_SIZE`
        and write to ``gl_PointSize`` in the vertex or geometry shader.

        .. Note::

            Using a geometry shader to create triangle strips from points is often a safer
            way to render large points since you don't have have any size restrictions.
        """
        return self._point_size

    @point_size.setter
    def point_size(self, value: float):
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
        A suggestion to the driver to execute all the queued
        drawing calls even if the queue is not full yet.
        This is not a blocking call and only a suggestion.
        This can potentially be used for speedups when
        we don't have anything else to render.
        """
        gl.glFlush()

    # Various utility methods

    def copy_framebuffer(self, src: Framebuffer, dst: Framebuffer):
        """
        Copies/blits a framebuffer to another one.

        This operation has many restrictions to ensure it works across
        different platforms and drivers:

        * The source and destination framebuffer must be the same size
        * The formats of the attachments must be the same
        * Only the source framebuffer can be multisampled
        * Framebuffers cannot have integer attachments

        :param Framebuffer src: The framebuffer to copy from
        :param Framebuffer dst: The framebuffer we copy to
        """
        gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, src._glo)
        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, dst._glo)
        gl.glBlitFramebuffer(
            0, 0, src.width, src.height,  # Make source and dest size the same
            0, 0, src.width, src.height,
            gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT,
            gl.GL_NEAREST,
        )
        self.active_framebuffer.use(force=True)

    # --- Resource methods ---

    def buffer(
        self, *, data: Optional[Any] = None, reserve: int = 0, usage: str = "static"
    ) -> Buffer:
        """
        Create an OpenGL Buffer object. The buffer will contain all zero-bytes if no data is supplied.

        Examples::

            # Create 1024 byte buffer
            ctx.buffer(reserve=1024)
            # Create a buffer with 1000 float values using python's array.array
            from array import array
            ctx.buffer(data=array('f', [i for in in range(1000)])
            # Create a buffer with 1000 random 32 bit floats using numpy
            self.ctx.buffer(data=np.random.random(1000).astype("f4"))

        The ``usage`` parameter enables the GL implementation to make more intelligent
        decisions that may impact buffer object performance. It does not add any restrictions.
        If in doubt, skip this parameter and revisit when optimizing. The result
        are likely to be different between vendors/drivers or may not have any effect.

        The available values means the following::

            stream
                The data contents will be modified once and used at most a few times.
            static
                The data contents will be modified once and used many times.
            dynamic
                The data contents will be modified repeatedly and used many times.

        :param Any data: The buffer data, This can be ``bytes`` or an object supporting the buffer protocol.
        :param int reserve: The number of bytes reserve
        :param str usage: Buffer usage. 'static', 'dynamic' or 'stream'
        :rtype: :py:class:`~arcade.gl.Buffer`
        """
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
        filter: Tuple[gl.GLenum, gl.GLenum] = None,
        samples: int = 0,
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
        :param int samples: Creates a multisampled texture for values > 0
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
            samples=samples,
        )

    def depth_texture(self, size: Tuple[int, int], *, data=None) -> Texture:
        """
        Create a 2D depth texture. Can be used as a depth attachment
        in a :py:class:`~arcade.gl.Framebuffer`.

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
        Create a Geomtry instance. This is Arcade's version of a vertex array adding
        a lot of convenice for the user. Geometry objects are fairly light. They are
        mainly responsible for automatically map buffer inputs to your shader(s)
        and provide various methods for rendering or processing this geometry,

        The same geometry can be rendered with different
        programs as long as your shader is using one or more of the input attribute.
        This means geometry with positions and colors can be rendered with a program
        only using the positions. We will automatically map what is necessary and
        cache these mappings internally for performace.

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

            # Single interlaved buffer with two attributes. A vec2 position and vec2 velocity
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

        :param list content: List of :py:class:`~arcade.gl.BufferDescription` (optional)
        :param Buffer index_buffer: Index/element buffer (optional)
        :param int mode: The default draw mode (optional)
        :param int mode: The default draw mode (optional)
        :param int index_element_size: Byte size of a single index/element in the index buffer.
                                       In other words, the index buffer can be 8, 16 or 32 bit integers.
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
        fragment_shader: str = None,
        geometry_shader: str = None,
        tess_control_shader: str = None,
        tess_evaluation_shader: str = None,
        defines: Dict[str, str] = None,
        varyings: Optional[Sequence[str]] = None,
        varyings_capture_mode: str = "interleaved",
    ) -> Program:
        """Create a :py:class:`~arcade.gl.Program` given the vertex, fragment and geometry shader.

        :param str vertex_shader: vertex shader source
        :param str fragment_shader: fragment shader source (optional)
        :param str geometry_shader: geometry shader source (optional)
        :param str tess_control_shader: tessellation control shader source (optional)
        :param str tess_evaluation_shader: tessellation evaluation shader source (optional)
        :param dict defines: Substitute #defines values in the source (optional)
        :param Optional[Sequence[str]] varyings: The name of the out attributes in a transform shader.
                                                 This is normally not necessary since we auto detect them,
                                                 but some more complex out structures we can't detect.
        :param str varyings_capture_mode: The capture mode for transforms.
                                          ``"interleaved"`` means all out attribute will be written to a single buffer.
                                          ``"separate"`` means each out attribute will be written separate buffers.
                                          Based on these settings the `transform()` method will accept a single
                                          buffer or a list of buffer.
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
        out_attributes = list(varyings) if varyings is not None else []  # type: List[str]
        if not source_fs and not out_attributes:
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
            varyings=out_attributes,
            varyings_capture_mode=varyings_capture_mode,
        )

    def query(self, *, samples=True, time=True, primitives=True):
        """
        Create a query object for measuring rendering calls in opengl.

        :param bool samples: Collect written samples
        :param bool time: Measure rendering duration
        :param bool primitives: Collect the number of primitives emitted

        :rtype: :py:class:`~arcade.gl.Query`
        """
        return Query(self, samples=samples, time=time, primitives=primitives)

    def compute_shader(self, *, source: str) -> ComputeShader:
        """
        Create a compute shader.

        :param str source: The glsl source
        """
        return ComputeShader(self, source)


class ContextStats:
    """
    Runtime allocation statistics of OpenGL objects.
    """
    def __init__(self, warn_threshold=100):
        self.warn_threshold = warn_threshold
        #: Textures (created, freed)
        self.texture = (0, 0)
        #: Framebuffers (created, freed)
        self.framebuffer = (0, 0)
        #: Buffers (created, freed)
        self.buffer = (0, 0)
        #: Programs (created, freed)
        self.program = (0, 0)
        #: Vertex Arrays (created, freed)
        self.vertex_array = (0, 0)
        #: Geometry (created, freed)
        self.geometry = (0, 0)
        #: Compute Shaders (created, freed)
        self.compute_shader = (0, 0)
        #: Queries (created, freed)
        self.query = (0, 0)

    def incr(self, key: str) -> None:
        """
        Increments a counter.

        :param str key: The attribute name / counter to increment.
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

        :param str key: The attribute name / counter to decrement.
        """
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
        #: The vendor string. For example "NVIDIA Corporation"
        self.VENDOR = self.get_str(gl.GL_VENDOR)
        #: The renderer things. For example "NVIDIA GeForce RTX 2080 SUPER/PCIe/SSE2"
        self.RENDERER = self.get_str(gl.GL_RENDERER)
        #: Value indicating the number of sample buffers associated with the framebuffer
        self.SAMPLE_BUFFERS = self.get(gl.GL_SAMPLE_BUFFERS)
        #: An estimate of the number of bits of subpixel resolution
        #: that are used to position rasterized geometry in window coordinates
        self.SUBPIXEL_BITS = self.get(gl.GL_SUBPIXEL_BITS)
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
        #: The highest supported anisotropy value. Usually 8.0 or 16.0.
        self.MAX_TEXTURE_MAX_ANISOTROPY = self.get_float(gl.GL_MAX_TEXTURE_MAX_ANISOTROPY)
        #: The maximum support window or framebuffer viewport.
        #: This is usually the same as the maximum texture size
        self.MAX_VIEWPORT_DIMS = self.get_int_tuple(gl.GL_MAX_VIEWPORT_DIMS, 2)
        #: How many buffers we can have as output when doing a transform(feedback).
        #: This is usually 4
        self.MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS = self.get(gl.GL_MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS)
        #: The minimum and maximum point size
        self.POINT_SIZE_RANGE = self.get_int_tuple(gl.GL_POINT_SIZE_RANGE, 2)

        err = self._ctx.error
        if err:
            from warnings import warn

            warn("Error happened while querying of limits. Moving on ..")

    def get_int_tuple(self, enum: gl.GLenum, length: int):
        """Get an enum as an int tuple"""
        values = (c_int * length)()
        gl.glGetIntegerv(enum, values)
        return tuple(values)

    def get(self, enum: gl.GLenum) -> int:
        """Get an integer limit"""
        value = c_int()
        gl.glGetIntegerv(enum, value)
        return value.value

    def get_float(self, enum: gl.GLenum) -> float:
        """Get a float limit"""
        try:
            value = c_float()
            gl.glGetFloatv(enum, value)
            return value.value
        except Exception:
            return 0.0

    def get_str(self, enum: gl.GLenum) -> str:
        """Get a string limit"""
        return cast(gl.glGetString(enum), c_char_p).value.decode()  # type: ignore
