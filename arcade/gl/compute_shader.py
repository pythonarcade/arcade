from __future__ import annotations

import weakref
from ctypes import (
    POINTER,
    byref,
    c_buffer,
    c_char,
    c_char_p,
    c_int,
    cast,
    create_string_buffer,
    pointer,
)
from typing import TYPE_CHECKING

from pyglet import gl

from .uniform import Uniform, UniformBlock

if TYPE_CHECKING:
    from arcade.gl import Context


class ComputeShader:
    """
    A higher level wrapper for an OpenGL compute shader.

    Args:
        ctx:
            The context this shader belongs to.
        glsl_source:
            The GLSL source code for the compute shader.
    """

    def __init__(self, ctx: Context, glsl_source: str) -> None:
        self._ctx = ctx
        self._source = glsl_source
        self._uniforms: dict[str, UniformBlock | Uniform] = dict()

        from arcade.gl import ShaderException

        # Create the program
        self._glo = glo = gl.glCreateProgram()
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
                    f"{str(i + 1).zfill(3)}: {line} "
                    for i, line in enumerate(self._source.split("\n"))
                )
            )

        # Attach and link shader
        gl.glAttachShader(self._glo, self._shader_obj)
        gl.glLinkProgram(self._glo)
        gl.glDeleteShader(self._shader_obj)
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

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, ComputeShader.delete_glo, self._ctx, glo)

        ctx.stats.incr("compute_shader")

    @property
    def glo(self) -> int:
        """The name/id of the OpenGL resource"""
        return self._glo

    def _use(self) -> None:
        """
        Use/activate the compute shader.

        .. Note::

            This is not necessary to call in normal use cases
            since ``run()`` already does this for you.
        """
        gl.glUseProgram(self._glo)
        self._ctx.active_program = self

    def run(self, group_x=1, group_y=1, group_z=1) -> None:
        """
        Run the compute shader.

        When running a compute shader we specify how many work groups should
        be executed on the ``x``, ``y`` and ``z`` dimension. The size of the work group
        is defined in the compute shader.

        .. code:: glsl

            // Work group with one dimension. 16 work groups executed.
            layout(local_size_x=16) in;
            // Work group with two dimensions. 256 work groups executed.
            layout(local_size_x=16, local_size_y=16) in;
            // Work group with three dimensions. 4096 work groups executed.
            layout(local_size_x=16, local_size_y=16, local_size_z=16) in;

        Group sizes are ``1`` by default. If your compute shader doesn't specify
        a size for a dimension or uses ``1`` as size you don't have to supply
        this parameter.

        Args:
            group_x: The number of work groups to be launched in the X dimension.
            group_y: The number of work groups to be launched in the y dimension.
            group_z: The number of work groups to be launched in the z dimension.
        """
        self._use()
        gl.glDispatchCompute(group_x, group_y, group_z)

    def __getitem__(self, item) -> Uniform | UniformBlock:
        """Get a uniform or uniform block"""
        try:
            uniform = self._uniforms[item]
        except KeyError:
            raise KeyError(f"Uniform with the name `{item}` was not found.")

        return uniform.getter()

    def __setitem__(self, key, value):
        """Set a uniform value"""
        # Ensure we are setting the uniform on this program
        # if self._ctx.active_program != self:
        #     self.use()

        try:
            uniform = self._uniforms[key]
        except KeyError:
            raise KeyError(f"Uniform with the name `{key}` was not found.")

        uniform.setter(value)

    def __hash__(self) -> int:
        return id(self)

    def __del__(self):
        if self._ctx.gc_mode == "context_gc" and self._glo > 0:
            self._ctx.objects.append(self)

    def delete(self) -> None:
        """
        Destroy the internal compute shader object.

        This is normally not necessary, but depends on the
        garbage collection configured in the context.
        """
        ComputeShader.delete_glo(self._ctx, self._glo)
        self._glo = 0

    @staticmethod
    def delete_glo(ctx, prog_id):
        """
        Low level method for destroying a compute shader by id.

        Args:
            ctx: The context this program belongs to.
            prog_id: The OpenGL id of the program.
        """
        # Check to see if the context was already cleaned up from program
        # shut down. If so, we don't need to delete the shaders.
        if gl.current_context is None:
            return

        gl.glDeleteProgram(prog_id)
        # TODO: Count compute shaders
        ctx.stats.decr("compute_shader")

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
                self._ctx, self._glo, u_location, u_name, u_type, u_size
            )

    def _introspect_uniform_blocks(self):
        """Finds uniform blocks and maps the to python objectss"""
        active_uniform_blocks = gl.GLint(0)
        gl.glGetProgramiv(self._glo, gl.GL_ACTIVE_UNIFORM_BLOCKS, byref(active_uniform_blocks))
        # print('GL_ACTIVE_UNIFORM_BLOCKS', active_uniform_blocks)

        for loc in range(active_uniform_blocks.value):
            index, size, name = self._query_uniform_block(loc)
            block = UniformBlock(self._glo, index, size, name)
            self._uniforms[name] = block

    def _query_uniform(self, location: int) -> tuple[str, int, int]:
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

    def _query_uniform_block(self, location: int) -> tuple[int, int, str]:
        """Query active uniform block by retrieving the name and index and size"""
        # Query name
        u_size = gl.GLint()
        buf_size = 192  # max uniform character length
        u_name = create_string_buffer(buf_size)
        gl.glGetActiveUniformBlockName(
            self._glo,  # program to query
            location,  # location to query
            256,  # max size if the name
            u_size,  # length
            u_name,
        )
        # Query index
        index = gl.glGetUniformBlockIndex(self._glo, u_name)
        # Query size
        b_size = gl.GLint()
        gl.glGetActiveUniformBlockiv(self._glo, index, gl.GL_UNIFORM_BLOCK_DATA_SIZE, b_size)
        return index, b_size.value, u_name.value.decode()
