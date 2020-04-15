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


# Thank you Benjamin Moran for writing part of this code!
# https://bitbucket.org/HigashiNoKaze/pyglet/src/shaders/pyglet/graphics/shader.py


class ShaderException(Exception):
    """ Exception class for shader-specific problems. """
    pass


class TypeInfo:
    __slots__ = 'name', 'enum', 'gl_type', 'gl_size', 'components'

    def __init__(self, name, enum, gl_type, gl_size, components):
        """Describes an opengl type

        :param name: the string represenation of this type
        :param enum: The enum of this type
        :param gl_type: the base enum of this type
        :param gl_size: byte size if the gl_type
        :param components: Number of components for this enum
        """
        self.name = name  # type: str
        self.enum = enum  # type: gl.GLenum
        self.gl_type = gl_type  # type: gl.GLenum
        self.gl_size = gl_size # type: int
        self.components = components  # type: int

    @property
    def size(self):
        return self.gl_size * self.components

    def __repr__(self):
        return (
            f"<TypeInfo name={self.name}, enum={self.enum} gl_type={self.gl_type} "
            f"gl_size={self.gl_size} components={self.components}>"
        )


class GLTypes:
    """
    Get information about an attribute type.
    During introspection we often just get integers telling us what type is used.
    This can for example be `35664` telling us it's a `GL_FLOAT_VEC2`.
    We want to know this is a `gl.GLfloat` with 2 components so we can compare
    that to the types in the `BufferDescription`.
    These an also be used for uniform introspection.
    """
    # Source : https://github.com/Contraz/demosys-py/blob/f63f5dc727eafb8302cce64a890ce4527303588b/demosys/opengl/constants.py#L37-L139
    types = {
        # Floats
        gl.GL_FLOAT: TypeInfo("GL_FLOAT", gl.GL_FLOAT, gl.GL_FLOAT, 4, 1),
        gl.GL_FLOAT_VEC2: TypeInfo("GL_FLOAT_VEC2", gl.GL_FLOAT_VEC2, gl.GL_FLOAT, 4, 2),
        gl.GL_FLOAT_VEC3: TypeInfo("GL_FLOAT_VEC3", gl.GL_FLOAT_VEC3, gl.GL_FLOAT, 4, 3),
        gl.GL_FLOAT_VEC4: TypeInfo("GL_FLOAT_VEC4", gl.GL_FLOAT_VEC4, gl.GL_FLOAT, 4, 4),
        # Doubles
        gl.GL_DOUBLE: TypeInfo("GL_DOUBLE", gl.GL_DOUBLE, gl.GL_DOUBLE,  8, 1),
        gl.GL_DOUBLE_VEC2: TypeInfo("GL_DOUBLE_VEC2", gl.GL_DOUBLE_VEC2, gl.GL_DOUBLE, 8, 2),
        gl.GL_DOUBLE_VEC3: TypeInfo("GL_DOUBLE_VEC3", gl.GL_DOUBLE_VEC3, gl.GL_DOUBLE, 8, 3),
        gl.GL_DOUBLE_VEC4: TypeInfo("GL_DOUBLE_VEC4", gl.GL_DOUBLE_VEC4, gl.GL_DOUBLE, 8, 4),
        # Booleans (ubyte)
        gl.GL_BOOL: TypeInfo("GL_BOOL", gl.GL_BOOL, gl.GL_BOOL, 1, 1),
        gl.GL_BOOL_VEC2: TypeInfo("GL_BOOL_VEC2", gl.GL_BOOL_VEC2, gl.GL_BOOL, 1, 2),
        gl.GL_BOOL_VEC3: TypeInfo("GL_BOOL_VEC3", gl.GL_BOOL_VEC3, gl.GL_BOOL, 1, 3),
        gl.GL_BOOL_VEC4: TypeInfo("GL_BOOL_VEC4", gl.GL_BOOL_VEC4, gl.GL_BOOL, 1, 4),
        # Integers
        gl.GL_INT: TypeInfo("GL_INT", gl.GL_INT, gl.GL_INT, 4, 1),
        gl.GL_INT_VEC2: TypeInfo("GL_INT_VEC2", gl.GL_INT_VEC2, gl.GL_INT, 4, 2),
        gl.GL_INT_VEC3: TypeInfo("GL_INT_VEC3", gl.GL_INT_VEC3, gl.GL_INT, 4, 3),
        gl.GL_INT_VEC4: TypeInfo("GL_INT_VEC4", gl.GL_INT_VEC4, gl.GL_INT, 4, 4),
        # Unsigned Integers
        gl.GL_UNSIGNED_INT: TypeInfo("GL_UNSIGNED_INT", gl.GL_UNSIGNED_INT, gl.GL_UNSIGNED_INT, 4, 1),
        gl.GL_UNSIGNED_INT_VEC2: TypeInfo("GL_UNSIGNED_INT_VEC2", gl.GL_UNSIGNED_INT_VEC2, gl.GL_UNSIGNED_INT, 4, 2),
        gl.GL_UNSIGNED_INT_VEC3: TypeInfo("GL_UNSIGNED_INT_VEC3", gl.GL_UNSIGNED_INT_VEC3, gl.GL_UNSIGNED_INT, 4, 3),
        gl.GL_UNSIGNED_INT_VEC4: TypeInfo("GL_UNSIGNED_INT_VEC4", gl.GL_UNSIGNED_INT_VEC4, gl.GL_UNSIGNED_INT, 4, 4),
        # Unsigned Short (mostly used for short index buffers)
        gl.GL_UNSIGNED_SHORT: TypeInfo("GL.GL_UNSIGNED_SHORT", gl.GL_UNSIGNED_SHORT, gl.GL_UNSIGNED_SHORT, 2, 2),
        # Byte
        gl.GL_BYTE: TypeInfo("GL_BYTE", gl.GL_BYTE, gl.GL_BYTE, 1, 1),
        gl.GL_UNSIGNED_BYTE: TypeInfo("GL_UNSIGNED_BYTE", gl.GL_UNSIGNED_BYTE, gl.GL_UNSIGNED_BYTE, 1, 1),
        # TODO: Add sampler types if needed. Only needed for better uniform introspection.
    }

    @classmethod
    def get(cls, enum: int):
        try:
            return cls.types[enum]
        except KeyError:
            raise ValueError(f"Unknown gl type {enum}. Someone needs to add it")


class Uniform:
    """A Program uniform"""

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

    __slots__ = '_program_id', '_location', '_name', '_data_type', '_array_length', 'getter', 'setter'

    def __init__(self, program_id, location, name, data_type, array_length):
        """Create a Uniform

        :param int location: The location of the uniform in the program
        :param str name: Name of the uniform in the program
        :param gl.GLenum data_type: The data type of the uniform (GL_FLOAT
        """
        self._program_id = program_id
        self._location = location
        self._name = name
        self._data_type = data_type
        self._array_length = array_length
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

    def _setup_getters_and_setters(self):
        """Maps the right getter and setter functions for this uniform"""
        try:
            gl_type, gl_setter, length, count = self._uniform_setters[self._data_type]
        except KeyError:
            raise ShaderException(f"Unsupported Uniform type: {self._data_type}")

        gl_getter = self._uniform_getters[gl_type]
        is_matrix = self._data_type in (gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3, gl.GL_FLOAT_MAT4)

        # Create persistent mini c_array for getters and setters:
        length = length * self._array_length  # Increase buffer size to include arrays
        c_array = (gl_type * length)()
        ptr = cast(c_array, POINTER(gl_type))

        # Create custom dedicated getters and setters for each uniform:
        self.getter = Uniform._create_getter_func(self._program_id, self._location, gl_getter, c_array, length)
        self.setter = Uniform._create_setter_func(self._location, gl_setter, c_array, length, count, ptr, is_matrix)

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

    def __repr__(self):
        return f"<Uniform '{self._name}' loc={self._location} array_length={self._array_length}"


class AttribFormat:
    """Describes a format for a single attribute"""
    __slots__ = 'name', 'gl_type', 'components', 'bytes_per_component', 'offset', 'location',

    def __init__(self, name, gl_type, components, bytes_per_component, offset=0, location=0):
        """Represents an attribute in a BufferDescription or a Program.

        :param str name: Name of the attribute
        :param gl.GLEnum gl_type: The OpenGL type such as GL_FLOAT, GL_HALF_FLOAT etc.
        :param int bytes_per_component: Number of bytes a single component takes
        :param int offset: (Optional offset for BufferDescription)
        :param int location: (Optional location for program attribute)
        """
        self.name = name  # type: str
        self.gl_type = gl_type  # type: gl.GLenum
        self.components = components  # type: int
        self.bytes_per_component = bytes_per_component  # type: int
        self.offset = offset  # type: int
        self.location = location  # type: int

    @property
    def bytes_total(self) -> int:
        """Total number of bytes for this attribute"""
        return self.components * self.bytes_per_component

    def __repr__(self):
        return (
            f"<AttribFormat {self.name} {self.gl_type} components={self.components} "
            f"bytes_per_component={self.bytes_per_component}>"
        )


class Program:
    """Compiled and linked shader program.

    Currently supports vertex, fragment and geometry shaders.
    Transform feedback also supported when output attributes
    names are passed in the varyings parameter.

    Access Uniforms via the [] operator.
    Example:
        program['MyUniform'] = value
    """
    __slots__ = (
        '_ctx', '_glo', '_uniforms', '_out_attributes', '_geometry_info',
        '_attributes', 'attribute_key', '__weakref__'
    )

    _shader_types_names = {
        gl.GL_VERTEX_SHADER: "vertex shader",
        gl.GL_FRAGMENT_SHADER: "fragment shader",
        gl.GL_GEOMETRY_SHADER: "geometry shader",
    }

    def __init__(self,
                 ctx,
                 *,
                 vertex_shader: str,
                 fragment_shader: str = None,
                 geometry_shader: str = None,
                 out_attributes: List[str] = None):
        """Create a Program.

        :param Context ctx: The context this program belongs to
        :param str vertex_shader: vertex shader source
        :param str fragment_shader: fragment shader source
        :param str geometry_shader: geometry shader source
        :param List[str] out_attributes: List of out attributes used in transform feedback.
        """
        self._ctx = ctx
        self._glo = glo = gl.glCreateProgram()
        self._out_attributes = out_attributes or []
        self._geometry_info = (0, 0, 0)
        self._attributes = []  # type: List[AttribFormat]
        self.attribute_key = "INVALID"  # type: str

        shaders = [(vertex_shader, gl.GL_VERTEX_SHADER)]
        if fragment_shader:
            shaders.append((fragment_shader, gl.GL_FRAGMENT_SHADER))
        if geometry_shader:
            shaders.append((geometry_shader, gl.GL_GEOMETRY_SHADER))

        shaders_id = []
        for shader_code, shader_type in shaders:
            shader = Program.compile_shader(shader_code, shader_type)
            gl.glAttachShader(self._glo, shader)
            shaders_id.append(shader)

        # For now we assume varyings can be set up if no fragment shader
        if not fragment_shader:
            self._setup_out_attributes()

        Program.link(self._glo)
        if geometry_shader:
            geometry_in = gl.GLint()
            geometry_out = gl.GLint()
            geometry_vertices = gl.GLint()
            gl.glGetProgramiv(self._glo, gl.GL_GEOMETRY_INPUT_TYPE, geometry_in);
            gl.glGetProgramiv(self._glo, gl.GL_GEOMETRY_OUTPUT_TYPE, geometry_out);
            gl.glGetProgramiv(self._glo, gl.GL_GEOMETRY_VERTICES_OUT, geometry_vertices);
            self._geometry_info = (geometry_in.value, geometry_out.value, geometry_vertices.value)

        # Flag shaders for deletion. Will only be deleted once detached from program.
        for shader in shaders_id:
            gl.glDeleteShader(shader)

        # Handle uniforms
        self._uniforms: Dict[str, Uniform] = {}
        self._introspect_attributes()
        self._introspect_uniforms()

        self.ctx.stats.incr('program')
        weakref.finalize(self, Program._delete, self.ctx, shaders_id, glo)

    @property
    def ctx(self) -> 'Context':
        """The context this program belongs to"""
        return self._ctx

    @property
    def glo(self) -> int:
        """The OpenGL resource id for this program"""
        return self._glo

    @property
    def attributes(self) -> Iterable[AttribFormat]:
        return self._attributes

    @property
    def out_attributes(self) -> List[str]:
        """Out attributes names used in transform feedback"""
        return self._out_attributes

    @property
    def geometry_input(self) -> int:
        """The geometry shader's input primitive type.
        This an be compared with ``GL_TRIANGLES``, ``GL_POINTS`` etc.
        """
        return self._geometry_info[0]

    @property
    def geometry_output(self) -> int:
        """The geometry shader's output primitive type.
        This an be compared with ``GL_TRIANGLES``, ``GL_POINTS`` etc.
        """
        return self._geometry_info[1]

    @property
    def geometry_vertices(self) -> int:
        """The maximum number of vertices that can be emitted"""
        return self._geometry_info[2]

    @staticmethod
    def _delete(ctx, shaders_id, prog_id):
        # Check to see if the context was already cleaned up from program
        # shut down. If so, we don't need to delete the shaders.
        if gl.current_context is None:
            return

        for shader_id in shaders_id:
            gl.glDetachShader(prog_id, shader_id)

        gl.glDeleteProgram(prog_id)

        ctx.stats.decr('program')

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

    def _setup_out_attributes(self):
        """Set up transform feedback varyings"""
        if not self._out_attributes:
            return

        # Covert names to char**
        c_array = (c_char_p * len(self._out_attributes))()
        for i, name in enumerate(self._out_attributes):
            c_array[i] = name.encode()

        ptr = cast(c_array, POINTER(POINTER(c_char)))

        # NOTE: We only support interleaved attributes for now
        gl.glTransformFeedbackVaryings(
            self._glo,  # program
            len(self._out_attributes),  # number of varying variables used for transform feedback
            ptr,  # zero-terminated strings specifying the names of the varying variables
            gl.GL_INTERLEAVED_ATTRIBS,
        )

    def _introspect_attributes(self):
        """Introspect and store detailed info about an attribute"""
        # TODO: Ensure gl_* attributes are ignored
        num_attrs = gl.GLint()
        gl.glGetProgramiv(self._glo, gl.GL_ACTIVE_ATTRIBUTES, num_attrs)
        num_varyings = gl.GLint()
        gl.glGetProgramiv(self._glo, gl.GL_TRANSFORM_FEEDBACK_VARYINGS, num_varyings)
        # print(f"attrs {num_attrs.value} varyings={num_varyings.value}")

        for i in range(num_attrs.value):
            c_name = create_string_buffer(256)
            c_size = gl.GLint()
            c_type = gl.GLenum()
            gl.glGetActiveAttrib(
                self._glo,  # program to query
                i,  # index (not the same as location)
                256,  # max attr name size
                None,  # c_length,  # length of name
                c_size,  # size of attribute (array or not)
                c_type,  # attribute type (enum)
                c_name,  # name buffer
            )

            # Get the actual location. Do not trust the original order
            location = gl.glGetAttribLocation(self._glo, c_name)

            # print(c_name.value, c_size, c_type)
            type_info = GLTypes.get(c_type.value)
            # print(type_info)
            self._attributes.append(AttribFormat(
                c_name.value.decode(),
                type_info.gl_type,
                type_info.components,
                type_info.gl_size,
                location=location,
            ))

        # The attribute key is used to cache VertexArrays
        self.attribute_key = ':'.join(f'{attr.name}[{attr.gl_type}/{attr.components}]' for attr in self._attributes)

    def _introspect_uniforms(self):
        """Figure out what uniforms are available and build an internal map"""
        # Number of active uniforms in the program
        active_uniforms = gl.GLint(0)
        gl.glGetProgramiv(self._glo, gl.GL_ACTIVE_UNIFORMS, byref(active_uniforms))

        # Loop all the active uniforms
        for index in range(active_uniforms.value):
            # Query uniform information like name, type, size etc.
            u_name, u_type, u_size = self._query_uniform(index)
            u_location = gl.glGetUniformLocation(self._glo, u_name.encode())

            # Skip uniforms that may be in Uniform Blocks
            # TODO: We should handle all uniforms
            if u_location == -1:
                # print(f"Uniform {u_location} {u_name} {u_size} {u_type} skipped")
                continue

            u_name = u_name.replace('[0]', '')  # Remove array suffix
            self._uniforms[u_name] = Uniform(self._glo, u_location, u_name, u_type, u_size)

    def _query_uniform(self, location: int) -> Tuple[str, int, int]:
        """Retrieve Uniform information at given location.

        Returns the name, the type as a GLenum (GL_FLOAT, ...) and the size. Size is
        greater than 1 only for Uniform arrays, like an array of floats or an array
        of Matrices.
        """
        usize = gl.GLint()
        utype = gl.GLenum()
        buf_size = 192  # max uniform character length
        uname = create_string_buffer(buf_size)
        gl.glGetActiveUniform(
            self._glo,  # program to query
            location,  # location to query
            buf_size,  # size of the character/name buffer
            None,  # the number of characters actually written by OpenGL in the string
            usize,  # size of the uniform variable
            utype,  # data type of the uniform variable
            uname  # string buffer for storing the name
        )
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
            raise ShaderException((
                f"Error compiling {Program._shader_types_names[shader_type]} "
                f"({result.value}): {msg.value.decode('utf-8')}\n"
                f"---- [{Program._shader_types_names[shader_type]}] ---\n"
            ) + '\n'.join(f"{str(i+1).zfill(3)}: {line} " for i, line in enumerate(source.split('\n'))))
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

        self.ctx.stats.incr('buffer')
        weakref.finalize(self, Buffer.release, self.ctx, glo)

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
    def release(ctx: 'Context', glo: gl.GLuint):
        """ Release/delete open gl buffer. """
        # print(f"*** Buffer {glo} have no more references. Deleting.")

        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteBuffers(1, byref(glo))
            glo.value = 0

        ctx.stats.decr('buffer')

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

    def bind(self):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self._glo)


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
    # Describe all variants of a format string to simplify parsing (single component)
    # format: gl_type, byte_size
    # TODO: Can we support separate per-instance attributes in an interleaved buffer?
    # TODO: Consider adding normalized integers
    _formats = {
        # (gl enum, byte size)
        # Floats
        'f':  (gl.GL_FLOAT, 4),
        'f1': (gl.GL_UNSIGNED_BYTE, 1),
        'f2': (gl.GL_HALF_FLOAT, 2),
        'f4': (gl.GL_FLOAT, 4),
        'f8': (gl.GL_DOUBLE, 8),
        # Unsigned integers
        'u':  (gl.GL_FLOAT, 4),
        'u1': (gl.GL_FLOAT, 1),
        'u2': (gl.GL_FLOAT, 2),
        'u4': (gl.GL_FLOAT, 4),
        # Signed integers
        'i': (gl.GL_INT, 4),
        'i1': (gl.GL_BYTE, 1),
        'i2': (gl.GL_SHORT, 2),
        'i4': (gl.GL_INT, 4),
        # Padding (1, 2, 4, 8 bytes)
        'x1': (None, 1),
        'x2': (None, 2),
        'x4': (None, 4),
        'x8': (None, 8),
    }

    __slots__ = 'buffer', 'attributes', 'normalized', 'instanced', 'formats', 'stride', 'num_vertices'

    def __init__(self,
                 buffer: Buffer,
                 formats: str,
                 attributes: Iterable[str],
                 normalized: Iterable[str] = None,
                 instanced: bool = False):
        self.buffer = buffer  # type: Buffer
        self.attributes = list(attributes)
        self.normalized = set() if normalized is None else set(normalized)
        self.instanced = instanced  # type: bool
        self.formats = []  # type: List[AttribFormat]
        self.stride = -1  # type: int
        self.num_vertices = -1  # type: int

        if self.normalized > set(self.attributes):
            raise ShaderException("Normalized attribute not found in attributes.")

        formats_list = formats.split(" ")

        if len(formats_list) != len(self.attributes):
            raise ShaderException(
                f"Different lengths of formats ({len(formats_list)}) and "
                f"attributes ({len(self.attributes)})"
            )

        self.stride = 0
        for attr_fmt, attr_name in zip(formats_list, self.attributes):
            try:
                components_str, data_type_str, data_size_str = re.split(r'([fiu])', attr_fmt)
                data_type = f"{data_type_str}{data_size_str}"if data_size_str else data_type_str
                components = int(components_str) if components_str else 1  # 1 component is default
                data_size = int(data_size_str) if data_size_str else 4  # 4 byte float and integer types are default
                # Limit components to 4 for non-padded formats
                if components > 4 and data_size is not None:
                    raise ValueError("Number of components must be 1, 2, 3 or 4")
            except Exception as ex:
                raise ValueError(f"Could not parse attribute format: '{attr_fmt} : {ex}'")

            gl_type, byte_size = self._formats[data_type]
            self.formats.append(AttribFormat(attr_name, gl_type, components, byte_size, offset=self.stride))

            self.stride += byte_size * components

        if self.buffer.size % self.stride != 0:
            raise ValueError(
                f"Buffer size must align by {self.stride} bytes. "
                f"{self.buffer} size={self.buffer.size}"
            )

        # Estimate number of vertices for this buffer
        self.num_vertices = self.buffer.size // self.stride

    def __repr__(self) -> str:
        return f"<BufferDescription {self.formats}>"


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
    __slots__ = '_ctx', '_glo', '_program', '_content', '_ibo', '_content', '_num_vertices', '__weakref__'

    # TODO: Resolve what VertexArray should actually store
    def __init__(self,
                 ctx: 'Context',
                 program: Program,
                 content: Iterable[BufferDescription],
                 index_buffer: Buffer = None):
        self._ctx = ctx
        self._program = program
        self._content = content
        self._glo = glo = gl.GLuint()
        self._num_vertices = -1
        self._ibo = index_buffer

        self._build(program, content, index_buffer)

        self.ctx.stats.incr('vertex_array')
        weakref.finalize(self, VertexArray.release, self.ctx, glo)

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
    def release(ctx: 'Context', glo: gl.GLuint):
        """Delete the object"""
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteVertexArrays(1, byref(glo))
            glo.value = 0

        ctx.stats.decr('vertex_array')

    def _build(self, program: Program, content: Iterable[BufferDescription], index_buffer):
        gl.glGenVertexArrays(1, byref(self._glo))
        gl.glBindVertexArray(self._glo)

        # Lookup dict for BufferDescription attrib names
        # print(content)
        descr_attribs = {attr.name: (descr, attr) for descr in content for attr in descr.formats}
        # print('->', descr_attribs)

        # Build the vao according to the shader's attribute specifications
        for i, prog_attr in enumerate(program.attributes):
            # print('prog_attr', prog_attr)
            # Do we actually have an attribute with this name in buffer descriptions?
            try:
                buff_descr, attr_descr = descr_attribs[prog_attr.name]
            except KeyError:
                raise ShaderException((
                    f"Program needs attribute '{prog_attr.name}', but is not present in buffer description. "
                    f"Buffer descriptions: {content}"
                ))

            # TODO: Sanity check this
            # if buff_descr.instanced and i == 0:
            #     raise ShaderException("The first vertex attribute cannot be a per instance attribute.")

            # Make sure components described in BufferDescription and in the shader match
            if prog_attr.components != attr_descr.components:
                raise ShaderException((
                    f"Program attribute '{prog_attr.name}' has {prog_attr.components} components "
                    f"while the buffer description has {attr_descr.components} components. "
                ))

            # TODO: Compare gltype between buffer descr and program attr

            gl.glEnableVertexAttribArray(prog_attr.location)
            buff_descr.buffer.bind()

            # TODO: Detect normalization
            normalized = gl.GL_TRUE if attr_descr.name in buff_descr.normalized else gl.GL_FALSE
            gl.glVertexAttribPointer(
                prog_attr.location,  # attrib location
                attr_descr.components,  # 1, 2, 3 or 4
                attr_descr.gl_type,  # GL_FLOAT etc
                normalized,  # normalize
                buff_descr.stride,
                c_void_p(attr_descr.offset),
            )
            # print((
            #     f"gl.glVertexAttribPointer(\n"
            #     f"    {prog_attr.location},  # attrib location\n"
            #     f"    {attr_descr.components},  # 1, 2, 3 or 4\n"
            #     f"    {attr_descr.gl_type},  # GL_FLOAT etc\n"
            #     f"    {normalized},  # normalize\n"
            #     f"    {buff_descr.stride},\n"
            #     f"    c_void_p({attr_descr.offset}),\n"
            # ))
            # TODO: Sanity check this
            if buff_descr.instanced:
                gl.glVertexAttribDivisor(prog_attr.location, 1)

        if index_buffer is not None:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, index_buffer.glo)

    def render(self, mode: gl.GLenum, first: int = 0, vertices: int = 0, instances: int = 1):
        """Render the VertexArray to the currently active framebuffer.

        :param GLunit mode: Primitive type to render. TRIANGLES, LINES etc.
        :param int first: The first vertex to render from
        :param int vertices: Number of vertices to render
        :param int instances: OpenGL instance, used in using vertexes over and over
        """
        gl.glBindVertexArray(self._glo)
        if self._ibo is not None:
            count = self._ibo.size // 4
            # TODO: Support first argument by offsetting pointer (second last arg)
            gl.glDrawElementsInstanced(mode, count, gl.GL_UNSIGNED_INT, None, instances)
        else:
            # print(f"glDrawArraysInstanced({mode}, {first}, {vertices}, {instances})")
            gl.glDrawArraysInstanced(mode, first, vertices, instances)


class Geometry:
    """A higher level abstraction of the VertexArray.
    It generates VertexArray instances on the fly internally matching the incoming program.
    This means we can render the same geometry with different programs as long as the
    Program and BufferDescription have compatible attributes.
    """
    __slots__ = '_ctx', '_content', '_index_buffer', '_mode', '_vao_cache', '_num_vertices', '__weakref__'

    def __init__(
            self,
            ctx: 'Context',
            content: Iterable[BufferDescription],
            index_buffer: Buffer = None,
            mode=None):
        self._ctx = ctx
        self._content = content
        self._index_buffer = index_buffer
        self._mode = mode or ctx.TRIANGLES
        self._vao_cache = {}  # type: Dict[str, VertexArray]
        self._num_vertices = -1

        if not content:
            raise ValueError("Geometry without buffer descriptions not supported")

        # Calculate vertices. Use the minimum for now
        self._num_vertices = next(iter(content)).num_vertices
        for descr in self._content:
            if descr.instanced:
                continue
            self._num_vertices = min(self._num_vertices, descr.num_vertices)

        # No cleanup is needed, but we want to count them
        weakref.finalize(self, Geometry._release, self._ctx)
        self._ctx.stats.incr('geometry')

    @property
    def ctx(self) -> 'Context':
        return self._ctx

    @property
    def index_buffer(self):
        return self._index_buffer

    @property
    def num_vertices(self) -> int:
        # TODO: Calculate this better...
        return self._num_vertices

    @num_vertices.setter
    def num_vertices(self, value):
        self._num_vertices = value

    def instance(self, program: Program) -> VertexArray:
        """Get the VertexArray compatible with this program"""
        vao = self._vao_cache.get(program.attribute_key)
        if vao:
            return vao

        return self._generate_vao(program)

    def render(self, program: Program, *, mode: gl.GLenum = None,
               first: int = 0, vertices: int = None, instances: int = 1):
        """Render the geometry with a specific program.
        :param Program program: The Program to render with
        :param gl.GLenum mode: Override what primitive mode should be used
        :param int first: Offset start vertex
        :param int vertices: Number of vertices to render
        :param int instances: Number of instances to render
        """
        program.use()
        vao = self.instance(program)
        mode = self._mode if mode is None else mode
        if mode:
            vao.render(mode=mode, first=first, vertices=vertices or self._num_vertices, instances=instances)
        else:
            vao.render(mode=mode, first=first, vertices=vertices or self._num_vertices, instances=instances)

    def transform(self, program: Program):
        """Render with transform feedback"""
        raise NotImplementedError()

    def flush(self):
        """Flush all generated VertexArrays"""
        self._vao_cache = {}

    def _generate_vao(self, program: Program) -> VertexArray:
        """Here we do the VertexArray building"""
        # print(f"Generating vao for key {program.attribute_key}")

        vao = VertexArray(self._ctx, program, self._content, index_buffer=self._index_buffer)
        self._vao_cache[program.attribute_key] = vao
        return vao

    @staticmethod
    def _release(ctx):
        """Mainly here to count destroyed instances"""
        ctx.stats.decr('geometry')


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
                 *,
                 components: int = 4,
                 dtype: str = 'f1',
                 data: bytes = None,
                 filter: Tuple[gl.GLuint, gl.GLuint] = None,
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
                "MAX_TEXTURE_SIZE = {self.ctx.limits.MAX_TEXTURE_SIZE}"
            ))

        self.filter = filter or self._filter
        self.wrap_x = wrap_x or self._wrap_x
        self.wrap_y = wrap_y or self._wrap_y

        self.ctx.stats.incr('texture')
        weakref.finalize(self, Texture.release, self._ctx, glo)

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
    def release(ctx: 'Context', glo: gl.GLuint):
        """Destroy the texture"""
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if glo.value != 0:
            gl.glDeleteTextures(1, byref(glo))

        ctx.stats.decr('texture')

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

    def __init__(self, ctx, *, color_attachments=None, depth_attachment=None):
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

        self.ctx.stats.incr('framebuffer')
        weakref.finalize(self, Framebuffer.release, ctx, fbo_id)

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
              *,
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
    def release(ctx, framebuffer_id):
        """
        Destroys the framebuffer object

        :param framebuffer_id: Frame buffer to destroy
        """
        if gl.current_context is None:
            return

        gl.glDeleteFramebuffers(1, framebuffer_id)
        ctx.stats.decr('framebuffer')

    # NOTE: This is an experiment using a bind stack (can be explored later)
    # def __enter__(self):
    #     """Enter method for context manager"""
    #     self._stack.push(self)
    #     self.use()

    # def __exit__(self):
    #     """Exit method for context manager"""
    #     self._stack.pop()
    #     # TODO: Bind previous. if this is the window, how do we know the viewport etc?

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

    def __repr__(self):
        return "<Framebuffer glo={}>".format(self._glo.value)


class Limits:
    """OpenGL Limitations"""
    def __init__(self, ctx):
        self._ctx = ctx
        #: Minor version number of the OpenGL API supported by the current context
        self.MINOR_VERSION = self.get(gl.GL_MINOR_VERSION)
        #: Major version number of the OpenGL API supported by the current context.
        self.MAJOR_VERSION = self.get(gl.GL_MAJOR_VERSION)
        #: Value indicating the number of sample buffers associated with the framebuffer
        self.SAMPLE_BUFFERS = self.get(gl.GL_SAMPLE_BUFFERS)
        #: An estimate of the number of bits of subpixel resolution
        #: that are used to position rasterized geometry in window coordinates
        self.SUBPIXEL_BITS = self.get(gl.GL_SUBPIXEL_BITS)
        #: A mask value indicating what context profile is used (core, compat etc.)
        self.CONTEXT_PROFILE_MASK = self.get(gl.GL_CONTEXT_PROFILE_MASK)
        #: Minimum required alignment for uniform buffer sizes and offset
        self.UNIFORM_BUFFER_OFFSET_ALIGNMENT = self.get(gl.GL_UNIFORM_BUFFER_OFFSET_ALIGNMENT)
        #: Value indicates the maximum number of layers allowed in an array texture, and must be at least 256
        self.MAX_ARRAY_TEXTURE_LAYERS = self.get(gl.GL_MAX_ARRAY_TEXTURE_LAYERS)
        #: A rough estimate of the largest 3D texture that the GL can handle. The value must be at least 64
        self.MAX_3D_TEXTURE_SIZE = self.get(gl.GL_MAX_3D_TEXTURE_SIZE)
        #: Maximum number of color attachments in a framebuffer
        self.MAX_COLOR_ATTACHMENTS = self.get(gl.GL_MAX_COLOR_ATTACHMENTS)
        #: Maximum number of samples in a color multisample texture
        self.MAX_COLOR_TEXTURE_SAMPLES = self.get(gl.GL_MAX_COLOR_TEXTURE_SAMPLES)
        #: the number of words for fragment shader uniform variables in all uniform blocks
        self.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS)
        #: Number of words for geometry shader uniform variables in all uniform blocks
        self.MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_COMBINED_GEOMETRY_UNIFORM_COMPONENTS)
        #: Maximum supported texture image units that can be used to access texture maps from the vertex shader
        self.MAX_COMBINED_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_COMBINED_TEXTURE_IMAGE_UNITS)
        #: Maximum number of uniform blocks per program
        self.MAX_COMBINED_UNIFORM_BLOCKS = self.get(gl.GL_MAX_COMBINED_UNIFORM_BLOCKS)
        #: Number of words for vertex shader uniform variables in all uniform blocks
        self.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS)
        #: A rough estimate of the largest cube-map texture that the GL can handle
        self.MAX_CUBE_MAP_TEXTURE_SIZE = self.get(gl.GL_MAX_CUBE_MAP_TEXTURE_SIZE)
        #: Maximum number of samples in a multisample depth or depth-stencil texture
        self.MAX_DEPTH_TEXTURE_SAMPLES = self.get(gl.GL_MAX_DEPTH_TEXTURE_SAMPLES)
        #: Maximum number of simultaneous outputs that may be written in a fragment shader
        self.MAX_DRAW_BUFFERS = self.get(gl.GL_MAX_DRAW_BUFFERS)
        #: Maximum number of active draw buffers when using dual-source blending
        self.MAX_DUAL_SOURCE_DRAW_BUFFERS = self.get(gl.GL_MAX_DUAL_SOURCE_DRAW_BUFFERS)
        #: Recommended maximum number of vertex array indices
        self.MAX_ELEMENTS_INDICES = self.get(gl.GL_MAX_ELEMENTS_INDICES)
        #: Recommended maximum number of vertex array vertices
        self.MAX_ELEMENTS_VERTICES = self.get(gl.GL_MAX_ELEMENTS_VERTICES)
        #: Maximum number of components of the inputs read by the fragment shader
        self.MAX_FRAGMENT_INPUT_COMPONENTS = self.get(gl.GL_MAX_FRAGMENT_INPUT_COMPONENTS)
        #: Maximum number of individual floating-point, integer, or boolean values that can be
        #: held in uniform variable storage for a fragment shader
        self.MAX_FRAGMENT_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_COMPONENTS)
        #: maximum number of individual 4-vectors of floating-point, integer,
        #: or boolean values that can be held in uniform variable storage for a fragment shader
        self.MAX_FRAGMENT_UNIFORM_VECTORS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_VECTORS)
        #: Maximum number of uniform blocks per fragment shader.
        self.MAX_FRAGMENT_UNIFORM_BLOCKS = self.get(gl.GL_MAX_FRAGMENT_UNIFORM_BLOCKS)
        #: Maximum number of components of inputs read by a geometry shader
        self.MAX_GEOMETRY_INPUT_COMPONENTS = self.get(gl.GL_MAX_GEOMETRY_INPUT_COMPONENTS)
        #: Maximum number of components of outputs written by a geometry shader
        self.MAX_GEOMETRY_OUTPUT_COMPONENTS = self.get(gl.GL_MAX_GEOMETRY_OUTPUT_COMPONENTS)
        #: Maximum supported texture image units that can be used to access texture maps from the geometry shader
        self.MAX_GEOMETRY_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_GEOMETRY_TEXTURE_IMAGE_UNITS)
        #: Maximum number of uniform blocks per geometry shader
        self.MAX_GEOMETRY_UNIFORM_BLOCKS = self.get(gl.GL_MAX_GEOMETRY_UNIFORM_BLOCKS)
        #: Maximum number of individual floating-point, integer, or boolean values that can
        #: be held in uniform variable storage for a geometry shader
        self.MAX_GEOMETRY_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_GEOMETRY_UNIFORM_COMPONENTS)
        #: Maximum number of samples supported in integer format multisample buffers
        self.MAX_INTEGER_SAMPLES = self.get(gl.GL_MAX_INTEGER_SAMPLES)
        #: Maximum samples for a framebuffer
        self.MAX_SAMPLES = self.get(gl.GL_MAX_SAMPLES)
        #: A rough estimate of the largest rectangular texture that the GL can handle
        self.MAX_RECTANGLE_TEXTURE_SIZE = self.get(gl.GL_MAX_RECTANGLE_TEXTURE_SIZE)
        #: Maximum supported size for renderbuffers
        self.MAX_RENDERBUFFER_SIZE = self.get(gl.GL_MAX_RENDERBUFFER_SIZE)
        #: Maximum number of sample mask words
        self.MAX_SAMPLE_MASK_WORDS = self.get(gl.GL_MAX_SAMPLE_MASK_WORDS)
        #: Maximum number of texels allowed in the texel array of a texture buffer object
        self.MAX_TEXTURE_BUFFER_SIZE = self.get(gl.GL_MAX_TEXTURE_BUFFER_SIZE)
        #: Maximum number of uniform buffer binding points on the context
        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        #: Maximum number of uniform buffer binding points on the context
        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        #: The value gives a rough estimate of the largest texture that the GL can handle
        self.MAX_TEXTURE_SIZE = self.get(gl.GL_MAX_TEXTURE_SIZE)
        #: Maximum number of uniform buffer binding points on the context
        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get(gl.GL_MAX_UNIFORM_BUFFER_BINDINGS)
        #: Maximum size in basic machine units of a uniform block
        self.MAX_UNIFORM_BLOCK_SIZE = self.get(gl.GL_MAX_UNIFORM_BLOCK_SIZE)
        #: The number 4-vectors for varying variables
        self.MAX_VARYING_VECTORS = self.get(gl.GL_MAX_VARYING_VECTORS)
        #: Maximum number of 4-component generic vertex attributes accessible to a vertex shader.
        self.MAX_VERTEX_ATTRIBS = self.get(gl.GL_MAX_VERTEX_ATTRIBS)
        #: Maximum supported texture image units that can be used to access texture maps from the vertex shader.
        self.MAX_VERTEX_TEXTURE_IMAGE_UNITS = self.get(gl.GL_MAX_VERTEX_TEXTURE_IMAGE_UNITS)
        #: Maximum number of individual floating-point, integer, or boolean values that
        #: can be held in uniform variable storage for a vertex shader
        self.MAX_VERTEX_UNIFORM_COMPONENTS = self.get(gl.GL_MAX_VERTEX_UNIFORM_COMPONENTS)
        #: Maximum number of 4-vectors that may be held in uniform variable storage for the vertex shader
        self.MAX_VERTEX_UNIFORM_VECTORS = self.get(gl.GL_MAX_VERTEX_UNIFORM_VECTORS)
        #: Maximum number of components of output written by a vertex shader
        self.MAX_VERTEX_OUTPUT_COMPONENTS = self.get(gl.GL_MAX_VERTEX_OUTPUT_COMPONENTS)
        #: Maximum number of uniform blocks per vertex shader.
        self.MAX_VERTEX_UNIFORM_BLOCKS = self.get(gl.GL_MAX_VERTEX_UNIFORM_BLOCKS)
        # self.MAX_VERTEX_ATTRIB_RELATIVE_OFFSET = self.get(gl.GL_MAX_VERTEX_ATTRIB_RELATIVE_OFFSET)
        # self.MAX_VERTEX_ATTRIB_BINDINGS = self.get(gl.GL_MAX_VERTEX_ATTRIB_BINDINGS)

        err = self._ctx.error
        if err:
            from warnings import warn
            warn('Error happened while querying of limits. Moving on ..')

    def get(self, enum: gl.GLenum):
        value = c_int()
        gl.glGetIntegerv(enum, value)
        return value.value


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
        self._window_ref = weakref.ref(window)
        self.limits = Limits(self)
        self._gl_version = (self.limits.MAJOR_VERSION, self.limits.MINOR_VERSION)

        # Tracking active program
        self.active_program = None  # type: Program
        # Tracking active program. On context creation the window is the default render target
        self.active_framebuffer = window
        self.stats = ContextStats(warn_threshold=1000)

        # --- Store the most commonly used OpenGL constants
        # Texture
        self.NEAREST = gl.GL_NEAREST
        self.LINEAR = gl.GL_LINEAR
        self.NEAREST_MIPMAP_NEAREST = gl.GL_NEAREST_MIPMAP_NEAREST
        self.LINEAR_MIPMAP_NEAREST = gl.GL_LINEAR_MIPMAP_NEAREST
        self.NEAREST_MIPMAP_LINEAR = gl.GL_NEAREST_MIPMAP_LINEAR
        self.LINEAR_MIPMAP_LINEAR = gl.GL_LINEAR_MIPMAP_LINEAR

        self.REPEAT = gl.GL_REPEAT
        self.CLAMP_TO_EDGE = gl.GL_CLAMP_TO_EDGE
        self.CLAMP_TO_BORDER = gl.GL_CLAMP_TO_BORDER
        self.MIRRORED_REPEAT = gl.GL_MIRRORED_REPEAT

        # VertexArray: Primitives
        self.POINTS = gl.GL_POINTS  # 0
        self.LINES = gl.GL_LINES  # 1
        self.LINE_STRIP = gl.GL_LINE_STRIP  # 3
        self.TRIANGLES = gl.GL_TRIANGLES  # 4
        self.TRIANGLE_STRIP = gl.GL_TRIANGLE_STRIP  # 5
        self.TRIANGLE_FAN = gl.GL_TRIANGLE_FAN  # 6
        self.LINES_ADJACENCY = gl.GL_LINES_ADJACENCY  # 10
        self.LINE_STRIP_ADJACENCY = gl.GL_LINE_STRIP_ADJACENCY  # 11
        self.TRIANGLES_ADJACENCY = gl.GL_TRIANGLES_ADJACENCY  # 12
        self.TRIANGLE_STRIP_ADJACENCY = gl.GL_TRIANGLE_STRIP_ADJACENCY  # 13

        # --- Pre-load system shaders here ---

        self.line_vertex_shader = self.load_program(
            vertex_shader=self.resource_root / 'shaders/line_vertex_shader_vs.glsl',
            fragment_shader=self.resource_root / 'shaders/line_vertex_shader_fs.glsl',
        )
        self.line_generic_with_colors_program = self.load_program(
            vertex_shader=self.resource_root / 'shaders/line_generic_with_colors_vs.glsl',
            fragment_shader=self.resource_root / 'shaders/line_generic_with_colors_fs.glsl',
        )
        self.shape_element_list_program = self.load_program(
            vertex_shader=self.resource_root / 'shaders/shape_element_list_vs.glsl',
            fragment_shader=self.resource_root / 'shaders/shape_element_list_fs.glsl',
        )
        self.sprite_list_program = self.load_program(
            vertex_shader=self.resource_root / 'shaders/sprite_list_vs.glsl',
            fragment_shader=self.resource_root / 'shaders/sprite_list_fs.glsl',
        )

        # Shapes
        self.shape_line_program = self.load_program(
            vertex_shader=":resources:/shaders/shapes/line_vs.glsl",
            fragment_shader=":resources:/shaders/shapes/line_fs.glsl",
            geometry_shader=":resources:/shaders/shapes/line_geo.glsl",
        )

        # --- Pre-created geometry and buffers for unbuffered draw calls ----
        # FIXME: This is a temporary test
        self.generic_draw_line_strip_color = self.buffer(reserve=4 * 1000)
        self.generic_draw_line_strip_vbo = self.buffer(reserve=8 * 1000)
        self.generic_draw_line_strip_geometry = self.geometry(
            [
                BufferDescription(
                    self.generic_draw_line_strip_vbo,
                    '2f',
                    ['in_vert']
                ),
                BufferDescription(
                    self.generic_draw_line_strip_color,
                    '4f1',
                    ['in_color'],
                    normalized=['in_color'],
                ),
            ]
        )

        # Shape line(s)
        # Reserve space for 1000 lines (2f pos, 4f color)
        self.shape_line_buffer_pos = self.buffer(reserve=8 * 10)
        self.shape_line_buffer_color = self.buffer(reserve=4 * 10)
        self.shape_line_geometry = self.geometry([
            BufferDescription(self.shape_line_buffer_pos, '2f', ['in_vert']),
            BufferDescription(self.shape_line_buffer_color, '4f1', ['in_color'], normalized=['in_color']),
        ])

    @property
    def window(self):
        """The window this context belongs to"""
        return self._window_ref()

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

    def buffer(self, *, data: bytes = None, reserve: int = 0, usage: str = 'static') -> Buffer:
        """Create a new OpenGL Buffer object.

        :param bytes data: The buffer data
        :param int reserve: The number of bytes reserve
        :param str usage: Buffer usage. 'static', 'dynamic' or 'stream'
        """
        # create_with_size
        return Buffer(self, data, reserve=reserve, usage=usage)

    def framebuffer(
            self,
            *,
            color_attachments: Union[Texture, List[Texture]] = None,
            depth_attachment: Texture = None) -> Framebuffer:
        """Create a Framebuffer.

        :param List[Texture] color_attachments: List of textures we want to render into
        :param Texture depth_attachment: Depth texture
        """
        return Framebuffer(self, color_attachments=color_attachments, depth_attachment=depth_attachment)

    def texture(self,
                size: Tuple[int, int],
                *,
                components: int = 4,
                dtype: str = 'f1',
                data: bytes = None,
                wrap_x: gl.GLenum = None,
                wrap_y: gl.GLenum = None,
                filter: Tuple[gl.GLenum, gl.GLenum] = None) -> Texture:
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
        :param Tuple[GLenum, GLenum] filter: Minification and magnification filter
        """
        return Texture(self, size, components=components, data=data, dtype=dtype,
                       wrap_x=wrap_x, wrap_y=wrap_y,
                       filter=filter)

    # def vertex_array(self, prog: gl.GLuint, content, index_buffer=None):
    #     """Create a new Vertex Array.
    #     """
    #     return VertexArray(self, prog, content, index_buffer)

    def geometry(self, content, index_buffer=None):
        return Geometry(self, content, index_buffer=index_buffer)

    def program(
            self,
            *,
            vertex_shader: str,
            fragment_shader: str = None,
            geometry_shader: str = None,
            defines: Dict[str, str] = None) -> Program:
        """Create a new program given the vertex_shader and fragment shader code.

        :param str vertex_shader: vertex shader source
        :param str fragment_shader: fragment shader source
        :param str geometry_shader: geometry shader source
        :param dict defines: Substitute #defines values in the source
        """
        source_vs = ShaderSource(vertex_shader, gl.GL_VERTEX_SHADER)
        source_fs = ShaderSource(fragment_shader, gl.GL_FRAGMENT_SHADER) if fragment_shader else None
        source_geo = ShaderSource(geometry_shader, gl.GL_GEOMETRY_SHADER) if geometry_shader else None

        # If we don't have a fragment shader we are doing transform feedback.
        # When a geometry shader is present the out attributes will be located there
        out_attributes = []  # type: List[str]
        if not source_fs:
            if source_geo:
                out_attributes = source_geo.out_attributes
            else:
                out_attributes = source_vs.out_attributes

        return Program(
            self,
            vertex_shader=source_vs.get_source(defines=defines),
            fragment_shader=source_fs.get_source(defines=defines) if source_fs else None,
            geometry_shader=source_geo.get_source(defines=defines) if source_geo else None,
            out_attributes=out_attributes,
        )

    def load_program(
            self,
            *,
            vertex_shader: Union[str, Path],
            fragment_shader: Union[str, Path] = None,
            geometry_shader: Union[str, Path] = None,
            defines: dict = None) -> Program:
        """ Create a new program given a file names that contain the vertex shader and
        fragment shader.

        :param Union[str, Path] vertex_shader: path to vertex shader
        :param Union[str, Path] fragment_shader: path to fragment shader
        :param Union[str, Path] geometry_shader: path to geometry shader
        :param dict defines: Substitute #defines values in the source
        """
        from arcade import resources

        # TODO: Cache these files using absolute path as key
        vertex_shader_src = resources.resolve_resource_path(vertex_shader).read_text()
        fragment_shader_src = None
        geometry_shader_src = None

        if fragment_shader:
            fragment_shader_src = resources.resolve_resource_path(fragment_shader).read_text()

        if geometry_shader:
            geometry_shader_src = resources.resolve_resource_path(geometry_shader).read_text()

        return self.program(
            vertex_shader=vertex_shader_src,
            fragment_shader=fragment_shader_src,
            geometry_shader=geometry_shader_src,
            defines=defines,
        )


class ShaderSource:
    """
    GLSL source container for making source parsing simpler.
    We support locating out attributes and applying #defines values.

    This wrapper should ideally contain an unmodified version
    of the original source for caching. Getting the specific
    source with defines applied through ``get_source``.

    NOTE: We do assume the source is neat enough to be parsed
    this way and don't contain several statements on one line.
    """
    def __init__(self, source: str, source_type: gl.GLenum):
        """Create a shader source wrapper.

        :param str source: The shader source
        :param gl.GLenum: The shader type (vertex, fragment, geometry etc)
        """
        self._source = source.strip()
        self._type = source_type
        self._lines = self._source.split('\n')
        self._out_attributes = []  # type: List[str]

        self._version = self._find_glsl_version()

        if self._type in [gl.GL_VERTEX_SHADER, gl.GL_FRAGMENT_SHADER]:
            self._parse_out_attributes()

    @property
    def version(self) -> int:
        """The glsl version"""
        return self._version

    @property
    def out_attributes(self) -> List[str]:
        """The out attributes for this program"""
        return self._out_attributes

    def get_source(self, *, defines: Dict[str, str] = None) -> str:
        """Return the shader source

        :param dict defines: Defines to replace in the source.
        """
        if not defines:
            return self._source

        lines = ShaderSource.apply_defines(self._lines, defines)
        return '\n'.join(lines)

    def _find_glsl_version(self) -> int:
        for line in self._lines:
            if line.strip().startswith('#version'):
                try:
                    return int(line.split()[1])
                except:
                    pass

        raise ShaderException((
            "Cannot find #version in shader source. "
            "Please provide at least a #version 330 statement in the beginning of the shader"
        ))

    @staticmethod
    def apply_defines(lines: List[str], defines: Dict[str, str]) -> List[str]:
        """Locate and apply #define values

        :param List[str] lines: List of source lines
        :param dict defines: dict with ``name: value`` pairs.
        """
        for nr, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#define'):
                try:
                    name = line.split()[1]
                    value = defines.get(name)
                    if not value:
                        continue

                    lines[nr] = "#define {} {}".format(name, str(value))
                except IndexError:
                    pass

        return lines

    def _parse_out_attributes(self):
        """Locates """
        for line in self._lines:
            if line.strip().startswith("out "):
                self._out_attributes.append(line.split()[2].replace(';', ''))


class ContextStats:

    def __init__(self, warn_threshold=100):
        self.warn_threshold = warn_threshold
        # (created, freed)
        self.texture = (0, 0)
        self.framebuffer = (0, 0)
        self.buffer = (0, 0)
        self.program = (0, 0)
        self.vertex_array = (0, 0)
        self.geometry = (0, 0)

    def incr(self, key):
        created, freed = getattr(self, key)
        setattr(self, key, (created + 1, freed))
        if created % self.warn_threshold == 0 and created > 0:
            from warnings import warn
            warn((
                f'{key} allocations passed threshold ({self.warn_threshold}). '
                f'created = {created}, freed = {freed} = {created - freed} active.'
            ))

    def decr(self, key):
        created, freed = getattr(self, key)
        setattr(self, key, (created, freed + 1))
