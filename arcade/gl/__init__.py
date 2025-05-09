"""
A wrapper over OpenGL 3.3 core making OpenGL more reasonable to work with and easier
to learn. The API is based on `ModernGL <https://github.com/moderngl/moderngl>`_
implementing a subset of the features. We use pyglet's OpenGL bindings based on ctypes.

Creating OpenGL resources such as buffers, framebuffers, programs (shaders) and textures
should be done through methods in a context.

* Arcade users should access :py:attr:`arcade.Window.ctx` exposing an
  :py:class:`arcade.ArcadeContext`
* Pyglet users can instantiate an :py:class:`arcade.gl.Context` for the window or
  extend this class with more features if needed.

.. warning:: This module contains the low level rendering API for arcade
             and is only recommended for more advanced users
"""

from .context import Context
from .types import BufferDescription
from .compute_shader import ComputeShader
from .exceptions import ShaderException
from .enums import *  # noqa
from .buffer import Buffer
from .vertex_array import Geometry, VertexArray
from .texture import Texture2D
from .texture_array import TextureArray
from .sampler import Sampler
from .framebuffer import Framebuffer
from .program import Program
from .query import Query
from . import geometry

__all__ = [
    "Buffer",
    "BufferDescription",
    "ComputeShader",
    "Context",
    "Framebuffer",
    "Geometry",
    "Program",
    "Query",
    "ShaderException",
    "VertexArray",
    "Texture2D",
    "TextureArray",
    "Sampler",
    "geometry",
]
