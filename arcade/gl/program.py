import typing
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
from typing import TYPE_CHECKING, Any, Iterable

from pyglet import gl

from .exceptions import ShaderException
from .types import SHADER_TYPE_NAMES, AttribFormat, GLTypes, PyGLenum
from .uniform import Uniform, UniformBlock

if TYPE_CHECKING:
    from arcade.gl import Context


class Program:
    """
    Compiled and linked shader program.

    Currently supports

    - vertex shader
    - fragment shader
    - geometry shader
    - tessellation control shader
    - tessellation evaluation shader

    Transform feedback also supported when output attributes
    names are passed in the varyings parameter.

    The best way to create a program instance is through :py:meth:`arcade.gl.Context.program`

    Args:
        ctx:
            The context this program belongs to
        vertex_shader:
            Vertex shader source
        fragment_shader:
            Fragment shader source
        geometry_shader:
            Geometry shader source
        tess_control_shader:
            Tessellation control shader source
        tess_evaluation_shader:
            Tessellation evaluation shader source
        varyings:
            List of out attributes used in transform feedback.
        varyings_capture_mode:
            The capture mode for transforms.
            ``"interleaved"`` means all out attribute will be written to a single buffer.
            ``"separate"`` means each out attribute will be written separate buffers.
            Based on these settings the `transform()` method will accept a single
            buffer or a list of buffer.
    """

    __slots__ = (
        "_ctx",
        "_glo",
        "_uniforms",
        "_varyings",
        "_varyings_capture_mode",
        "_geometry_info",
        "_attributes",
        "attribute_key",
        "__weakref__",
    )

    _valid_capture_modes = ("interleaved", "separate")

    def __init__(
        self,
        ctx: "Context",
        *,
        vertex_shader: str,
        fragment_shader: str | None = None,
        geometry_shader: str | None = None,
        tess_control_shader: str | None = None,
        tess_evaluation_shader: str | None = None,
        varyings: list[str] | None = None,
        varyings_capture_mode: str = "interleaved",
    ):
        self._ctx = ctx
        self._glo = glo = gl.glCreateProgram()
        self._varyings = varyings or []
        self._varyings_capture_mode = varyings_capture_mode.strip().lower()
        self._geometry_info = (0, 0, 0)
        self._attributes = []  # type: list[AttribFormat]
        #: Internal cache key used with vertex arrays
        self.attribute_key = "INVALID"  # type: str
        self._uniforms: dict[str, Uniform | UniformBlock] = {}

        if self._varyings_capture_mode not in self._valid_capture_modes:
            raise ValueError(
                f"Invalid capture mode '{self._varyings_capture_mode}'. "
                f"Valid modes are: {self._valid_capture_modes}."
            )

        shaders: list[tuple[str, int]] = [(vertex_shader, gl.GL_VERTEX_SHADER)]
        if fragment_shader:
            shaders.append((fragment_shader, gl.GL_FRAGMENT_SHADER))
        if geometry_shader:
            shaders.append((geometry_shader, gl.GL_GEOMETRY_SHADER))
        if tess_control_shader:
            shaders.append((tess_control_shader, gl.GL_TESS_CONTROL_SHADER))
        if tess_evaluation_shader:
            shaders.append((tess_evaluation_shader, gl.GL_TESS_EVALUATION_SHADER))

        # Inject a dummy fragment shader on gles when doing transforms
        if self._ctx.gl_api == "gles" and not fragment_shader:
            dummy_frag_src = """
                #version 310 es
                precision mediump float;
                out vec4 fragColor;
                void main() { fragColor = vec4(1.0); }
            """
            shaders.append((dummy_frag_src, gl.GL_FRAGMENT_SHADER))

        shaders_id = []
        for shader_code, shader_type in shaders:
            shader = Program.compile_shader(shader_code, shader_type)
            gl.glAttachShader(self._glo, shader)
            shaders_id.append(shader)

        # For now we assume varyings can be set up if no fragment shader
        if not fragment_shader:
            self._configure_varyings()

        Program.link(self._glo)

        if geometry_shader:
            geometry_in = gl.GLint()
            geometry_out = gl.GLint()
            geometry_vertices = gl.GLint()
            gl.glGetProgramiv(self._glo, gl.GL_GEOMETRY_INPUT_TYPE, geometry_in)
            gl.glGetProgramiv(self._glo, gl.GL_GEOMETRY_OUTPUT_TYPE, geometry_out)
            gl.glGetProgramiv(self._glo, gl.GL_GEOMETRY_VERTICES_OUT, geometry_vertices)
            self._geometry_info = (
                geometry_in.value,
                geometry_out.value,
                geometry_vertices.value,
            )

        # Delete shaders (not needed after linking)
        for shader in shaders_id:
            gl.glDeleteShader(shader)
            gl.glDetachShader(self._glo, shader)

        # Handle uniforms
        self._introspect_attributes()
        self._introspect_uniforms()
        self._introspect_uniform_blocks()

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, Program.delete_glo, self._ctx, glo)

        self.ctx.stats.incr("program")

    def __del__(self):
        # Intercept garbage collection if we are using Context.gc()
        if self._ctx.gc_mode == "context_gc" and self._glo > 0:
            self._ctx.objects.append(self)

    @property
    def ctx(self) -> "Context":
        """The context this program belongs to."""
        return self._ctx

    @property
    def glo(self) -> int:
        """The OpenGL resource id for this program."""
        return self._glo

    @property
    def attributes(self) -> Iterable[AttribFormat]:
        """List of attribute information."""
        return self._attributes

    @property
    def varyings(self) -> list[str]:
        """Out attributes names used in transform feedback."""
        return self._varyings

    @property
    def out_attributes(self) -> list[str]:
        """
        Out attributes names used in transform feedback.

        Alias for `varyings`.
        """
        return self._varyings

    @property
    def varyings_capture_mode(self) -> str:
        """
        Get the capture more for transform feedback (single, multiple).

        This is a read only property since capture mode
        can only be set before the program is linked.
        """
        return self._varyings_capture_mode

    @property
    def geometry_input(self) -> int:
        """
        The geometry shader's input primitive type.

        This an be compared with ``GL_TRIANGLES``, ``GL_POINTS`` etc.
        and is queried when the program is created.
        """
        return self._geometry_info[0]

    @property
    def geometry_output(self) -> int:
        """The geometry shader's output primitive type.

        This an be compared with ``GL_TRIANGLES``, ``GL_POINTS`` etc.
        and is queried when the program is created.
        """
        return self._geometry_info[1]

    @property
    def geometry_vertices(self) -> int:
        """
        The maximum number of vertices that can be emitted.
        This is queried when the program is created.
        """
        return self._geometry_info[2]

    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        Program.delete_glo(self._ctx, self._glo)
        self._glo = 0

    @staticmethod
    def delete_glo(ctx, prog_id):
        """
        Deletes a program. This is normally called automatically when the
        program is garbage collected.

        Args:
            ctx:
                The context this program belongs to
            prog_id:
                The OpenGL resource id
        """
        # Check to see if the context was already cleaned up from program
        # shut down. If so, we don't need to delete the shaders.
        if gl.current_context is None:
            return

        gl.glDeleteProgram(prog_id)
        ctx.stats.decr("program")

    def __getitem__(self, item) -> Uniform | UniformBlock:
        """Get a uniform or uniform block"""
        try:
            uniform = self._uniforms[item]
        except KeyError:
            raise KeyError(f"Uniform with the name `{item}` was not found.")

        return uniform.getter()

    def __setitem__(self, key, value):
        """
        Set a uniform value.

        Example::

            program['color'] = 1.0, 1.0, 1.0, 1.0
            program['mvp'] = projection @ view @ model

        Args:
            key:
                The uniform name
            value:
                The uniform value
        """
        try:
            uniform = self._uniforms[key]
        except KeyError:
            raise KeyError(f"Uniform with the name `{key}` was not found.")

        uniform.setter(value)

    def set_uniform_safe(self, name: str, value: Any):
        """
        Safely set a uniform catching KeyError.

        Args:
            name:
                The uniform name
            value:
                The uniform value
        """
        try:
            self[name] = value
        except KeyError:
            pass

    def set_uniform_array_safe(self, name: str, value: list[Any]):
        """
        Safely set a uniform array.

        Arrays can be shortened by the glsl compiler not all elements are determined
        to be in use. This function checks the length of the actual array and sets a
        subset of the values if needed. If the uniform don't exist no action will be
        done.

        Args:
            name:
                Name of uniform
            value:
                List of values
        """
        if name not in self._uniforms:
            return

        uniform = typing.cast(Uniform, self._uniforms[name])
        _len = uniform._array_length * uniform._components
        if _len == 1:
            self.set_uniform_safe(name, value[0])
        else:
            self.set_uniform_safe(name, value[:_len])

    def use(self):
        """
        Activates the shader.

        This is normally done for you automatically.
        """
        # IMPORTANT: This is the only place glUseProgram should be called
        #            so we can track active program.
        # if self._ctx.active_program != self:
        gl.glUseProgram(self._glo)
        # self._ctx.active_program = self

    def _configure_varyings(self):
        """Set up transform feedback varyings"""
        if not self._varyings:
            return

        # Covert names to char**
        c_array = (c_char_p * len(self._varyings))()
        for i, name in enumerate(self._varyings):
            c_array[i] = name.encode()

        ptr = cast(c_array, POINTER(POINTER(c_char)))

        # Are we capturing in interlaved or separate buffers?
        mode = (
            gl.GL_INTERLEAVED_ATTRIBS
            if self._varyings_capture_mode == "interleaved"
            else gl.GL_SEPARATE_ATTRIBS
        )

        gl.glTransformFeedbackVaryings(
            self._glo,  # program
            len(self._varyings),  # number of varying variables used for transform feedback
            ptr,  # zero-terminated strings specifying the names of the varying variables
            mode,
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
            self._attributes.append(
                AttribFormat(
                    c_name.value.decode(),
                    type_info.gl_type,
                    type_info.components,
                    type_info.gl_size,
                    location=location,
                )
            )

        # The attribute key is used to cache VertexArrays
        self.attribute_key = ":".join(
            f"{attr.name}[{attr.gl_type}/{attr.components}]" for attr in self._attributes
        )

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

    @staticmethod
    def compile_shader(source: str, shader_type: PyGLenum) -> gl.GLuint:
        """
        Compile the shader code of the given type.

        Args:
            source:
                The shader source code
            shader_type:
                The type of shader to compile.
                ``GL_VERTEX_SHADER``, ``GL_FRAGMENT_SHADER`` etc.

        Returns:
            The created shader id
        """
        shader = gl.glCreateShader(shader_type)
        source_bytes = source.encode("utf-8")
        # Turn the source code string into an array of c_char_p arrays.
        strings = byref(cast(c_char_p(source_bytes), POINTER(c_char)))
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
                (
                    f"Error compiling {SHADER_TYPE_NAMES[shader_type]} "
                    f"({result.value}): {msg.value.decode('utf-8')}\n"
                    f"---- [{SHADER_TYPE_NAMES[shader_type]}] ---\n"
                )
                + "\n".join(
                    f"{str(i + 1).zfill(3)}: {line} " for i, line in enumerate(source.split("\n"))
                )
            )
        return shader

    @staticmethod
    def link(glo):
        """Link a shader program"""
        gl.glLinkProgram(glo)
        status = c_int()
        gl.glGetProgramiv(glo, gl.GL_LINK_STATUS, status)
        if not status.value:
            length = c_int()
            gl.glGetProgramiv(glo, gl.GL_INFO_LOG_LENGTH, length)
            log = c_buffer(length.value)
            gl.glGetProgramInfoLog(glo, len(log), None, log)
            raise ShaderException("Program link error: {}".format(log.value.decode()))

    def __repr__(self):
        return "<Program id={}>".format(self._glo)
