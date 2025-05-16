from __future__ import annotations

import weakref
from ctypes import byref, c_void_p
from typing import TYPE_CHECKING, Sequence

from pyglet import gl

from arcade.gl.types import BufferDescription, GLenumLike, GLuintLike, gl_name
from arcade.gl.vertex_array import Geometry, VertexArray

from .buffer import Buffer
from .program import Program

if TYPE_CHECKING:
    from arcade.gl import Context

# Index buffer types based on index element size
index_types = [
    None,  # 0 (not supported)
    gl.GL_UNSIGNED_BYTE,  # 1 ubyte8
    gl.GL_UNSIGNED_SHORT,  # 2 ubyte16
    None,  # 3 (not supported)
    gl.GL_UNSIGNED_INT,  # 4 ubyte32
]


class OpenGLVertexArray(VertexArray):
    """
    Wrapper for Vertex Array Objects (VAOs).

    This objects should not be instantiated from user code.
    Use :py:class:`arcade.gl.Geometry` instead. It will create VAO instances for you
    automatically. There is a lot of complex interaction between programs
    and vertex arrays that will be done for you automatically.

    Args:
        ctx:
            The context this object belongs to
        program:
            The program to use
        content:
            List of BufferDescriptions
        index_buffer:
            Index/element buffer
        index_element_size:
            Byte size of the index buffer datatype.
    """

    __slots__ = (
        "glo",
        "_index_element_type",
    )

    def __init__(
        self,
        ctx: Context,
        program: Program,
        content: Sequence[BufferDescription],
        index_buffer: Buffer | None = None,
        index_element_size: int = 4,
    ) -> None:
        super().__init__(ctx, program, content, index_buffer, index_element_size)

        self.glo = glo = gl.GLuint()
        """The OpenGL resource ID"""

        self._index_element_type = index_types[index_element_size]

        self._build(program, content, index_buffer)

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, OpenGLVertexArray.delete_glo, self.ctx, glo)

    def __repr__(self) -> str:
        return f"<VertexArray {self.glo.value}>"

    def __del__(self) -> None:
        # Intercept garbage collection if we are using Context.gc()
        if self._ctx.gc_mode == "context_gc" and self.glo.value > 0:
            self._ctx.objects.append(self)

    def delete(self) -> None:
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        OpenGLVertexArray.delete_glo(self._ctx, self.glo)
        self.glo.value = 0

    @staticmethod
    def delete_glo(ctx: Context, glo: gl.GLuint) -> None:
        """
        Delete the OpenGL resource.

        This is automatically called when this object is garbage collected.
        """
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteVertexArrays(1, byref(glo))
            glo.value = 0

        ctx.stats.decr("vertex_array")

    def _build(
        self, program: Program, content: Sequence[BufferDescription], index_buffer: Buffer | None
    ) -> None:
        """
        Build a vertex array compatible with the program passed in.

        This method will bind the vertex array and set up all the vertex attributes
        according to the program's attribute specifications.

        Args:
            program:
                The program to use
            content:
                List of BufferDescriptions
            index_buffer:
                Index/element buffer
        """
        gl.glGenVertexArrays(1, byref(self.glo))
        gl.glBindVertexArray(self.glo)

        if index_buffer is not None:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, index_buffer.glo)

        # Lookup dict for BufferDescription attrib names
        descr_attribs = {attr.name: (descr, attr) for descr in content for attr in descr.formats}

        # Build the vao according to the shader's attribute specifications
        for _, prog_attr in enumerate(program.attributes):
            # Do we actually have an attribute with this name in buffer descriptions?
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

            # Make sure components described in BufferDescription and in the shader match
            if prog_attr.components != attr_descr.components:
                raise ValueError(
                    (
                        f"Program attribute '{prog_attr.name}' has {prog_attr.components} "
                        f"components while the buffer description has {attr_descr.components} "
                        " components. "
                    )
                )

            gl.glEnableVertexAttribArray(prog_attr.location)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buff_descr.buffer.glo)

            # TODO: Detect normalization
            normalized = gl.GL_TRUE if attr_descr.name in buff_descr.normalized else gl.GL_FALSE

            # Map attributes groups
            float_types = (gl.GL_FLOAT, gl.GL_HALF_FLOAT)
            double_types = (gl.GL_DOUBLE,)
            int_types = (
                gl.GL_INT,
                gl.GL_UNSIGNED_INT,
                gl.GL_SHORT,
                gl.GL_UNSIGNED_SHORT,
                gl.GL_BYTE,
                gl.GL_UNSIGNED_BYTE,
            )
            attrib_type = attr_descr.gl_type
            # Normalized integers must be mapped as floats
            if attrib_type in int_types and buff_descr.normalized:
                attrib_type = prog_attr.gl_type

            # Sanity check attribute types between shader and buffer description
            if attrib_type != prog_attr.gl_type:
                raise ValueError(
                    (
                        f"Program attribute '{prog_attr.name}' has type "
                        f"{gl_name(prog_attr.gl_type)} "
                        f"while the buffer description has type {gl_name(attr_descr.gl_type)}. "
                    )
                )

            if attrib_type in float_types:
                gl.glVertexAttribPointer(
                    prog_attr.location,  # attrib location
                    attr_descr.components,  # 1, 2, 3 or 4
                    attr_descr.gl_type,  # GL_FLOAT etc
                    normalized,  # normalize
                    buff_descr.stride,
                    c_void_p(attr_descr.offset),
                )
            elif attrib_type in double_types:
                gl.glVertexAttribLPointer(
                    prog_attr.location,  # attrib location
                    attr_descr.components,  # 1, 2, 3 or 4
                    attr_descr.gl_type,  # GL_DOUBLE etc
                    buff_descr.stride,
                    c_void_p(attr_descr.offset),
                )
            elif attrib_type in int_types:
                gl.glVertexAttribIPointer(
                    prog_attr.location,  # attrib location
                    attr_descr.components,  # 1, 2, 3 or 4
                    attr_descr.gl_type,  # GL_FLOAT etc
                    buff_descr.stride,
                    c_void_p(attr_descr.offset),
                )
            else:
                raise ValueError(f"Unsupported attribute type: {attr_descr.gl_type}")

            # print((
            #     f"gl.glVertexAttribXPointer(\n"
            #     f"    {prog_attr.location},  # attrib location\n"
            #     f"    {attr_descr.components},  # 1, 2, 3 or 4\n"
            #     f"    {attr_descr.gl_type},  # GL_FLOAT etc\n"
            #     f"    {normalized},  # normalize\n"
            #     f"    {buff_descr.stride},\n"
            #     f"    c_void_p({attr_descr.offset}),\n"
            # ))
            # TODO: Sanity check this
            if buff_descr.instanced:
                gl.glVertexAttribDivisor(prog_attr.location, 1)

    def render(
        self, mode: GLenumLike, first: int = 0, vertices: int = 0, instances: int = 1
    ) -> None:
        """
        Render the VertexArray to the currently active framebuffer.

        Args:
            mode:
                Primitive type to render. TRIANGLES, LINES etc.
            first:
                The first vertex to render from
            vertices:
                Number of vertices to render
            instances:
                OpenGL instance, used in using vertices over and over
        """
        gl.glBindVertexArray(self.glo)
        if self._ibo is not None:
            # HACK: re-bind index buffer just in case.
            #       pyglet rendering was somehow replacing the index buffer.
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._ibo.glo)
            gl.glDrawElementsInstanced(
                mode,
                vertices,
                self._index_element_type,
                first * self._index_element_size,
                instances,
            )
        else:
            gl.glDrawArraysInstanced(mode, first, vertices, instances)

    def render_indirect(self, buffer: Buffer, mode: GLuintLike, count, first, stride) -> None:
        """
        Render the VertexArray to the framebuffer using indirect rendering.

        .. Warning:: This requires OpenGL 4.3

        Args:
            buffer:
                The buffer containing one or multiple draw parameters
            mode:
                Primitive type to render. TRIANGLES, LINES etc.
            count:
                The number if indirect draw calls to run
            first:
                The first indirect draw call to start on
            stride:
                The byte stride of the draw command buffer.
                Keep the default (0) if the buffer is tightly packed.
        """
        # The default buffer stride for array and indexed
        _stride = 20 if self._ibo is not None else 16
        stride = stride or _stride
        if stride % 4 != 0 or stride < 0:
            raise ValueError(f"stride must be positive integer in multiples of 4, not {stride}.")

        # The maximum number of draw calls in the buffer
        max_commands = buffer.size // stride
        if count < 0:
            count = max_commands
        elif (first + count) > max_commands:
            raise ValueError(
                "Attempt to issue rendering commands outside the buffer. "
                f"first = {first}, count = {count} is reaching past "
                f"the buffer end. The buffer have room for {max_commands} "
                f"draw commands. byte size {buffer.size}, stride {stride}."
            )

        gl.glBindVertexArray(self.glo)
        gl.glBindBuffer(gl.GL_DRAW_INDIRECT_BUFFER, buffer._glo)
        if self._ibo:
            gl.glMultiDrawElementsIndirect(
                mode, self._index_element_type, first * stride, count, stride
            )
        else:
            gl.glMultiDrawArraysIndirect(mode, first * stride, count, stride)

    def transform_interleaved(
        self,
        buffer: Buffer,
        mode: GLenumLike,
        output_mode: GLenumLike,
        first: int = 0,
        vertices: int = 0,
        instances: int = 1,
        buffer_offset=0,
    ) -> None:
        """
        Run a transform feedback.

        Args:
            buffer:
                The buffer to write the output
            mode:
                The input primitive mode
            output_mode:
                The output primitive mode
            first:
                Offset start vertex
            vertices:
                Number of vertices to render
            instances:
                Number of instances to render
            buffer_offset:
                Byte offset for the buffer (target)
        """
        if vertices < 0:
            raise ValueError(f"Cannot determine the number of vertices: {vertices}")

        if buffer_offset >= buffer.size:
            raise ValueError("buffer_offset at end or past the buffer size")

        gl.glBindVertexArray(self.glo)
        gl.glEnable(gl.GL_RASTERIZER_DISCARD)

        if buffer_offset > 0:
            gl.glBindBufferRange(
                gl.GL_TRANSFORM_FEEDBACK_BUFFER,
                0,
                buffer.glo,
                buffer_offset,
                buffer.size - buffer_offset,
            )
        else:
            gl.glBindBufferBase(gl.GL_TRANSFORM_FEEDBACK_BUFFER, 0, buffer.glo)

        gl.glBeginTransformFeedback(output_mode)

        if self._ibo is not None:
            count = self._ibo.size // 4
            # TODO: Support first argument by offsetting pointer (second last arg)
            gl.glDrawElementsInstanced(mode, vertices or count, gl.GL_UNSIGNED_INT, None, instances)
        else:
            # print(f"glDrawArraysInstanced({mode}, {first}, {vertices}, {instances})")
            gl.glDrawArraysInstanced(mode, first, vertices, instances)

        gl.glEndTransformFeedback()
        gl.glDisable(gl.GL_RASTERIZER_DISCARD)

    def transform_separate(
        self,
        buffers: list[Buffer],
        mode: GLenumLike,
        output_mode: GLenumLike,
        first: int = 0,
        vertices: int = 0,
        instances: int = 1,
        buffer_offset=0,
    ) -> None:
        """
        Run a transform feedback writing to separate buffers.

        Args:
            buffers:
                The buffers to write the output
            mode:
                The input primitive mode
            output_mode:
                The output primitive mode
            first:
                Offset start vertex
            vertices:
                Number of vertices to render
            instances:
                Number of instances to render
            buffer_offset:
                Byte offset for the buffer (target)
        """
        if vertices < 0:
            raise ValueError(f"Cannot determine the number of vertices: {vertices}")

        # Get size from the smallest buffer
        size = min(buf.size for buf in buffers)
        if buffer_offset >= size:
            raise ValueError("buffer_offset at end or past the buffer size")

        gl.glBindVertexArray(self.glo)
        gl.glEnable(gl.GL_RASTERIZER_DISCARD)

        if buffer_offset > 0:
            for index, buffer in enumerate(buffers):
                gl.glBindBufferRange(
                    gl.GL_TRANSFORM_FEEDBACK_BUFFER,
                    index,
                    buffer.glo,
                    buffer_offset,
                    buffer.size - buffer_offset,
                )
        else:
            for index, buffer in enumerate(buffers):
                gl.glBindBufferBase(gl.GL_TRANSFORM_FEEDBACK_BUFFER, index, buffer.glo)

        gl.glBeginTransformFeedback(output_mode)

        if self._ibo is not None:
            count = self._ibo.size // 4
            # TODO: Support first argument by offsetting pointer (second last arg)
            gl.glDrawElementsInstanced(mode, vertices or count, gl.GL_UNSIGNED_INT, None, instances)
        else:
            # print(f"glDrawArraysInstanced({mode}, {first}, {vertices}, {instances})")
            gl.glDrawArraysInstanced(mode, first, vertices, instances)

        gl.glEndTransformFeedback()
        gl.glDisable(gl.GL_RASTERIZER_DISCARD)


class OpenGLGeometry(Geometry):
    """A higher level abstraction of the VertexArray.

    It generates VertexArray instances on the fly internally matching the incoming
    program. This means we can render the same geometry with different programs
    as long as the :py:class:`~arcade.gl.Program` and :py:class:`~arcade.gl.BufferDescription`
    have compatible attributes. This is an extremely powerful concept that allows
    for very flexible rendering pipelines and saves the user from a lot of manual
    bookkeeping.

    Geometry objects should be created through :py:meth:`arcade.gl.Context.geometry`

    Args:
        ctx:
            The context this object belongs to
        content:
            List of BufferDescriptions
        index_buffer:
            Index/element buffer
        mode:
            The default draw mode
        index_element_size:
            Byte size of the index buffer datatype.
            Can be 1, 2 or 4 (8, 16 or 32bit integer)
    """

    def __init__(
        self,
        ctx: "Context",
        content: Sequence[BufferDescription] | None,
        index_buffer: Buffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ) -> None:
        super().__init__(ctx, content, index_buffer, mode, index_element_size)

    def _generate_vao(self, program: Program) -> VertexArray:
        """
        Create a new VertexArray for the given program.

        Args:
            program: The program to use
        """
        # print(f"Generating vao for key {program.attribute_key}")

        vao = OpenGLVertexArray(
            self._ctx,
            program,
            self._content,
            index_buffer=self._index_buffer,
            index_element_size=self._index_element_size,
        )
        self._vao_cache[program.attribute_key] = vao
        return vao
