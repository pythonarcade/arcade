from __future__ import annotations

import weakref
from typing import TYPE_CHECKING

import js  # type: ignore

from arcade.gl import enums
from arcade.gl.buffer import Buffer, _usages
from arcade.types import BufferProtocol

from .utils import data_to_memoryview

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLBuffer as JSWebGLBuffer

    from arcade.gl.backends.webgl.context import WebGLContext


class WebGLBuffer(Buffer):
    __slots__ = "_glo", "_usage"

    def __init__(
        self,
        ctx: WebGLContext,
        data: BufferProtocol | None = None,
        reserve: int = 0,
        usage: str = "static",
    ):
        super().__init__(ctx)
        self._ctx: WebGLContext = ctx
        self._usage = _usages[usage]
        self._glo: JSWebGLBuffer | None = ctx._gl.createBuffer()

        if self._glo is None:
            raise RuntimeError("Cannot create Buffer object.")

        ctx._gl.bindBuffer(enums.ARRAY_BUFFER, self._glo)

        if data is not None and len(data) > 0:  # type: ignore
            self._size, data = data_to_memoryview(data)
            js_array_buffer = js.ArrayBuffer.new(self._size)
            js_array_buffer.assign(data)
            ctx._gl.bufferData(enums.ARRAY_BUFFER, js_array_buffer, self._usage)
        elif reserve > 0:
            self._size = reserve
            # WebGL allows passing an integer size instead of a memoryview
            # to populate the buffer with zero bytes. We have to provide the bytes
            # ourselves in OpenGL
            ctx._gl.bufferData(enums.ARRAY_BUFFER, self._size, self._usage)
        else:
            raise ValueError("Buffer takes byte data or number of reserved bytes")

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, WebGLBuffer.delete_glo, self.ctx, self._glo)  # type: ignore

    def __repr__(self):
        return f"<Buffer {self._glo}>"

    def __del__(self):
        if self._ctx.gc_mode == "context_gc" and self._glo is not None:
            self._ctx.objects.append(self)

    @property
    def glo(self) -> JSWebGLBuffer | None:
        return self._glo

    def delete(self) -> None:
        WebGLBuffer.delete_glo(self._ctx, self._glo)  # type: ignore
        self._glo = None

    @staticmethod
    def delete_glo(ctx: WebGLContext, glo: JSWebGLBuffer | None):
        if glo is not None:
            ctx._gl.deleteBuffer(glo)

        ctx.stats.decr("buffer")

    def read(self, size: int = -1, offset: int = 0) -> bytes:
        # framebuffer has kind of an example to do this but it's with typed arrays
        # need to figure out how to read to a generic ArrayBuffer and get a memoryview from that
        # for generic buffers since we have no idea what the data type might be
        raise NotImplementedError("Not done yet")

    def write(self, data: BufferProtocol, offset: int = 0):
        self._ctx._gl.bindBuffer(enums.ARRAY_BUFFER, self._glo)
        size, data = data_to_memoryview(data)
        js_array_buffer = js.ArrayBuffer.new(size)
        js_array_buffer.assign(data)
        # Ensure we don't write outside the buffer
        size = min(size, self._size - offset)
        if size < 0:
            raise ValueError("Attempting to write negative number bytes to buffer")
        self._ctx._gl.bufferSubData(enums.ARRAY_BUFFER, offset, js_array_buffer)

    def copy_from_buffer(self, source: WebGLBuffer, size=-1, offset=0, source_offset=0):
        if size == -1:
            size = source.size

        if size + source_offset > source.size:
            raise ValueError("Attempting to read outside the source buffer")

        if size + offset > self._size:
            raise ValueError("Attempting to write outside the buffer")

        self._ctx._gl.bindBuffer(enums.COPY_READ_BUFFER, source.glo)
        self._ctx._gl.bindBuffer(enums.COPY_WRITE_BUFFER, self._glo)
        self._ctx._gl.copyBufferSubData(
            enums.COPY_READ_BUFFER, enums.COPY_WRITE_BUFFER, source_offset, offset, size
        )

    def orphan(self, size: int = -1, double: bool = False):
        if size > 0:
            self._size = size
        elif double is True:
            self._size *= 2

        self._ctx._gl.bindBuffer(enums.ARRAY_BUFFER, self._glo)
        self._ctx._gl.bufferData(enums.ARRAY_BUFFER, self._size, self._usage)

    def bind_to_uniform_block(self, binding: int = 0, offset: int = 0, size: int = -1):
        if size < 0:
            size = self.size

        self._ctx._gl.bindBufferRange(enums.UNIFORM_BUFFER, binding, self._glo, offset, size)

    def bind_to_storage_buffer(self, *, binding=0, offset=0, size=-1):
        raise NotImplementedError("bind_to_storage_buffer is not suppported with WebGL")
