"""Utilities for dealing with Shaders in OpenGL 3.3+.
"""

from ctypes import *
from collections import namedtuple
import weakref
from typing import List, Tuple, Iterable, Dict

from pyglet import gl


class ShaderException(Exception):
    pass


# Thank you Benjamin Moran for writing part of this code!
# https://bitbucket.org/HigashiNoKaze/pyglet/src/shaders/pyglet/graphics/shader.py

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
        def setter_func(value):  # type: ignore #conditional function variants must have identical signature
            c_array[:] = value
            gl_setter(location, count, gl.GL_FALSE, ptr)

    elif length == 1 and count == 1:
        def setter_func(value):  # type: ignore #conditional function variants must have identical signature
            c_array[0] = value
            gl_setter(location, count, ptr)
    elif length > 1 and count == 1:
        def setter_func(values):  # type: ignore #conditional function variants must have identical signature
            c_array[:] = values
            gl_setter(location, count, ptr)

    else:
        raise NotImplementedError("Uniform type not yet supported.")

    return setter_func


Uniform = namedtuple('Uniform', 'getter, setter')
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
    active = None  # Keeps track of the active program

    def __init__(self, *shaders: Shader):
        self.prog_id = prog_id = gl.glCreateProgram()
        shaders_id = []
        for shader_code, shader_type in shaders:
            shader = compile_shader(shader_code, shader_type)
            gl.glAttachShader(self.prog_id, shader)
            shaders_id.append(shader)

        gl.glLinkProgram(self.prog_id)

        for shader in shaders_id:
            # Flag shaders for deletion. Will only be deleted once detached from program.
            gl.glDeleteShader(shader)

        self._uniforms: Dict[str, Uniform] = {}
        self._introspect_uniforms()
        weakref.finalize(self, Program._delete, shaders_id, prog_id)

    @staticmethod
    def _delete(shaders_id, prog_id):
        # Check to see if the context was already cleaned up from program
        # shut down. If so, we don't need to delete the shaders.
        if gl.current_context is None:
            return

        for shader_id in shaders_id:
            gl.glDetachShader(prog_id, shader_id)

        gl.glDeleteProgram(prog_id)

    def release(self):
        if self.prog_id != 0:
            gl.glDeleteProgram(self.prog_id)
            self.prog_id = 0

    def __getitem__(self, item):
        try:
            uniform = self._uniforms[item]
        except KeyError:
            raise ShaderException(f"Uniform with the name `{item}` was not found.")

        return uniform.getter()

    def __setitem__(self, key, value):
        # Ensure we are setting the uniform on this program
        if Program.active != self:
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
        if Program.active != self:
            gl.glUseProgram(self.prog_id)
            Program.active = self

    def get_num_active(self, variable_type: gl.GLenum) -> int:
        """Get the number of active variables of the passed GL type.

        variable_type can be GL_ACTIVE_ATTRIBUTES, GL_ACTIVE_UNIFORMS, etc.
        """
        num_active = gl.GLint(0)
        gl.glGetProgramiv(self.prog_id, variable_type, byref(num_active))
        return num_active.value

    def _introspect_uniforms(self):
        for index in range(self.get_num_active(gl.GL_ACTIVE_UNIFORMS)):
            uniform_name, u_type, u_size = self.query_uniform(index)
            loc = gl.glGetUniformLocation(self.prog_id, uniform_name.encode('utf-8'))

            if loc == -1:      # Skip uniforms that may be in Uniform Blocks
                continue

            try:
                gl_type, gl_setter, length, count = _uniform_setters[u_type]
            except KeyError:
                raise ShaderException(f"Unsupported Uniform type {u_type}")

            gl_getter = _uniform_getters[gl_type]

            is_matrix = u_type in (gl.GL_FLOAT_MAT2, gl.GL_FLOAT_MAT3, gl.GL_FLOAT_MAT4)

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
        usize = gl.GLint()
        utype = gl.GLenum()
        buf_size = 192
        uname = create_string_buffer(buf_size)
        gl.glGetActiveUniform(self.prog_id, index, buf_size, None, usize, utype, uname)
        return uname.value.decode(), utype.value, usize.value


def program(vertex_shader: str, fragment_shader: str) -> Program:
    """Create a new program given the vertex_shader and fragment shader code.
    """
    return Program(
        (vertex_shader, gl.GL_VERTEX_SHADER),
        (fragment_shader, gl.GL_FRAGMENT_SHADER)
    )


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


class Buffer:
    """OpenGL Buffer object of type GL_ARRAY_BUFFER.

    Apparently it's possible to initialize a GL_ELEMENT_ARRAY_BUFFER with
    GL_ARRAY_BUFFER, provided we later on bind to it with the right type.

    The buffer knows its id `buffer_id` and its `size` in bytes.
    """
    usages = {
        'static': gl.GL_STATIC_DRAW,
        'dynamic': gl.GL_DYNAMIC_DRAW,
        'stream': gl.GL_STREAM_DRAW
    }

    def __init__(self, data: bytes, usage: str = 'static'):
        self.buffer_id = buffer_id = gl.GLuint()
        self.size = len(data)

        gl.glGenBuffers(1, byref(self.buffer_id))
        if self.buffer_id.value == 0:
            raise ShaderException("Cannot create Buffer object.")

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer_id)
        self.usage = Buffer.usages[usage]
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.size, data, self.usage)
        weakref.finalize(self, Buffer.release, buffer_id)

    @classmethod
    def create_with_size(cls, size: int, usage: str = 'static'):
        """Create an empty Buffer storage of the given size."""
        empty_buffer = Buffer(b"", usage=usage)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, empty_buffer.buffer_id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, size, None, Buffer.usages[usage])
        empty_buffer.size = size
        return empty_buffer

    @staticmethod
    def release(buffer_id):

        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if buffer_id.value != 0:
            gl.glDeleteBuffers(1, byref(buffer_id))
            buffer_id.value = 0

    def write(self, data: bytes, offset: int = 0):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer_id)
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, gl.GLintptr(offset), len(data), data)
        # print(f"Writing data:\n{data[:60]}")
        # ptr = glMapBufferRange(gl.GL_ARRAY_BUFFER, gl.GLintptr(0), 20, GL_MAP_READ_BIT)
        # print(f"Reading back from buffer:\n{string_at(ptr, size=60)}")
        # glUnmapBuffer(gl.GL_ARRAY_BUFFER)

    def orphan(self):
        """
        Re-allocate the entire buffer memory.
        If the current buffer is busy in redering operations
        it will be deallocated by OpenGL when completed.
        """
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer_id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, self.size, None, self.usage)

    def _read(self, size):
        """ Debug method to read data from the buffer. """

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.buffer_id)
        ptr = gl.glMapBufferRange(gl.GL_ARRAY_BUFFER, gl.GLintptr(0), size, gl.GL_MAP_READ_BIT)
        print(f"Reading back from buffer:\n{string_at(ptr, size=size)}")
        gl.glUnmapBuffer(gl.GL_ARRAY_BUFFER)


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

    def __init__(self,
                 prog: Program,
                 content: Iterable[BufferDescription],
                 index_buffer: Buffer = None):
        self.program = prog
        self.vao = vao = gl.GLuint()
        self.num_vertices = -1
        self.ibo = index_buffer

        gl.glGenVertexArrays(1, byref(self.vao))
        gl.glBindVertexArray(self.vao)

        for buffer_desc in content:
            self._enable_attrib(buffer_desc)

        if self.ibo is not None:
            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ibo.buffer_id)
        weakref.finalize(self, VertexArray.release, vao)

    @staticmethod
    def release(vao):
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if vao.value != 0:
            gl.glDeleteVertexArrays(1, byref(vao))
            vao.value = 0

    def _enable_attrib(self, buf_desc: BufferDescription):
        buff = buf_desc.buffer
        stride = sum(attribsize for _, attribsize, _ in buf_desc.formats)

        if buf_desc.instanced:
            if self.num_vertices == -1:
                raise ShaderException(
                    "The first vertex attribute cannot be a per instance attribute."
                )
        else:
            self.num_vertices = max(self.num_vertices, buff.size // stride)
            # print(f"Number of vertices: {self.num_vertices}")

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buff.buffer_id)
        offset = 0
        for (size, attribsize, gl_type_enum), attrib in zip(buf_desc.formats, buf_desc.attributes):
            loc = gl.glGetAttribLocation(self.program.prog_id, attrib.encode('utf-8'))
            if loc == -1:
                raise ShaderException(f"Attribute {attrib} not found in shader program")
            normalized = gl.GL_TRUE if attrib in buf_desc.normalized else gl.GL_FALSE
            gl.glVertexAttribPointer(
                loc, size, gl_type_enum,
                normalized, stride, c_void_p(offset)
            )
            # print(f"{attrib} of size {size} with stride {stride} and offset {offset}")
            if buf_desc.instanced:
                gl.glVertexAttribDivisor(loc, 1)
            offset += attribsize
            gl.glEnableVertexAttribArray(loc)

    def render(self, mode: gl.GLuint, instances: int = 1):
        gl.glBindVertexArray(self.vao)
        self.program.use()
        if self.ibo is not None:
            count = self.ibo.size // 4
            gl.glDrawElementsInstanced(mode, count, gl.GL_UNSIGNED_INT, None, instances)
        else:
            gl.glDrawArraysInstanced(mode, 0, self.num_vertices, instances)


def vertex_array(prog: gl.GLuint, content, index_buffer=None):
    """Create a new Vertex Array.
    """
    return VertexArray(prog, content, index_buffer)


class Texture:
    def __init__(self, size: Tuple[int, int], components: int, data=None):
        """Represents an OpenGL texture.

        A texture can be created with or without initial data.
        NOTE: Currently do notsupport multisample textures even
        thought ``samples`` is exposed.
        
        :param Tuple[int, int] size: The size of the texture.
        :param int components: The number of components (1: R, 2: RG, 3: RGB, 4: RGBA).
        :param data: The texture data (optional)
        """
        self.width, self.height = size
        self._components = components

        sized_format = (gl.GL_R8, gl.GL_RG8, gl.GL_RGB8, gl.GL_RGBA8)[components - 1]
        self.format = (gl.GL_R, gl.GL_RG, gl.GL_RGB, gl.GL_RGBA)[components - 1]
        gl.glActiveTexture(gl.GL_TEXTURE0)  # Create textures in the default channel (0)

        self.texture_id = texture_id = gl.GLuint()
        gl.glGenTextures(1, byref(self.texture_id))

        if self.texture_id.value == 0:
            raise ShaderException("Cannot create Texture.")

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        try:
            gl.glTexImage2D(
                gl.GL_TEXTURE_2D, 0, sized_format, self.width, self.height, 0,
                self.format, gl.GL_UNSIGNED_BYTE, data
            )
        except gl.GLException:
            raise gl.GLException(f"Unable to create texture. {gl.GL_MAX_TEXTURE_SIZE} {size}")

        self.filter = gl.GL_LINEAR, gl.GL_LINEAR
        weakref.finalize(self, Texture.release, texture_id)

    @property
    def glo(self) -> gl.GLuint:
        """The opengl texture id"""
        return self.texture_id

    @property
    def size(self) -> Tuple[int, int]:
        """The size of the texture as a tuple"""
        return self.width, self.height

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
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, self._filter[0])
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, self._filter[1])

    def build_mipmaps(self, base=0, max=1000):
        """Generate mipmaps for this texture.
        Also see: https://www.khronos.org/opengl/wiki/Texture#Mip_maps
        """
        self.use()
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BASE_LEVEL, base)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAX_LEVEL, max)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    @staticmethod
    def release(texture_id):
        """Destroy the texture"""
        # If we have no context, then we are shutting down, so skip this
        if gl.current_context is None:
            return

        if texture_id.value != 0:
            gl.glDeleteTextures(1, byref(texture_id))

    def use(self, unit: int = 0):
        """Bind the texture to a channel,

        :param int unit: The texture unit to bind the texture.
        """
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)

    def __repr__(self):
        return "<Texture glo={} size={}x{} components={}>".format(
            self.texture_id.value, self.width, self.height, self._components)


def texture(size: Tuple[int, int], components: int, data=None) -> Texture:
    """Create a Texture.

    :param Tuple[int, int] size: The size of the texture
    :param int components: Number of components (1: R, 2: RG, 3: RGB, 4: RGBA)
    :param buffer data: The texture data (optional)
    """
    return Texture(size, components, data)


class Framebuffer:
    """
    An offscreen render target also called a Framebuffer Object in OpenGL.
    This implementation is using texture attachments. When createing a
    Framebuffer we supply it with textures we want our scene rendered into.
    """
    active = None  # The framebuffer that is bound currently

    def __init__(self, color_attachments=None, depth_attachment=None):
        """Create a framebuffer.

        :param List[Texture] color_attachments: List of color attachments.
        :param Texture depth_attachment: A depth attachment (optional)
        """
        self._color_attachments = color_attachments
        self._depth_attachment = depth_attachment
        self._glo = gl.GLuint()  # The OpenGL alias/name
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
        self._check_completness()

        # Set up draw buffers. This is simply a prepared list of attachments enums
        # we use in the use() method to activate the different color attachment layers
        layers = [gl.GL_COLOR_ATTACHMENT0 + i for i, _ in enumerate(self._color_attachments)]
        # pyglet wants this as a ctypes thingy, so let's prepare it
        self._draw_buffers = (c_ulong * len(layers))(*layers)

        # Fall back to window
        Framebuffer.active.use()

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
        if Framebuffer.active == self:
             gl.glViewport(*self._viewport)

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
        if Framebuffer.active == self:
            gl.glDepthMask(self._depth_mask)

    def use(self):
        """Bind the framebuffer making it the target of all redering commands"""
        # Don't bind the same framebuffer multiple times
        self._use()
        Framebuffer.active = self

    def _use(self):
        """Internal use that do not change the global active framebuffer"""
        if Framebuffer.active == self:
            return

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._glo)
        # Note: gl.glDrawBuffer(GL_NONE) if no texture attachments (future)
        gl.glDrawBuffers(len(self._draw_buffers), self._draw_buffers)
        gl.glDepthMask(self._depth_mask)
        gl.glViewport(*self._viewport)

    def clear(self, color=(0.0, 0.0, 0.0, 0.0), depth=1.0):
        """Clears the framebuffer. This will also activate/use it"""
        self._use()
        gl.glClearColor(*color)
        if self.depth_attachment:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # Ensure we don't change framebuffer unless it's already activated
        Framebuffer.active.use()

    def release(self, release_attachments=False):
        """Destroys the framebuffer object
        
        :param bool release_attachments: Also release the attachments
        """
        if gl.current_context is None:
            return

        gl.glDeleteFramebuffers(1, self._glo)
        if release_attachments:
            for tex in self._color_attachments:
                tex.release()
            if self._depth_attachment:
                self._depth_attachment.release()

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

    def _check_completness(self):
        """
        Checks the completness of the framebuffer.
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


def framebuffer(color_attachments: List[Texture]=None, depth_attachment: Texture=None) -> Texture:
    """Create a Framebuffer.

    :param List[Texture] color_attachments: List of textures we want to render into 
    :param Texture depth_attachment: Depth texture
    """
    return Framebuffer(color_attachments, depth_attachment)
