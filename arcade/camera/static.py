from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional

from arcade.camera import (
    CameraData,
    PerspectiveProjectionData,
    OrthographicProjectionData,
    generate_view_matrix,
    generate_perspective_matrix,
    generate_orthographic_matrix
)
from arcade import get_window, Window

from pyglet.math import Mat4


class _StaticCamera:

    def __init__(self, view_matrix: Mat4, projection_matrix: Mat4,
                 viewport: Optional[tuple[int, int, int, int]] = None, window: Optional[Window] = None):
        self._win: Window = window or get_window()
        self._viewport: tuple[int, int, int, int] = viewport or self._win.ctx.viewport
        self._view = view_matrix
        self._projection = projection_matrix

    def use(self):
        self._win.current_camera = self

        self._win.ctx.viewport = self._viewport
        self._win.ctx.projection_matrix = self._projection
        self._win.ctx.view_matrix = self._view

    def activate(self) -> Generator[_StaticCamera]:
        prev = self._win.ctx.current_camera
        try:
            self.use()
            yield self
        finally:
            prev.use()


@contextmanager
def static_from_orthographic(
        view: CameraData,
        orthographic: OrthographicProjectionData,
        *,
        window: Optional[Window] = None
) -> Generator[_StaticCamera]:
    try:
        static = _StaticCamera(
            generate_view_matrix(view),
            generate_orthographic_matrix(orthographic, view.zoom),
            orthographic.viewport, window
        )
        with static.activate():
            yield static
    finally:
        pass


@contextmanager
def static_from_perspective(
        view: CameraData,
        perspective: OrthographicProjectionData,
        *,
        window: Optional[Window] = None
) -> Generator[_StaticCamera]:
    try:
        static = _StaticCamera(
            generate_view_matrix(view),
            generate_orthographic_matrix(perspective, view.zoom),
            perspective.viewport, window
        )
        with static.activate():
            yield static
    finally:
        pass


@contextmanager
def static_from_raw_orthographic(
        position: tuple[float, float, float],
        forward: tuple[float, float, float],
        up: tuple[float, float, float],
        projection: tuple[float, float, float],
        near: float = -100.0, far: float = 100.0,
        zoom: float = 1.0,
        viewport: Optional[tuple[int, int, int, int]] = None,
        *,
        window: Optional[Window] = None
) -> Generator[_StaticCamera]:
    try:
        view = generate_view_matrix(
            CameraData(position, forward, up, zoom)
        )
        proj = generate_orthographic_matrix(
            OrthographicProjectionData(*projection, near, far), zoom
        )
        static = _StaticCamera(view, proj, viewport, window)
        with static.activate():
            yield static
    finally:
        pass


@contextmanager
def static_from_raw_perspective(
        position: tuple[float, float, float],
        forward: tuple[float, float, float],
        up: tuple[float, float, float],
        aspect: float, fov: float,
        near: float = -100.0, far: float = 100.0,
        zoom: float = 1.0,
        viewport: Optional[tuple[int, int, int, int]] = None,
        *,
        window: Optional[Window] = None
) -> Generator[_StaticCamera]:
    try:
        view = generate_view_matrix(
            CameraData(position, forward, up, zoom)
        )
        proj = generate_perspective_matrix(
            PerspectiveProjectionData(aspect, fov, near, far, viewport), zoom
        )

        static = _StaticCamera(view, proj, viewport, window)
        with static.activate():
            yield static
    finally:
        pass


@contextmanager
def static_from_matrices(
        view: Mat4, projection: Mat4,
        viewport: Optional[tuple[int, int, int, int]],
        *,
        window: Optional[Window] = None
) -> Generator[_StaticCamera]:
    try:
        static = _StaticCamera(view, projection, viewport, window)
        with static.activate():
            yield static
    finally:
        pass
