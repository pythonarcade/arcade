from typing import Protocol, Tuple, Iterator
from contextlib import contextmanager

from arcade.camera.data import CameraData


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
    def activate(self) -> Iterator["Projector"]:
        ...

    def map_coordinate(self, screen_coordinate: Tuple[float, float]) -> Tuple[float, ...]:
        ...


class Camera(Protocol):
    _view: CameraData
    _projection: Projection

