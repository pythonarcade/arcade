from array import array
from typing import Any, Tuple
from ctypes import c_byte


def data_to_ctypes(data: Any) -> Tuple[int, Any]:
    """
    Attempts to convert the data to ctypes if needed by using the buffer protocol.

    Returns the byte size and the data.
    """
    if isinstance(data, bytes):
        return len(data), data
    else:
        if isinstance(data, tuple):
            data = array('f', data)
        try:
            m_view = memoryview(data)
            c_bytes = c_byte * m_view.nbytes
            return m_view.nbytes, c_bytes.from_buffer(m_view)
        except Exception as ex:
            raise TypeError(f"Failed to convert data to ctypes: {ex}")
