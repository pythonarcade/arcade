from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.gl import Context


class ComputeShader(ABC):
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

        ctx.stats.incr("compute_shader")

    @abstractmethod
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
        raise NotImplementedError("The enabled graphics backend does not support this method.")

    def __hash__(self) -> int:
        return id(self)

    @abstractmethod
    def delete(self) -> None:
        """
        Destroy the internal compute shader object.

        This is normally not necessary, but depends on the
        garbage collection configured in the context.
        """
        raise NotImplementedError("The enabled graphics backend does not support this method.")
