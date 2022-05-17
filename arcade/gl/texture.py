from array import array
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
    An OpenGL 2D texture.
    We can create an empty black texture or a texture from byte data.
    A texture can also be created with different datatypes such as
    float, integer or unsigned integer.

    NOTE: Currently does not support multisample textures even
    though ``_samples`` is set.

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
    :param int target: The texture type (Ignored. Legacy)
    :param bool depth: creates a depth texture if `True`
    :param int samples: Creates a multisampled texture for values > 0.
                        This value will be clamped between 0 and the max
                        sample capability reported by the drivers.
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
        "_anisotropy",
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
    # Swizzle conversion lookup
    _swizzle_enum_to_str = {
        gl.GL_RED: 'R',
        gl.GL_GREEN: 'G',
        gl.GL_BLUE: 'B',
        gl.GL_ALPHA: 'A',
        gl.GL_ZERO: '0',
        gl.GL_ONE: '1',
    }
    _swizzle_str_to_enum = {
        'R': gl.GL_RED,
        'G': gl.GL_GREEN,
        'B': gl.GL_BLUE,
        'A': gl.GL_ALPHA,
        '0': gl.GL_ZERO,
        '1': gl.GL_ONE,
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
        samples: int = 0,
    ):
        self._glo = glo = gl.GLuint()
        self._ctx = ctx
        self._width, self._height = size
        self._dtype = dtype
        self._components = components
        self._alignment = 1
        self._target = target
        self._samples = min(max(0, samples), self._ctx.info.MAX_SAMPLES)
        self._depth = depth
        self._compare_func: Optional[str] = None
        self._anisotropy = 1.0
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

        if data and self._samples > 0:
            raise ValueError("Multisamples textures are not writable (cannot be initialized with data)")

        self._target = gl.GL_TEXTURE_2D if self._samples == 0 else gl.GL_TEXTURE_2D_MULTISAMPLE

        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glGenTextures(1, byref(self._glo))

        if self._glo.value == 0:
            raise RuntimeError(
                "Cannot create Texture. OpenGL failed to generate a texture id"
            )

        gl.glBindTexture(self._target, self._glo)

        if data is not None:
            byte_length, data = data_to_ctypes(data)

        self._texture_2d(data)

        # Only set texture parameters on non-multisamples textures
        if self._samples == 0:
            self.filter = filter or self._filter
            self.wrap_x = wrap_x or self._wrap_x
            self.wrap_y = wrap_y or self._wrap_y

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, Texture.delete_glo, self._ctx, glo)

        self.ctx.stats.incr("texture")

    def resize(self, size: Tuple[int, int]):
        """
        Resize the texture. This will re-allocate the internal
        memory and all pixel data will be lost.
        """
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)

        self._width, self._height = size
        self._texture_2d(None)

    def __del__(self):
        # Intercept garbage collection if we are using Context.gc()
        if self._ctx.gc_mode == "context_gc" and self._glo.value > 0:
            self._ctx.objects.append(self)

    def _texture_2d(self, data):
        """Create a 2D texture"""
        # Start by resolving the texture format
        try:
            format_info = pixel_formats[self._dtype]
        except KeyError:
            raise ValueError(
                f"dype '{self._dtype}' not support. Supported types are : {tuple(pixel_formats.keys())}"
            )
        _format, _internal_format, self._type, self._component_size = format_info

        # If we are dealing with a multisampled texture we have less options
        if self._target == gl.GL_TEXTURE_2D_MULTISAMPLE:
            gl.glTexImage2DMultisample(
                self._target,
                self._samples,
                _internal_format[self._components],
                self._width,
                self._height,
                True,  # Fixed sample locations
            )
            return

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
                        f"Unable to create texture: {ex} : dtype={self._dtype} "
                        f"size={self.size} components={self._components} "
                        f"MAX_TEXTURE_SIZE = {self.ctx.info.MAX_TEXTURE_SIZE}"
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
    def samples(self) -> int:
        """
        Number of samples if multisampling is enabled (read only)

        :type: int
        """
        return self._samples

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
    def swizzle(self) -> str:
        """
        str: The swizzle mask of the texture (Default ``'RGBA'``).

        The swizzle mask change/reorder the ``vec4`` value returned by the ``texture()`` function
        in a GLSL shaders. This is represented by a 4 character string were each
        character can be::

            'R' GL_RED
            'G' GL_GREEN
            'B' GL_BLUE
            'A' GL_ALPHA
            '0' GL_ZERO
            '1' GL_ONE

        Example::

            # Alpha channel will always return 1.0
            texture.swizzle = 'RGB1'

            # Only return the red component. The rest is masked to 0.0
            texture.swizzle = 'R000'

            # Reverse the components
            texture.swizzle = 'ABGR'        
        """
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)

        # Read the current swizzle values from the texture
        swizzle_r = gl.GLint()
        swizzle_g = gl.GLint()
        swizzle_b = gl.GLint()
        swizzle_a = gl.GLint()

        gl.glGetTexParameteriv(self._target, gl.GL_TEXTURE_SWIZZLE_R, swizzle_r)
        gl.glGetTexParameteriv(self._target, gl.GL_TEXTURE_SWIZZLE_G, swizzle_g)
        gl.glGetTexParameteriv(self._target, gl.GL_TEXTURE_SWIZZLE_B, swizzle_b)
        gl.glGetTexParameteriv(self._target, gl.GL_TEXTURE_SWIZZLE_A, swizzle_a)

        swizzle_str = ""
        for v in [swizzle_r, swizzle_g, swizzle_b, swizzle_a]:
            swizzle_str += self._swizzle_enum_to_str[v.value]

        return swizzle_str

    @swizzle.setter
    def swizzle(self, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Swizzle must be a string, not '{type(str)}'")

        if len(value) != 4:
            raise ValueError("Swizzle must be a string of length 4")

        swizzle_enums = []
        for c in value:
            try:
                c = c.upper()
                swizzle_enums.append(self._swizzle_str_to_enum[c])
            except KeyError:
                raise ValueError(f"Swizzle value '{c}' invalid. Must be one of RGBA01")

        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_R, swizzle_enums[0])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_G, swizzle_enums[1])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_B, swizzle_enums[2])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_A, swizzle_enums[3])

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
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)
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
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)
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
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_WRAP_T, value)

    @property
    def anisotropy(self) -> float:
        """
        Get or set the anisotropy for this texture.
        """
        return self._anisotropy

    @anisotropy.setter
    def anisotropy(self, value):
        self._anisotropy = max(1.0, min(value, self._ctx.info.MAX_TEXTURE_MAX_ANISOTROPY))
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)
        gl.glTexParameterf(self._target, gl.GL_TEXTURE_MAX_ANISOTROPY, self._anisotropy)

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
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
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
        if self._samples > 0:
            raise ValueError("Multisampled textures cannot be read directly")

        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, alignment)

        buffer = (
            gl.GLubyte
            * (self.width * self.height * self._component_size * self._components)
        )()
        gl.glGetTexImage(gl.GL_TEXTURE_2D, level, self._format, self._type, buffer)

        return bytearray(buffer)

    def write(self, data: Union[bytes, Buffer, array], level: int = 0, viewport=None) -> None:
        """Write byte data to the texture. This can be bytes or a :py:class:`~arcade.gl.Buffer`.

        :param Union[bytes,Buffer] data: bytes or a Buffer with data to write
        :param int level: The texture level to write
        :param tuple viewport: The are of the texture to write. 2 or 4 component tuple
        """
        # TODO: Support writing to layers using viewport + alignment
        if self._samples > 0:
            raise ValueError("Writing to multisampled textures not supported")

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
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
            gl.glBindTexture(self._target, self._glo)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexSubImage2D(
                self._target, level, x, y, w, h, self._format, self._type, 0
            )
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, 0)
        else:
            byte_size, data = data_to_ctypes(data)
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
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
        if self._samples > 0:
            raise ValueError("Multisampled textures don't support mimpmaps")

        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._glo)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BASE_LEVEL, base)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_LEVEL, max_level)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    def delete(self):
        """
        Destroy the underlying OpenGL resource.
        Don't use this unless you know exactly what you are doing.
        """
        Texture.delete_glo(self._ctx, self._glo)
        self._glo.value = 0

    @staticmethod
    def delete_glo(ctx: "Context", glo: gl.GLuint):
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
        gl.glBindTexture(self._target, self._glo)

    def bind_to_image(self, unit: int, read: bool = True, write: bool = True, level: int = 0):
        """
        Bind textures to image units.

        Note that either or both ``read`` and ``write`` needs to be ``True``.
        The supported modes are: read only, write only, read-write

        :param int unit: The image unit
        :param bool read: The compute shader intends to read from this image
        :param bool write: The compute shader intends to write to this image
        :param int level:
        """

        access = gl.GL_READ_WRITE
        if read and write:
            access = gl.GL_READ_WRITE
        elif read and not write:
            access = gl.GL_READ_ONLY
        elif not read and write:
            access = gl.GL_WRITE_ONLY
        else:
            raise ValueError("Illegal access mode. The texture must at least be read or write only")

        gl.glBindImageTexture(unit, self._glo, level, 0, 0, access, self._internal_format)

    def __repr__(self) -> str:
        return "<Texture glo={} size={}x{} components={}>".format(
            self._glo.value, self._width, self._height, self._components
        )
