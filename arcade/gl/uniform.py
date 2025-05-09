import struct
from ctypes import POINTER, c_double, c_float, c_int, c_uint, cast
from typing import Callable

from pyglet import gl

from .exceptions import ShaderException


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

    _type_to_struct = {
        c_float: "f",
        c_int: "i",
        c_uint: "I",
        c_double: "d",
    }

    _uniform_getters = {
        gl.GLint: gl.glGetUniformiv,
        gl.GLuint: gl.glGetUniformuiv,
        gl.GLfloat: gl.glGetUniformfv,
    }

    _uniform_setters = {
        # uniform type: (gl_type, setter, length, count)
        # Integers 32 bit
        gl.GL_INT: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_INT_VEC2: (gl.GLint, gl.glProgramUniform2iv, gl.glUniform2iv, 2, 1),
        gl.GL_INT_VEC3: (gl.GLint, gl.glProgramUniform3iv, gl.glUniform3iv, 3, 1),
        gl.GL_INT_VEC4: (gl.GLint, gl.glProgramUniform4iv, gl.glUniform4iv, 4, 1),
        # Unsigned integers 32 bit
        gl.GL_UNSIGNED_INT: (gl.GLuint, gl.glProgramUniform1uiv, gl.glUniform1uiv, 1, 1),
        gl.GL_UNSIGNED_INT_VEC2: (gl.GLuint, gl.glProgramUniform2uiv, gl.glUniform2uiv, 2, 1),
        gl.GL_UNSIGNED_INT_VEC3: (gl.GLuint, gl.glProgramUniform3uiv, gl.glUniform3uiv, 3, 1),
        gl.GL_UNSIGNED_INT_VEC4: (gl.GLuint, gl.glProgramUniform4uiv, gl.glUniform4uiv, 4, 1),
        # Integers 64 bit unsigned
        gl.GL_INT64_ARB: (gl.GLint64, gl.glProgramUniform1i64vARB, gl.glUniform1i64vARB, 1, 1),
        gl.GL_INT64_VEC2_ARB: (gl.GLint64, gl.glProgramUniform2i64vARB, gl.glUniform2i64vARB, 2, 1),
        gl.GL_INT64_VEC3_ARB: (gl.GLint64, gl.glProgramUniform3i64vARB, gl.glUniform3i64vARB, 3, 1),
        gl.GL_INT64_VEC4_ARB: (gl.GLint64, gl.glProgramUniform4i64vARB, gl.glUniform4i64vARB, 4, 1),
        # Unsigned integers 64 bit
        gl.GL_UNSIGNED_INT64_ARB: (
            gl.GLuint64,
            gl.glProgramUniform1ui64vARB,
            gl.glUniform1ui64vARB,
            1,
            1,
        ),
        gl.GL_UNSIGNED_INT64_VEC2_ARB: (
            gl.GLuint64,
            gl.glProgramUniform2ui64vARB,
            gl.glUniform2ui64vARB,
            2,
            1,
        ),
        gl.GL_UNSIGNED_INT64_VEC3_ARB: (
            gl.GLuint64,
            gl.glProgramUniform3ui64vARB,
            gl.glUniform3ui64vARB,
            3,
            1,
        ),
        gl.GL_UNSIGNED_INT64_VEC4_ARB: (
            gl.GLuint64,
            gl.glProgramUniform4ui64vARB,
            gl.glUniform4ui64vARB,
            4,
            1,
        ),
        # Bools
        gl.GL_BOOL: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_BOOL_VEC2: (gl.GLint, gl.glProgramUniform2iv, gl.glUniform2iv, 2, 1),
        gl.GL_BOOL_VEC3: (gl.GLint, gl.glProgramUniform3iv, gl.glUniform3iv, 3, 1),
        gl.GL_BOOL_VEC4: (gl.GLint, gl.glProgramUniform4iv, gl.glUniform4iv, 4, 1),
        # Floats 32 bit
        gl.GL_FLOAT: (gl.GLfloat, gl.glProgramUniform1fv, gl.glUniform1fv, 1, 1),
        gl.GL_FLOAT_VEC2: (gl.GLfloat, gl.glProgramUniform2fv, gl.glUniform2fv, 2, 1),
        gl.GL_FLOAT_VEC3: (gl.GLfloat, gl.glProgramUniform3fv, gl.glUniform3fv, 3, 1),
        gl.GL_FLOAT_VEC4: (gl.GLfloat, gl.glProgramUniform4fv, gl.glUniform4fv, 4, 1),
        # Floats 64 bit
        gl.GL_DOUBLE: (gl.GLdouble, gl.glProgramUniform1dv, gl.glUniform1dv, 1, 1),
        gl.GL_DOUBLE_VEC2: (gl.GLdouble, gl.glProgramUniform2dv, gl.glUniform2dv, 2, 1),
        gl.GL_DOUBLE_VEC3: (gl.GLdouble, gl.glProgramUniform3dv, gl.glUniform3dv, 3, 1),
        gl.GL_DOUBLE_VEC4: (gl.GLdouble, gl.glProgramUniform4dv, gl.glUniform4dv, 4, 1),
        # 1D Samplers
        gl.GL_SAMPLER_1D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_INT_SAMPLER_1D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_UNSIGNED_INT_SAMPLER_1D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_1D_ARRAY: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        # 2D samplers
        gl.GL_SAMPLER_2D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_SAMPLER_2D_MULTISAMPLE: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_INT_SAMPLER_2D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_UNSIGNED_INT_SAMPLER_2D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_2D_MULTISAMPLE: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        # Array
        gl.GL_SAMPLER_2D_ARRAY: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_2D_MULTISAMPLE_ARRAY: (
            gl.GLint,
            gl.glProgramUniform1iv,
            gl.glUniform1iv,
            1,
            1,
        ),
        # 3D
        gl.GL_SAMPLER_3D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        # Cube
        gl.GL_SAMPLER_CUBE: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_CUBE_MAP_ARRAY: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        # Matrices
        gl.GL_FLOAT_MAT2: (gl.GLfloat, gl.glProgramUniformMatrix2fv, gl.glUniformMatrix2fv, 4, 1),
        gl.GL_FLOAT_MAT3: (gl.GLfloat, gl.glProgramUniformMatrix3fv, gl.glUniformMatrix3fv, 9, 1),
        gl.GL_FLOAT_MAT4: (gl.GLfloat, gl.glProgramUniformMatrix4fv, gl.glUniformMatrix4fv, 16, 1),
        # Image (compute shader)
        gl.GL_IMAGE_1D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_RECT: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_3D: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_CUBE: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_1D_ARRAY: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_ARRAY: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_CUBE_MAP_ARRAY: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_MULTISAMPLE: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_MULTISAMPLE_ARRAY: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_BUFFER: (gl.GLint, gl.glProgramUniform1iv, gl.glUniform1iv, 1, 1),
        # TODO: test/implement these:
        # gl.GL_FLOAT_MAT2x3: glUniformMatrix2x3fv,
        # gl.GL_FLOAT_MAT2x4: glUniformMatrix2x4fv,
        #
        # gl.GL_FLOAT_MAT3x2: glUniformMatrix3x2fv,
        # gl.GL_FLOAT_MAT3x4: glUniformMatrix3x4fv,
        #
        # gl.GL_FLOAT_MAT4x2: glUniformMatrix4x2fv,
        # gl.GL_FLOAT_MAT4x3: glUniformMatrix4x3fv,
    }

    __slots__ = (
        "_program_id",
        "_location",
        "_name",
        "_data_type",
        "_array_length",
        "_components",
        "getter",
        "setter",
        "_ctx",
    )

    def __init__(self, ctx, program_id, location, name, data_type, array_length):
        self._ctx = ctx
        self._program_id = program_id
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
            gl_type, gl_program_setter, gl_setter, length, count = self._uniform_setters[
                self._data_type
            ]
            self._components = length
        except KeyError:
            raise ShaderException(f"Unsupported Uniform type: {self._data_type}")

        gl_getter = self._uniform_getters[gl_type]
        is_matrix = self._data_type in (
            gl.GL_FLOAT_MAT2,
            gl.GL_FLOAT_MAT3,
            gl.GL_FLOAT_MAT4,
        )

        # Create persistent mini c_array for getters and setters:
        length = length * self._array_length  # Increase buffer size to include arrays
        c_array = (gl_type * length)()
        ptr = cast(c_array, POINTER(gl_type))

        # Create custom dedicated getters and setters for each uniform:
        self.getter = Uniform._create_getter_func(
            self._program_id,
            self._location,
            gl_getter,
            c_array,
            length,
        )

        self.setter = Uniform._create_setter_func(
            self._ctx,
            self._program_id,
            self._location,
            gl_program_setter,
            gl_setter,
            c_array,
            gl_type,
            length,
            self._array_length,
            count,
            ptr,
            is_matrix,
        )

    @staticmethod
    def _create_getter_func(program_id, location, gl_getter, c_array, length):
        """Create a function for getting/setting OpenGL data."""

        def getter_func1():
            """Get single-element OpenGL uniform data."""
            gl_getter(program_id, location, c_array)
            return c_array[0]

        def getter_func2():
            """Get list of OpenGL uniform data."""
            gl_getter(program_id, location, c_array)
            return tuple(c_array)

        if length == 1:
            return getter_func1
        else:
            return getter_func2

    @classmethod
    def _create_setter_func(
        cls,
        ctx,
        program_id,
        location,
        gl_program_setter,
        gl_setter,
        c_array,
        gl_type,
        length,
        array_length,
        count,
        ptr,
        is_matrix,
    ):
        """Create setters for OpenGL data."""
        # Matrix uniforms
        if is_matrix:
            if ctx._ext_separate_shader_objects_enabled:

                def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                    """Set OpenGL matrix uniform data."""
                    try:
                        # FIXME: Configure the struct format on the uniform to support
                        #        other types than float
                        fmt = cls._type_to_struct[gl_type]
                        c_array[:] = struct.unpack(f"{length}{fmt}", value)
                    except Exception:
                        c_array[:] = value
                    gl_program_setter(program_id, location, array_length, gl.GL_FALSE, ptr)

            else:

                def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                    """Set OpenGL matrix uniform data."""
                    c_array[:] = value
                    gl.glUseProgram(program_id)
                    gl_setter(location, array_length, gl.GL_FALSE, ptr)

        # Single value uniforms
        elif length == 1 and count == 1:
            if ctx._ext_separate_shader_objects_enabled:

                def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                    """Set OpenGL uniform data value."""
                    c_array[0] = value
                    gl_program_setter(program_id, location, array_length, ptr)

            else:

                def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                    """Set OpenGL uniform data value."""
                    c_array[0] = value
                    gl.glUseProgram(program_id)
                    gl_setter(location, array_length, ptr)

        # Uniforms types with multiple components
        elif length > 1 and count == 1:
            if ctx._ext_separate_shader_objects_enabled:

                def setter_func(values):  # type: ignore #conditional function variants must have identical signature
                    """Set list of OpenGL uniform data."""
                    # Support buffer protocol
                    try:
                        # FIXME: Configure the struct format on the uniform to support
                        #        other types than float
                        fmt = cls._type_to_struct[gl_type]
                        c_array[:] = struct.unpack(f"{length}{fmt}", values)
                    except Exception:
                        c_array[:] = values

                    gl_program_setter(program_id, location, array_length, ptr)

            else:

                def setter_func(values):  # type: ignore #conditional function variants must have identical signature
                    """Set list of OpenGL uniform data."""
                    c_array[:] = values
                    gl.glUseProgram(program_id)
                    gl_setter(location, array_length, ptr)

        else:
            raise NotImplementedError("Uniform type not yet supported.")

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

    __slots__ = ("glo", "index", "size", "name")

    def __init__(self, glo: int, index: int, size: int, name: str):
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
        binding = gl.GLint()
        gl.glGetActiveUniformBlockiv(self.glo, self.index, gl.GL_UNIFORM_BLOCK_BINDING, binding)
        return binding.value

    @binding.setter
    def binding(self, binding: int):
        gl.glUniformBlockBinding(self.glo, self.index, binding)

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
