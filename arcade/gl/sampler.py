from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.gl import Context, Texture2D


class Sampler(ABC):
    """
    OpenGL sampler object.

    When bound to a texture unit it overrides all the
    sampling parameters of the texture channel.
    """

    def __init__(
        self,
        ctx: "Context",
        texture: Texture2D,
        *,
        filter=None,  # TODO: Typing, should be tuple[PyGLuint, PyGLuint] | None
        wrap_x=None,  # TODO: Typing, should be PyGLuint | None
        wrap_y=None,  # TODO: Typing, should be PyGLuint | None
    ):
        self._ctx = ctx

        # These three ultimately need to be set by the implementing backend.
        # We're creating them here first to trick some of the methods on the
        # base class to being able to see them. So that we don't have to
        # implement a getter on every backend
        self._filter = (0, 0)  # Mypy needs this to be a tuple[int, int] to be happy
        self._wrap_x = 0  # Mypy needs this to be an int to be happy
        self._wrap_y = 0  # Mypy needs this to be an int to be happy

        self.texture = texture

        self._anisotropy = 1.0
        self._compare_func: str | None = None

    @abstractmethod
    def use(self, unit: int):
        """
        Bind the sampler to a texture unit
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def clear(self, unit: int):
        """
        Unbind the sampler from a texture unit
        """
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
