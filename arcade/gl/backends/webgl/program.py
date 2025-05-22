from __future__ import annotations

import weakref
from typing import TYPE_CHECKING, Any, Iterable, cast

from arcade.gl import enums
from arcade.gl.exceptions import ShaderException
from arcade.gl.program import Program
from arcade.gl.types import SHADER_TYPE_NAMES, AttribFormat, GLTypes

from .uniform import Uniform, UniformBlock

if TYPE_CHECKING:
    from pyglet.graphics.api.webgl.webgl_js import WebGLProgram as JSWebGLProgram

    from arcade.gl.backends.webgl.context import WebGLContext


class WebGLProgram(Program):
    _valid_capture_modes = ("interleaved", "separate")

    def __init__(
        self,
        ctx: WebGLContext,
        *,
        vertex_shader: str,
        fragment_shader: str | None = None,
        geometry_shader: str | None = None,
        tess_control_shader: str | None = None,
        tess_evaluation_shader: str | None = None,
        varyings: list[str] | None = None,
        varyings_capture_mode: str = "interleaved",
    ):
        if geometry_shader is not None:
            raise NotImplementedError("Geometry Shaders not supported with WebGL")

        if tess_control_shader is not None:
            raise NotImplementedError("Tessellation Shaders not supported with WebGL")

        if tess_evaluation_shader is not None:
            raise NotImplementedError("Tessellation Shaders not supported with WebGL")

        super().__init__(ctx)
        self._ctx = ctx

        glo = self._ctx._gl.createProgram()
        assert glo is not None, "Failed to create GL program"
        self._glo: JSWebGLProgram = glo

        self._varyings = varyings or []
        self._varyings_capture_mode = varyings_capture_mode.strip().lower()
        self._geometry_info = (0, 0, 0)
        self._attributes = []
        self._uniforms: dict[str, Uniform | UniformBlock] = {}

        if self._varyings_capture_mode not in self._valid_capture_modes:
            raise ValueError(
                f"Invalid Capture Mode: {self._varyings_capture_mode}. "
                f"Valid Modes are: {self._valid_capture_modes}."
            )

        shaders: list[tuple[str, int]] = [(vertex_shader, enums.VERTEX_SHADER)]
        if fragment_shader:
            shaders.append((fragment_shader, enums.FRAGMENT_SHADER))

        # TODO: Do we need to inject a dummy fragment shader for transforms like OpenGL ES?

        compiled_shaders = []
        for shader_code, shader_type in shaders:
            shader = WebGLProgram.compile_shader(self._ctx, shader_code, shader_type)
            self._ctx._gl.attachShader(self._glo, shader)
            compiled_shaders.append(shader)

        if not fragment_shader:
            self._configure_varyings()

        WebGLProgram.link(self._ctx, self._glo)

        for shader in compiled_shaders:
            self._ctx._gl.deleteShader(shader)
            self._ctx._gl.detachShader(self._glo, shader)

        self._introspect_attributes()
        self._introspect_uniforms()
        self._introspect_uniform_blocks()

        if self._ctx.gc_mode == "auto":
            weakref.finalize(self, WebGLProgram.delete_glo, self._ctx, self._glo)

    def __del__(self):
        if self._ctx.gc_mode == "context_gc" and self._glo is not None:
            self._ctx.objects.append(self)

    @property
    def ctx(self) -> WebGLContext:
        """The context this program belongs to."""
        return self._ctx

    @property
    def glo(self) -> JSWebGLProgram | None:
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
        raise NotImplementedError("Geometry Shaders not supported with WebGL")

    @property
    def geometry_output(self) -> int:
        """The geometry shader's output primitive type.

        This an be compared with ``GL_TRIANGLES``, ``GL_POINTS`` etc.
        and is queried when the program is created.
        """
        raise NotImplementedError("Geometry Shaders not supported with WebGL")

    @property
    def geometry_vertices(self) -> int:
        """
        The maximum number of vertices that can be emitted.
        This is queried when the program is created.
        """
        raise NotImplementedError("Geometry Shaders not supported with WebGL")

    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        WebGLProgram.delete_glo(self._ctx, self._glo)
        self._glo = None  # type: ignore

    @staticmethod
    def delete_glo(ctx: WebGLContext, program: JSWebGLProgram | None):
        ctx._gl.deleteProgram(program)
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

        uniform = cast(Uniform, self._uniforms[name])
        _len = uniform._array_length * uniform._components
        if _len == 1:
            self.set_uniform_safe(name, value[0])
        else:
            self.set_uniform_safe(name, value[:_len])

    def use(self):
        self._ctx._gl.useProgram(self._glo)

    def _configure_varyings(self):
        if not self._varyings:
            return

        mode = (
            enums.INTERLEAVED_ATTRIBS
            if self._varyings_capture_mode == "interleaved"
            else enums.SEPARATE_ATTRIBS
        )

        self._ctx._gl.transformFeedbackVaryings(
            self._glo,  # type: ignore this is guaranteed to not be None at this point
            self._varyings,
            mode,
        )

    def _introspect_attributes(self):
        num_attrs = self._ctx._gl.getProgramParameter(self._glo, enums.ACTIVE_ATTRIBUTES)

        # TODO: Do we need to instrospect the varyings? The OpenGL backend doesn't
        # num_varyings = self._ctx._gl.getProgramParameter(
        #   self._glo,
        #   enums.TRANSFORM_FEEDBACK_VARYINGS
        # )

        for i in range(num_attrs):
            info = self._ctx._gl.getActiveAttrib(self._glo, i)
            location = self._ctx._gl.getAttribLocation(self._glo, info.name)
            type_info = GLTypes.get(info.type)
            self._attributes.append(
                AttribFormat(
                    info.name,
                    type_info.gl_type,
                    type_info.components,
                    type_info.gl_size,
                    location=location,
                )
            )

        self.attribute_key = ":".join(
            f"{attr.name}[{attr.gl_type}/{attr.components}]" for attr in self._attributes
        )

    def _introspect_uniforms(self):
        active_uniforms = self._ctx._gl.getProgramParameter(self._glo, enums.ACTIVE_UNIFORMS)

        for i in range(active_uniforms):
            name, type, size = self._query_uniform(i)
            location = self._ctx._gl.getUniformLocation(self._glo, name)

            if location == -1:
                continue

            name = name.replace("[0]", "")
            self._uniforms[name] = Uniform(self._ctx, self._glo, location, name, type, size)

    def _introspect_uniform_blocks(self):
        active_uniform_blocks = self._ctx._gl.getProgramParameter(
            self._glo, enums.ACTIVE_UNIFORM_BLOCKS
        )

        for location in range(active_uniform_blocks):
            index, size, name = self._query_uniform_block(location)
            block = UniformBlock(self._ctx, self._glo, index, size, name)
            self._uniforms[name] = block

    def _query_uniform(self, location: int) -> tuple[str, int, int]:
        info = self._ctx._gl.getActiveUniform(self._glo, location)
        return info.name, info.type, info.size

    def _query_uniform_block(self, location: int) -> tuple[int, int, str]:
        name = self._ctx._gl.getActiveUniformBlockName(self._glo, location)
        index = self._ctx._gl.getActiveUniformBlockParameter(
            self._glo, location, enums.UNIFORM_BLOCK_BINDING
        )
        size = self._ctx._gl.getActiveUniformBlockParameter(
            self._glo, location, enums.UNIFORM_BLOCK_DATA_SIZE
        )
        return index, size, name

    @staticmethod
    def compile_shader(ctx: WebGLContext, source: str, shader_type: int):
        shader = ctx._gl.createShader(shader_type)
        assert shader is not None, "Failed to WebGL Shader Object"
        ctx._gl.shaderSource(shader, source)
        ctx._gl.compileShader(shader)
        compile_result = ctx._gl.getShaderParameter(shader, enums.COMPILE_STATUS)
        if not compile_result:
            msg = ctx._gl.getShaderInfoLog(shader)
            raise ShaderException(
                (
                    f"Error compiling {SHADER_TYPE_NAMES[shader_type]} "
                    f"{compile_result}): {msg}\n"
                    f"---- [{SHADER_TYPE_NAMES[shader_type]}] ---\n"
                )
                + "\n".join(
                    f"{str(i + 1).zfill(3)}: {line} " for i, line in enumerate(source.split("\n"))
                )
            )
        return shader

    @staticmethod
    def link(ctx: WebGLContext, glo: JSWebGLProgram):
        ctx._gl.linkProgram(glo)
        status = ctx._gl.getProgramParameter(glo, enums.LINK_STATUS)
        if not status:
            log = ctx._gl.getProgramInfoLog(glo)
            raise ShaderException("Program link error: {}".format(log))

    def __repr__(self):
        return "<Program id={}>".format(self._glo)
