from __future__ import annotations

import weakref
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

from .buffer import Buffer
from .program import Program

if TYPE_CHECKING:
    from arcade.gl import Context


class VertexArray(ABC):
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
        "_ctx",
        "_program",
        "_content",
        "_ibo",
        "_index_element_size",
        "_num_vertices",
        "__weakref__",
    )

    def __init__(
        self,
        ctx: Context,
        program: Program,
        content: Sequence,  # TODO: typing, this should be Sequence[BufferDescription]
        index_buffer: Buffer | None = None,
        index_element_size: int = 4,
    ) -> None:
        self._ctx = ctx
        self._program = program
        self._content = content

        self._num_vertices = -1
        self._ibo = index_buffer
        self._index_element_size = index_element_size

        self.ctx.stats.incr("vertex_array")

    @property
    def ctx(self) -> Context:
        """The Context this object belongs to."""
        return self._ctx

    @property
    def program(self) -> Program:
        """The assigned program."""
        return self._program

    @property
    def ibo(self) -> Buffer | None:
        """Element/index buffer."""
        return self._ibo

    @property
    def num_vertices(self) -> int:
        """The number of vertices."""
        return self._num_vertices

    @abstractmethod
    def delete(self) -> None:
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def render(
        self,
        mode: int,
        first: int = 0,
        vertices: int = 0,
        instances: int = 1,  # TODO: typing, mode can also be a ctypes uint in GL backend
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def render_indirect(
        self, buffer: Buffer, mode: int, count, first, stride
    ) -> None:  # TODO: typing, mode can also be a ctypes uint in GL backend
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def transform_interleaved(
        self,
        buffer: Buffer,
        mode,  # TODO, typing. This should be GLenumLike type
        output_mode,  # TODO, typing. This should be GLenumLike type
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    def transform_separate(
        self,
        buffers: list[Buffer],
        mode,  # TODO, typing. This should be GLenumLike type
        output_mode,  # TODO, typing. This should be GLenumLike type
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")


class Geometry(ABC):
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

    __slots__ = (
        "_ctx",
        "_content",
        "_index_buffer",
        "_index_element_size",
        "_mode",
        "_vao_cache",
        "_num_vertices",
        "__weakref__",
    )

    def __init__(
        self,
        ctx: Context,
        content: Sequence | None,  # TODO: typing, this should be Sequence[BufferDescription]
        index_buffer: Buffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ) -> None:
        self._ctx = ctx
        self._content = list(content or [])
        self._index_buffer = index_buffer
        self._index_element_size = index_element_size
        self._mode = mode if mode is not None else ctx.TRIANGLES
        self._vao_cache: dict[str, VertexArray] = {}
        self._num_vertices: int = -1

        if self._index_buffer and self._index_element_size not in (1, 2, 4):
            raise ValueError("index_element_size must be 1, 2, or 4")

        if content:
            # Calculate vertices. Use the minimum for now
            if self._index_buffer:
                self._num_vertices = self._index_buffer.size // self._index_element_size
            else:
                self._num_vertices = content[0].num_vertices
                for descr in self._content:
                    if descr.instanced:
                        continue
                    self._num_vertices = min(self._num_vertices, descr.num_vertices)

        # No cleanup is needed, but we want to count them
        weakref.finalize(self, Geometry._release, self._ctx)
        self._ctx.stats.incr("geometry")

    @property
    def ctx(self) -> "Context":
        """The context this geometry belongs to."""
        return self._ctx

    @property
    def index_buffer(self) -> Buffer | None:
        """Index/element buffer if supplied at creation."""
        return self._index_buffer

    @property
    def num_vertices(self) -> int:
        """
        Get or set the number of vertices.

        Be careful when modifying this properly
        and be absolutely sure what you are doing.
        """
        # TODO: Calculate this better...
        return self._num_vertices

    @num_vertices.setter
    def num_vertices(self, value: int):
        self._num_vertices = value

    def append_buffer_description(self, descr):  # TODO: typing, descr should be BufferDescription
        """
        Append a new BufferDescription to the existing Geometry.

        .. Warning:: Geometry cannot contain two BufferDescriptions which share an attribute name.
        """
        for other_descr in self._content:
            if other_descr == descr:
                raise ValueError(
                    "Geometry cannot contain two BufferDescriptions which share an "
                    f"attribute name. Found a conflict in {descr} and {other_descr}"
                )
        self._content.append(descr)

    def instance(self, program: Program) -> VertexArray:
        """
        Get the :py:class:`arcade.gl.VertexArray` compatible with this program.
        """
        vao = self._vao_cache.get(program.attribute_key)
        if vao:
            return vao

        return self._generate_vao(program)

    def render(
        self,
        program: Program,
        *,
        mode=None,  # TODO: typing, mode should be GLenumLike | None
        first: int = 0,
        vertices: int | None = None,
        instances: int = 1,
    ) -> None:
        """Render the geometry with a specific program.

        The geometry object will know how many vertices your buffers contains
        so overriding vertices is not needed unless you have a special case
        or have resized the buffers after the geometry instance was created.

        Args:
            program:
                The Program to render with
            mode:
                Override what primitive mode should be used
            first:
                Offset start vertex
            vertices:
                Override the number of vertices to render
            instances:
                Number of instances to render
        """
        program.use()
        vao = self.instance(program)

        mode = self._mode if mode is None else mode

        # If we have a geometry shader we need to sanity check that
        # the primitive mode is supported
        if program.geometry_vertices > 0:
            if program.geometry_input == self._ctx.POINTS:
                mode = program.geometry_input
            if program.geometry_input == self._ctx.LINES:
                if mode not in [
                    self._ctx.LINES,
                    self._ctx.LINE_STRIP,
                    self._ctx.LINE_LOOP,
                    self._ctx.LINES_ADJACENCY,
                ]:
                    raise ValueError(
                        "Geometry shader expects LINES, LINE_STRIP, LINE_LOOP "
                        " or LINES_ADJACENCY as input"
                    )
            if program.geometry_input == self._ctx.LINES_ADJACENCY:
                if mode not in [self._ctx.LINES_ADJACENCY, self._ctx.LINE_STRIP_ADJACENCY]:
                    raise ValueError(
                        "Geometry shader expects LINES_ADJACENCY or LINE_STRIP_ADJACENCY as input"
                    )
            if program.geometry_input == self._ctx.TRIANGLES:
                if mode not in [
                    self._ctx.TRIANGLES,
                    self._ctx.TRIANGLE_STRIP,
                    self._ctx.TRIANGLE_FAN,
                ]:
                    raise ValueError(
                        "Geometry shader expects GL_TRIANGLES, GL_TRIANGLE_STRIP "
                        "or GL_TRIANGLE_FAN as input"
                    )
            if program.geometry_input == self._ctx.TRIANGLES_ADJACENCY:
                if mode not in [self._ctx.TRIANGLES_ADJACENCY, self._ctx.TRIANGLE_STRIP_ADJACENCY]:
                    raise ValueError(
                        "Geometry shader expects GL_TRIANGLES_ADJACENCY or "
                        "GL_TRIANGLE_STRIP_ADJACENCY as input"
                    )

        vao.render(
            mode=mode,
            first=first,
            vertices=vertices or self._num_vertices,
            instances=instances,
        )

    def render_indirect(
        self,
        program: Program,
        buffer: Buffer,
        *,
        mode=None,  # TODO: typing, mode should be GLuintLike | None
        count: int = -1,
        first: int = 0,
        stride: int = 0,
    ) -> None:
        """
        Render the VertexArray to the framebuffer using indirect rendering.

        .. Warning:: This requires OpenGL 4.3

        The following structs are expected for the buffer::

            // Array rendering - no index buffer (16 bytes)
            typedef  struct {
                uint  count;
                uint  instanceCount;
                uint  first;
                uint  baseInstance;
            } DrawArraysIndirectCommand;

            // Index rendering - with index buffer 20 bytes
            typedef  struct {
                GLuint  count;
                GLuint  instanceCount;
                GLuint  firstIndex;
                GLuint  baseVertex;
                GLuint  baseInstance;
            } DrawElementsIndirectCommand;

        The ``stride`` is the byte stride between every rendering command
        in the buffer. By default we assume this is 16 for array rendering
        (no index buffer) and 20 for indexed rendering (with index buffer)

        Args:
            program:
                The program to execute
            buffer:
                The buffer containing one or multiple draw parameters
            mode:
                Primitive type to render. TRIANGLES, LINES etc.
            count:
                The number if indirect draw calls to run.
                If omitted all draw commands in the buffer will be executed.
            first:
                The first indirect draw call to start on
            stride:
                The byte stride of the draw command buffer.
                Keep the default (0) if the buffer is tightly packed.
        """
        program.use()
        vao = self.instance(program)

        mode = self._mode if mode is None else mode
        vao.render_indirect(buffer, mode, count, first, stride)

    def transform(
        self,
        program: Program,
        buffer: Buffer | list[Buffer],
        *,
        first: int = 0,
        vertices: int | None = None,
        instances: int = 1,
        buffer_offset: int = 0,
    ) -> None:
        """
        Render with transform feedback. Instead of rendering to the screen
        or a framebuffer the result will instead end up in the ``buffer`` we supply.

        If a geometry shader is used the output primitive mode is automatically detected.

        Args:
            program:
                The Program to render with
            buffer:
                The buffer(s) we transform into.
                This depends on the programs ``varyings_capture_mode``. We can transform
                into one buffer interleaved or transform each attribute into separate buffers.
            first:
                Offset start vertex
            vertices:
                Number of vertices to render
            instances:
                Number of instances to render
            buffer_offset:
                Byte offset for the buffer
        """
        program.use()
        vao = self.instance(program)
        if program._varyings_capture_mode == "interleaved":
            if not isinstance(buffer, Buffer):
                raise ValueError(
                    (
                        "Buffer must be a single Buffer object "
                        "because the capture mode of the program is: "
                        f"{program.varyings_capture_mode}"
                    )
                )
            vao.transform_interleaved(
                buffer,
                mode=program.geometry_input,
                output_mode=program.geometry_output,
                first=first,
                vertices=vertices or self._num_vertices,
                instances=instances,
                buffer_offset=buffer_offset,
            )
        else:
            if not isinstance(buffer, list):
                raise ValueError(
                    (
                        "buffer must be a list of Buffer object "
                        "because the capture mode of the program is: "
                        f"{program.varyings_capture_mode}"
                    )
                )
            vao.transform_separate(
                buffer,
                mode=program.geometry_input,
                output_mode=program.geometry_output,
                first=first,
                vertices=vertices or self._num_vertices,
                instances=instances,
                buffer_offset=buffer_offset,
            )

    def flush(self) -> None:
        """
        Flush all the internally generated VertexArrays.

        The Geometry instance will store a VertexArray
        for every unique set of input attributes it
        stumbles over when rendering and transform calls
        are issued. This data is usually pretty light weight
        and usually don't need flushing.
        """
        self._vao_cache = {}

    @abstractmethod
    def _generate_vao(self, program: Program) -> VertexArray:
        """
        Create a new VertexArray for the given program.

        Args:
            program: The program to use
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @staticmethod
    def _release(ctx) -> None:
        """Mainly here to count destroyed instances"""
        ctx.stats.decr("geometry")
