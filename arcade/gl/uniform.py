from ctypes import cast, POINTER
from pyglet import gl

from .exceptions import ShaderException


class Uniform:
    """
    A Program uniform

    :param int location: The location of the uniform in the program
    :param str name: Name of the uniform in the program
    :param gl.GLenum data_type: The data type of the uniform (GL_FLOAT
    """

    _uniform_getters = {
        gl.GLint: gl.glGetUniformiv,
        gl.GLuint: gl.glGetUniformuiv,
        gl.GLfloat: gl.glGetUniformfv,
    }

    _uniform_setters = {
        # uniform type: (gl_type, setter, length, count)
        # integers
        gl.GL_INT: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_INT_VEC2: (gl.GLint, gl.glUniform2iv, 2, 1),
        gl.GL_INT_VEC3: (gl.GLint, gl.glUniform3iv, 3, 1),
        gl.GL_INT_VEC4: (gl.GLint, gl.glUniform4iv, 4, 1),
        # Unsigned integers
        gl.GL_UNSIGNED_INT: (gl.GLuint, gl.glUniform1uiv, 1, 1),
        gl.GL_UNSIGNED_INT_VEC2: (gl.GLuint, gl.glUniform2uiv, 2, 1),
        gl.GL_UNSIGNED_INT_VEC3: (gl.GLuint, gl.glUniform3uiv, 3, 1),
        gl.GL_UNSIGNED_INT_VEC4: (gl.GLuint, gl.glUniform4uiv, 4, 1),
        # Bools
        gl.GL_BOOL: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_BOOL_VEC2: (gl.GLint, gl.glUniform2iv, 2, 1),
        gl.GL_BOOL_VEC3: (gl.GLint, gl.glUniform3iv, 3, 1),
        gl.GL_BOOL_VEC4: (gl.GLint, gl.glUniform4iv, 4, 1),
        gl.GL_FLOAT: (gl.GLfloat, gl.glUniform1fv, 1, 1),
        gl.GL_FLOAT_VEC2: (gl.GLfloat, gl.glUniform2fv, 2, 1),
        gl.GL_FLOAT_VEC3: (gl.GLfloat, gl.glUniform3fv, 3, 1),
        gl.GL_FLOAT_VEC4: (gl.GLfloat, gl.glUniform4fv, 4, 1),
        # 1D Samplers
        gl.GL_SAMPLER_1D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_INT_SAMPLER_1D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_UNSIGNED_INT_SAMPLER_1D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_1D_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        # 2D samplers
        gl.GL_SAMPLER_2D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_SAMPLER_2D_MULTISAMPLE: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_INT_SAMPLER_2D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_UNSIGNED_INT_SAMPLER_2D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_2D_MULTISAMPLE: (gl.GLint, gl.glUniform1iv, 1, 1),
        # Array
        gl.GL_SAMPLER_2D_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_2D_MULTISAMPLE_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        # 3D
        gl.GL_SAMPLER_3D: (gl.GLint, gl.glUniform1iv, 1, 1),
        # Cube
        gl.GL_SAMPLER_CUBE: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_TEXTURE_CUBE_MAP_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        # Matrices
        gl.GL_FLOAT_MAT2: (gl.GLfloat, gl.glUniformMatrix2fv, 4, 1),
        gl.GL_FLOAT_MAT3: (gl.GLfloat, gl.glUniformMatrix3fv, 9, 1),
        gl.GL_FLOAT_MAT4: (gl.GLfloat, gl.glUniformMatrix4fv, 16, 1),
        # Image (compute shader)
        gl.GL_IMAGE_1D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_RECT: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_3D: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_CUBE: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_1D_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_CUBE_MAP_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_MULTISAMPLE: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_2D_MULTISAMPLE_ARRAY: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_IMAGE_BUFFER: (gl.GLint, gl.glUniform1iv, 1, 1),

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
    )

    def __init__(self, program_id, location, name, data_type, array_length):

        self._program_id = program_id
        self._location = location
        self._name = name
        self._data_type = data_type
        # Array length of the uniform (1 if no array)
        self._array_length = array_length
        # Number of components (including per array entry)
        self._components = 0
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
            gl_type, gl_setter, length, count = self._uniform_setters[self._data_type]
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
            self._program_id, self._location, gl_getter, c_array, length
        )
        self.setter = Uniform._create_setter_func(
            self._location, gl_setter, c_array, length, self._array_length, count, ptr, is_matrix
        )

    @staticmethod
    def _create_getter_func(program_id, location, gl_getter, c_array, length):
        """ Create a function for getting/setting OpenGL data. """
        if length == 1:

            def getter_func():
                """ Get single-element OpenGL uniform data. """
                gl_getter(program_id, location, c_array)
                return c_array[0]

        else:

            def getter_func():
                """ Get list of OpenGL uniform data. """
                gl_getter(program_id, location, c_array)
                return tuple(c_array)

        return getter_func

    @staticmethod
    def _create_setter_func(
        location, gl_setter, c_array, length, array_length, count, ptr, is_matrix
    ):
        """ Create setters for OpenGL data. """
        if is_matrix:

            def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                """ Set OpenGL matrix uniform data. """
                c_array[:] = value
                gl_setter(location, array_length, gl.GL_FALSE, ptr)

        elif length == 1 and count == 1:

            def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                """ Set OpenGL uniform data value. """
                c_array[0] = value
                gl_setter(location, array_length, ptr)

        elif length > 1 and count == 1:

            def setter_func(values):  # type: ignore #conditional function variants must have identical signature
                """ Set list of OpenGL uniform data. """
                c_array[:] = values
                gl_setter(location, array_length, ptr)

        else:
            raise NotImplementedError("Uniform type not yet supported.")

        return setter_func

    def __repr__(self):
        return f"<Uniform '{self._name}' loc={self._location} array_length={self._array_length}>"


class UniformBlock:
    """
    Wrapper for a uniform block in shaders.
    """
    __slots__ = ("glo", "index", "size", "name")

    def __init__(self, glo: int, index: int, size: int, name: str):
        self.glo = glo
        self.index = index
        self.size = size
        self.name = name

    @property
    def binding(self) -> int:
        """Get or set the binding index for this uniform block"""
        binding = gl.GLint()
        gl.glGetActiveUniformBlockiv(
            self.glo, self.index, gl.GL_UNIFORM_BLOCK_BINDING, binding
        )
        return binding.value

    @binding.setter
    def binding(self, binding: int):
        gl.glUniformBlockBinding(self.glo, self.index, binding)

    def getter(self):
        return self

    def setter(self, value: int):
        self.binding = value

    def __str__(self):
        return f"<UniformBlock {self.name} index={self.index} size={self.size}>"
