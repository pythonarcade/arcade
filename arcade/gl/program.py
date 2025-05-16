from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from arcade.gl import Context


class Program(ABC):
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
        "_varyings_capture_mode",
        "attribute_key",
        "__weakref__",
    )

    def __init__(
        self,
        ctx: Context,
        *,
        varyings_capture_mode: str = "interleaved",
    ):
        self._ctx = ctx
        self.attribute_key = "INVALID"  # type: str
        self._varyings_capture_mode = varyings_capture_mode.strip().lower()
        self._ctx.stats.incr("program")

    @property
    def ctx(self) -> "Context":
        """The context this program belongs to."""
        return self._ctx

    @property
    @abstractmethod
    def attributes(
        self,
    ) -> Iterable:  # TODO: Typing on this Iterable, need generic type for AttribFormat?
        """List of attribute information."""
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def varyings(self) -> list[str]:
        """Out attributes names used in transform feedback."""
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def out_attributes(self) -> list[str]:
        """
        Out attributes names used in transform feedback.

        Alias for `varyings`.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def varyings_capture_mode(self) -> str:
        """
        Get the capture more for transform feedback (single, multiple).

        This is a read only property since capture mode
        can only be set before the program is linked.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def geometry_input(self) -> int:
        """
        The geometry shader's input primitive type.

        This an be compared with ``GL_TRIANGLES``, ``GL_POINTS`` etc.
        and is queried when the program is created.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def geometry_output(self) -> int:
        """The geometry shader's output primitive type.

        This an be compared with ``GL_TRIANGLES``, ``GL_POINTS`` etc.
        and is queried when the program is created.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @property
    @abstractmethod
    def geometry_vertices(self) -> int:
        """
        The maximum number of vertices that can be emitted.
        This is queried when the program is created.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def delete(self):
        """
        Destroy the underlying OpenGL resource.

        Don't use this unless you know exactly what you are doing.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def __getitem__(self, item):  # TODO: typing, this should return Uniform | UniformBlock
        """Get a uniform or uniform block"""
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def set_uniform_safe(self, name: str, value: Any):
        """
        Safely set a uniform catching KeyError.

        Args:
            name:
                The uniform name
            value:
                The uniform value
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    @abstractmethod
    def use(self):
        """
        Activates the shader.

        This is normally done for you automatically.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")
