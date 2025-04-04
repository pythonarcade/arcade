from __future__ import annotations

from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context
    from .program import Program

@runtime_checkable
class VertexArray(Protocol):

    def ctx(self) -> Context: ...
    def program(self) -> Program: ...


@runtime_checkable
class Geometry(Protocol):

    def ctx(self) -> Context: ...