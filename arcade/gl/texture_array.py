from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..types import BufferProtocol
from .types import (
    BufferOrBufferProtocol,
    pixel_formats,
)

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.gl import Context


class TextureArray(ABC):
    """
    An OpenGL 2D texture array.

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
            The size of the texture (width, height, layers)
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
        "_width",
        "_height",
        "_layers",
        "_dtype",
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
        size: tuple[int, int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        filter=None,
        wrap_x=None,
        wrap_y=None,
        depth=False,
        samples: int = 0,
        immutable: bool = False,
        internal_format=None,
        compressed: bool = False,
        compressed_data: bool = False,
    ):
        self._ctx = ctx
        self._width, self._height, self._layers = size
        self._dtype = dtype
        self._components = components
        self._component_size = 0
        self._alignment = 1
        self._samples = min(max(0, samples), self._ctx.info.MAX_SAMPLES)
        self._depth = depth
        self._immutable = immutable
        self._compare_func: str | None = None
        self._anisotropy = 1.0
        self._internal_format = internal_format
        self._compressed = compressed
        self._compressed_data = compressed_data

        # These three ultimately need to be set by the implementing backend.
        # We're creating them here first to trick some of the methods on the
        # base class to being able to see them. So that we don't have to
        # implement a getter on every backend
        self._filter = (0, 0)  # Mypy needs this to be a tuple[int, int] to be happy
        self._wrap_x = 0  # Mypy needs this to be an int to be happy
        self._wrap_y = 0  # Mypy needs this to be an int to be happy

        if self._components not in [1, 2, 3, 4]:
            raise ValueError("Components must be 1, 2, 3 or 4")

        if data and self._samples > 0:
            raise ValueError(
                "Multisampled textures are not writable (cannot be initialized with data)"
            )

        self.ctx.stats.incr("texture")

    @abstractmethod
    def resize(self, size: tuple[int, int]):
        """
        Resize the texture. This will re-allocate the internal
        memory and all pixel data will be lost.

        .. note:: Immutable textures cannot be resized.

        Args:
            size: The new size of the texture
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    def ctx(self) -> Context:
        """The context this texture belongs to."""
        return self._ctx

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
    def layers(self) -> int:
        """The number of layers in the texture"""
        return self._layers

    @property
    def dtype(self) -> str:
        """The data type of each component"""
        return self._dtype

    @property
    def size(self) -> tuple[int, int, int]:
        """The size of the texture as a tuple"""
        return self._width, self._height, self._layers

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
    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @swizzle.setter
    @abstractmethod
    def swizzle(self, value: str):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def filter(self, value: tuple[int, int]):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def wrap_x(self, value: int):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def wrap_y(self, value: int):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    def anisotropy(self) -> float:
        """Get or set the anisotropy for this texture."""
        return self._anisotropy

    @anisotropy.setter
    @abstractmethod
    def anisotropy(self, value):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

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
    @abstractmethod
    def compare_func(self, value: str | None):
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def write(self, data: BufferOrBufferProtocol, level: int = 0, viewport=None) -> None:
        """Write byte data into layers of the texture.

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
                The texture level to write (LoD level, now layer)
            viewport:
                The area of the texture to write. Should be a 3 or 5-component tuple
                `(x, y, layer, width, height)` writes to an area of a single layer.
                If not provided the entire texture is written to.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    def _validate_data_size(
        self, byte_data, byte_size: int, width: int, height: int, layers: int
    ) -> None:
        """Validate the size of the data to be written to the texture"""
        # TODO: Validate data size for compressed textures
        #       This might be a bit tricky since the size of the compressed
        #       data would depend on the algorithm used.
        if self._compressed is True:
            return

        expected_size = width * height * layers * self._component_size * self._components
        if byte_size != expected_size:
            raise ValueError(
                f"Data size {len(byte_data)} does not match expected size {expected_size}"
            )
        if len(byte_data) != byte_size:
            raise ValueError(
                f"Data size {len(byte_data)} does not match reported size {expected_size}"
            )

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def use(self, unit: int = 0) -> None:
        """Bind the texture to a channel,

        Args:
            unit: The texture unit to bind the texture.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")
