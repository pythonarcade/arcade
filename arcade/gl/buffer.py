from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from arcade.types import BufferProtocol

if TYPE_CHECKING:
    from arcade.gl import Context


class Buffer(ABC):
    """OpenGL buffer object. Buffers store byte data and upload it
    to graphics memory so shader programs can process the data.
    They are used for storage of vertex data,
    element data (vertex indexing), uniform block data etc.

    The ``data`` parameter can be anything that implements the
    `Buffer Protocol <https://docs.python.org/3/c-api/buffer.html>`_.

    This includes ``bytes``, ``bytearray``, ``array.array``, and
    more. You may need to use typing workarounds for non-builtin
    types. See :ref:`prog-guide-gl-buffer-protocol-typing` for more
    information.

    .. warning:: Buffer objects should be created using :py:meth:`arcade.gl.Context.buffer`

    Args:
        ctx:
            The context this buffer belongs to
        data:
            The data this buffer should contain. It can be a ``bytes`` instance or any
            object supporting the buffer protocol.
        reserve:
            Create a buffer of a specific byte size
        usage:
            A hit of this buffer is ``static`` or ``dynamic`` (can mostly be ignored)
    """

    __slots__ = "_ctx", "_size", "__weakref__"

    def __init__(
        self,
        ctx: Context,
    ):
        self._ctx = ctx
        self._size = -1
        self._ctx.stats.incr("buffer")

    @property
    def size(self) -> int:
        """The byte size of the buffer."""
        return self._size

    @property
    def ctx(self) -> "Context":
        """The context this resource belongs to."""
        return self._ctx

    @abstractmethod
    def delete(self) -> None:
        """
        Destroy the underlying native buffer resource.

        .. warning:: Don't use this unless you know exactly what you are doing.
        """
        pass

    @abstractmethod
    def read(self, size: int = -1, offset: int = 0) -> bytes:
        """Read data from the buffer.

        Args:
            size:
                The bytes to read. -1 means the entire buffer (default)
            offset:
                Byte read offset
        """
        pass

    @abstractmethod
    def write(self, data: BufferProtocol, offset: int = 0):
        """Write byte data to the buffer from a buffer protocol object.

        The ``data`` value can be anything that implements the
        `Buffer Protocol <https://docs.python.org/3/c-api/buffer.html>`_.

        This includes ``bytes``, ``bytearray``, ``array.array``, and
        more. You may need to use typing workarounds for non-builtin
        types. See :ref:`prog-guide-gl-buffer-protocol-typing` for more
        information.

        If the supplied data is larger than the buffer, it will be
        truncated to fit. If the supplied data is smaller than the
        buffer, the remaining bytes will be left unchanged.

        Args:
            data:
                The byte data to write. This can be bytes or any object
                supporting the buffer protocol.
            offset:
                The byte offset
        """
        pass

    @abstractmethod
    def copy_from_buffer(self, source: Buffer, size=-1, offset=0, source_offset=0):
        """Copy data into this buffer from another buffer.

        Args:
            source:
                The buffer to copy from
            size:
                The amount of bytes to copy
            offset:
                The byte offset to write the data in this buffer
            source_offset:
                The byte offset to read from the source buffer
        """
        pass

    @abstractmethod
    def orphan(self, size: int = -1, double: bool = False):
        """
        Re-allocate the entire buffer memory. This can be used to resize
        a buffer or for re-specification (orphan the buffer to avoid blocking).

        If the current buffer is busy in rendering operations
        it will be deallocated by OpenGL when completed.

        Args:
            size:
                New size of buffer. -1 will retain the current size.
                Takes precedence over ``double`` parameter if specified.
            double:
                Is passed in with `True` the buffer size will be doubled
                from its current size.
        """
        pass

    @abstractmethod
    def bind_to_uniform_block(self, binding: int = 0, offset: int = 0, size: int = -1):
        """Bind this buffer to a uniform block location.
        In most cases it will be sufficient to only provide a binding location.

        Args:
            binding:
                The binding location
            offset:
                Byte offset
            size:
                Size of the buffer to bind.
        """
        pass

    @abstractmethod
    def bind_to_storage_buffer(self, *, binding=0, offset=0, size=-1):
        """
        Bind this buffer as a shader storage buffer.

        Args:
            binding:
                The binding location
            offset:
                Byte offset in the buffer
            size:
                The size in bytes. The entire buffer will be mapped by default.
        """
        pass
