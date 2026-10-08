"""
Various utility functions for the gl module.
"""

from array import array
from typing import Any, Union


def data_to_memoryview(data: Any) -> tuple[int, Union[bytes, memoryview]]:
    """
    Attempts to convert the data to a memoryview if needed

    - bytes will be returned as is
    - Tuples will be converted to array
    - Other types will be converted directly to memoryview

    Args:
        data: The data to convert to ctypes.
    Returns:
        A tuple containing the size of the data in bytes
        and the data object optionally converted to a memoryview.
    """
    if isinstance(data, bytes):
        return len(data), data
    else:
        if isinstance(data, tuple):
            data = array("f", data)
        try:
            m_view = memoryview(data)
            return m_view.nbytes, m_view
        except Exception as ex:
            raise TypeError(f"Failed to convert data to memoryview: {ex}")
