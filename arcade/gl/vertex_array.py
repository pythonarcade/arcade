from ctypes import c_void_p, byref
from typing import Dict, List, Optional, Sequence, TYPE_CHECKING, Union
import weakref

from pyglet import gl

from .buffer import Buffer
from .types import BufferDescription
from .program import Program

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.gl import Context

index_types = [None, gl.GL_UNSIGNED_BYTE, gl.GL_UNSIGNED_SHORT, None, gl.GL_UNSIGNED_INT]


class VertexArray:
    """Wrapper for Vertex Array Objects (VAOs).
    This objects should not be instantiated from user code.
    Use :py:class:`arcade.gl.Geometry` instead. It will create VAO instances for you
    automatically. There is a lot of complex interaction between programs
    and vertex arrays that will be done for you automatically.
    """

    __slots__ = (
        "_ctx",
        "glo",
        "_program",
        "_content",
        "_ibo",
        "_index_element_size",
        "_index_element_type",
        "_content",
        "_num_vertices",
        "__weakref__",
    )

    # TODO: Resolve what VertexArray should actually store
    def __init__(
        self,
        ctx: "Context",
        program: Program,
        content: Sequence[BufferDescription],
        index_buffer: Buffer = None,
        index_element_size: int = 4,
    ):
        self._ctx = ctx
        self._program = program
        self._content = content
        self.glo = glo = gl.GLuint()
        self._num_vertices = -1
        self._ibo = index_buffer
        self._index_element_size = index_element_size
        self._index_element_type = index_types[index_element_size]

        self._build(program, content, index_buffer)

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, VertexArray.delete_glo, self.ctx, glo)

        self.ctx.stats.incr("vertex_array")

    def __repr__(self):
        return f"<VertexArray {self.glo.value}>"

    def __del__(self):
        # Intercept garbage collection if we are using Context.gc()
        if self._ctx.gc_mode == "context_gc" and self.glo.value > 0:
            self._ctx.objects.append(self)

    @property
    def ctx(self) -> "Context":
        """
        The Context this object belongs to

        :type: :py:class:`arcade.gl.Context`
        """
        return self._ctx

    @property
    def program(self) -> Program:
        """
        The assigned program

        :type: :py:class:`arcade.gl.Program`
        """
        return self._program

    @property
    def ibo(self) -> Optional[Buffer]:
        """
        Element/index buffer

        :type: :py:class:`arcade.gl.Buffer`
        """
        return self._ibo

    @property
    def num_vertices(self) -> int:
        """
        The number of vertices

        :type: int
        """
        return self._num_vertices

    def delete(self):
        """
        Destroy the underlying OpenGL resource.
        Don't use this unless you know exactly what you are doing.
        """
        VertexArray.delete_glo(self._ctx, self.glo)
        self.glo.value = 0

    @staticmethod
    def delete_glo(ctx: "Context", glo: gl.GLuint):
        """
        Delete this object.
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
        self, program: Program, content: Sequence[BufferDescription], index_buffer
    ):
        """Build a vertex array compatible with the program passed in"""
        gl.glGenVertexArrays(1, byref(self.glo))
        gl.glBindVertexArray(self.glo)

        if index_buffer is not None:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, index_buffer.glo)

        # Lookup dict for BufferDescription attrib names
        # print(content)
        descr_attribs = {
            attr.name: (descr, attr) for descr in content for attr in descr.formats
        }
        # print('->', descr_attribs)

        # Build the vao according to the shader's attribute specifications
        for i, prog_attr in enumerate(program.attributes):
            # print('prog_attr', prog_attr)
            # Do we actually have an attribute with this name in buffer descriptions?
            if prog_attr.name.startswith("gl_"):
                continue
            try:
                buff_descr, attr_descr = descr_attribs[prog_attr.name]
            except KeyError:
                raise ValueError(
                    (
                        f"Program needs attribute '{prog_attr.name}', but is not present in buffer description. "
                        f"Buffer descriptions: {content}"
                    )
                )

            # TODO: Sanity check this
            # if buff_descr.instanced and i == 0:
            #     raise ValueError("The first vertex attribute cannot be a per instance attribute.")

            # Make sure components described in BufferDescription and in the shader match
            if prog_attr.components != attr_descr.components:
                raise ValueError(
                    (
                        f"Program attribute '{prog_attr.name}' has {prog_attr.components} components "
                        f"while the buffer description has {attr_descr.components} components. "
                    )
                )

            # TODO: Compare gltype between buffer descr and program attr

            gl.glEnableVertexAttribArray(prog_attr.location)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buff_descr.buffer.glo)

            # TODO: Detect normalization
            normalized = (
                gl.GL_TRUE if attr_descr.name in buff_descr.normalized else gl.GL_FALSE
            )
            gl.glVertexAttribPointer(
                prog_attr.location,  # attrib location
                attr_descr.components,  # 1, 2, 3 or 4
                attr_descr.gl_type,  # GL_FLOAT etc
                normalized,  # normalize
                buff_descr.stride,
                c_void_p(attr_descr.offset),
            )
            # print((
            #     f"gl.glVertexAttribPointer(\n"
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
        self, mode: gl.GLenum, first: int = 0, vertices: int = 0, instances: int = 1
    ):
        """Render the VertexArray to the currently active framebuffer.

        :param GLuint mode: Primitive type to render. TRIANGLES, LINES etc.
        :param int first: The first vertex to render from
        :param int vertices: Number of vertices to render
        :param int instances: OpenGL instance, used in using vertices over and over
        """
        gl.glBindVertexArray(self.glo)
        if self._ibo is not None:
            # HACK: re-bind index buffer just in case. pyglet rendering was somehow replacing the index buffer.
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._ibo.glo)
            gl.glDrawElementsInstanced(
                mode, vertices, self._index_element_type,
                first * self._index_element_size, instances
            )
        else:
            gl.glDrawArraysInstanced(mode, first, vertices, instances)

    def render_indirect(self, buffer: Buffer, mode: gl.GLuint, count, first, stride):
        """
        Render the VertexArray to the framebuffer using indirect rendering.

        .. Warning:: This requires OpenGL 4.3

        :param Buffer buffer: The buffer containing one or multiple draw parameters
        :param GLuint mode: Primitive type to render. TRIANGLES, LINES etc.
        :param int count: The number if indirect draw calls to run
        :param int first: The first indirect draw call to start on
        :param int stride: The byte stride of the draw command buffer.
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
            gl.glMultiDrawElementsIndirect(mode, self._index_element_type, first * stride, count, stride)
        else:
            gl.glMultiDrawArraysIndirect(mode, first * stride, count, stride)

    def transform_interleaved(
        self,
        buffer: Buffer,
        mode: gl.GLenum,
        output_mode: gl.GLenum,
        first: int = 0,
        vertices: int = 0,
        instances: int = 1,
        buffer_offset=0,
    ):
        """Run a transform feedback.

        :param Buffer buffer: The buffer to write the output
        :param gl.GLenum mode: The input primitive mode
        :param gl.GLenum output_mode: The output primitive mode
        :param int first: Offset start vertex
        :param int vertices: Number of vertices to render
        :param int instances: Number of instances to render
        :param int buffer_offset: Byte offset for the buffer (target)
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
            gl.glBindBufferBase(
                gl.GL_TRANSFORM_FEEDBACK_BUFFER, 0, buffer.glo
            )

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
        buffers: List[Buffer],
        mode: gl.GLenum,
        output_mode: gl.GLenum,
        first: int = 0,
        vertices: int = 0,
        instances: int = 1,
        buffer_offset=0,
    ):
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
                gl.glBindBufferBase(
                    gl.GL_TRANSFORM_FEEDBACK_BUFFER, index, buffer.glo
                )

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


class Geometry:
    """A higher level abstraction of the VertexArray.
    It generates VertexArray instances on the fly internally matching the incoming program.
    This means we can render the same geometry with different programs as long as the
    :py:class:`~arcade.gl.Program` and :py:class:`~arcade.gl.BufferDescription` have compatible attributes.

    Geometry objects should be created through :py:meth:`arcade.gl.Context.geometry`

    :param Contex ctx: The context this object belongs to
    :param list content: List of BufferDescriptions
    :param Buffer index_buffer: Index/element buffer
    :param int mode: The default draw mode
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
        ctx: "Context",
        content: Optional[Sequence[BufferDescription]],
        index_buffer: Buffer = None,
        mode=None,
        index_element_size: int = 4,
    ):
        self._ctx = ctx
        self._content = content or []
        self._index_buffer = index_buffer
        self._index_element_size = index_element_size
        self._mode = mode if mode is not None else ctx.TRIANGLES
        self._vao_cache = {}  # type: Dict[str, VertexArray]
        self._num_vertices = -1
        """
        :param Contex ctx: The context this object belongs to
        :param list content: List of BufferDescriptions
        :param Buffer index_buffer: Index/element buffer
        :param int mode: The default draw mode (optional)
        :param int index_element_size: Byte size of the index buffer datatype. Can be 1, 2 or 4 (8, 16 or 32bit integer)
        """
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
        """
        The context this geometry belongs to.

        :type: :py:class:`~arcade.gl.Geometry`
        """
        return self._ctx

    @property
    def index_buffer(self) -> Optional[Buffer]:
        """
        Index/element buffer if supplied at creation.

        :type: :py:class:`~arcade.gl.Buffer`
        """
        return self._index_buffer

    @property
    def num_vertices(self) -> int:
        """
        Get or set the number of vertices.
        Be careful when modifying this properly
        and be absolutely sure what you are doing.

        :type: int
        """
        # TODO: Calculate this better...
        return self._num_vertices

    @num_vertices.setter
    def num_vertices(self, value: int):
        self._num_vertices = value

    def instance(self, program: Program) -> VertexArray:
        """
        Get the :py:class:`arcade.gl.VertexArray` compatible with this program
        """
        vao = self._vao_cache.get(program.attribute_key)
        if vao:
            return vao

        return self._generate_vao(program)

    def render(
        self,
        program: Program,
        *,
        mode: gl.GLenum = None,
        first: int = 0,
        vertices: int = None,
        instances: int = 1,
    ) -> None:
        """Render the geometry with a specific program.

        The geometry object will know how many vertices your buffers contains
        so overriding vertices is not needed unless you have a special case
        or have resized the buffers after the geometry instance was created.

        :param Program program: The Program to render with
        :param gl.GLenum mode: Override what primitive mode should be used
        :param int first: Offset start vertex
        :param int vertices: Override the number of vertices to render
        :param int instances: Number of instances to render
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
                if mode not in [self._ctx.LINES, self._ctx.LINE_STRIP, self._ctx.LINE_LOOP, self._ctx.LINES_ADJACENCY]:
                    raise ValueError(
                        "Geometry shader expects LINES, LINE_STRIP, LINE_LOOP or LINES_ADJACENCY as input")
            if program.geometry_input == self._ctx.LINES_ADJACENCY:
                if mode not in [self._ctx.LINES_ADJACENCY, self._ctx.LINE_STRIP_ADJACENCY]:
                    raise ValueError(
                        "Geometry shader expects LINES_ADJACENCY or LINE_STRIP_ADJACENCY as input")
            if program.geometry_input == self._ctx.TRIANGLES:
                if mode not in [self._ctx.TRIANGLES, self._ctx.TRIANGLE_STRIP, self._ctx.TRIANGLE_FAN]:
                    raise ValueError(
                        "Geometry shader expects GL_TRIANGLES, GL_TRIANGLE_STRIP or GL_TRIANGLE_FAN as input")
            if program.geometry_input == self._ctx.TRIANGLES_ADJACENCY:
                if mode not in [self._ctx.TRIANGLES_ADJACENCY, self._ctx.TRIANGLE_STRIP_ADJACENCY]:
                    raise ValueError(
                        "Geometry shader expects GL_TRIANGLES_ADJACENCY or GL_TRIANGLE_STRIP_ADJACENCY as input")

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
        mode: gl.GLuint = None,
        count: int = -1,
        first: int = 0,
        stride: int = 0,
    ):
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

        The ``stride`` is the byte stride between every redering command
        in the buffer. By default we assume this is 16 for array rendering
        (no index buffer) and 20 for indexed rendering (with index buffer)

        :param Program program: The program to execute
        :param Buffer buffer: The buffer containing one or multiple draw parameters
        :param GLuint mode: Primitive type to render. TRIANGLES, LINES etc.
        :param int count: The number if indirect draw calls to run.
                          If omitted all draw commands in the buffer will be executed.
        :param int first: The first indirect draw call to start on
        :param int stride: The byte stride of the draw command buffer.
                           Keep the default (0) if the buffer is tightly packed.
        """
        program.use()
        vao = self.instance(program)

        mode = self._mode if mode is None else mode
        vao.render_indirect(buffer, mode, count, first, stride)

    def transform(
        self,
        program: Program,
        buffer: Union[Buffer, List[Buffer]],
        *,
        first: int = 0,
        vertices: int = None,
        instances: int = 1,
        buffer_offset: int = 0,
    ) -> None:
        """Render with transform feedback. Instead of rendering to the screen
        or a framebuffer the result will instead end up in the ``buffer`` we supply.

        If a geometry shader is used the output primitive mode is automatically detected.

        :param Program program: The Program to render with
        :param Union[Buffer, Sequence[Buffer]] buffer: The buffer(s) we transform into.
            This depends on the programs ``varyings_capture_mode``. We can transform
            into one buffer interlaved or transform each attribute into separate buffers.
        :param int first: Offset start vertex
        :param int vertices: Number of vertices to render
        :param int instances: Number of instances to render
        :param int buffer_offset: Byte offset for the buffer
        """
        program.use()
        vao = self.instance(program)
        if program._varyings_capture_mode == "interleaved":
            if not isinstance(buffer, Buffer):
                raise ValueError(
                    (
                        "Buffer must be a single Buffer object "
                        f"because the capture mode of the program is: {program.varyings_capture_mode}"
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
                        f"because the capture mode of the program is: {program.varyings_capture_mode}"
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
        stumbles over when redering and transform calls
        are issued. This data is usually pretty light weight
        and usually don't need flushing.
        """
        self._vao_cache = {}

    def _generate_vao(self, program: Program) -> VertexArray:
        """Here we do the VertexArray building"""
        # print(f"Generating vao for key {program.attribute_key}")

        vao = VertexArray(
            self._ctx,
            program,
            self._content,
            index_buffer=self._index_buffer,
            index_element_size=self._index_element_size,
        )
        self._vao_cache[program.attribute_key] = vao
        return vao

    @staticmethod
    def _release(ctx):
        """Mainly here to count destroyed instances"""
        ctx.stats.decr("geometry")
