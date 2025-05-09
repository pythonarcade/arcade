from __future__ import annotations

import weakref
from ctypes import byref, c_uint32
from typing import TYPE_CHECKING

from pyglet import gl

from .types import PyGLuint, compare_funcs

if TYPE_CHECKING:
    from arcade.gl import Context, Texture2D


class Sampler:
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
        filter: tuple[PyGLuint, PyGLuint] | None = None,
        wrap_x: PyGLuint | None = None,
        wrap_y: PyGLuint | None = None,
    ):
        self._ctx = ctx
        self._glo = -1

        value = c_uint32()
        gl.glGenSamplers(1, byref(value))
        self._glo = value.value

        self.texture = texture

        # Default filters for float and integer textures
        # Integer textures should have NEAREST interpolation
        # by default 3.3 core doesn't really support it consistently.
        if "f" in self.texture._dtype:
            self._filter = gl.GL_LINEAR, gl.GL_LINEAR
        else:
            self._filter = gl.GL_NEAREST, gl.GL_NEAREST

        self._wrap_x = gl.GL_REPEAT
        self._wrap_y = gl.GL_REPEAT
        self._anisotropy = 1.0
        self._compare_func: str | None = None

        # Only set texture parameters on non-multisample textures
        if self.texture._samples == 0:
            self.filter = filter or self._filter
            self.wrap_x = wrap_x or self._wrap_x
            self.wrap_y = wrap_y or self._wrap_y

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, Sampler.delete_glo, self._glo)

    @property
    def glo(self) -> PyGLuint:
        """The OpenGL sampler id"""
        return self._glo

    def use(self, unit: int):
        """
        Bind the sampler to a texture unit
        """
        gl.glBindSampler(unit, self._glo)

    def clear(self, unit: int):
        """
        Unbind the sampler from a texture unit
        """
        gl.glBindSampler(unit, 0)

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
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_MIN_FILTER, self._filter[0])
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_MAG_FILTER, self._filter[1])

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
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_WRAP_S, value)

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
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_WRAP_T, value)

    @property
    def anisotropy(self) -> float:
        """Get or set the anisotropy for this texture."""
        return self._anisotropy

    @anisotropy.setter
    def anisotropy(self, value):
        self._anisotropy = max(1.0, min(value, self._ctx.info.MAX_TEXTURE_MAX_ANISOTROPY))
        gl.glSamplerParameterf(self._glo, gl.GL_TEXTURE_MAX_ANISOTROPY, self._anisotropy)

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
        if not self.texture._depth:
            raise ValueError("Depth comparison function can only be set on depth textures")

        if not isinstance(value, str) and value is not None:
            raise ValueError(f"value must be as string: {self._compare_funcs.keys()}")

        func = compare_funcs.get(value, None)
        if func is None:
            raise ValueError(f"value must be as string: {compare_funcs.keys()}")

        self._compare_func = value
        if value is None:
            gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_COMPARE_MODE, gl.GL_NONE)
        else:
            gl.glSamplerParameteri(
                self._glo, gl.GL_TEXTURE_COMPARE_MODE, gl.GL_COMPARE_REF_TO_TEXTURE
            )
            gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_COMPARE_FUNC, func)

    @staticmethod
    def delete_glo(glo: int) -> None:
        """
        Delete the OpenGL object
        """
        gl.glDeleteSamplers(1, glo)
