"""Utilities for dealing with Shaders in OpenGL 3.3+.
"""

from ctypes import *
from collections import namedtuple
import weakref
from typing import Type, Tuple, Iterable

from pyglet.gl import *
from pyglet import gl

import numpy as np


class ShaderException(Exception):
    pass


# Thank you Benjamin Moran for writing part of this code!
# https://bitbucket.org/HigashiNoKaze/pyglet/src/shaders/pyglet/graphics/shader.py

_uniform_getters = {
    GLint: glGetUniformiv,
    GLfloat: glGetUniformfv,
}

_uniform_setters = {
    # uniform type: (gl_type, setter, length, count)
    GL_INT: (GLint, glUniform1iv, 1, 1),
    GL_INT_VEC2: (GLint, glUniform2iv, 2, 1),
    GL_INT_VEC3: (GLint, glUniform3iv, 3, 1),
    GL_INT_VEC4: (GLint, glUniform4iv, 4, 1),

    GL_FLOAT: (GLfloat, glUniform1fv, 1, 1),
    GL_FLOAT_VEC2: (GLfloat, glUniform2fv, 2, 1),
    GL_FLOAT_VEC3: (GLfloat, glUniform3fv, 3, 1),
    GL_FLOAT_VEC4: (GLfloat, glUniform4fv, 4, 1),

    GL_SAMPLER_2D: (GLint, glUniform1iv, 1, 1),

    GL_FLOAT_MAT2: (GLfloat, glUniformMatrix2fv, 4, 1),
    GL_FLOAT_MAT3: (GLfloat, glUniformMatrix3fv, 6, 1),
    GL_FLOAT_MAT4: (GLfloat, glUniformMatrix4fv, 16, 1),

    # TODO: test/implement these:
    # GL_FLOAT_MAT2x3: glUniformMatrix2x3fv,
    # GL_FLOAT_MAT2x4: glUniformMatrix2x4fv,
    #
    # GL_FLOAT_MAT3x2: glUniformMatrix3x2fv,
    # GL_FLOAT_MAT3x4: glUniformMatrix3x4fv,
    #
    # GL_FLOAT_MAT4x2: glUniformMatrix4x2fv,
    # GL_FLOAT_MAT4x3: glUniformMatrix4x3fv,
}


def _create_getter_func(program_id, location, gl_getter, c_array, length):

    if length == 1:
        def getter_func():
            gl_getter(program_id, location, c_array)
            return c_array[0]
    else:
        def getter_func():
            gl_getter(program_id, location, c_array)
            return c_array[:]

    return getter_func


def _create_setter_func(location, gl_setter, c_array, length, count, ptr, is_matrix):

    if is_matrix:
        def setter_func(value):
            c_array[:] = value
            gl_setter(location, count, GL_FALSE, ptr)

    elif length == 1 and count == 1:
        def setter_func(value):
            c_array[0] = value
            gl_setter(location, count, ptr)
    elif length > 1 and count == 1:
        def setter_func(values):
            c_array[:] = values
            gl_setter(location, count, ptr)

    else:
        raise NotImplementedError("Uniform type not yet supported.")

    return setter_func


Uniform = namedtuple('Uniform', 'getter, setter')
ShaderCode = str
ShaderType = GLuint
Shader = type(Tuple[ShaderCode, ShaderType])


class Program:
    """Compiled and linked shader program.

    Access Uniforms via the [] operator.
    Example:
        program['MyUniform'] = value
    For Matrices, pass the flatten array.
    Example:
        matrix = np.array([[...]])
        program['MyMatrix'] = matrix.flatten()
    """
    def __init__(self, *shaders: Shader):
        self.prog_id = prog_id = glCreateProgram()
        shaders_id = []
        for shader_code, shader_type in shaders:
            shader = compile_shader(shader_code, shader_type)
            glAttachShader(self.prog_id, shader)
            shaders_id.append(shader)

        glLinkProgram(self.prog_id)

        for shader in shaders_id:
            # Flag shaders for deletion. Will only be deleted once detached from program.
            glDeleteShader(shader)

        self._uniforms = {}
        self._introspect_uniforms()
        weakref.finalize(self, Program._delete, shaders_id, prog_id)

    @staticmethod
    def _delete(shaders_id, prog_id):
        # Check to see if the context was already cleaned up from program
        # shut down. If so, we don't need to delete the shaders.
        if gl.current_context is None:
            return

        for shader_id in shaders_id:
            glDetachShader(prog_id, shader_id)

        glDeleteProgram(prog_id)

    def release(self):
        if self.prog_id != 0:
            glDeleteProgram(self.prog_id)
            self.prog_id = 0

    def __getitem__(self, item):
        try:
            uniform = self._uniforms[item]
        except KeyError:
            raise ShaderException(f"Uniform with the name `{item}` was not found.")

        return uniform.getter()

    def __setitem__(self, key, value):
        try:
            uniform = self._uniforms[key]
        except KeyError:
            raise ShaderException(f"Uniform with the name `{key}` was not found.")

        uniform.setter(value)

    def __enter__(self):
        glUseProgram(self.prog_id)

    def __exit__(self, exception_type, exception_value, traceback):
        glUseProgram(0)

    def get_num_active(self, variable_type: GLenum) -> int:
        """Get the number of active variables of the passed GL type.

        variable_type can be GL_ACTIVE_ATTRIBUTES, GL_ACTIVE_UNIFORMS, etc.
        """
        num_active = GLint(0)
        glGetProgramiv(self.prog_id, variable_type, byref(num_active))
        return num_active.value

    def _introspect_uniforms(self):
        for index in range(self.get_num_active(GL_ACTIVE_UNIFORMS)):
            uniform_name, u_type, u_size = self.query_uniform(index)
            loc = glGetUniformLocation(self.prog_id, uniform_name.encode('utf-8'))

            if loc == -1:      # Skip uniforms that may be in Uniform Blocks
                continue

            try:
                gl_type, gl_setter, length, count = _uniform_setters[u_type]
            except KeyError:
                raise ShaderException(f"Unsupported Uniform type {u_type}")

            gl_getter = _uniform_getters[gl_type]

            is_matrix = u_type in (GL_FLOAT_MAT2, GL_FLOAT_MAT3, GL_FLOAT_MAT4)

            # Create persistant mini c_array for getters and setters:
            c_array = (gl_type * length)()
            ptr = cast(c_array, POINTER(gl_type))

            # Create custom dedicated getters and setters for each uniform:
            getter = _create_getter_func(self.prog_id, loc, gl_getter, c_array, length)
            setter = _create_setter_func(loc, gl_setter, c_array, length, count, ptr, is_matrix)

            # print(f"Found uniform: {uniform_name}, type: {u_type}, size: {u_size}, "
            #       f"location: {loc}, length: {length}, count: {count}")

            self._uniforms[uniform_name] = Uniform(getter, setter)

    def query_uniform(self, index: int) -> Tuple[str, int, int]:
        """Retrieve Uniform information at given location.

        Returns the name, the type as a GLenum (GL_FLOAT, ...) and the size. Size is
        greater than 1 only for Uniform arrays, like an array of floats or an array
        of Matrices.
        """
        usize = GLint()
        utype = GLenum()
        buf_size = 192
        uname = create_string_buffer(buf_size)
        glGetActiveUniform(self.prog_id, index, buf_size, None, usize, utype, uname)
        return uname.value.decode(), utype.value, usize.value


def program(vertex_shader: str, fragment_shader: str) -> Program:
    """Create a new program given the vertex_shader and fragment shader code.
    """
    return Program(
        (vertex_shader, GL_VERTEX_SHADER),
        (fragment_shader, GL_FRAGMENT_SHADER)
    )


def compile_shader(source: str, shader_type: GLenum) -> GLuint:
    """Compile the shader code of the given type.

    `shader_type` could be GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, ...

    Returns the shader id as a GLuint
    """
    shader = glCreateShader(shader_type)
    source = source.encode('utf-8')
    # Turn the source code string into an array of c_char_p arrays.
    strings = byref(
        cast(
            c_char_p(source),
            POINTER(c_char)
        )
    )
    # Make an array with the strings lengths
    lengths = pointer(c_int(len(source)))
    glShaderSource(shader, 1, strings, lengths)
    glCompileShader(shader)
    result = c_int()
    glGetShaderiv(shader, GL_COMPILE_STATUS, byref(result))
    if result.value == GL_FALSE:
        msg = create_string_buffer(512)
        length = c_int()
        glGetShaderInfoLog(shader, 512, byref(length), msg)
        raise ShaderException(
            f"Shader compile failure ({result.value}): {msg.value.decode('utf-8')}")
    return shader


class Buffer:
    """OpenGL Buffer object of type GL_ARRAY_BUFFER.

    Apparently it's possible to initialize a GL_ELEMENT_ARRAY_BUFFER with
    GL_ARRAY_BUFFER, provided we later on bind to it with the right type.

    The buffer knows its id `buffer_id` and its `size` in bytes.
    """
    usages = {
        'static': GL_STATIC_DRAW,
        'dynamic': GL_DYNAMIC_DRAW,
        'stream': GL_STREAM_DRAW
    }

    def __init__(self, data: bytes, usage: str = 'static'):
        self.buffer_id = buffer_id = GLuint()
        self.size = len(data)

        glGenBuffers(1, byref(self.buffer_id))
        if self.buffer_id.value == 0:
            raise ShaderException("Cannot create Buffer object.")

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_id)
        self.usage = Buffer.usages[usage]
        glBufferData(GL_ARRAY_BUFFER, self.size, data, self.usage)
        weakref.finalize(self, Buffer.release, buffer_id)

    @classmethod
    def create_with_size(cls, size: int, usage: str = 'static'):
        """Create an empty Buffer storage of the given size."""
        buffer = Buffer(b"", usage = usage)
        glBindBuffer(GL_ARRAY_BUFFER, buffer.buffer_id)
        glBufferData(GL_ARRAY_BUFFER, size, None, Buffer.usages[usage])
        buffer.size = size
        return buffer

    @staticmethod
    def release(buffer_id):

        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if buffer_id.value != 0:
            glDeleteBuffers(1, byref(buffer_id))
            buffer_id.value = 0

    def write(self, data: bytes, offset: int = 0):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_id)
        glBufferSubData(GL_ARRAY_BUFFER, GLintptr(offset), len(data), data)
        # print(f"Writing data:\n{data[:60]}")
        # ptr = glMapBufferRange(GL_ARRAY_BUFFER, GLintptr(0), 20, GL_MAP_READ_BIT)
        # print(f"Reading back from buffer:\n{string_at(ptr, size=60)}")
        # glUnmapBuffer(GL_ARRAY_BUFFER)

    def orphan(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_id)
        glBufferData(GL_ARRAY_BUFFER, self.size, None, self.usage)

    def _read(self, size):
        """ Debug method to read data from the buffer. """

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer_id)
        ptr = glMapBufferRange(GL_ARRAY_BUFFER, GLintptr(0), size, GL_MAP_READ_BIT)
        print(f"Reading back from buffer:\n{string_at(ptr, size=size)}")
        glUnmapBuffer(GL_ARRAY_BUFFER)


def buffer(data: bytes, usage: str = 'static') -> Buffer:
    """Create a new OpenGL Buffer object.
    """
    return Buffer(data, usage)


class BufferDescription:
    """Vertex Buffer Object description, allowing easy use with VAOs.

    This class provides a Buffer object with a description of its content, allowing
    a VertexArray object to correctly enable its shader attributes with the
    vertex Buffer object.

    The formats is a string providing the number and type of each attribute. Currently
    we only support f (float), i (integer) and B (unsigned byte).

    `normalized` enumerates the attributes which must have their values normalized.
    This is useful for instance for colors attributes given as unsigned byte and
    normalized to floats with values between 0.0 and 1.0.

    `instanced` allows this buffer to be used as instanced buffer. Each value will
    be used once for the whole geometry. The geometry will be repeated a number of
    times equal to the number of items in the Buffer.
    """
    GL_TYPES_ENUM = {
        'B': GL_UNSIGNED_BYTE,
        'f': GL_FLOAT,
        'i': GL_INT,
    }
    GL_TYPES = {
        'B': GLubyte,
        'f': GLfloat,
        'i': GLint,
    }

    def __init__(self,
                 buffer: Buffer,
                 formats: str,
                 attributes: Iterable[str],
                 normalized: Iterable[str] = None,
                 instanced: bool = False):
        self.buffer = buffer
        self.attributes = list(attributes)
        self.normalized = set() if normalized is None else set(normalized)
        self.instanced = instanced

        if self.normalized > set(self.attributes):
            raise ShaderException("Normalized attribute not found in attributes.")

        formats = formats.split(" ")

        if len(formats) != len(self.attributes):
            raise ShaderException(
                f"Different lengths of formats ({len(formats)}) and "
                f"attributes ({len(self.attributes)})"
            )

        self.formats = []
        for i, fmt in enumerate(formats):
            size, type_ = fmt
            if size not in ('1234') or type_ not in 'fiB':
                raise ShaderException("Wrong format {fmt}.")
            size = int(size)
            gl_type_enum = BufferDescription.GL_TYPES_ENUM[type_]
            gl_type = BufferDescription.GL_TYPES[type_]
            attribsize = size * sizeof(gl_type)
            self.formats.append((size, attribsize, gl_type_enum))


class VertexArray:
    """Vertex Array Object (VAO) is holding all the different OpenGL objects
    together.

    A VAO is the glue between a Shader program and buffers data.

    Buffer information is provided through a list of tuples `content`
    content = [
        (buffer, 'format str', 'attrib1', 'attrib2', ...),
    ]
    The first item is a Buffer object. Then comes a format string providing information
    about the count and type of data in the buffer. Type can be `f` for floats or `i`
    for integers. Count can be 1, 2, 3 or 4.
    Finally comes the strings representing the attributes found in the shader.

    Example:
        Providing a buffer with data of interleaved positions (x, y) and colors
        (r, g, b, a):
        content = [(buffer, '2f 4f', 'in_pos', 'in_color')]

    You can use the VAO as a context manager. This is required for setting Uniform
    variables or for rendering.

    vao = VertexArrax(...)
    with vao:
        vao['MyUniform'] = value
        vao.render
    """

    def __init__(self,
                 program: Program,
                 content: Iterable[BufferDescription],
                 index_buffer: Buffer = None):
        self.program = program.prog_id
        self.vao = vao = GLuint()
        self.num_vertices = -1
        self.ibo = index_buffer

        glGenVertexArrays(1, byref(self.vao))
        glBindVertexArray(self.vao)

        for buffer_desc in content:
            self._enable_attrib(buffer_desc)

        if self.ibo is not None:
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo.buffer_id)
        weakref.finalize(self, VertexArray.release, vao)

    @staticmethod
    def release(vao):
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if vao.value != 0:
            glDeleteVertexArrays(1, byref(vao))
            vao.value = 0

    def __enter__(self):
        glBindVertexArray(self.vao)
        glUseProgram(self.program)

    def __exit__(self, exception_type, exception_value, traceback):
        glUseProgram(0)

    def _enable_attrib(self, buf_desc: BufferDescription):
        buffer = buf_desc.buffer
        stride = sum(attribsize for _, attribsize, _ in buf_desc.formats)

        if buf_desc.instanced:
            if self.num_vertices == -1:
                raise ShaderException(
                    "The first vertex attribute cannot be a per instance attribute."
                )
        else:
            self.num_vertices = max(self.num_vertices, buffer.size // stride)
            # print(f"Number of vertices: {self.num_vertices}")

        glBindBuffer(GL_ARRAY_BUFFER, buffer.buffer_id)
        offset = 0
        for (size, attribsize, gl_type_enum), attrib in zip(buf_desc.formats, buf_desc.attributes):
            loc = glGetAttribLocation(self.program, attrib.encode('utf-8'))
            if loc == -1:
                raise ShaderException(f"Attribute {attrib} not found in shader program")
            normalized = GL_TRUE if attrib in buf_desc.normalized else GL_FALSE
            glVertexAttribPointer(
                loc, size, gl_type_enum,
                normalized, stride, c_void_p(offset)
            )
            # print(f"{attrib} of size {size} with stride {stride} and offset {offset}")
            if buf_desc.instanced:
                glVertexAttribDivisor(loc, 1)
            offset += attribsize
            glEnableVertexAttribArray(loc)

    def render(self, mode: GLuint, instances: int = 1):
        if self.ibo is not None:
            count = self.ibo.size // 4
            glDrawElementsInstanced(mode, count, GL_UNSIGNED_INT, None, instances)
        else:
            glDrawArraysInstanced(mode, 0, self.num_vertices, instances)


def vertex_array(program: GLuint, content, index_buffer = None):
    """Create a new Vertex Array.
    """
    return VertexArray(program, content, index_buffer)


class Texture:
    def __init__(self, size: Tuple[int, int], component: int, data: np.array):
        self.width, self.height = size
        sized_format = (GL_R8, GL_RG8, GL_RGB8, GL_RGBA8)[component - 1]
        self.format = (GL_R, GL_RG, GL_RGB, GL_RGBA)[component - 1]
        glActiveTexture(GL_TEXTURE0 + 0)  # If we need other texture unit...
        self.texture_id = texture_id = GLuint()
        glGenTextures(1, byref(self.texture_id))

        if self.texture_id.value == 0:
            raise ShaderException("Cannot create Texture.")

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        try:
            glTexImage2D(
                GL_TEXTURE_2D, 0, sized_format, self.width, self.height, 0,
                self.format, GL_UNSIGNED_BYTE, data.ctypes.data_as(c_void_p)
            )
        except GLException as e:
            raise GLException(f"Unable to create texture. {GL_MAX_TEXTURE_SIZE} {size}")

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        weakref.finalize(self, Texture.release, texture_id)

    @staticmethod
    def release(texture_id):
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if texture_id.value != 0:
            glDeleteTextures(1, byref(texture_id))

    def use(self, texture_unit: int = 0):
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)


def texture(size: Tuple[int, int], component: int, data: np.array) -> Texture:
    return Texture(size, component, data)
