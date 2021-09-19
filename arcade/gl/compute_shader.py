from typing import TYPE_CHECKING
from ctypes import c_char, cast, byref, POINTER, c_char_p, pointer, c_int, create_string_buffer, c_buffer

from pyglet import gl
from arcade.gl import ShaderException


if TYPE_CHECKING:
    from arcade.gl import Context


class ComputeShader:
    """
    Represent an OpenGL compute shader
    """

    def __init__(self, ctx: "Context", glsl_source: str) -> None:
        self._ctx = ctx
        self._source = glsl_source
        self._members = {}

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

        # Introspection
        # Uniforms
        # UniformBlock

    @property
    def glo(self) -> int:
        return self._glo

    def run(self, group_x=1, group_y=1, group_z=1) -> None:
        """
        Run the compute shader.

        :param int group_x: The number of work groups to be launched in the X dimension.
        :param int group_y: The number of work groups to be launched in the y dimension.
        :param int group_z: The number of work groups to be launched in the z dimension.
        """
        gl.glUseProgram(self._glo)
        gl.glDispatchCompute(group_x, group_y, group_z)

    def __getitem__(self, key):
        # Get members here
        pass

    def __setitem__(self, key, value):
        # Set member values here
        pass

    def __hash__(self) -> int:
        return id(self)

    def __del__(self):
        # Delete opengl resource
        pass
