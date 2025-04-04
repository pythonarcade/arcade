from typing import Protocol, runtime_checkable, Any, TypeVar, List, Dict, Sequence

from .buffer import Buffer
from .program import Program
from .vertex_array import Geometry

from arcade.types import BufferProtocol
from arcade.gl.backends.gl.types import BufferDescription

@runtime_checkable
class Context(Protocol):

    def buffer(self, *args, data: BufferProtocol | None = None, reserve: int = 0, usage: str = "static") -> Buffer: ...

    def program(
        self,
        *args,
        vertex_shader: str | None = None,
        fragment_shader: str | None = None,
        geometry_shader: str | None = None,
        tess_control_shader: str | None = None,
        tess_evaluation_shader: str | None = None,
        common: List[str] | None = None,
        defines: Dict[str, str] | None = None,
        varyings: Sequence[str] | None = None,
        varyings_capture_mode: str = "interleaved",
    ) -> Program: ...

    def geometry(
        self,
        content: Sequence[BufferDescription] | None = None, # TODO: Hack for not having generic BufferDescription yet
        index_buffer: Buffer | None = None,
        mode: int | None = None,
        index_element_size: int = 4,
    ) -> Geometry: ...

T = TypeVar("T", bound=Context)