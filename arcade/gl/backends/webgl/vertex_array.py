from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Sequence

from arcade.gl import enums
from arcade.gl.types import BufferDescription, gl_name
from arcade.gl.vertex_array import Geometry, VertexArray

from .buffer import WebGLBuffer
from .program import WebGLProgram

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLVertexArrayObject as JSWebGLVertexArray

    from arcade.gl.backends.webgl.context import WebGLContext

index_types = [None, enums.UNSIGNED_BYTE, enums.UNSIGNED_SHORT, None, enums.UNSIGNED_INT]


class WebGLVertexArray(VertexArray):
    __slots__ = (
        "_glo",
        "_index_element_type",
    )

    def __init__(
        self,
        ctx: WebGLContext,
        program: WebGLProgram,
        content: Sequence[BufferDescription],
        index_buffer: WebGLBuffer | None = None,
        index_element_size: int = 4,
    ):
        super().__init__(ctx, program, content, index_buffer, index_element_size)
        self._ctx = ctx

        glo = self._ctx._gl.createVertexArray()
        assert glo is not None, "Failed to create WebGL VertexArray object"
        self._glo = glo

        self._index_element_type = index_types[index_element_size]

        self._build(program, content, index_buffer)

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, WebGLVertexArray.delete_glo, self._ctx, self._glo)

    def __repr__(self) -> str:
        return f"<VertexArray {self._glo}>"

    def __del__(self) -> None:
        # Intercept garbage collection if we are using Context.gc()
        if self._ctx.gc_mode == "context_gc" and self._glo is not None:
            self._ctx.objects.append(self)

    def delete(self) -> None:
        WebGLVertexArray.delete_glo(self._ctx, self._glo)
        self._glo = None

    @staticmethod
    def delete_glo(ctx: WebGLContext, glo: JSWebGLVertexArray | None):
        if glo is not None:
            ctx._gl.deleteVertexArray(glo)

        ctx.stats.decr("vertex_array")

    def _build(
        self,
        program: WebGLProgram,
        content: Sequence[BufferDescription],
        index_buffer: WebGLBuffer | None,
    ) -> None:
        self._ctx._gl.bindVertexArray(self._glo)

        if index_buffer is not None:
            self._ctx._gl.bindBuffer(enums.ELEMENT_ARRAY_BUFFER, index_buffer._glo)

        descr_attribs = {attr.name: (descr, attr) for descr in content for attr in descr.formats}

        for _, prog_attr in enumerate(program.attributes):
            if prog_attr.name is not None and prog_attr.name.startswith("gl_"):
                continue
            try:
                buff_descr, attr_descr = descr_attribs[prog_attr.name]
            except KeyError:
                raise ValueError(
                    (
                        f"Program needs attribute '{prog_attr.name}', but is not present in buffer "
                        f"description. Buffer descriptions: {content}"
                    )
                )

            if prog_attr.components != attr_descr.components:
                raise ValueError(
                    (
                        f"Program attribute '{prog_attr.name}' has {prog_attr.components} "
                        f"components while the buffer description has {attr_descr.components} "
                        " components. "
                    )
                )

            self._ctx._gl.enableVertexAttribArray(prog_attr.location)
            self._ctx._gl.bindBuffer(enums.ARRAY_BUFFER, buff_descr.buffer.glo)  # type: ignore

            normalized = True if attr_descr.name in buff_descr.normalized else False

            float_types = (enums.FLOAT, enums.HALF_FLOAT)
            int_types = (
                enums.INT,
                enums.UNSIGNED_INT,
                enums.SHORT,
                enums.UNSIGNED_SHORT,
                enums.BYTE,
                enums.UNSIGNED_BYTE,
            )
            attrib_type = attr_descr.gl_type
            if attrib_type in int_types and buff_descr.normalized:
                attrib_type = prog_attr.gl_type

            if attrib_type != prog_attr.gl_type:
                raise ValueError(
                    (
                        f"Program attribute '{prog_attr.name}' has type "
                        f"{gl_name(prog_attr.gl_type)}"
                        f"while the buffer description has type {gl_name(attr_descr.gl_type)}. "
                    )
                )

            if attrib_type in float_types or attrib_type in int_types:
                self._ctx._gl.vertexAttribPointer(
                    prog_attr.location,
                    attr_descr.components,
                    attr_descr.gl_type,
                    normalized,
                    buff_descr.stride,
                    attr_descr.offset,
                )
            else:
                raise ValueError(f"Unsupported attribute type: {attr_descr.gl_type}")

            if buff_descr.instanced:
                self._ctx._gl.vertexAttribDivisor(prog_attr.location, 1)

    def render(self, mode: int, first: int = 0, vertices: int = 0, instances: int = 1) -> None:
        self._ctx._gl.bindVertexArray(self._glo)
        if self._ibo is not None:
            self._ctx._gl.bindBuffer(enums.ELEMENT_ARRAY_BUFFER, self._ibo.glo)  # type: ignore
            self._ctx._gl.drawElementsInstanced(
                mode,
                vertices,
                self._index_element_type,
                first * self._index_element_size,
                instances,
            )
        else:
            self._ctx._gl.drawArraysInstanced(mode, first, vertices, instances)

    def render_indirect(self, buffer: WebGLBuffer, mode: int, count, first, stride) -> None:
        raise NotImplementedError("Indrect Rendering not supported with WebGL")

    def transform_interleaved(
        self,
        buffer: WebGLBuffer,
        mode: int,
        output_mode: int,
        first: int = 0,
        vertices: int = 0,
        instances: int = 1,
        buffer_offset=0,
    ) -> None:
        if vertices < 0:
            raise ValueError(f"Cannot determine the number of verticies: {vertices}")

        if buffer_offset >= buffer.size:
            raise ValueError("buffer_offset at end or past the buffer size")

        self._ctx._gl.bindVertexArray(self._glo)
        self._ctx._gl.enable(enums.RASTERIZER_DISCARD)

        if buffer_offset > 0:
            self._ctx._gl.bindBufferRange(
                enums.TRANSFORM_FEEDBACK_BUFFER,
                0,
                buffer.glo,
                buffer_offset,
                buffer.size - buffer_offset,
            )
        else:
            self._ctx._gl.bindBufferBase(enums.TRANSFORM_FEEDBACK_BUFFER, 0, buffer.glo)

        self._ctx._gl.beginTransformFeedback(output_mode)

        if self._ibo is not None:
            count = self._ibo.size // 4
            self._ctx._gl.drawElementsInstanced(
                mode, vertices or count, enums.UNSIGNED_INT, 0, instances
            )
        else:
            self._ctx._gl.drawArraysInstanced(mode, first, vertices, instances)

        self._ctx._gl.endTransformFeedback()
        self._ctx._gl.disable(enums.RASTERIZER_DISCARD)

    def transform_separate(
        self,
        buffers: list[WebGLBuffer],
        mode: int,
        output_mode: int,
        first: int = 0,
        vertices: int = 0,
        instances: int = 1,
        buffer_offset=0,
    ) -> None:
        if vertices < 0:
            raise ValueError(f"Cannot determine the number of vertices: {vertices}")

        size = min(buf.size for buf in buffers)
        if buffer_offset >= size:
            raise ValueError("buffer_offset at end or past the buffer size")

        self._ctx._gl.bindVertexArray(self._glo)
        self._ctx._gl.enable(enums.RASTERIZER_DISCARD)

        if buffer_offset > 0:
            for index, buffer in enumerate(buffers):
                self._ctx._gl.bindBufferRange(
                    enums.TRANSFORM_FEEDBACK_BUFFER,
                    index,
                    buffer.glo,
                    buffer_offset,
                    buffer.size - buffer_offset,
                )
        else:
            for index, buffer in enumerate(buffers):
                self._ctx._gl.bindBufferBase(enums.TRANSFORM_FEEDBACK_BUFFER, index, buffer.glo)

        self._ctx._gl.beginTransformFeedback(output_mode)

        if self._ibo is not None:
            count = self._ibo.size // 4
            self._ctx._gl.drawElementsInstanced(
                mode, vertices or count, enums.UNSIGNED_INT, 0, instances
            )
        else:
            self._ctx._gl.drawArraysInstanced(mode, first, vertices, instances)

        self._ctx._gl.endTransformFeedback()
        self._ctx._gl.disable(enums.RASTERIZER_DISCARD)


class WebGLGeometry(Geometry):
    def __init__(
        self,
        ctx: WebGLContext,
        content: Sequence[BufferDescription] | None,
        index_buffer: WebGLBuffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ) -> None:
        super().__init__(ctx, content, index_buffer, mode, index_element_size)

    def _generate_vao(self, program: WebGLProgram) -> WebGLVertexArray:
        vao = WebGLVertexArray(
            self._ctx,  # type: ignore
            program,
            self._content,
            index_buffer=self._index_buffer,  # type: ignore
            index_element_size=self._index_element_size,
        )
        self._vao_cache[program.attribute_key] = vao
        return vao
