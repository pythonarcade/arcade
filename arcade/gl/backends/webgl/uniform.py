from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from arcade.gl import enums
from arcade.gl.exceptions import ShaderException

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLProgram as JSWebGLProgram

    from arcade.gl.backends.webgl.context import WebGLContext


class Uniform:
    """
    A Program uniform

    Args:
        ctx:
            The context
        program_id:
            The program id to which this uniform belongs
        location:
            The uniform location
        name:
            The uniform name
        data_type:
            The data type of the uniform
        array_length:
            The array length of the uniform
    """

    __slots__ = (
        "_program",
        "_location",
        "_name",
        "_data_type",
        "_array_length",
        "_components",
        "getter",
        "setter",
        "_ctx",
    )

    def __init__(
        self, ctx: WebGLContext, program: JSWebGLProgram, location, name, data_type, array_length
    ):
        self._ctx = ctx
        self._program = program
        self._location = location
        self._name = name
        self._data_type = data_type
        # Array length of the uniform (1 if no array)
        self._array_length = array_length
        # Number of components (including per array entry)
        self._components = 0
        self.getter: Callable
        """The getter function configured for this uniform"""
        self.setter: Callable
        """The setter function configured for this uniform"""
        self._setup_getters_and_setters()

    @property
    def location(self) -> int:
        """The location of the uniform in the program"""
        return self._location

    @property
    def name(self) -> str:
        """Name of the uniform"""
        return self._name

    @property
    def array_length(self) -> int:
        """Length of the uniform array. If not an array 1 will be returned"""
        return self._array_length

    @property
    def components(self) -> int:
        """
        How many components for the uniform.

        A vec4 will for example have 4 components.
        """
        return self._components

    def _setup_getters_and_setters(self):
        """Maps the right getter and setter functions for this uniform"""
        try:
            gl_type, gl_setter, length, count = self._ctx._uniform_setters[self._data_type]
            self._components = length
        except KeyError:
            raise ShaderException(f"Unsupported Uniform type: {self._data_type}")

        is_matrix = self._data_type in (
            enums.FLOAT_MAT2,
            enums.FLOAT_MAT3,
            enums.FLOAT_MAT4,
        )

        self.setter = Uniform._create_setter_func(
            self._ctx,
            self._program,
            self._location,
            gl_setter,
            is_matrix,
        )

    @classmethod
    def _create_setter_func(
        cls,
        ctx: WebGLContext,
        program: JSWebGLProgram,
        location,
        gl_setter,
        is_matrix,
    ):
        """Create setters for OpenGL data."""
        # Matrix uniforms
        if is_matrix:

            def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                """Set OpenGL matrix uniform data."""
                ctx._gl.useProgram(program)
                gl_setter(location, False, value)

        # Single value and multi componentuniforms
        else:

            def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                """Set OpenGL uniform data value."""
                ctx._gl.useProgram(program)
                gl_setter(location, value)

        return setter_func

    def __repr__(self) -> str:
        return f"<Uniform '{self._name}' loc={self._location} array_length={self._array_length}>"


class UniformBlock:
    """
    Wrapper for a uniform block in shaders.

    Args:
        glo:
            The OpenGL object handle
        index:
            The index of the uniform block
        size:
            The size of the uniform block
        name:
            The name of the uniform
    """

    __slots__ = ("_ctx", "glo", "index", "size", "name")

    def __init__(self, ctx: WebGLContext, glo, index: int, size: int, name: str):
        self._ctx = ctx
        self.glo = glo
        """The OpenGL object handle"""

        self.index = index
        """The index of the uniform block"""

        self.size = size
        """The size of the uniform block"""

        self.name = name
        """The name of the uniform block"""

    @property
    def binding(self) -> int:
        """Get or set the binding index for this uniform block"""
        return self._ctx._gl.getActiveUniformBlockParameter(
            self.glo, self.index, enums.UNIFORM_BLOCK_BINDING
        )

    @binding.setter
    def binding(self, binding: int):
        self._ctx._gl.uniformBlockBinding(self.glo, self.index, binding)

    def getter(self):
        """
        The getter function for this uniform block.

        Returns self.
        """
        return self

    def setter(self, value: int):
        """
        The setter function for this uniform block.

        Args:
            value: The binding index to set.
        """
        self.binding = value

    def __str__(self) -> str:
        return f"<UniformBlock {self.name} index={self.index} size={self.size}>"
