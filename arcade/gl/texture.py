from ctypes import byref
import weakref
from typing import Any, Optional, Tuple, Union, TYPE_CHECKING

from pyglet import gl

from .buffer import Buffer
from .utils import data_to_ctypes
from .types import pixel_formats

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.gl import Context


class Texture:
    """
    An OpenGL texture.
    We can create an empty black texture or a texture from byte data.
    A texture can also be created with different datatypes such as
    float, integer or unsigned integer.

    The best way to create a texture instance is through :py:meth:`arcade.gl.Context.texture`

    Supported ``dtype`` values are::

        # Float formats
        'f1': UNSIGNED_BYTE
        'f2': HALF_FLOAT
        'f4': FLOAT
        # int formats
        'i1': BYTE
        'i2': SHORT
        'i4': INT
        # uint formats
        'u1': UNSIGNED_BYTE
        'u2': UNSIGNED_SHORT
        'u4': UNSIGNED_INT

    :param Context ctx: The context the object belongs to
    :param Tuple[int, int] size: The size of the texture
    :param int components: The number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
    :param str dtype: The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
    :param data: The texture data (optional). Can be bytes or any object supporting the buffer protocol.
    :param Any data: The byte data of the texture. bytes or anything supporting the buffer protocol.
    :param Tuple[gl.GLuint,gl.GLuint] filter: The minification/magnification filter of the texture
    :param gl.GLuint wrap_x: Wrap mode x
    :param gl.GLuint wrap_y: Wrap mode y
    """

    __slots__ = (
        "_ctx",
        "_glo",
        "_width",
        "_height",
        "_dtype",
        "_target",
        "_components",
        "_alignment",
        "_depth",
        "_compare_func",
        "_format",
        "_internal_format",
        "_type",
        "_component_size",
        "_samples",
        "_filter",
        "_wrap_x",
        "_wrap_y",
        "__weakref__",
    )
    _compare_funcs = {
        None: gl.GL_NONE,
        "<=": gl.GL_LEQUAL,
        "<": gl.GL_LESS,
        ">=": gl.GL_GEQUAL,
        ">": gl.GL_GREATER,
        "==": gl.GL_EQUAL,
        "!=": gl.GL_NOTEQUAL,
        "0": gl.GL_NEVER,
        "1": gl.GL_ALWAYS,
    }

    def __init__(
        self,
        ctx: "Context",
        size: Tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: Any = None,
        filter: Tuple[gl.GLuint, gl.GLuint] = None,
        wrap_x: gl.GLuint = None,
        wrap_y: gl.GLuint = None,
        target=gl.GL_TEXTURE_2D,
        depth=False,
    ):
        """
        A texture can be created with or without initial data.
        NOTE: Currently does not support multisample textures even
        thought ``samples`` is exposed.

        :param Context ctx: The context the object belongs to
        :param Tuple[int,int] size: The size of the texture
        :param int components: The number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
        :param str dtype: The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
        :param Any data: The byte data of the texture. bytes or anything supporting the buffer protocol.
        :param Tuple[gl.GLuint, gl.GLuint] filter: The minification/magnification filter of the texture
        :param gl.GLuint wrap_x: Wrap mode x
        :param gl.GLuint wrap_y: Wrap mode y
        :param int target: The texture type
        :param bool depth: creates a depth texture if `True`
        """
        self._ctx = ctx
        self._width, self._height = size
        self._dtype = dtype
        self._components = components
        self._alignment = 1
        self._target = target
        self._samples = 0
        self._depth = depth
        self._compare_func = None
        # Default filters for float and integer textures
        # Integer textures should have NEAREST interpolation
        # by default 3.3 core doesn't really support it consistently.
        if "f" in self._dtype:
            self._filter = gl.GL_LINEAR, gl.GL_LINEAR
        else:
            self._filter = gl.GL_NEAREST, gl.GL_NEAREST
        self._wrap_x = gl.GL_REPEAT
        self._wrap_y = gl.GL_REPEAT

        if self._components not in [1, 2, 3, 4]:
            raise ValueError("Components must be 1, 2, 3 or 4")

        gl.glActiveTexture(gl.GL_TEXTURE0)  # Create textures in the default channel (0)

        self._glo = glo = gl.GLuint()
        gl.glGenTextures(1, byref(self._glo))

        if self._glo.value == 0:
            raise RuntimeError(
                "Cannot create Texture. OpenGL failed to generate a texture id"
            )

        gl.glBindTexture(self._target, self._glo)

        if data is not None:
            byte_length, data = data_to_ctypes(data)

        if self._target == gl.GL_TEXTURE_2D:
            self._texture_2d(data)
        else:
            raise ValueError("Unsupported texture target")

        self.filter = filter or self._filter
        self.wrap_x = wrap_x or self._wrap_x
        self.wrap_y = wrap_y or self._wrap_y

        self.ctx.stats.incr("texture")
        weakref.finalize(self, Texture.release, self._ctx, glo)

    def _texture_2d(self, data):
        """Create a 2D texture"""
        # Make sure we unpack the pixel data with correct alignment
        # or we'll end up with corrupted textures
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, self._alignment)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, self._alignment)

        # Create depth 2d texture
        if self._depth:
            gl.glTexImage2D(
                self._target,
                0,  # level
                gl.GL_DEPTH_COMPONENT24,
                self._width,
                self._height,
                0,
                gl.GL_DEPTH_COMPONENT,
                gl.GL_FLOAT,
                data,
            )
            self.compare_func = "<="
        # Create normal 2d texture
        else:
            try:
                format_info = pixel_formats[self._dtype]
            except KeyError:
                raise ValueError(
                    f"dype '{self._dtype}' not support. Supported types are : {tuple(pixel_formats.keys())}"
                )

            try:
                (
                    _format,
                    _internal_format,
                    self._type,
                    self._component_size,
                ) = format_info
                self._format = _format[self._components]
                self._internal_format = _internal_format[self._components]
                gl.glTexImage2D(
                    self._target,  # target
                    0,  # level
                    self._internal_format,  # internal_format
                    self._width,  # width
                    self._height,  # height
                    0,  # border
                    self._format,  # format
                    self._type,  # type
                    data,  # data
                )
            except gl.GLException as ex:
                raise gl.GLException(
                    (
                        f"Unable to create texture: {ex} : dtype={self._dtype} size={self.size} components={self._components} "
                        "MAX_TEXTURE_SIZE = {self.ctx.limits.MAX_TEXTURE_SIZE}"
                    )
                )

    @property
    def ctx(self) -> "Context":
        """
        The context this texture belongs to

        :type: :py:class:`~arcade.gl.Context`
        """
        return self._ctx

    @property
    def glo(self) -> gl.GLuint:
        """
        The OpenGL texture id

        :type: GLuint
        """
        return self._glo

    @property
    def width(self) -> int:
        """
        The width of the texture in pixels

        :type: int
        """
        return self._width

    @property
    def height(self) -> int:
        """
        The height of the texture in pixels

        :type: int
        """
        return self._height

    @property
    def dtype(self) -> str:
        """
        The data type of each component

        :type: str
        """
        return self._dtype

    @property
    def size(self) -> Tuple[int, int]:
        """
        The size of the texture as a tuple

        :type: tuple (width, height)
        """
        return self._width, self._height

    @property
    def byte_size(self) -> int:
        """
        The byte size of the texture.

        :type: int
        """
        return pixel_formats[self._dtype][3] * self._components * self.width * self.height

    @property
    def components(self) -> int:
        """
        Number of components in the texture

        :type: int
        """
        return self._components

    @property
    def depth(self) -> bool:
        """
        If this is a depth texture.

        :type: bool
        """
        return self._depth

    @property
    def filter(self) -> Tuple[int, int]:
        """Get or set the ``(min, mag)`` filter for this texture.
        These are rules for how a texture interpolates.
        The filter is specified for minification and magnification.

        Default value is ``LINEAR, LINEAR``.
        Can be set to ``NEAREST, NEAREST`` for pixelated graphics.

        When mipmapping is used the min filter needs to be one of the
        ``MIPMAP`` variants.

        Accepted values::

            # Enums can be accessed on the context or arcade.gl
            NEAREST                # Nearest pixel
            LINEAR                 # Linear interpolate
            NEAREST_MIPMAP_NEAREST # Minification filter for mipmaps
            LINEAR_MIPMAP_NEAREST  # Minification filter for mipmaps
            NEAREST_MIPMAP_LINEAR  # Minification filter for mipmaps
            LINEAR_MIPMAP_LINEAR   # Minification filter for mipmaps

        Also see

        * https://www.khronos.org/opengl/wiki/Texture#Mip_maps
        * https://www.khronos.org/opengl/wiki/Sampler_Object#Filtering

        :type: tuple (min filter, mag filter)
        """
        return self._filter

    @filter.setter
    def filter(self, value: Tuple[int, int]):
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError("Texture filter must be a 2 component tuple (min, mag)")

        self._filter = value
        self.use()
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_MIN_FILTER, self._filter[0])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_MAG_FILTER, self._filter[1])

    @property
    def wrap_x(self) -> int:
        """
        Get or set the horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the ``[0.0, 1.0]`` area.
        Default value is ``REPEAT``.

        Valid options are::

            # Note: Enums can also be accessed in arcade.gl
            # Repeat pixels on the y axis
            texture.wrap_x = ctx.REPEAT
            # Repeat pixels on the y axis mirrored
            texture.wrap_x = ctx.MIRRORED_REPEAT
            # Repeat the edge pixels when reading outside the texture
            texture.wrap_x = ctx.CLAMP_TO_EDGE
            # Use the border color (black by default) when reading outside the texture
            texture.wrap_x = ctx.CLAMP_TO_BORDER

        :type: int
        """
        return self._wrap_x

    @wrap_x.setter
    def wrap_x(self, value: int):
        self._wrap_x = value
        self.use()
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_WRAP_S, value)

    @property
    def wrap_y(self) -> int:
        """
        Get or set the horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the ``[0.0, 1.0]`` area.
        Default value is ``REPEAT``.

        Valid options are::

            # Note: Enums can also be accessed in arcade.gl
            # Repeat pixels on the x axis
            texture.wrap_x = ctx.REPEAT
            # Repeat pixels on the x axis mirrored
            texture.wrap_x = ctx.MIRRORED_REPEAT
            # Repeat the edge pixels when reading outside the texture
            texture.wrap_x = ctx.CLAMP_TO_EDGE
            # Use the border color (black by default) when reading outside the texture
            texture.wrap_x = ctx.CLAMP_TO_BORDER

        :type: int
        """
        return self._wrap_y

    @wrap_y.setter
    def wrap_y(self, value: int):
        self._wrap_y = value
        self.use()
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_WRAP_T, value)

    @property
    def compare_func(self) -> Optional[str]:
        """
        Get or set the compare function for a depth texture::

            texture.compare_func = None  # Disable depth comparison completely
            texture.compare_func = '<='  # GL_LEQUAL
            texture.compare_func = '<'   # GL_LESS
            texture.compare_func = '>='  # GL_GEQUAL
            texture.compare_func = '>'   # GL_GREATER
            texture.compare_func = '=='  # GL_EQUAL
            texture.compare_func = '!='  # GL_NOTEQUAL
            texture.compare_func = '0'   # GL_NEVER
            texture.compare_func = '1'   # GL_ALWAYS

        :type: str
        """
        return self._compare_func

    @compare_func.setter
    def compare_func(self, value: Union[str, None]):
        if not self._depth:
            raise ValueError(
                "Depth comparison function can only be set on depth textures"
            )

        if not isinstance(value, str) and value is not None:
            raise ValueError(f"value must be as string: {self._compare_funcs.keys()}")

        func = self._compare_funcs.get(value, None)
        if func is None:
            raise ValueError(f"value must be as string: {self._compare_funcs.keys()}")

        self._compare_func = value
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self._target, self._glo)
        if value is None:
            gl.glTexParameteri(self._target, gl.GL_TEXTURE_COMPARE_MODE, gl.GL_NONE)
        else:
            gl.glTexParameteri(
                self._target, gl.GL_TEXTURE_COMPARE_MODE, gl.GL_COMPARE_REF_TO_TEXTURE
            )
            gl.glTexParameteri(self._target, gl.GL_TEXTURE_COMPARE_FUNC, func)

    def read(self, level: int = 0, alignment: int = 1) -> bytearray:
        """
        Read the contents of the texture.

        :param int level:  The texture level to read
        :param int alignment: Alignment of the start of each row in memory in number of bytes. Possible values: 1,2,4
        :rtype: bytearray
        """
        gl.glBindTexture(self._target, self._glo)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, alignment)

        buffer = (
            gl.GLubyte
            * (self.width * self.height * self._component_size * self._components)
        )()
        gl.glGetTexImage(gl.GL_TEXTURE_2D, level, self._format, self._type, buffer)

        return bytearray(buffer)

    def write(self, data: Union[bytes, Buffer], level: int = 0, viewport=None) -> None:
        """Write byte data to the texture. This can be bytes or a :py:class:`~arcade.gl.Buffer`.

        :param Union[bytes,Buffer] data: bytes or a Buffer with data to write
        :param int level: The texture level to write
        :param tuple viewport: The are of the texture to write. 2 or 4 component tuple
        """
        # TODO: Support writing to layers using viewport + alignment
        if self._samples > 0:
            raise ValueError("Writing to multisample textures not supported")

        x, y, w, h = 0, 0, self._width, self._height
        if viewport:
            if len(viewport) == 2:
                w, h = viewport
            elif len(viewport) == 4:
                x, y, w, h = viewport
            else:
                raise ValueError("Viewport must be of length 2 or 4")

        if isinstance(data, Buffer):
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, data.glo)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(self._target, self._glo)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexSubImage2D(
                self._target, level, x, y, w, h, self._format, self._type, 0
            )
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, 0)
        else:
            byte_size, data = data_to_ctypes(data)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(self._target, self._glo)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexSubImage2D(
                self._target,  # target
                level,  # level
                x,  # x offset
                y,  # y offset
                w,  # width
                h,  # height
                self._format,  # format
                self._type,  # type
                data,  # pixel data
            )

    def build_mipmaps(self, base: int = 0, max_level: int = 1000) -> None:
        """Generate mipmaps for this texture. Leaveing the default arguments
        will usually does the job. Building mipmaps will create several
        smaller versions of the texture (256 x 256, 128 x 128, 64 x 64, 32 x 32 etc)
        helping OpenGL in rendering a nicer version of texture
        when it's rendered to the screen in smaller version.

        Note that mipmaps will only be used if the texture filter is
        configured with a mipmap-type minification::

            # Set up linear interpolating minification filter
            texture.filter = ctx.LINEAR_MIPMAP_LINEAR, ctx.LINEAR

        :param int base: Level the mipmaps start at (usually 0)
        :param int max_level: The maximum levels to generate

        Also see: https://www.khronos.org/opengl/wiki/Texture#Mip_maps
        """
        self.use()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BASE_LEVEL, base)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_LEVEL, max_level)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    @staticmethod
    def release(ctx: "Context", glo: gl.GLuint):
        """
        Destroy the texture.
        This is called automatically when the object is garbage collected.

        :param arcade.gl.Context ctx: OpenGL Context
        :param gl.GLuint glo: The OpenGL texture id
        """
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteTextures(1, byref(glo))

        ctx.stats.decr("texture")

    def use(self, unit: int = 0) -> None:
        """Bind the texture to a channel,

        :param int unit: The texture unit to bind the texture.
        """
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._glo)

    def __repr__(self) -> str:
        return "<Texture glo={} size={}x{} components={}>".format(
            self._glo.value, self._width, self._height, self._components
        )
