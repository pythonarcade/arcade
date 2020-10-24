from ctypes import c_byte, byref, string_at
import weakref
from typing import Any, Optional, Tuple, TYPE_CHECKING

from pyglet import gl

from .utils import data_to_ctypes

if TYPE_CHECKING:  # handle import cycle caused by type hinting
    from arcade.gl import Context


class Buffer:
    """OpenGL buffer object. Buffers store byte data and upload it
    to graphics memory so shader programs can process the data.
    They are used for storage of vertex data,
    element data (vertex indexing), uniform block data etc.

    Buffer objects should be created using :py:meth:`arcade.gl.Context.buffer`
    """

    __slots__ = "_ctx", "_glo", "_size", "_usage", "__weakref__"
    _usages = {
        "static": gl.GL_STATIC_DRAW,
        "dynamic": gl.GL_DYNAMIC_DRAW,
        "stream": gl.GL_STREAM_DRAW,
    }

    def __init__(
        self, ctx: "Context", data: Optional[Any] = None, reserve: int = 0, usage: str = "static"
    ):
        """
        :param Context ctx: The context this buffer belongs to
        :param Any data: The data this buffer should contain. It can be bytes or any object supporting the buffer protocol.
        :param int reserve: Create a buffer of a specific byte size
        :param str usage: A hit of this buffer is ``static`` or ``dynamic`` (can mostly be ignored)
        """
        self._ctx = ctx
        self._glo = glo = gl.GLuint()
        self._size = -1
        self._usage = Buffer._usages[usage]

        gl.glGenBuffers(1, byref(self._glo))
        # print(f"glGenBuffers() -> {self._glo.value}")
        if self._glo.value == 0:
            raise RuntimeError("Cannot create Buffer object.")

        # print(f"glBindBuffer({self._glo.value})")
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        # print(f"glBufferData(gl.GL_ARRAY_BUFFER, {self._size}, data, {self._usage})")

        if data is not None and len(data) > 0:
            self._size, data = data_to_ctypes(data)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self._size, data, self._usage)
        elif reserve > 0:
            self._size = reserve
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self._size, None, self._usage)
        else:
            raise ValueError("Buffer takes byte data or number of reserved bytes")

        self.ctx.stats.incr("buffer")
        weakref.finalize(self, Buffer.release, self.ctx, glo)

    @property
    def size(self) -> int:
        """
        The byte size of the buffer.

        :type: int
        """
        return self._size

    @property
    def ctx(self) -> "Context":
        """
        The context this resource belongs to.

        :type: :py:class:`arcade.gl.Context`
        """
        return self._ctx

    @property
    def glo(self) -> gl.GLuint:
        """
        The OpenGL resource id

        :type: gl.GLuint
        """
        return self._glo

    @staticmethod
    def release(ctx: "Context", glo: gl.GLuint):
        """
        Release/delete open gl buffer.
        This is automatically called when the object is garbage collected.
        """
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteBuffers(1, byref(glo))
            glo.value = 0

        ctx.stats.decr("buffer")

    def read(self, size=-1, offset=0) -> bytes:
        """Read data from the buffer.

        :param int size: The bytes to read. -1 means the entire buffer (default)
        :param int offset: Byte read offset
        :rtype: bytes
        """
        if size == -1:
            size = self._size

        # Catch this before confusing INVALID_OPERATION is raised
        if size < 1:
            raise ValueError("Attempting to read 0 or less bytes from buffer")

        # Manually detect this so it doesn't raise a confusing INVALID_VALUE error
        if size + offset > self._size:
            raise ValueError(
                (
                    "Attempting to read outside the buffer. "
                    f"Buffer size: {self._size} "
                    f"Reading from {offset} to {size + offset}"
                )
            )

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        ptr = gl.glMapBufferRange(gl.GL_ARRAY_BUFFER, offset, size, gl.GL_MAP_READ_BIT)
        data = string_at(ptr, size=size)
        gl.glUnmapBuffer(gl.GL_ARRAY_BUFFER)
        return data

    def write(self, data: Any, offset: int = 0):
        """Write byte data to the buffer.

        :param bytes data: The byte data to write. This can be bytes or any object supporting the buffer protocol.
        :param int offset: The byte offset
        """
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        size, data = data_to_ctypes(data)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, gl.GLintptr(offset), size, data)

    def copy_from_buffer(self, source: "Buffer", size=-1, offset=0, source_offset=0):
        """Copy data into this buffer from another buffer

        :param Buffer source: The buffer to copy from
        :param int size: The amount of bytes to copy
        :param int offset: The byte offset to write the data in this buffer
        :param int source_offset: The byte offset to read from the source buffer
        """
        # Read the entire source buffer into this buffer
        if size == -1:
            size = source.size

        # TODO: Check buffer bounds
        if size + source_offset > source.size:
            raise ValueError("Attempting to read outside the source buffer")

        if size + offset > self._size:
            raise ValueError("Attempting to write outside the buffer")

        gl.glBindBuffer(gl.GL_COPY_READ_BUFFER, source.glo)
        gl.glBindBuffer(gl.GL_COPY_WRITE_BUFFER, self._glo)
        gl.glCopyBufferSubData(
            gl.GL_COPY_READ_BUFFER,
            gl.GL_COPY_WRITE_BUFFER,
            gl.GLintptr(source_offset),  # readOffset
            gl.GLintptr(offset),  # writeOffset
            size,  # size (number of bytes to copy)
        )

    def orphan(self, size=-1, double: bool = False):
        """
        Re-allocate the entire buffer memory. This can be used to resize
        a buffer or for re-specification (orphan the buffer to avoid blocking).

        If the current buffer is busy in redering operations
        it will be deallocated by OpenGL when completed.

        :param int size: New size of buffer. -1 will retain the current size.
        :param bool double: Is passed in with `True` the buffer size will be doubled
        """
        if size > -1:
            self._size = size

        if double:
            self._size *= 2

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self._size, None, self._usage)

    def bind_to_uniform_block(self, binding: int = 0, offset: int = 0, size: int = -1):
        """Bind this buffer to a uniform block location.
        In most cases it will be sufficient to only provice a binding location.
        
        :param int binding: The binding location
        :param int offset: byte offset
        :param int size: size of the buffer to bind.
        """
        if size < 0:
            size = self.size

        gl.glBindBufferRange(gl.GL_UNIFORM_BUFFER, binding, self._glo, offset, size)
