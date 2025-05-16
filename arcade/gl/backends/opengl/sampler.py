from __future__ import annotations

import weakref
from ctypes import byref, c_uint32
from typing import TYPE_CHECKING

from pyglet import gl

from arcade.gl.sampler import Sampler
from arcade.gl.types import PyGLuint, compare_funcs

if TYPE_CHECKING:
    from arcade.gl import Context, Texture2D


class OpenGLSampler(Sampler):
    """
    OpenGL sampler object.

    When bound to a texture unit it overrides all the
    sampling parameters of the texture channel.
    """

    def __init__(
        self,
        ctx: Context,
        texture: Texture2D,
        *,
        filter: tuple[PyGLuint, PyGLuint] | None = None,
        wrap_x: PyGLuint | None = None,
        wrap_y: PyGLuint | None = None,
    ):
        super().__init__(ctx, texture, filter=filter, wrap_x=wrap_x, wrap_y=wrap_y)
        self._glo = -1

        value = c_uint32()
        gl.glGenSamplers(1, byref(value))
        self._glo = value.value

        # Default filters for float and integer textures
        # Integer textures should have NEAREST interpolation
        # by default 3.3 core doesn't really support it consistently.
        if "f" in self.texture._dtype:
            self._filter = gl.GL_LINEAR, gl.GL_LINEAR
        else:
            self._filter = gl.GL_NEAREST, gl.GL_NEAREST

        self._wrap_x = gl.GL_REPEAT
        self._wrap_y = gl.GL_REPEAT

        # Only set texture parameters on non-multisample textures
        if self.texture._samples == 0:
            self.filter = filter or self._filter
            self.wrap_x = wrap_x or self._wrap_x
            self.wrap_y = wrap_y or self._wrap_y

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, OpenGLSampler.delete_glo, self._glo)

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

    @Sampler.filter.setter
    def filter(self, value: tuple[int, int]):
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError("Texture filter must be a 2 component tuple (min, mag)")

        self._filter = value
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_MIN_FILTER, self._filter[0])
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_MAG_FILTER, self._filter[1])

    @Sampler.wrap_x.setter
    def wrap_x(self, value: int):
        self._wrap_x = value
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_WRAP_S, value)

    @Sampler.wrap_y.setter
    def wrap_y(self, value: int):
        self._wrap_y = value
        gl.glSamplerParameteri(self._glo, gl.GL_TEXTURE_WRAP_T, value)

    @Sampler.anisotropy.setter
    def anisotropy(self, value):
        self._anisotropy = max(1.0, min(value, self._ctx.info.MAX_TEXTURE_MAX_ANISOTROPY))
        gl.glSamplerParameterf(self._glo, gl.GL_TEXTURE_MAX_ANISOTROPY, self._anisotropy)

    @Sampler.compare_func.setter
    def compare_func(self, value: str | None):
        if not self.texture._depth:
            raise ValueError("Depth comparison function can only be set on depth textures")

        if not isinstance(value, str) and value is not None:
            raise ValueError(f"value must be as string: {compare_funcs.keys()}")

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
