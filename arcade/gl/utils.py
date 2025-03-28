"""
Various utility functions for the gl module.
"""

from array import array
from ctypes import c_byte
from typing import Any


def data_to_ctypes(data: Any) -> tuple[int, Any]:
    """
    Attempts to convert the data to ctypes if needed by using the buffer protocol.

    - bytes will be returned as is
    - Tuples will be converted to array
    - Other types will be converted to ctypes by using the buffer protocol
      by creating a memoryview and then a ctypes array of bytes.

    Args:
        data: The data to convert to ctypes.
    Returns:
        A tuple containing the size of the data in bytes
        and the data object optionally converted to ctypes.
    """
    if isinstance(data, bytes):
        return len(data), data
    else:
        if isinstance(data, tuple):
            data = array("f", data)
        try:
            m_view = memoryview(data)
            c_bytes = c_byte * m_view.nbytes
            return m_view.nbytes, c_bytes.from_buffer(m_view)
        except Exception as ex:
            raise TypeError(f"Failed to convert data to ctypes: {ex}")
