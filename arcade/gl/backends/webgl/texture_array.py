from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

from pyodide.ffi import to_js

from arcade.gl import enums
from arcade.gl.texture_array import TextureArray
from arcade.gl.types import BufferOrBufferProtocol, compare_funcs, pixel_formats
from arcade.types import BufferProtocol

from .buffer import Buffer
from .utils import data_to_memoryview

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLTexture as JSWebGLTexture

    from arcade.gl.backends.webgl.context import WebGLContext


class WebGLTextureArray(TextureArray):
    __slots__ = (
        "_glo",
        "_target",
    )

    def __init__(
        self,
        ctx: WebGLContext,
        size: tuple[int, int, int],
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

        self._wrap_x = enums.REPEAT
        self._wrap_y = enums.REPEAT

        self._target = enums.TEXTURE_2D_ARRAY

        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._glo = self._ctx._gl.createTexture()
        if self._glo is None:
            raise RuntimeError("Cannot create TextureArray. WebGL failed to generate a texture")

        self._ctx._gl.bindTexture(self._target, self._glo)
        self._texture_2d_array(data)

        self.filter = filter = self._filter
        self.wrap_x = wrap_x or self._wrap_x
        self.wrap_y = wrap_y or self._wrap_y

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, WebGLTextureArray.delete_glo, self._ctx, self._glo)

    def resize(self, size: tuple[int, int]):
        if self._immutable:
            raise ValueError("Immutable textures cannot be resized")

        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)

        self._width, self._height = size

        self._texture_2d_array(None)

    def __del__(self):
        if self._ctx.gc_mode == "context_gc" and self._glo is not None:
            self._ctx.objects.append(self)

    def _texture_2d_array(self, data):
        try:
            format_info = pixel_formats[self._dtype]
        except KeyError:
            raise ValueError(
                f"dype '{self._dtype}' not support. Supported types are : "
                f"{tuple(pixel_formats.keys())}"
            )
        _format, _internal_format, self._type, self._component_size = format_info
        if data is not None:
            byte_length, data = data_to_memoryview(data)
            self._validate_data_size(data, byte_length, self._width, self._height, self._layers)

        self._ctx._gl.pixelStorei(enums.UNPACK_ALIGNMENT, self._alignment)
        self._ctx._gl.pixelStorei(enums.PACK_ALIGNMENT, self._alignment)

        if self._depth:
            self._ctx._gl.texImage3D(
                self._target,
                0,
                enums.DEPTH_COMPONENT24,
                self._width,
                self._height,
                self._layers,
                0,
                enums.DEPTH_COMPONENT,
                enums.UNSIGNED_INT,
                data,
            )
            self.compare_func = "<="
        else:
            self._format = _format[self._components]
            if self._internal_format is None:
                self._internal_format = _internal_format[self._components]

            if self._immutable:
                self._ctx._gl.texStorage3D(
                    self._target,
                    1,
                    self._internal_format,
                    self._width,
                    self._height,
                    self._layers,
                )
                if data:
                    self.write(data)
            else:
                if self._compressed_data is True:
                    self._ctx._gl.compressedTexImage3D(
                        self._target,
                        0,
                        self._internal_format,
                        self._width,
                        self._height,
                        self._layers,
                        0,
                        len(data),
                        data,
                    )
                else:
                    self._ctx._gl.texImage3D(
                        self._target,
                        0,
                        self._internal_format,
                        self._width,
                        self._height,
                        self._layers,
                        0,
                        self._format,
                        self._type,
                        data,
                    )

    @property
    def glo(self) -> JSWebGLTexture | None:
        return self._glo

    @property
    def swizzle(self) -> str:
        raise NotImplementedError("Texture Swizzle is not support with WebGL")

    @swizzle.setter
    def swizzle(self, value: str):
        raise NotImplementedError("Texture Swizzle is not supported with WebGL")

    @TextureArray.filter.setter
    def filter(self, value: tuple[int, int]):
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError("Texture filter must be a 2 component tuple (min, mag)")

        self._filter = value
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_MIN_FILTER, self._filter[0])
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_MAG_FILTER, self._filter[1])

    @TextureArray.wrap_x.setter
    def wrap_x(self, value: int):
        self._wrap_x = value
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_WRAP_T, value)

    @TextureArray.wrap_y.setter
    def wrap_y(self, value: int):
        self._wrap_y = value
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_WRAP_S, value)

    @TextureArray.anisotropy.setter
    def anisotropy(self, value):
        self._anisotropy = max(1.0, min(value, self._ctx.info.MAX_TEXTURE_MAX_ANISOTROPY))
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameterf(
            self._target, enums.TEXTURE_MAX_ANISOTROPY_EXT, self._anisotropy
        )

    @TextureArray.compare_func.setter
    def compare_func(self, value: str | None):
        if not self._depth:
            raise ValueError("Depth comparison function can only be set on depth textures")

        if not isinstance(value, str) and value is not None:
            raise ValueError(f"value must be as string: {compare_funcs.keys()}")

        func = compare_funcs.get(value, None)
        if func is None:
            raise ValueError(f"value must be as string: {compare_funcs.keys()}")

        self._compare_func = value
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        if value is None:
            self._ctx._gl.texParameteri(self._target, enums.TEXTURE_COMPARE_MODE, enums.NONE)
        else:
            self._ctx._gl.texParameteri(
                self._target, enums.TEXTURE_COMPARE_MODE, enums.COMPARE_REF_TO_TEXTURE
            )
            self._ctx._gl.texParameteri(self._target, enums.TEXTURE_COMPARE_FUNC, func)

    def read(self, level: int = 0, alignment: int = 1) -> bytes:
        # FIXME: Check if we can attach a layer to framebuffer for reading. OpenGL ES has same
        # problems in the OpenGL backend.
        raise NotImplementedError("Reading texture array data not supported with WebGL")

    def write(self, data: BufferOrBufferProtocol, level: int = 0, viewport=None) -> None:
        x, y, l, w, h = 0, 0, 0, self._width, self._height
        if viewport:
            if len(viewport) == 5:
                x, y, l, w, h = viewport
            else:
                raise ValueError("Viewport must be of length 5")

        if isinstance(data, Buffer):
            self._ctx._gl.bindBuffer(enums.PIXEL_UNPACK_BUFFER, data.glo)  # type: ignore
            self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
            self._ctx._gl.bindTexture(self._target, self._glo)
            self._ctx._gl.pixelStorei(enums.PACK_ALIGNMENT, 1)
            self._ctx._gl.pixelStorei(enums.UNPACK_ALIGNMENT, 1)
            self._ctx._gl.texSubImage3D(
                self._target, level, x, y, l, w, h, 1, self._format, self._type, 0
            )
            self._ctx._gl.bindBuffer(enums.PIXEL_UNPACK_BUFFER, None)
        else:
            byte_size, data = data_to_memoryview(data)
            self._validate_data_size(data, byte_size, w, h, 1)
            self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
            self._ctx._gl.bindTexture(self._target, self._glo)
            self._ctx._gl.pixelStorei(enums.PACK_ALIGNMENT, 1)
            self._ctx._gl.pixelStorei(enums.UNPACK_ALIGNMENT, 1)
            self._ctx._gl.texSubImage3D(
                self._target, level, x, y, l, w, h, 1, self._format, self._type, to_js(data), 0
            )

    def _validate_data_size(self, byte_data, byte_size, width, height) -> None:
        if self._compressed is True:
            return

        expected_size = width * height * self._component_size * self._components
        if byte_size != expected_size:
            raise ValueError(
                f"Data size {len(byte_data)} does not match expected size {expected_size}"
            )
        byte_length = len(byte_data) if isinstance(byte_data, bytes) else byte_data.nbytes
        if byte_length != byte_size:
            raise ValueError(
                f"Data size {len(byte_data)} does not match reported size {expected_size}"
            )

    def build_mipmaps(self, base: int = 0, max_level: int = 1000) -> None:
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_BASE_LEVEL, base)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_MAX_LEVEL, max_level)
        self._ctx._gl.generateMipmap(self._target)

    def delete(self):
        self.delete_glo(self._ctx, self._glo)
        self._glo = None

    @staticmethod
    def delete_glo(ctx: WebGLContext, glo: JSWebGLTexture | None):
        ctx._gl.deleteTexture(glo)
        ctx.stats.decr("texture")

    def use(self, unit: int = 0) -> None:
        self._ctx._gl.activeTexture(enums.TEXTURE0 + unit)
        self._ctx._gl.bindTexture(self._target, self._glo)

    def bind_to_image(self, unit: int, read: bool = True, write: bool = True, level: int = 0):
        raise NotImplementedError("bind_to_image not supported with WebGL")

    def get_handle(self, resident: bool = True) -> int:
        raise NotImplementedError("get_handle is not supported with WebGL")

    def __repr__(self) -> str:
        return "<TextureArray glo={} size={}x{}x{} components={}>".format(
            self._glo, self._width, self._layers, self._height, self._components
        )
