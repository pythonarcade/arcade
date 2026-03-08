from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Optional

from pyodide.ffi import to_js

from arcade.gl import enums
from arcade.gl.texture import Texture2D
from arcade.gl.types import BufferOrBufferProtocol, compare_funcs, pixel_formats
from arcade.types import BufferProtocol

from .buffer import Buffer
from .utils import data_to_memoryview

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLTexture

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

    def __del__(self):
        if self._ctx.gc_mode == "context_gc" and self._glo is not None:
            self._ctx.objects.append(self)

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
                        self._target, 0, self._internal_format, self._width, self._height, 0, data
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
                        data,
                    )

    @property
    def ctx(self) -> WebGLContext:
        return self._ctx

    @property
    def glo(self) -> Optional[WebGLTexture]:
        return self._glo

    @property
    def compressed(self) -> bool:
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
        raise NotImplementedError("Texture Swizzle is not supported with WebGL")

    @swizzle.setter
    def swizzle(self, value: str):
        raise NotImplementedError("Texture Swizzle is not supported with WebGL")

    @Texture2D.filter.setter
    def filter(self, value: tuple[int, int]):
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError("Texture filter must be a 2 component tuple (min, mag)")

        self._filter = value
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_MIN_FILTER, self._filter[0])
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_MAG_FILTER, self._filter[1])

    @Texture2D.wrap_x.setter
    def wrap_x(self, value: int):
        self._wrap_x = value
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_WRAP_S, value)

    @Texture2D.wrap_y.setter
    def wrap_y(self, value: int):
        self._wrap_y = value
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameteri(self._target, enums.TEXTURE_WRAP_T, value)

    @Texture2D.anisotropy.setter
    def anisotropy(self, value):
        # Technically anisotropy needs EXT_texture_filter_anisotropic but it's universally supported
        self._anisotropy = max(1.0, min(value, self._ctx.info.MAX_TEXTURE_MAX_ANISOTROPY))
        self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
        self._ctx._gl.bindTexture(self._target, self._glo)
        self._ctx._gl.texParameterf(
            self._target, enums.TEXTURE_MAX_ANISOTROPY_EXT, self._anisotropy
        )

    @Texture2D.compare_func.setter
    def compare_func(self, value: str | None):
        if not self._depth:
            raise ValueError("Depth comparison function can only be set on depth textures")

        if not isinstance(value, str) and value is not None:
            raise ValueError(f"Value must a string of: {compare_funcs.keys()}")

        func = compare_funcs.get(value, None)
        if func is None:
            raise ValueError(f"Value must a string of: {compare_funcs.keys()}")

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
        # WebGL has no getTexImage, so attach this to a framebuffer and read from that
        fbo = self._ctx.framebuffer(color_attachments=[self])
        return fbo.read(components=self._components, dtype=self._dtype)

    def write(self, data: BufferOrBufferProtocol, level: int = 0, viewport=None) -> None:
        x, y, w, h = 0, 0, self._width, self._height
        if viewport:
            if len(viewport) == 2:
                (
                    w,
                    h,
                ) = viewport
            elif len(viewport) == 4:
                x, y, w, h = viewport
            else:
                raise ValueError("Viewport must be of length 2 or 4")

        if isinstance(data, Buffer):
            # type ignore here because
            self._ctx._gl.bindBuffer(enums.PIXEL_UNPACK_BUFFER, data.glo)  # type: ignore
            self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
            self._ctx._gl.bindTexture(self._target, self._glo)
            self._ctx._gl.pixelStorei(enums.PACK_ALIGNMENT, 1)
            self._ctx._gl.pixelStorei(enums.UNPACK_ALIGNMENT, 1)
            self._ctx._gl.texSubImage2D(
                self._target, level, x, y, w, h, self._format, self._type, 0
            )  # type: ignore
            self._ctx._gl.bindBuffer(enums.PIXEL_UNPACK_BUFFER, None)
        else:
            byte_size, data = data_to_memoryview(data)
            self._validate_data_size(data, byte_size, w, h)
            self._ctx._gl.activeTexture(enums.TEXTURE0 + self._ctx.default_texture_unit)
            self._ctx._gl.bindTexture(self._target, self._glo)
            self._ctx._gl.pixelStorei(enums.PACK_ALIGNMENT, 1)
            self._ctx._gl.pixelStorei(enums.UNPACK_ALIGNMENT, 1)
            # TODO: Does this to_js call create a memory leak? Need to investigate this more
            # https://pyodide.org/en/stable/usage/type-conversions.html#type-translations-pyproxy-to-js
            self._ctx._gl.texSubImage2D(
                self._target, level, x, y, w, h, self._format, self._type, to_js(data), 0
            )  # type: ignore

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
        self._ctx._gl.bindTexture(enums.TEXTURE_2D, self._glo)
        self._ctx._gl.texParameteri(enums.TEXTURE_2D, enums.TEXTURE_BASE_LEVEL, base)
        self._ctx._gl.texParameteri(enums.TEXTURE_2D, enums.TEXTURE_MAX_LEVEL, max_level)
        self._ctx._gl.generateMipmap(enums.TEXTURE_2D)

    def delete(self):
        WebGLTexture2D.delete_glo(self._ctx, self._glo)
        self._glo = None

    @staticmethod
    def delete_glo(ctx: WebGLContext, glo: WebGLTexture | None):
        if glo is not None:
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
        return "<Texture glo={} size={}x{} components={}>".format(
            self._glo, self._width, self._height, self._components
        )
