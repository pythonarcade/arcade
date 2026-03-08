from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from arcade.gl import enums
from arcade.gl.sampler import Sampler
from arcade.gl.types import compare_funcs

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLSampler as JSWebGLSampler

    from arcade.gl.backends.webgl.context import WebGLContext
    from arcade.gl.backends.webgl.texture import WebGLTexture2D


class WebGLSampler(Sampler):
    def __init__(
        self,
        ctx: WebGLContext,
        texture: WebGLTexture2D,
        *,
        filter: tuple[int, int] | None = None,
        wrap_x: int | None = None,
        wrap_y: int | None = None,
    ):
        super().__init__(ctx, texture, filter=filter, wrap_x=wrap_x, wrap_y=wrap_y)
        self._ctx = ctx

        self._glo = self._ctx._gl.createSampler()

        if "f" in self.texture._dtype:
            self._filter = enums.LINEAR, enums.LINEAR
        else:
            self._filter = enums.NEAREST, enums.NEAREST

        self._wrap_x = enums.REPEAT
        self._wrap_y = enums.REPEAT

        if self.texture._samples == 0:
            self.filter = filter or self._filter
            self.wrap_x = wrap_x or self._wrap_x
            self.wrap_y = wrap_y or self._wrap_y

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, WebGLSampler.delete_glo, self._ctx, self._glo)

    @property
    def glo(self) -> JSWebGLSampler | None:
        return self._glo

    def use(self, unit: int):
        self._ctx._gl.bindSampler(unit, self._glo)

    def clear(self, unit: int):
        self._ctx._gl.bindSampler(unit, None)

    @Sampler.filter.setter
    def filter(self, value: tuple[int, int]):
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError("Texture filter must be a 2 component tuple (min, mag)")

        self._filter = value
        self._ctx._gl.samplerParameteri(
            self._glo,  # type: ignore
            enums.TEXTURE_MIN_FILTER,
            self._filter[0],
        )
        self._ctx._gl.samplerParameterf(
            self._glo,  # type: ignore
            enums.TEXTURE_MAG_FILTER,
            self._filter[1],
        )

    @Sampler.wrap_x.setter
    def wrap_x(self, value: int):
        self._wrap_x = value
        self._ctx._gl.samplerParameteri(
            self._glo,  # type: ignore
            enums.TEXTURE_WRAP_S,
            value,
        )

    @Sampler.wrap_y.setter
    def wrap_y(self, value: int):
        self._wrap_y = value
        self._ctx._gl.samplerParameteri(
            self._glo,  # type: ignore
            enums.TEXTURE_WRAP_T,
            value,
        )

    @Sampler.anisotropy.setter
    def anisotropy(self, value):
        self._anistropy = max(1.0, min(value, self._ctx.info.MAX_TEXTURE_MAX_ANISOTROPY))
        self._ctx._gl.samplerParameterf(
            self._glo,  # type: ignore
            enums.TEXTURE_MAX_ANISOTROPY_EXT,
            self._anisotropy,
        )

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
            self._ctx._gl.samplerParameteri(
                self._glo,  # type: ignore
                enums.TEXTURE_COMPARE_MODE,
                enums.NONE,
            )
        else:
            self._ctx._gl.samplerParameteri(
                self._glo,  # type: ignore
                enums.TEXTURE_COMPARE_MODE,
                enums.COMPARE_REF_TO_TEXTURE,
            )
            self._ctx._gl.samplerParameteri(
                self._glo,  # type: ignore
                enums.TEXTURE_COMPARE_FUNC,
                func,
            )

    @staticmethod
    def delete_glo(ctx: WebGLContext, glo: JSWebGLSampler | None) -> None:
        ctx._gl.deleteSampler(glo)
