"""Utilities for dealing with Shaders in OpenGL 3.3+.
"""

from ctypes import (
    c_char, c_int, c_buffer,
    c_char_p, c_void_p,
    cast, POINTER, pointer, byref, sizeof,
    create_string_buffer, string_at,
)
import re
from collections import namedtuple
from pathlib import Path
import weakref
from typing import List, Tuple, Iterable, Dict, Optional, Union


from pyglet import gl
