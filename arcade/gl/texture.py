from ctypes import byref
import weakref
from typing import Tuple, Union, TYPE_CHECKING

from pyglet import gl

from .exceptions import ShaderException
from .buffer import Buffer

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.gl import Context


class Texture:
    """
    Class that represents an OpenGL texture.
    """
    __slots__ = (
        '_ctx', '_glo', '_width', '_height', '_dtype', '_target', '_components',
        '_format', '_internal_format', '_type', '_component_size', '_samples', '_filter', '_wrap_x', '_wrap_y', '__weakref__',
    )
    _float_base_format = (0, gl.GL_RED, gl.GL_RG, gl.GL_RGB, gl.GL_RGBA)
    _int_base_format = (0, gl.GL_RED_INTEGER, gl.GL_RG_INTEGER, gl.GL_RGB_INTEGER, gl.GL_RGBA_INTEGER)
    # format: (base_format, internal_format, type, size)
    _formats = {
        # float formats
        'f1': (_float_base_format, (0, gl.GL_R8, gl.GL_RG8, gl.GL_RGB8, gl.GL_RGBA8), gl.GL_UNSIGNED_BYTE, 1),
        'f2': (_float_base_format, (0, gl.GL_R16F, gl.GL_RG16F, gl.GL_RGB16F, gl.GL_RGBA16F), gl.GL_HALF_FLOAT, 2),
        'f4': (_float_base_format, (0, gl.GL_R32F, gl.GL_RG32F, gl.GL_RGB32F, gl.GL_RGBA32F), gl.GL_FLOAT, 4),
        # int formats
        'i1': (_int_base_format, (0, gl.GL_R8UI, gl.GL_RG8UI, gl.GL_RGB8UI, gl.GL_RGBA8UI), gl.GL_UNSIGNED_BYTE, 1),
        'i2': (_int_base_format, (0, gl.GL_R16UI, gl.GL_RG16UI, gl.GL_RGB16UI, gl.GL_RGBA16UI), gl.GL_UNSIGNED_SHORT, 2),
        'i4': (_int_base_format, (0, gl.GL_R32UI, gl.GL_RG32UI, gl.GL_RGB32UI, gl.GL_RGBA32UI), gl.GL_UNSIGNED_INT, 4),
        # uint formats
        'u1': (_int_base_format, (0, gl.GL_R8UI, gl.GL_RG8UI, gl.GL_RGB8UI, gl.GL_RGBA8UI), gl.GL_BYTE, 1),
        'u2': (_int_base_format, (0, gl.GL_R16UI, gl.GL_RG16UI, gl.GL_RGB16UI, gl.GL_RGBA16UI), gl.GL_SHORT, 2),
        'u4': (_int_base_format, (0, gl.GL_R32UI, gl.GL_RG32UI, gl.GL_RGB32UI, gl.GL_RGBA32UI), gl.GL_INT, 4),
    }

    def __init__(self,
                 ctx: 'Context',
                 size: Tuple[int, int],
                 *,
                 components: int = 4,
                 dtype: str = 'f1',
                 data: bytes = None,
                 filter: Tuple[gl.GLuint, gl.GLuint] = None,
                 wrap_x: gl.GLuint = None,
                 wrap_y: gl.GLuint = None):
        """Represents an OpenGL texture.

        A texture can be created with or without initial data.
        NOTE: Currently does not support multisample textures even
        thought ``samples`` is exposed.

        :param Context ctx: The context the object belongs to
        :param Tuple[int, int] size: The size of the texture
        :param int components: The number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
        :param str dtype: The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
        :param bytes data: The byte data to initialize the texture with
        :param Tuple[gl.GLuint, gl.GLuint] filter: The minification/magnification filter of the texture
        :param gl.GLuint wrap_s
        :param data: The texture data (optional)
        """
        self._ctx = ctx
        self._width, self._height = size
        self._dtype = dtype
        self._components = components
        self._target = gl.GL_TEXTURE_2D
        self._samples = 0
        # These are the default states in OpenGL
        self._filter = gl.GL_LINEAR, gl.GL_LINEAR
        self._wrap_x = gl.GL_REPEAT
        self._wrap_y = gl.GL_REPEAT

        if components not in [1, 2, 3, 4]:
            raise ValueError("Components must be 1, 2, 3 or 4")

        try:
            format_info = self._formats[self._dtype]
        except KeyError:
            raise ValueError(f"dype '{dtype}' not support. Supported types are : {tuple(self._formats.keys())}")

        gl.glActiveTexture(gl.GL_TEXTURE0)  # Create textures in the default channel (0)

        self._glo = glo = gl.GLuint()
        gl.glGenTextures(1, byref(self._glo))

        if self._glo.value == 0:
            raise ShaderException("Cannot create Texture. OpenGL failed to generate a texture id")

        gl.glBindTexture(self._target, self._glo)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        try:
            _format, _internal_format, self._type, self._component_size = format_info
            self._format = _format[components]
            self._internal_format = _internal_format[components]
            gl.glTexImage2D(
                self._target,  # target
                0,  # level
                self._internal_format,  # internal_format
                self._width,  # width
                self._height,  # height
                0,  # border
                self._format,  # format
                self._type,  # type
                data  # data
            )
        except gl.GLException as ex:
            raise gl.GLException((
                f"Unable to create texture: {ex} : dtype={dtype} size={size} components={components} "
                "MAX_TEXTURE_SIZE = {self.ctx.limits.MAX_TEXTURE_SIZE}"
            ))

        self.filter = filter or self._filter
        self.wrap_x = wrap_x or self._wrap_x
        self.wrap_y = wrap_y or self._wrap_y

        self.ctx.stats.incr('texture')
        weakref.finalize(self, Texture.release, self._ctx, glo)

    @property
    def ctx(self) -> 'Context':
        """The context this texture belongs to"""
        return self._ctx

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL texture id"""
        return self._glo

    @property
    def width(self) -> int:
        """The width of the texture in pixels"""
        return self._width

    @property
    def height(self) -> int:
        """The height of the texture in pixels"""
        return self._height

    @property
    def dtype(self) -> str:
        """The data type of each component"""
        return self._dtype

    @property
    def size(self) -> Tuple[int, int]:
        """The size of the texture as a tuple"""
        return self._width, self._height

    @property
    def components(self) -> int:
        """Number of components in the texture"""
        return self._components

    @property
    def filter(self) -> Tuple[int, int]:
        """The (min, mag) filter for this texture.

        Default value is ``GL_LINEAR, GL_LINEAR``.
        Can be set to ``GL_NEAREST, GL_NEAREST`` for pixelated graphics.

        When mipmapping is used the min filter needs to be `GL_*_MIPMAP_*`.

        Also see:
        * https://www.khronos.org/opengl/wiki/Texture#Mip_maps
        * https://www.khronos.org/opengl/wiki/Sampler_Object#Filtering
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
        The horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the [0.0, 1.0] area.

        Valid options are: ``GL_REPEAT``, ``GL_MIRRORED_REPEAT``, ``GL_CLAMP_TO_EDGE``, ``GL_CLAMP_TO_BORDER``
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
        The horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the [0.0, 1.0] area.

        Valid options are: ``GL_REPEAT``, ``GL_MIRRORED_REPEAT``, ``GL_CLAMP_TO_EDGE``, ``GL_CLAMP_TO_BORDER``
        """
        return self._wrap_y

    @wrap_y.setter
    def wrap_y(self, value: int):
        self._wrap_y = value
        self.use()
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_WRAP_T, value)

    def read(self, level: int = 0, alignment: int = 1) -> bytearray:
        """
        Read the contents of the texture.
        :param int level:  The texture level to read
        :param int alignment: Alignment of the start of each row in memory in number of bytes. Possible values: 1,2,4
        """

        gl.glBindTexture(self._target, self._glo)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, alignment)

        buffer = (gl.GLubyte * (self.width * self.height * self._component_size * self._components))()
        gl.glGetTexImage(gl.GL_TEXTURE_2D, level, self._format, self._type, buffer)
        
        return bytearray(buffer)

    def write(self, data: Union[bytes, Buffer], level: int = 0, viewport=None) -> None:
        """Write byte data to the texture

        :param Union[bytes, Buffer] data: bytes or a Buffer with data to write
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

        if isinstance(data, bytes):
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
        elif isinstance(data, Buffer):
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, data.glo)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(self._target, self._glo)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexSubImage2D(self._target, level, x, y, w, h, self._format, self._type, 0)
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, 0)
        else:
            raise TypeError(f"data must be bytes or a Buffer, not {type(data)}")

    def build_mipmaps(self, base=0, max_amount=1000) -> None:
        """Generate mipmaps for this texture.
        Also see: https://www.khronos.org/opengl/wiki/Texture#Mip_maps
        """
        self.use()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BASE_LEVEL, base)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_LEVEL, max_amount)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    @staticmethod
    def release(ctx: 'Context', glo: gl.GLuint):
        """Destroy the texture"""
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteTextures(1, byref(glo))

        ctx.stats.decr('texture')

    def use(self, unit: int = 0) -> None:
        """Bind the texture to a channel,

        :param int unit: The texture unit to bind the texture.
        """
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._glo)

    def __repr__(self) -> str:
        return "<Texture glo={} size={}x{} components={}>".format(
            self._glo.value, self._width, self._height, self._components)
