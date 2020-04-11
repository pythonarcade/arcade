"""Utilities for dealing with Shaders in OpenGL 3.3+.
"""

from ctypes import (
    c_char, c_int, c_buffer,
    c_char_p, c_void_p,
    cast, POINTER, pointer, byref, sizeof,
    create_string_buffer, string_at,
)
from collections import namedtuple
from pathlib import Path
import weakref
from typing import List, Tuple, Iterable, Dict, Optional, Union


from pyglet import gl


# Thank you Benjamin Moran for writing part of this code!
# https://bitbucket.org/HigashiNoKaze/pyglet/src/shaders/pyglet/graphics/shader.py


class ShaderException(Exception):
    """ Exception class for shader-specific problems. """
    pass


ShaderCode = str
Shader = Tuple[ShaderCode, gl.GLuint]


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
    __slots__ = '_ctx', '_glo', '_uniforms', '__weakref__'

    Uniform = namedtuple('Uniform', 'getter, setter')

    _uniform_getters = {
        gl.GLint: gl.glGetUniformiv,
        gl.GLfloat: gl.glGetUniformfv,
    }

    _uniform_setters = {
        # uniform type: (gl_type, setter, length, count)
        gl.GL_INT: (gl.GLint, gl.glUniform1iv, 1, 1),
        gl.GL_INT_VEC2: (gl.GLint, gl.glUniform2iv, 2, 1),
        gl.GL_INT_VEC3: (gl.GLint, gl.glUniform3iv, 3, 1),
        gl.GL_INT_VEC4: (gl.GLint, gl.glUniform4iv, 4, 1),

        gl.GL_FLOAT: (gl.GLfloat, gl.glUniform1fv, 1, 1),
        gl.GL_FLOAT_VEC2: (gl.GLfloat, gl.glUniform2fv, 2, 1),
        gl.GL_FLOAT_VEC3: (gl.GLfloat, gl.glUniform3fv, 3, 1),
        gl.GL_FLOAT_VEC4: (gl.GLfloat, gl.glUniform4fv, 4, 1),

        gl.GL_SAMPLER_2D: (gl.GLint, gl.glUniform1iv, 1, 1),

        gl.GL_FLOAT_MAT2: (gl.GLfloat, gl.glUniformMatrix2fv, 4, 1),
        gl.GL_FLOAT_MAT3: (gl.GLfloat, gl.glUniformMatrix3fv, 9, 1),
        gl.GL_FLOAT_MAT4: (gl.GLfloat, gl.glUniformMatrix4fv, 16, 1),

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

    def __init__(self, ctx, *shaders: Shader):
        self._ctx = ctx
        self._glo = prog_id = gl.glCreateProgram()
        shaders_id = []
        for shader_code, shader_type in shaders:
            shader = Program.compile_shader(shader_code, shader_type)
            gl.glAttachShader(self._glo, shader)
            shaders_id.append(shader)

        Program.link(self._glo)

        for shader in shaders_id:
            # Flag shaders for deletion. Will only be deleted once detached from program.
            gl.glDeleteShader(shader)

        self._uniforms: Dict[str, Program.Uniform] = {}
        self._introspect_uniforms()
        weakref.finalize(self, Program._delete, shaders_id, prog_id)

    @property
    def ctx(self) -> 'Context':
        """The context this program belongs to"""
        return self._ctx

    @property
    def glo(self) -> int:
        """The OpenGL resource id for this program"""
        return self._glo

    @staticmethod
    def _delete(shaders_id, prog_id):
        # Check to see if the context was already cleaned up from program
        # shut down. If so, we don't need to delete the shaders.
        if gl.current_context is None:
            return

        for shader_id in shaders_id:
            gl.glDetachShader(prog_id, shader_id)

        gl.glDeleteProgram(prog_id)

    def __getitem__(self, item):
        try:
            uniform = self._uniforms[item]
        except KeyError:
            raise ShaderException(f"Uniform with the name `{item}` was not found.")

        return uniform.getter()

    def __setitem__(self, key, value):
        # Ensure we are setting the uniform on this program
        if self._ctx.active_program != self:
            self.use()

        try:
            uniform = self._uniforms[key]
        except KeyError:
            raise ShaderException(f"Uniform with the name `{key}` was not found.")

        uniform.setter(value)

    def use(self):
        """Activates the shader"""
        # IMPORTANT: This is the only place glUseProgram should be called
        #            so we can track active program.
        if self._ctx.active_program != self:
            gl.glUseProgram(self._glo)
            self._ctx.active_program = self

    def _get_num_active(self, variable_type: gl.GLenum) -> int:
        """Get the number of active variables of the passed GL type.

        variable_type can be GL_ACTIVE_ATTRIBUTES, GL_ACTIVE_UNIFORMS, etc.
        """
        num_active = gl.GLint(0)
        gl.glGetProgramiv(self._glo, variable_type, byref(num_active))
        return num_active.value

    def _introspect_uniforms(self):
        for index in range(self._get_num_active(gl.GL_ACTIVE_UNIFORMS)):
            uniform_name, u_type, u_size = self._query_uniform(index)
            loc = gl.glGetUniformLocation(self._glo, uniform_name.encode('utf-8'))

            if loc == -1:      # Skip uniforms that may be in Uniform Blocks
                continue

            try:
                gl_type, gl_setter, length, count = Program._uniform_setters[u_type]
            except KeyError:
                raise ShaderException(f"Unsupported Uniform type {u_type}")

            gl_getter = Program._uniform_getters[gl_type]

            is_matrix = u_type in (gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3, gl.GL_FLOAT_MAT4)

            # Create persistent mini c_array for getters and setters:
            c_array = (gl_type * length)()
            ptr = cast(c_array, POINTER(gl_type))

            # Create custom dedicated getters and setters for each uniform:
            getter = Program._create_getter_func(self._glo, loc, gl_getter, c_array, length)
            setter = Program._create_setter_func(loc, gl_setter, c_array, length, count, ptr, is_matrix)

            # print(f"Found uniform: {uniform_name}, type: {u_type}, size: {u_size}, "
            #       f"location: {loc}, length: {length}, count: {count}")
            #       f"location: {loc}, length: {length}, count: {count}")

            self._uniforms[uniform_name] = Program.Uniform(getter, setter)

    def _query_uniform(self, index: int) -> Tuple[str, int, int]:
        """Retrieve Uniform information at given location.

        Returns the name, the type as a GLenum (GL_FLOAT, ...) and the size. Size is
        greater than 1 only for Uniform arrays, like an array of floats or an array
        of Matrices.
        """
        usize = gl.GLint()
        utype = gl.GLenum()
        buf_size = 192
        uname = create_string_buffer(buf_size)
        gl.glGetActiveUniform(self._glo, index, buf_size, None, usize, utype, uname)
        return uname.value.decode(), utype.value, usize.value

    @staticmethod
    def compile_shader(source: str, shader_type: gl.GLenum) -> gl.GLuint:
        """Compile the shader code of the given type.

        `shader_type` could be GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, ...

        Returns the shader id as a GLuint
        """
        shader = gl.glCreateShader(shader_type)
        source_bytes = source.encode('utf-8')
        # Turn the source code string into an array of c_char_p arrays.
        strings = byref(
            cast(
                c_char_p(source_bytes),
                POINTER(c_char)
            )
        )
        # Make an array with the strings lengths
        lengths = pointer(c_int(len(source_bytes)))
        gl.glShaderSource(shader, 1, strings, lengths)
        gl.glCompileShader(shader)
        result = c_int()
        gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS, byref(result))
        if result.value == gl.GL_FALSE:
            msg = create_string_buffer(512)
            length = c_int()
            gl.glGetShaderInfoLog(shader, 512, byref(length), msg)
            raise ShaderException(
                f"Shader compile failure ({result.value}): {msg.value.decode('utf-8')}")
        return shader

    @staticmethod
    def link(glo):
        gl.glLinkProgram(glo)
        status = c_int()
        gl.glGetProgramiv(glo, gl.GL_LINK_STATUS, status)
        if not status.value:
            length = c_int()
            gl.glGetProgramiv(glo, gl.GL_INFO_LOG_LENGTH, length)
            log = c_buffer(length.value)
            gl.glGetProgramInfoLog(glo, len(log), None, log)
            raise ShaderException('Program link error: {}'.format(log.value.decode()))

    def __repr__(self):
        return "<Program id={}>".format(self._glo)

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
                return c_array[:]

        return getter_func

    @staticmethod
    def _create_setter_func(location, gl_setter, c_array, length, count, ptr, is_matrix):
        """ Create setters for OpenGL data. """
        if is_matrix:
            def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                """ Set OpenGL matrix uniform data. """
                c_array[:] = value
                gl_setter(location, count, gl.GL_FALSE, ptr)

        elif length == 1 and count == 1:
            def setter_func(value):  # type: ignore #conditional function variants must have identical signature
                """ Set OpenGL uniform data value. """
                c_array[0] = value
                gl_setter(location, count, ptr)
        elif length > 1 and count == 1:
            def setter_func(values):  # type: ignore #conditional function variants must have identical signature
                """ Set list of OpenGL uniform data. """
                c_array[:] = values
                gl_setter(location, count, ptr)
        else:
            raise NotImplementedError("Uniform type not yet supported.")

        return setter_func


class Buffer:
    """OpenGL Buffer object. Buffers store byte data and upload it
    to graphics memory. They are used for storage og vertex data,
    element data (vertex indexing), uniform buffer data etc.

    Common bind targets are:  ``GL_ARRAY_BUFFER``, ``GL_ELEMENT_ARRAY_BUFFER``,
    ``GL_UNIFORM_BUFFER``, ``GL_SHADER_STORAGE_BUFFER``

    It doesn't matter what bind target the buffer has on creation. What
    matters is how we bind it in rendering calls.
    """
    __slots__ = '_ctx', '_glo', '_size', '_usage', '__weakref__'
    usages = {
        'static': gl.GL_STATIC_DRAW,
        'dynamic': gl.GL_DYNAMIC_DRAW,
        'stream': gl.GL_STREAM_DRAW
    }

    def __init__(self, ctx, data: bytes = None, reserve: int = 0, usage: str = 'static'):
        self._ctx = ctx
        self._glo = glo = gl.GLuint()
        self._size = -1
        self._usage = Buffer.usages[usage]

        gl.glGenBuffers(1, byref(self._glo))
        # print(f"glGenBuffers() -> {self._glo.value}")
        if self._glo.value == 0:
            raise ShaderException("Cannot create Buffer object.")

        # print(f"glBindBuffer({self._glo.value})")
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        # print(f"glBufferData(gl.GL_ARRAY_BUFFER, {self._size}, data, {self._usage})")

        if data and len(data) > 0:
            self._size = len(data)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self._size, data, self._usage)
        elif reserve > 0:
            self._size = reserve
            gl.glBufferData(gl.GL_ARRAY_BUFFER, self._size, None, self._usage)
        else:
            raise ValueError("Buffer takes byte data or number of reserved bytes")

        weakref.finalize(self, Buffer.release, glo)

    @property
    def size(self) -> int:
        """The byte size of the buffer"""
        return self._size

    @property
    def ctx(self) -> 'Context':
        """The context this resource belongs to"""
        return self._ctx

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL resource id"""
        return self._glo

    @staticmethod
    def release(glo: gl.GLuint):
        """ Release/delete open gl buffer. """
        # print(f"*** Buffer {glo} have no more references. Deleting.")

        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteBuffers(1, byref(glo))
            glo.value = 0

    def read(self, size=-1, offset=0) -> bytes:
        """Read data from the buffer.

        :param int size: The bytes to read. -1 means the entire buffer
        :param int offset: Byte read offset
        """
        if size == -1:
            size = self._size

        # Catch this before confusing INVALID_OPERATION is raised
        if size < 1:
            raise ValueError("Attempting to read 0 or less bytes from buffer")

        # Manually detect this so it doesn't raise a confusing INVALID_VALUE error
        if size + offset > self._size:
            raise ValueError(
                (
                    "Attempting to read outside the buffer. "
                    f"Buffer size: {self._size} "
                    f"Reading from {offset} to {size + offset}"
                )
            )

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        ptr = gl.glMapBufferRange(gl.GL_ARRAY_BUFFER, offset, size, gl.GL_MAP_READ_BIT)
        data = string_at(ptr, size=size)
        gl.glUnmapBuffer(gl.GL_ARRAY_BUFFER)
        return data

    def write(self, data: bytes, offset: int = 0):
        """Write byte data to the buffer.

        :param bytes data: The byte data to write
        :param int offset: The byte offset
        """
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, gl.GLintptr(offset), len(data), data)

    def copy_from_buffer(self, source: 'Buffer', size=-1, offset=0, source_offset=0):
        """Copy data into this buffer from another buffer

        :param Buffer source: The buffer to copy from
        :param int size: The amount of bytes to copy
        :param int offset: The byte offset to write the data in this buffer
        :param int source_offset: The byte offset to read from the source buffer
        """
        # Read the entire source buffer into this buffer
        if size == -1:
            size = source.size

        # TODO: Check buffer bounds
        if size + source_offset > source.size:
            raise ValueError("Attempting to read outside the source buffer")

        if size + offset > self._size:
            raise ValueError("Attempting to write outside the buffer")

        gl.glBindBuffer(gl.GL_COPY_READ_BUFFER, source.glo)
        gl.glBindBuffer(gl.GL_COPY_WRITE_BUFFER, self._glo)
        gl.glCopyBufferSubData(
            gl.GL_COPY_READ_BUFFER,
            gl.GL_COPY_WRITE_BUFFER,
            gl.GLintptr(source_offset),  # readOffset
            gl.GLintptr(offset),  # writeOffset
            size  # size (number of bytes to copy)
        )

    def orphan(self, size=-1):
        """
        Re-allocate the entire buffer memory.
        If the current buffer is busy in redering operations
        it will be deallocated by OpenGL when completed.

        :param int size: New size of buffer. -1 will retain the current size.
        """
        if size > -1:
            self._size = size

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self._size, None, self._usage)


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
        'B': gl.GL_UNSIGNED_BYTE,
        'f': gl.GL_FLOAT,
        'i': gl.GL_INT,
    }
    GL_TYPES = {
        'B': gl.GLubyte,
        'f': gl.GLfloat,
        'i': gl.GLint,
    }

    def __init__(self,
                 buff: Buffer,
                 formats: str,
                 attributes: Iterable[str],
                 normalized: Iterable[str] = None,
                 instanced: bool = False):
        self.buffer = buff
        self.attributes = list(attributes)
        self.normalized = set() if normalized is None else set(normalized)
        self.instanced = instanced

        if self.normalized > set(self.attributes):
            raise ShaderException("Normalized attribute not found in attributes.")

        formats_list = formats.split(" ")

        if len(formats_list) != len(self.attributes):
            raise ShaderException(
                f"Different lengths of formats ({len(formats_list)}) and "
                f"attributes ({len(self.attributes)})"
            )

        self.formats: List[Tuple[int, int, int]] = []
        for i, fmt in enumerate(formats_list):
            sizechar, type_ = fmt
            if sizechar not in '1234' or type_ not in 'fiB':
                raise ShaderException("Wrong format {fmt}.")

            size = int(sizechar)
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

    vao = VertexArray(...)
    """
    __slots__ = '_ctx', '_program', '_glo', '_ibo', '_num_vertices', '__weakref__'

    def __init__(self,
                 ctx,
                 prog: Program,
                 content: Iterable[BufferDescription],
                 index_buffer: Buffer = None):
        self._ctx = ctx
        self._program = prog
        self._glo = glo = gl.GLuint()
        self._num_vertices = -1
        self._ibo = index_buffer

        gl.glGenVertexArrays(1, byref(self._glo))
        gl.glBindVertexArray(self._glo)

        for buffer_desc in content:
            self._enable_attrib(buffer_desc)

        if self._ibo is not None:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self._ibo.glo)

        weakref.finalize(self, VertexArray.release, glo)

    @property
    def ctx(self) -> 'Context':
        """The Context this object belongs to"""
        return self._ctx

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL resource id"""
        return self._glo

    @property
    def program(self) -> Program:
        """The assigned program"""
        return self._program

    @property
    def ibo(self) -> Optional[Buffer]:
        """Element/index buffer"""
        return self._ibo

    @property
    def num_vertices(self) -> int:
        """The number of vertices"""
        return self._num_vertices

    @staticmethod
    def release(glo: gl.GLuint):
        """Delete the object"""
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteVertexArrays(1, byref(glo))
            glo.value = 0

    def _enable_attrib(self, buf_desc: BufferDescription):
        buff = buf_desc.buffer
        stride = sum(attribsize for _, attribsize, _ in buf_desc.formats)

        if buf_desc.instanced:
            if self._num_vertices == -1:
                raise ShaderException(
                    "The first vertex attribute cannot be a per instance attribute."
                )
        else:
            self._num_vertices = max(self._num_vertices, buff.size // stride)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buff.glo)
        offset = 0
        for (size, attribsize, gl_type_enum), attrib in zip(buf_desc.formats, buf_desc.attributes):
            loc = gl.glGetAttribLocation(self._program.glo, attrib.encode())
            if loc == -1:
                raise ShaderException(f"Attribute {attrib} not found in shader program")

            normalized = gl.GL_TRUE if attrib in buf_desc.normalized else gl.GL_FALSE
            gl.glVertexAttribPointer(
                loc, size, gl_type_enum,
                normalized, stride, c_void_p(offset)
            )
            if buf_desc.instanced:
                gl.glVertexAttribDivisor(loc, 1)

            offset += attribsize
            gl.glEnableVertexAttribArray(loc)

    def render(self, mode: gl.GLuint, instances: int = 1):
        """Render the VertexArray to the currently active framebuffer.

        :param GLunit mode: Primitive type to render. TRIANGLES, LINES etc.
        :param int instances: OpenGL instance, used in using vertexes over and over
        """
        gl.glBindVertexArray(self._glo)
        self._program.use()
        if self._ibo is not None:
            count = self._ibo.size // 4
            gl.glDrawElementsInstanced(mode, count, gl.GL_UNSIGNED_INT, None, instances)
        else:
            gl.glDrawArraysInstanced(mode, 0, self.num_vertices, instances)


class Texture:
    """
    Class that represents an OpenGL texture.
    """
    __slots__ = (
        '_ctx', '_glo', '_width', '_height', '_dtype', '_target', '_components',
        '_format', '_internal_format', '_type', '_component_size', '_samples', '_filter', '_wrap_x', '_wrap_y', '__weakref__',
    )
    _float_base_format = (0, gl.GL_RED, gl.GL_RG, gl.GL_RGB, gl.GL_RGBA)
    _int_base_format = (0, gl.GL_RED_INTEGER, gl.GL_RG_INTEGER, gl.GL_RGB_INTEGER, gl.GL_RGBA_INTEGER)
    # format: (base_format, internal_format, type, size)
    _formats = {
        # float formats
        'f1': (_float_base_format, (0, gl.GL_R8, gl.GL_RG8, gl.GL_RGB8, gl.GL_RGBA8), gl.GL_UNSIGNED_BYTE, 1),
        'f2': (_float_base_format, (0, gl.GL_R16F, gl.GL_RG16F, gl.GL_RGB16F, gl.GL_RGBA16F), gl.GL_HALF_FLOAT, 2),
        'f4': (_float_base_format, (0, gl.GL_R32F, gl.GL_RG32F, gl.GL_RGB32F, gl.GL_RGBA32F), gl.GL_FLOAT, 4),
        # int formats
        'i1': (_int_base_format, (0, gl.GL_R8UI, gl.GL_RG8UI, gl.GL_RGB8UI, gl.GL_RGBA8UI), gl.GL_UNSIGNED_BYTE, 1),
        'i2': (_int_base_format, (0, gl.GL_R16UI, gl.GL_RG16UI, gl.GL_RGB16UI, gl.GL_RGBA16UI), gl.GL_UNSIGNED_SHORT, 2),
        'i4': (_int_base_format, (0, gl.GL_R32UI, gl.GL_RG32UI, gl.GL_RGB32UI, gl.GL_RGBA32UI), gl.GL_UNSIGNED_INT, 4),
        # uint formats
        'u1': (_int_base_format, (0, gl.GL_R8UI, gl.GL_RG8UI, gl.GL_RGB8UI, gl.GL_RGBA8UI), gl.GL_BYTE, 1),
        'u2': (_int_base_format, (0, gl.GL_R16UI, gl.GL_RG16UI, gl.GL_RGB16UI, gl.GL_RGBA16UI), gl.GL_SHORT, 2),
        'u4': (_int_base_format, (0, gl.GL_R32UI, gl.GL_RG32UI, gl.GL_RGB32UI, gl.GL_RGBA32UI), gl.GL_INT, 4),
    }

    def __init__(self,
                 ctx: 'Context',
                 size: Tuple[int, int],
                 components: int = 4,
                 dtype: str = 'f1',
                 data: bytes = None,
                 texture_filter: Tuple[gl.GLuint, gl.GLuint] = None,
                 wrap_x: gl.GLuint = None,
                 wrap_y: gl.GLuint = None):
        """Represents an OpenGL texture.

        A texture can be created with or without initial data.
        NOTE: Currently does not support multisample textures even
        thought ``samples`` is exposed.

        :param Context ctx: The context the object belongs to
        :param Tuple[int, int] size: The size of the texture
        :param int components: The number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
        :param str dtype: The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
        :param bytes data: The byte data to initialize the texture with
        :param Tuple[gl.GLuint, gl.GLuint] filter: The minification/magnification filter of the texture
        :param gl.GLuint wrap_s
        :param data: The texture data (optional)
        """
        self._ctx = ctx
        self._width, self._height = size
        self._dtype = dtype
        self._components = components
        self._target = gl.GL_TEXTURE_2D
        self._samples = 0
        # These are the default states in OpenGL
        self._filter = gl.GL_LINEAR, gl.GL_LINEAR
        self._wrap_x = gl.GL_REPEAT
        self._wrap_y = gl.GL_REPEAT

        if components not in [1, 2, 3, 4]:
            raise ValueError("Components must be 1, 2, 3 or 4")

        try:
            format_info = self._formats[self._dtype]
        except KeyError:
            raise ValueError(f"dype '{dtype}' not support. Supported types are : {tuple(self._formats.keys())}")

        gl.glActiveTexture(gl.GL_TEXTURE0)  # Create textures in the default channel (0)

        self._glo = glo = gl.GLuint()
        gl.glGenTextures(1, byref(self._glo))

        if self._glo.value == 0:
            raise ShaderException("Cannot create Texture. OpenGL failed to generate a texture id")

        gl.glBindTexture(self._target, self._glo)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        try:
            _format, _internal_format, self._type, self._component_size = format_info
            self._format = _format[components]
            self._internal_format = _internal_format[components]
            gl.glTexImage2D(
                self._target,  # target
                0,  # level
                self._internal_format,  # internal_format
                self._width,  # width
                self._height,  # height
                0,  # border
                self._format,  # format
                self._type,  # type
                data  # data
            )
        except gl.GLException as ex:
            raise gl.GLException((
                f"Unable to create texture: {ex} : dtype={dtype} size={size} components={components} "
                "GL_MAX_TEXTURE_SIZE = {gl.GL_MAX_TEXTURE_SIZE}"
            ))

        self.filter = texture_filter or self._filter
        self.wrap_x = wrap_x or self._wrap_x
        self.wrap_y = wrap_y or self._wrap_y

        weakref.finalize(self, Texture.release, glo)

    @property
    def ctx(self) -> 'Context':
        """The context this texture belongs to"""
        return self._ctx

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL texture id"""
        return self._glo

    @property
    def width(self) -> int:
        """The width of the texture in pixels"""
        return self._width

    @property
    def height(self) -> int:
        """The height of the texture in pixels"""
        return self._height

    @property
    def dtype(self) -> str:
        """The data type of each component"""
        return self._dtype

    @property
    def size(self) -> Tuple[int, int]:
        """The size of the texture as a tuple"""
        return self._width, self._height

    @property
    def components(self) -> int:
        """Number of components in the texture"""
        return self._components

    @property
    def filter(self) -> Tuple[int, int]:
        """The (min, mag) filter for this texture.

        Default value is ``GL_LINEAR, GL_LINEAR``.
        Can be set to ``GL_NEAREST, GL_NEAREST`` for pixelated graphics.

        When mipmapping is used the min filter needs to be `GL_*_MIPMAP_*`.

        Also see:
        * https://www.khronos.org/opengl/wiki/Texture#Mip_maps
        * https://www.khronos.org/opengl/wiki/Sampler_Object#Filtering
        """
        return self._filter

    @filter.setter
    def filter(self, value):
        if not isinstance(value, tuple) or not len(value) == 2:
            raise ValueError("Texture filter must be a 2 component tuple (min, mag)")

        self._filter = value
        self.use()
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_MIN_FILTER, self._filter[0])
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_MAG_FILTER, self._filter[1])

    @property
    def wrap_x(self):
        """
        The horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the [0.0, 1.0] area.

        Valid options are: ``GL_REPEAT``, ``GL_MIRRORED_REPEAT``, ``GL_CLAMP_TO_EDGE``, ``GL_CLAMP_TO_BORDER``
        """
        return self._wrap_x

    @wrap_x.setter
    def wrap_x(self, value):
        self._wrap_x = value
        self.use()
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_WRAP_S, value)

    @property
    def wrap_y(self):
        """
        The horizontal wrapping of the texture. This decides how textures
        are read when texture coordinates are outside the [0.0, 1.0] area.

        Valid options are: ``GL_REPEAT``, ``GL_MIRRORED_REPEAT``, ``GL_CLAMP_TO_EDGE``, ``GL_CLAMP_TO_BORDER``
        """
        return self._wrap_y

    @wrap_y.setter
    def wrap_y(self, value):
        self._wrap_y = value
        self.use()
        gl.glTexParameteri(self._target, gl.GL_TEXTURE_WRAP_T, value)

    def read(self, level: int = 0, alignment: int = 1) -> bytearray:
        """
        Read the contents of the texture.
        """
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(self._target, self._glo)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)

        buffer = (gl.GLubyte * (self.width * self.height * self._component_size))()
        gl.glGetTexImage(gl.GL_TEXTURE_2D, 0, self._format, self._type, buffer)
        return bytearray(buffer)

    def write(self, data: Union[bytes, Buffer], level: int = 0, viewport=None):
        """Write byte data to the texture

        :param Union[bytes, Buffer] data: bytes or a Buffer with data to write
        :param int level: The texture level to write
        :param tuple viewport: The are of the texture to write. 2 or 4 component tuple
        """
        # TODO: Support writing to layers using viewport + alignment
        if self._samples > 0:
            raise ValueError("Writing to multisample textures not supported")

        x, y, w, h = 0, 0, self._width, self._height
        if viewport:
            if len(viewport) == 2:
                w, h = viewport
            elif len(viewport) == 4:
                x, y, w, h = viewport
            else:
                raise ValueError("Viewport must be of length 2 or 4")

        if isinstance(data, bytes):
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(self._target, self._glo)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexSubImage2D(
                self._target,  # target
                level,  # level
                x,  # x offset
                y,  # y offset
                w,  # width
                h,  # height
                self._format,  # format
                self._type,  # type
                data,  # pixel data
            )
        elif isinstance(data, Buffer):
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, data.glo)
            gl.glActiveTexture(gl.GL_TEXTURE0)
            gl.glBindTexture(self._target, self._glo)
            gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexSubImage2D(self._target, level, x, y, w, h, self._format, self._type, 0)
            gl.glBindBuffer(gl.GL_PIXEL_UNPACK_BUFFER, 0)
        else:
            raise ValueError("data must be bytes or a Buffer")

    def build_mipmaps(self, base=0, max_amount=1000):
        """Generate mipmaps for this texture.
        Also see: https://www.khronos.org/opengl/wiki/Texture#Mip_maps
        """
        self.use()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BASE_LEVEL, base)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_LEVEL, max_amount)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    @staticmethod
    def release(glo: gl.GLuint):
        """Destroy the texture"""
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteTextures(1, byref(glo))

    def use(self, unit: int = 0):
        """Bind the texture to a channel,

        :param int unit: The texture unit to bind the texture.
        """
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._glo)

    def __repr__(self):
        return "<Texture glo={} size={}x{} components={}>".format(
            self._glo.value, self._width, self._height, self._components)


class Framebuffer:
    """
    An offscreen render target also called a Framebuffer Object in OpenGL.
    This implementation is using texture attachments. When createing a
    Framebuffer we supply it with textures we want our scene rendered into.
    """
    __slots__ = (
        '_ctx', '_glo', '_width', '_height', '_color_attachments', '_depth_attachment',
        '_samples', '_viewport', '_depth_mask', '_draw_buffers', '__weakref__')

    def __init__(self, ctx, color_attachments=None, depth_attachment=None):
        """Create a framebuffer.

        :param List[Texture] color_attachments: List of color attachments.
        :param Texture depth_attachment: A depth attachment (optional)
        """
        if not color_attachments:
            raise ValueError("Framebuffer must at least have one color attachment")

        self._ctx = ctx
        self._color_attachments = color_attachments if isinstance(color_attachments, list) else [color_attachments]
        self._depth_attachment = depth_attachment
        self._glo = fbo_id = gl.GLuint()  # The OpenGL alias/name
        self._samples = 0  # Leaving this at 0 for future sample support
        self._viewport = None
        self._depth_mask = True  # Determines of the depth buffer should be affected
        self._width = 0
        self._height = 0

        # Create the framebuffer object
        gl.glGenFramebuffers(1, self._glo)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)

        # Ensure all attachments have the same size.
        # OpenGL do actually support different sizes,
        # but let's keep this simple with high compatibility.
        expected_size = (self._color_attachments[0] if self._color_attachments else self._depth_attachment).size
        for layer in [*self._color_attachments, self._depth_attachment]:
            if layer and layer.size != expected_size:
                raise ValueError("All framebuffer attachments should have the same size")

        self._width, self._height = expected_size
        self._viewport = 0, 0, self._width, self._height

        # Attach textures to it
        for i, tex in enumerate(self._color_attachments):
            # TODO: Possibly support attaching a specific mipmap level
            #       but we can read from specific mip levels from shaders.
            gl.glFramebufferTexture2D(
                gl.GL_FRAMEBUFFER,
                gl.GL_COLOR_ATTACHMENT0 + i,
                gl.GL_TEXTURE_2D,
                tex.glo,
                0,  # Level 0
            )

        # Ensure the framebuffer is sane!
        self._check_completeness()

        # Set up draw buffers. This is simply a prepared list of attachments enums
        # we use in the use() method to activate the different color attachment layers
        layers = [gl.GL_COLOR_ATTACHMENT0 + i for i, _ in enumerate(self._color_attachments)]
        # pyglet wants this as a ctypes thingy, so let's prepare it
        self._draw_buffers = (gl.GLuint * len(layers))(*layers)

        # Restore the original bound framebuffer to avoid confusion
        self.ctx.active_framebuffer.use()
        weakref.finalize(self, Framebuffer.release, fbo_id)

    @property
    def glo(self) -> gl.GLuint:
        """The OpenGL id/name of the framebuffer"""
        return self._glo

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        """The framebuffer's viewport.

        Two or four integer values can be assigned::

            # Explicitly set start and end values
            fb.viewport = 100, 100, 200, 200
            # Implies 0, 0, 100, 100
            fb.viewport = 100, 100
        """
        return self._viewport

    @viewport.setter
    def viewport(self, value):
        if not isinstance(value, tuple):
            raise ValueError("viewport should be a tuple with length 2 or 4")

        if len(value) == 2:
            self._viewport = 0, 0, *value
        elif len(value) == 4:
            self._viewport = value
        else:
            raise ValueError("viewport should be a tuple with length 2 or 4")

        # If the framebuffer is bound we need to set the viewport.
        # Otherwise it will be set on use()
        if self._ctx.active_framebuffer == self:
            gl.glViewport(*self._viewport)

    @property
    def ctx(self) -> 'Context':
        """The context this object belongs to"""
        return self._ctx

    @property
    def width(self) -> int:
        """The width of the framebuffer in pixels"""
        return self._width

    @property
    def height(self) -> int:
        """The height of the framebuffer in pixels"""
        return self._height

    @property
    def size(self) -> Tuple[int, int]:
        """Size as a ``(w, h)`` tuple"""
        return self._width, self._height

    @property
    def samples(self) -> int:
        """Number of samples (MSAA)"""
        return self._samples

    @property
    def color_attachments(self) -> List[Texture]:
        """A list of color attachments"""
        return self._color_attachments

    @property
    def depth_attachment(self) -> Texture:
        """Depth attachment"""
        return self._depth_attachment

    @property
    def depth_mask(self) -> bool:
        """The depth mask. It determines of depth values should be written
        to the depth texture when depth testing is enabled.
        """
        return self._depth_mask

    @depth_mask.setter
    def depth_mask(self, value):
        self._depth_mask = value
        # Set state if framebuffer is active
        if self._ctx.active_framebuffer == self:
            gl.glDepthMask(self._depth_mask)

    def use(self):
        """Bind the framebuffer making it the target of all redering commands"""
        self._use()
        self._ctx.active_framebuffer = self

    def _use(self):
        """Internal use that do not change the global active framebuffer"""
        if self.ctx.active_framebuffer == self:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)
        # NOTE: gl.glDrawBuffer(GL_NONE) if no texture attachments (future)
        gl.glDrawBuffers(len(self._draw_buffers), self._draw_buffers)
        gl.glDepthMask(self._depth_mask)
        gl.glViewport(*self._viewport)

    def clear(self,
              color=(0.0, 0.0, 0.0, 0.0),
              depth: float = 1.0,
              normalized: bool = False):
        """
        Clears the framebuffer.

        :param tuple color: A 3 of 4 component tuple containing the color
        :param float depth: Value to clear the depth buffer (unused)
        :param bool normalized: If the color values are normalized or not
        """
        self._use()

        if normalized:
            # If the colors are already normalized we can pass them right in
            if len(color) == 3:
                gl.glClearColor(*color, 0.0)
            else:
                gl.glClearColor(*color)
        else:
            # OpenGL wants normalized colors (0.0 -> 1.0)
            if len(color) == 3:
                gl.glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, 0.0)
            else:
                gl.glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255)

        if self.depth_attachment:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # Restore the original render target to avoid confusion
        self._ctx.active_framebuffer.use()

    @staticmethod
    def release(framebuffer_id):
        """
        Destroys the framebuffer object

        :param framebuffer_id: Frame buffer to destroy
        """
        if gl.current_context is None:
            return

        gl.glDeleteFramebuffers(1, framebuffer_id)

    # NOTE: This is an experiment using a bind stack (can be explored later)
    # def __enter__(self):
    #     """Enter method for context manager"""
    #     self._stack.push(self)
    #     self.use()

    # def __exit__(self):
    #     """Exit method for context manager"""
    #     self._stack.pop()
    #     # TODO: Bind previous. if this is the window, how do we know the viewport etc?

    def __repr__(self):
        return "<Framebuffer glo={}>".format(self._glo)

    @staticmethod
    def _check_completeness():
        """
        Checks the completeness of the framebuffer.
        If the framebuffer is not complete, we cannot continue.
        """
        # See completness rules : https://www.khronos.org/opengl/wiki/Framebuffer_Object
        states = {gl.GL_FRAMEBUFFER_UNSUPPORTED: "Framebuffer unsupported. Try another format.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: "Framebuffer incomplete attachment.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: "Framebuffer missing attachment.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS_EXT: "Framebuffer unsupported dimension.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_FORMATS_EXT: "Framebuffer incomplete formats.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_DRAW_BUFFER: "Framebuffer incomplete draw buffer.",
                  gl.GL_FRAMEBUFFER_INCOMPLETE_READ_BUFFER: "Framebuffer incomplete read buffer.",
                  gl.GL_FRAMEBUFFER_COMPLETE: "Framebuffer is complete."}

        status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
        if status != gl.GL_FRAMEBUFFER_COMPLETE:
            raise ValueError("Framebuffer is incomplete. {}".format(states.get(status, "Unknown error")))


class Context:
    """
    Represents an OpenGL context. This context belongs to an arcade.Window.
    """
    resource_root = (Path(__file__).parent / 'resources').resolve()
    _errors = {
        gl.GL_INVALID_ENUM: 'GL_INVALID_ENUM',
        gl.GL_INVALID_VALUE: 'GL_INVALID_VALUE',
        gl.GL_INVALID_OPERATION: 'GL_INVALID_OPERATION',
        gl.GL_INVALID_FRAMEBUFFER_OPERATION: 'GL_INVALID_FRAMEBUFFER_OPERATION',
        gl.GL_OUT_OF_MEMORY: 'GL_OUT_OF_MEMORY',
        gl.GL_STACK_UNDERFLOW: 'GL_STACK_UNDERFLOW',
        gl.GL_STACK_OVERFLOW: 'GL_STACK_OVERFLOW',
    }

    def __init__(self, window):
        self._window = window
        # TODO: Detect OpenGL version etc
        self._gl_version = (3, 3)

        # Tracking active program
        self.active_program = None  # type: Program
        # Tracking active program
        self.active_framebuffer = window

        # --- Store the most commonly used OpenGL constants
        # Texture
        self.NEAREST = gl.GL_NEAREST
        self.LINEAR = gl.GL_LINEAR
        self.REPEAT = gl.GL_REPEAT
        self.CLAMP_TO_EDGE = gl.GL_CLAMP_TO_EDGE
        self.CLAMP_TO_BORDER = gl.GL_CLAMP_TO_BORDER
        self.MIRRORED_REPEAT = gl.GL_MIRRORED_REPEAT

        # VertexArray: Primitives
        self.POINTS = gl.GL_POINTS
        self.LINES = gl.GL_LINES
        self.LINES_ADJACENCY = gl.GL_LINES_ADJACENCY
        self.LINE_STRIP = gl.GL_LINE_STRIP
        self.LINE_STRIP_ADJACENCY = gl.GL_LINE_STRIP_ADJACENCY
        self.TRIANGLES = gl.GL_TRIANGLES
        self.TRIANGLES_ADJACENCY = gl.GL_TRIANGLES_ADJACENCY
        self.TRIANGLE_STRIP = gl.GL_TRIANGLE_STRIP
        self.TRIANGLE_STRIP_ADJACENCY = gl.GL_TRIANGLE_STRIP_ADJACENCY
        self.TRIANGLE_FAN = gl.GL_TRIANGLE_FAN

        # --- Pre-load system shaders here ---

        self.line_vertex_shader = self.load_program(
            self.resource_root / 'shaders/line_vertex_shader_vs.glsl',
            self.resource_root / 'shaders/line_vertex_shader_fs.glsl',
        )
        self.line_generic_with_colors_program = self.load_program(
            self.resource_root / 'shaders/line_generic_with_colors_vs.glsl',
            self.resource_root / 'shaders/line_generic_with_colors_fs.glsl',
        )
        self.shape_element_list_program = self.load_program(
            self.resource_root / 'shaders/shape_element_list_vs.glsl',
            self.resource_root / 'shaders/shape_element_list_fs.glsl',
        )
        self.sprite_list_program = self.load_program(
            self.resource_root / 'shaders/sprite_list_vs.glsl',
            self.resource_root / 'shaders/sprite_list_fs.glsl',
        )

    @property
    def gl_version(self):
        """ Return OpenGL version. """
        return self._gl_version

    @property
    def error(self) -> Union[str, None]:
        """Check OpenGL error

        Returns a string representation of the occurring error
        or ``None`` of no errors has occurred.

        Example::

            err = ctx.error
            if err:
                raise RuntimeError("OpenGL error: {err}")
        """
        err = gl.glGetError()
        if err == gl.GL_NO_ERROR:
            return None

        return self._errors.get(err, 'GL_UNKNOWN_ERROR')

    def buffer(self, data: bytes = None, reserve: int = 0, usage: str = 'static') -> Buffer:
        """Create a new OpenGL Buffer object.

        :param bytes data: The buffer data
        :param int reserve: The number of bytes reserve
        :param str usage: Buffer usage. 'static', 'dynamic' or 'stream'
        """
        # create_with_size
        return Buffer(self, data, reserve=reserve, usage=usage)

    def framebuffer(self, color_attachments: List[Texture] = None, depth_attachment: Texture = None) -> Framebuffer:
        """Create a Framebuffer.

        :param List[Texture] color_attachments: List of textures we want to render into
        :param Texture depth_attachment: Depth texture
        """
        return Framebuffer(self, color_attachments, depth_attachment)

    def texture(self,
                size: Tuple[int, int],
                components: int = 4,
                dtype: str = 'f1',
                data: bytes = None,
                wrap_x: gl.GLenum = None,
                wrap_y: gl.GLenum = None,
                texture_filter: Tuple[gl.GLenum, gl.GLenum] = None) -> Texture:
        """Create a Texture.

        Wrap modes: ``GL_REPEAT``, ``GL_MIRRORED_REPEAT``, ``GL_CLAMP_TO_EDGE``, ``GL_CLAMP_TO_BORDER``

        Minifying filters: ``GL_NEAREST``, ``GL_LINEAR``, ``GL_NEAREST_MIPMAP_NEAREST``, ``GL_LINEAR_MIPMAP_NEAREST``
        ``GL_NEAREST_MIPMAP_LINEAR``, ``GL_LINEAR_MIPMAP_LINEAR``

        Magnifying filters: ``GL_NEAREST``, ``GL_LINEAR``

        :param Tuple[int, int] size: The size of the texture
        :param int components: Number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
        :param str dtype: The data type of each component: f1, f2, f4 / i1, i2, i4 / u1, u2, u4
        :param buffer data: The texture data (optional)
        :param GLenum wrap_x: How the texture wraps in x direction
        :param GLenum wrap_y: How the texture wraps in y direction
        :param Tuple[GLenum, GLenum] texture_filter: Minification and magnification filter
        """
        return Texture(self, size, components=components, data=data, dtype=dtype,
                       wrap_x=wrap_x, wrap_y=wrap_y,
                       texture_filter=texture_filter)

    def vertex_array(self, prog: gl.GLuint, content, index_buffer=None):
        """Create a new Vertex Array.
        """
        return VertexArray(self, prog, content, index_buffer)

    def program(self, vertex_shader: str, fragment_shader: str = None, geometry_shader: str = None) -> Program:
        """Create a new program given the vertex_shader and fragment shader code.
        """
        shaders = [(vertex_shader, gl.GL_VERTEX_SHADER)]
        if fragment_shader:
            shaders.append((fragment_shader, gl.GL_FRAGMENT_SHADER))
        if geometry_shader:
            shaders.append((geometry_shader, gl.GL_GEOMETRY_SHADER))

        return Program(self, *shaders)

    def load_program(self, vertex_shader_filename, fragment_shader_filename) -> Program:
        """ Create a new program given a file names that contain the vertex shader and
        fragment shader. """
        with open(vertex_shader_filename, "r") as myfile:
            vertex_shader = myfile.read()
        with open(fragment_shader_filename, "r") as myfile:
            fragment_shader = myfile.read()
        return self.program(vertex_shader, fragment_shader)
