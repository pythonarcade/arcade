from __future__ import annotations

from typing import Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from .context import Context


@runtime_checkable
class Program(Protocol):

    @property
    def ctx(self) -> Context: ...
