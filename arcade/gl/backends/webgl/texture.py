from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from arcade.gl import enums
from arcade.gl.texture import Texture2D
from arcade.gl.types import compare_funcs, pixel_formats
from arcade.types import BufferProtocol

from .buffer import Buffer
from .utils import data_to_memoryview

if TYPE_CHECKING:
    from arcade.gl.backends.webgl.context import WebGLContext


class WebGLTexture2D(Texture2D):
    __slots__ = (
        "_glo",
        "_target",
    )

    def __init__(
        self,
        ctx: WebGLContext,
        size: tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: BufferProtocol | None = None,
        filter: tuple[int, int] | None = None,
        wrap_x: int | None = None,
        wrap_y: int | None = None,
        depth=False,
        samples: int = 0,
        immutable: bool = False,
        internal_format: int | None = None,
        compressed: bool = False,
        compressed_data: bool = False,
    ):
        if samples > 0:
            raise NotImplementedError("Multisample Textures are unsupported with WebGL")

        super().__init__(
            ctx,
            size,
            components=components,
            dtype=dtype,
            data=data,
            filter=filter,
            wrap_x=wrap_x,
            wrap_y=wrap_y,
            depth=depth,
            samples=samples,
            immutable=immutable,
            internal_format=internal_format,
            compressed=compressed,
            compressed_data=compressed_data,
        )
        self._ctx = ctx

        if "f" in self._dtype:
            self._filter = enums.LINEAR, enums.LINEAR
        else:
            self._filter = enums.NEAREST, enums.NEAREST

        self._target = enums.TEXTURE_2D

        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._glo = self._ctx._gl.createTexture()
        if self._glo is None:
            raise RuntimeError("Cannot create Texture. WebGL failed to generate a texture")

        self._ctx._gl.bindTexture(self._target, self._glo)
        self._texture_2d(data)

        self.filter = filter = self._filter
        self.wrap_x = wrap_x or self._wrap_x
        self.wrap_y = wrap_y or self._wrap_y

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, WebGLTexture2D.delete_glo, self._ctx, self._glo)

    def resize(self, size: tuple[int, int]):
        if self._immutable:
            raise ValueError("Immutable textures cannot be resized")
        
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)

        self._width, self._height = size

        self._texture_2d(None)

    def _texture_2d(self, data):
        try:
            format_info = pixel_formats[self._dtype]
        except KeyError:
            raise ValueError(
                f"dtype '{self._dtype}' not supported. Supported types are: "
                f"{tuple(pixel_formats.keys())}"
            )
        _format, _internal_format, self._type, self._component_size = format_info
        if data is not None:
            byte_length, data = data_to_memoryview(data)
            self._validate_data_size(data, byte_length, self._width, self._height)

        self._ctx._gl.pixelStorei(enums.UNPACK_ALIGNMENT, self._alignment)
        self._ctx._gl.pixelStorei(enums.PACK_ALIGNMENT, self._alignment)

        if self._depth:
            self._ctx._gl.texImage2D(
                self._target,
                0,
                enums.DEPTH_COMPONENT24,
                self._width,
                self._height,
                0,
                enums.DEPTH_COMPONENT,  # type: ignore python doesn't have arg based function signatures
                enums.UNSIGNED_INT,
                data,
            )
            self.compare_func = "<="
        else:
            self._format = _format[self._components]
            if self._internal_format is None:
                self._internal_format = _internal_format[self._components]

            if self._immutable:
                self._ctx._gl.texStorage2D(
                    self._target,
                    1,
                    self._internal_format,
                    self._width,
                    self._height,
                )
                if data:
                    self.write(data)
            else:
                if self._compressed_data is True:
                    self._ctx._gl.compressedTexImage2D(
                        self._target,
                        0,
                        self._internal_format,
                        self._width,
                        self._height,
                        0,
                        data
                    )
                else:
                    self._ctx._gl.texImage2D(
                        self._target,
                        0,
                        self._internal_format,
                        self._width,
                        self._height,
                        0,
                        self._format,  # type: ignore
                        self._type,
                        data
                    )