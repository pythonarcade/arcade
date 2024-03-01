from __future__ import annotations
from typing import Protocol, Tuple, Iterator
from contextlib import contextmanager


__all__ = [
    'Projection',
    'Projector',
    'Camera'
]


class Projection(Protocol):
    viewport: Tuple[int, int, int, int]
    near: float
    far: float


class Projector(Protocol):

    def use(self) -> None:
        ...

    @contextmanager
    def activate(self) -> Iterator[Projector]:
        ...

    def map_coordinate(self, screen_coordinate: Tuple[float, float], depth: float = 0.0) -> Tuple[float, ...]:
        ...


class Camera(Protocol):

    def use(self) -> None:
        ...

    def activate(self) -> Iterator[Projector]:
        ...
