from __future__ import annotations

import weakref
from ctypes import byref, string_at
from typing import TYPE_CHECKING

from pyglet import gl

from ..types import BufferProtocol
from .buffer import Buffer
from .types import (
    BufferOrBufferProtocol,
    PyGLuint,
    compare_funcs,
    pixel_formats,
    swizzle_enum_to_str,
    swizzle_str_to_enum,
)
from .utils import data_to_ctypes

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.gl import Context


class Texture2D:
    """
    An OpenGL 2D texture.
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

    Args:
        ctx:
            The context the object belongs to
        size:
            The size of the texture
        components:
            The number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
        dtype:
            The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
        data:
            The texture data. Can be bytes or any object supporting
            the buffer protocol.
        filter:
            The minification/magnification filter of the texture
        wrap_x:
            Wrap mode x
        wrap_y:
            Wrap mode y
        target:
            The texture type (Ignored. Legacy)
        depth:
            creates a depth texture if `True`
        samples:
            Creates a multisampled texture for values > 0.
            This value will be clamped between 0 and the max
            sample capability reported by the drivers.
        immutable:
            Make the storage (not the contents) immutable. This can sometimes be
            required when using textures with compute shaders.
        internal_format:
            The internal format of the texture
        compressed:
            Is the texture compressed?
        compressed_data:
            The raw compressed data
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
        "_immutable",
        "__weakref__",
        "_compressed",
        "_compressed_data",
    )

    def __init__(
        self,
        ctx: Context,
        size: tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        filter: tuple[PyGLuint, PyGLuint] | None = None,
        wrap_x: PyGLuint | None = None,
        wrap_y: PyGLuint | None = None,
        target=gl.GL_TEXTURE_2D,
        depth=False,
        samples: int = 0,
        immutable: bool = False,
        internal_format: PyGLuint | None = None,
        compressed: bool = False,
        compressed_data: bool = False,
    ):
        self._glo = glo = gl.GLuint()
        self._ctx = ctx
        self._width, self._height = size
        self._dtype = dtype
        self._components = components
        self._component_size = 0
        self._alignment = 1
        self._target = target
        self._samples = min(max(0, samples), self._ctx.info.MAX_SAMPLES)
        self._depth = depth
        self._immutable = immutable
        self._compare_func: str | None = None
        self._anisotropy = 1.0
        self._internal_format = internal_format
        self._compressed = compressed
        self._compressed_data = compressed_data
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
            raise ValueError(
                "Multisampled textures are not writable (cannot be initialized with data)"
            )

        self._target = gl.GL_TEXTURE_2D if self._samples == 0 else gl.GL_TEXTURE_2D_MULTISAMPLE

        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glGenTextures(1, byref(self._glo))

        if self._glo.value == 0:
            raise RuntimeError("Cannot create Texture. OpenGL failed to generate a texture id")

        gl.glBindTexture(self._target, self._glo)

        self._texture_2d(data)

        # Only set texture parameters on non-multisample textures
        if self._samples == 0:
            self.filter = filter or self._filter
            self.wrap_x = wrap_x or self._wrap_x
            self.wrap_y = wrap_y or self._wrap_y

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, Texture2D.delete_glo, self._ctx, glo)

        self.ctx.stats.incr("texture")

    def resize(self, size: tuple[int, int]):
        """
        Resize the texture. This will re-allocate the internal
        memory and all pixel data will be lost.

        .. note:: Immutable textures cannot be resized.

        Args:
            size: The new size of the texture
        """
        if self._immutable:
            raise ValueError("Immutable textures cannot be resized")

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
                f"dype '{self._dtype}' not support. Supported types are : "
                f"{tuple(pixel_formats.keys())}"
            )
        _format, _internal_format, self._type, self._component_size = format_info
        if data is not None:
            byte_length, data = data_to_ctypes(data)
            self._validate_data_size(data, byte_length, self._width, self._height)

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
                gl.GL_UNSIGNED_INT,  # gl.GL_FLOAT,
                data,
            )
            self.compare_func = "<="
        # Create normal 2d texture
        else:
            try:
                self._format = _format[self._components]
                if self._internal_format is None:
                    self._internal_format = _internal_format[self._components]

                if self._immutable:
                    # Specify immutable storage for this texture.
                    # glTexStorage2D can only be called once
                    gl.glTexStorage2D(
                        self._target,
                        1,  # Levels
                        self._internal_format,
                        self._width,
                        self._height,
                    )
                    if data:
                        self.write(data)
                else:
                    # glTexImage2D can be called multiple times to re-allocate storage
                    # Specify mutable storage for this texture.
                    if self._compressed_data is True:
                        gl.glCompressedTexImage2D(
                            self._target,  # target
                            0,  # level
                            self._internal_format,  # internal_format
                            self._width,  # width
                            self._height,  # height
                            0,  # border
                            len(data),  # size
                            data,  # data
                        )
                    else:
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
                        f": {ex}"
                    )
                )

    @property
    def ctx(self) -> Context:
        """The context this texture belongs to."""
        return self._ctx

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL texture id"""
        return self._glo

    @property
    def compressed(self) -> bool:
        """Is this using a compressed format?"""
        return self._compressed

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
    def size(self) -> tuple[int, int]:
        """The size of the texture as a tuple"""
        return self._width, self._height

    @property
    def samples(self) -> int:
        """Number of samples if multisampling is enabled (read only)"""
        return self._samples

    @property
    def byte_size(self) -> int:
        """The byte size of the texture."""
        return pixel_formats[self._dtype][3] * self._components * self.width * self.height

    @property
    def components(self) -> int:
        """Number of components in the texture"""
        return self._components

    @property
    def component_size(self) -> int:
        """Size in bytes of each component"""
        return self._component_size

    @property
    def depth(self) -> bool:
        """If this is a depth texture."""
        return self._depth

    @property
    def immutable(self) -> bool:
        """Does this texture have immutable storage?"""
        return self._immutable

    @property
    def swizzle(self) -> str:
        """
        The swizzle mask of the texture (Default ``'RGBA'``).

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
            swizzle_str += swizzle_enum_to_str[v.value]

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
                swizzle_enums.append(swizzle_str_to_enum[c])
            except KeyError:
                raise ValueError(f"Swizzle value '{c}' invalid. Must be one of RGBA01")

        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)

        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_R, swizzle_enums[0])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_G, swizzle_enums[1])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_B, swizzle_enums[2])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_SWIZZLE_A, swizzle_enums[3])

    @property
    def filter(self) -> tuple[int, int]:
        """
        Get or set the ``(min, mag)`` filter for this texture.

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
        """
        return self._filter

    @filter.setter
    def filter(self, value: tuple[int, int]):
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
        Get or set the horizontal wrapping of the texture.

        This decides how textures are read when texture coordinates are outside
        the ``[0.0, 1.0]`` area. Default value is ``REPEAT``.

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
        Get or set the horizontal wrapping of the texture.

        This decides how textures are read when texture coordinates are outside the
        ``[0.0, 1.0]`` area. Default value is ``REPEAT``.

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
        """Get or set the anisotropy for this texture."""
        return self._anisotropy

    @anisotropy.setter
    def anisotropy(self, value):
        self._anisotropy = max(1.0, min(value, self._ctx.info.MAX_TEXTURE_MAX_ANISOTROPY))
        gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
        gl.glBindTexture(self._target, self._glo)
        gl.glTexParameterf(self._target, gl.GL_TEXTURE_MAX_ANISOTROPY, self._anisotropy)

    @property
    def compare_func(self) -> str | None:
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
        """
        return self._compare_func

    @compare_func.setter
    def compare_func(self, value: str | None):
        if not self._depth:
            raise ValueError("Depth comparison function can only be set on depth textures")

        if not isinstance(value, str) and value is not None:
            raise ValueError(f"value must be as string: {self._compare_funcs.keys()}")

        func = compare_funcs.get(value, None)
        if func is None:
            raise ValueError(f"value must be as string: {compare_funcs.keys()}")

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

    def read(self, level: int = 0, alignment: int = 1) -> bytes:
        """
        Read the contents of the texture.

        Args:
            level:
                The texture level to read
            alignment:
                Alignment of the start of each row in memory in number of bytes.
                Possible values: 1,2,4
        """
        if self._samples > 0:
            raise ValueError("Multisampled textures cannot be read directly")

        if self._ctx.gl_api == "gl":
            gl.glActiveTexture(gl.GL_TEXTURE0 + self._ctx.default_texture_unit)
            gl.glBindTexture(self._target, self._glo)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, alignment)

            buffer = (
                gl.GLubyte * (self.width * self.height * self._component_size * self._components)
            )()
            gl.glGetTexImage(gl.GL_TEXTURE_2D, level, self._format, self._type, buffer)
            return string_at(buffer, len(buffer))
        elif self._ctx.gl_api == "gles":
            fbo = self._ctx.framebuffer(color_attachments=[self])
            return fbo.read(components=self._components, dtype=self._dtype)
        else:
            raise ValueError("Unknown gl_api: '{self._ctx.gl_api}'")

    def write(self, data: BufferOrBufferProtocol, level: int = 0, viewport=None) -> None:
        """Write byte data from the passed source to the texture.

        The ``data`` value can be either an
        :py:class:`arcade.gl.Buffer` or anything that implements the
        `Buffer Protocol <https://docs.python.org/3/c-api/buffer.html>`_.

        The latter category includes ``bytes``, ``bytearray``,
        ``array.array``, and more. You may need to use typing
        workarounds for non-builtin types. See
        :ref:`prog-guide-gl-buffer-protocol-typing` for more
        information.

        Args:
            data:
                :class:`~arcade.gl.Buffer` or buffer protocol object with data to write.
            level:
                The texture level to write
            viewport:
                The area of the texture to write. 2 or 4 component tuple.
                (x, y, w, h) or (w, h). Default is the full texture.
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
            gl.glTexSubImage2D(self._target, level, x, y, w, h, self._format, self._type, 0)
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, 0)
        else:
            byte_size, data = data_to_ctypes(data)
            self._validate_data_size(data, byte_size, w, h)
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

    def _validate_data_size(self, byte_data, byte_size, width, height) -> None:
        """Validate the size of the data to be written to the texture"""
        # TODO: Validate data size for compressed textures
        #       This might be a bit tricky since the size of the compressed
        #       data would depend on the algorithm used.
        if self._compressed is True:
            return

        expected_size = width * height * self._component_size * self._components
        if byte_size != expected_size:
            raise ValueError(
                f"Data size {len(byte_data)} does not match expected size {expected_size}"
            )
        if len(byte_data) != byte_size:
            raise ValueError(
                f"Data size {len(byte_data)} does not match reported size {expected_size}"
            )

    def build_mipmaps(self, base: int = 0, max_level: int = 1000) -> None:
        """Generate mipmaps for this texture.

        The default values usually work well.

        Mipmaps are successively smaller versions of an original
        texture with special filtering applied. Using mipmaps allows
        OpenGL to render scaled versions of original textures with fewer
        scaling artifacts.

        Mipmaps can be made for textures of any size. Each mipmap
        version halves the width and height of the previous one (e.g.
        256 x 256, 128 x 128, 64 x 64, etc) down to a minimum of 1 x 1.

        .. note:: Mipmaps will only be used if a texture's filter is
                  configured with a mipmap-type minification::

                   # Set up linear interpolating minification filter
                   texture.filter = ctx.LINEAR_MIPMAP_LINEAR, ctx.LINEAR

        Args:
            base:
                Level the mipmaps start at (usually 0)
            max_level:
                The maximum number of levels to generate

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
        Texture2D.delete_glo(self._ctx, self._glo)
        self._glo.value = 0

    @staticmethod
    def delete_glo(ctx: "Context", glo: gl.GLuint):
        """
        Destroy the texture.

        This is called automatically when the object is garbage collected.

        Args:
            ctx: OpenGL Context
            glo: The OpenGL texture id
        """
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteTextures(1, byref(glo))

        ctx.stats.decr("texture")

    def use(self, unit: int = 0) -> None:
        """Bind the texture to a channel,

        Args:
            unit: The texture unit to bind the texture.
        """
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(self._target, self._glo)

    def bind_to_image(self, unit: int, read: bool = True, write: bool = True, level: int = 0):
        """
        Bind textures to image units.

        Note that either or both ``read`` and ``write`` needs to be ``True``.
        The supported modes are: read only, write only, read-write

        Args:
            unit: The image unit
            read: The compute shader intends to read from this image
            write: The compute shader intends to write to this image
            level: The mipmap level to bind
        """
        if self._ctx.gl_api == "gles" and not self._immutable:
            raise ValueError("Textures bound to image units must be created with immutable=True")

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

    def get_handle(self, resident: bool = True) -> int:
        """
        Get a handle for bindless texture access.

        Once a handle is created its parameters cannot be changed.
        Attempting to do so will have no effect. (filter, wrap etc).
        There is no way to undo this immutability.

        Handles cannot be used by shaders until they are resident.
        This method can be called multiple times to move a texture
        in and out of residency::

            >> texture.get_handle(resident=False)
            4294969856
            >> texture.get_handle(resident=True)
            4294969856

        Ths same handle is returned if the handle already exists.

        .. note:: Limitations from the OpenGL wiki

            The amount of storage available for resident images/textures may be less
            than the total storage for textures that is available. As such, you should
            attempt to minimize the time a texture spends being resident. Do not attempt
            to take steps like making textures resident/un-resident every frame or something.
            But if you are finished using a texture for some time, make it un-resident.

        Args:
            resident: Make the texture resident.
        """
        handle = gl.glGetTextureHandleARB(self._glo)
        is_resident = gl.glIsTextureHandleResidentARB(handle)

        # Ensure we don't try to make a resident texture resident again
        if resident:
            if not is_resident:
                gl.glMakeTextureHandleResidentARB(handle)
        else:
            if is_resident:
                gl.glMakeTextureHandleNonResidentARB(handle)

        return handle

    def __repr__(self) -> str:
        return "<Texture glo={} size={}x{} components={}>".format(
            self._glo.value, self._width, self._height, self._components
        )
