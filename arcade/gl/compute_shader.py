from typing import TYPE_CHECKING, Dict, Tuple, Union
from ctypes import c_char, cast, byref, POINTER, c_char_p, pointer, c_int, create_string_buffer, c_buffer

from pyglet import gl
from .uniform import Uniform, UniformBlock

if TYPE_CHECKING:
    from arcade.gl import Context


class ComputeShader:
    """
    Represent an OpenGL compute shader
    """

    def __init__(self, ctx: "Context", glsl_source: str) -> None:
        self._ctx = ctx
        self._source = glsl_source
        self._uniforms: Dict[str, Uniform] = dict()
        self._uniform_blocks: Dict[str, UniformBlock] = dict()

        from arcade.gl import ShaderException

        # Create the program
        self._glo = gl.glCreateProgram()
        if not self._glo:
            raise ShaderException("Failed to create program object")

        self._shader_obj = gl.glCreateShader(gl.GL_COMPUTE_SHADER)
        if not self._shader_obj:
            raise ShaderException("Failed to create compute shader object")

        # Set source
        source_bytes = self._source.encode("utf-8")
        strings = byref(cast(c_char_p(source_bytes), POINTER(c_char)))
        lengths = pointer(c_int(len(source_bytes)))
        gl.glShaderSource(self._shader_obj, 1, strings, lengths)

        # Compile and check result
        gl.glCompileShader(self._shader_obj)
        result = c_int()
        gl.glGetShaderiv(self._shader_obj, gl.GL_COMPILE_STATUS, byref(result))
        if result.value == gl.GL_FALSE:
            msg = create_string_buffer(512)
            length = c_int()
            gl.glGetShaderInfoLog(self._shader_obj, 512, byref(length), msg)
            raise ShaderException(
                (
                    f"Error compiling compute shader "
                    f"({result.value}): {msg.value.decode('utf-8')}\n"
                    f"---- [compute shader] ---\n"
                )
                + "\n".join(
                    f"{str(i+1).zfill(3)}: {line} "
                    for i, line in enumerate(self._source.split("\n"))
                )
            )

        # Attach and link shader
        gl.glAttachShader(self._glo, self._shader_obj)
        gl.glLinkProgram(self._glo)
        status = c_int()
        gl.glGetProgramiv(self._glo, gl.GL_LINK_STATUS, status)
        if not status.value:
            length = c_int()
            gl.glGetProgramiv(self._glo, gl.GL_INFO_LOG_LENGTH, length)
            log = c_buffer(length.value)
            gl.glGetProgramInfoLog(self._glo, len(log), None, log)
            raise ShaderException("Program link error: {}".format(log.value.decode()))        

        self._introspect_uniforms()
        self._introspect_uniform_blocks()

    @property
    def glo(self) -> int:
        return self._glo

    def use(self):
        gl.glUseProgram(self._glo)
        self._ctx.active_program = self

    def run(self, group_x=1, group_y=1, group_z=1) -> None:
        """
        Run the compute shader.

        :param int group_x: The number of work groups to be launched in the X dimension.
        :param int group_y: The number of work groups to be launched in the y dimension.
        :param int group_z: The number of work groups to be launched in the z dimension.
        """
        self.use()        
        gl.glDispatchCompute(group_x, group_y, group_z)

    def __getitem__(self, item) -> Union[Uniform, UniformBlock]:
        """Get a uniform or uniform block"""
        try:
            uniform = self._uniforms[item]
        except KeyError:
            raise KeyError(f"Uniform with the name `{item}` was not found.")

        return uniform.getter()

    def __setitem__(self, key, value):
        """Set a uniform value"""
        # Ensure we are setting the uniform on this program
        if self._ctx.active_program != self:
            self.use()

        try:
            uniform = self._uniforms[key]
        except KeyError:
            raise KeyError(f"Uniform with the name `{key}` was not found.")

        uniform.setter(value)

    def __hash__(self) -> int:
        return id(self)

    def __del__(self):
        # Delete opengl resource
        pass

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

            u_name = u_name.replace("[0]", "")  # Remove array suffix
            self._uniforms[u_name] = Uniform(
                self._glo, u_location, u_name, u_type, u_size
            )

    def _introspect_uniform_blocks(self):
        active_uniform_blocks = gl.GLint(0)
        gl.glGetProgramiv(
            self._glo, gl.GL_ACTIVE_UNIFORM_BLOCKS, byref(active_uniform_blocks)
        )
        # print('GL_ACTIVE_UNIFORM_BLOCKS', active_uniform_blocks)

        for loc in range(active_uniform_blocks.value):
            index, size, name = self._query_uniform_block(loc)
            block = UniformBlock(self._glo, index, size, name)
            self._uniforms[name] = block

    def _query_uniform(self, location: int) -> Tuple[str, int, int]:
        """Retrieve Uniform information at given location.

        Returns the name, the type as a GLenum (GL_FLOAT, ...) and the size. Size is
        greater than 1 only for Uniform arrays, like an array of floats or an array
        of Matrices.
        """
        u_size = gl.GLint()
        u_type = gl.GLenum()
        buf_size = 192  # max uniform character length
        u_name = create_string_buffer(buf_size)
        gl.glGetActiveUniform(
            self._glo,  # program to query
            location,  # location to query
            buf_size,  # size of the character/name buffer
            None,  # the number of characters actually written by OpenGL in the string
            u_size,  # size of the uniform variable
            u_type,  # data type of the uniform variable
            u_name,  # string buffer for storing the name
        )
        return u_name.value.decode(), u_type.value, u_size.value
