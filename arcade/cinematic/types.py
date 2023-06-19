from typing import Protocol, Tuple, Iterator
from contextlib import contextmanager

from arcade.cinematic.data import ViewData


class Projection(Protocol):
    near: float
    far: float


class Projector(Protocol):

    def use(self) -> None:
        ...

    @contextmanager
    def activate(self) -> Iterator["Projector"]:
        ...

    def get_map_coordinates(self, screen_coordinate: Tuple[float, float]) -> Tuple[float, float]:
        ...


class Camera(Protocol):
    _view: ViewData
    _projection: Projection

