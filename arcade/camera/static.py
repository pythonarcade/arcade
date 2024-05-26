from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Optional, Tuple, TYPE_CHECKING

from arcade.camera import (
    CameraData,
    PerspectiveProjectionData,
    OrthographicProjectionData,
    generate_view_matrix,
    generate_perspective_matrix,
    generate_orthographic_matrix
)
from arcade.window_commands import get_window

from pyglet.math import Mat4

if TYPE_CHECKING:
    from arcade.application import Window


class _StaticCamera:

    def __init__(self, view_matrix: Mat4, projection_matrix: Mat4,
                 viewport: Optional[Tuple[int, int, int, int]] = None, window: Optional[Window] = None):
        self._win: Window = window or get_window()
        self._viewport: Tuple[int, int, int, int] = viewport or self._win.ctx.viewport
        self._view = view_matrix
        self._projection = projection_matrix

    def use(self):
        self._win.current_camera = self

        self._win.ctx.viewport = self._viewport
        self._win.ctx.projection_matrix = self._projection
        self._win.ctx.view_matrix = self._view

    @contextmanager
    def activate(self) -> Generator[_StaticCamera, None, None]:
        prev = self._win.ctx.current_camera
        try:
            self.use()
            yield self
        finally:
            prev.use()


def static_from_orthographic(
        view: CameraData,
        orthographic: OrthographicProjectionData,
        *,
        window: Optional[Window] = None
) -> _StaticCamera:
    return _StaticCamera(
        generate_view_matrix(view),
        generate_orthographic_matrix(orthographic, view.zoom),
        orthographic.viewport, window
    )


def static_from_perspective(
        view: CameraData,
        perspective: OrthographicProjectionData,
        *,
        window: Optional[Window] = None
) -> _StaticCamera:
    return _StaticCamera(
        generate_view_matrix(view),
        generate_orthographic_matrix(perspective, view.zoom),
        perspective.viewport, window
    )


def static_from_raw_orthographic(
        projection: Tuple[float, float, float, float],
        near: float = -100.0, far: float = 100.0,
        zoom: float = 1.0,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        up: Tuple[float, float, float] = (0.0, 1.0, 0.0),
        forward: Tuple[float, float, float] = (0.0, 0.0, -1.0),
        viewport: Optional[Tuple[int, int, int, int]] = None,
        *,
        window: Optional[Window] = None
) -> _StaticCamera:
    view = generate_view_matrix(
        CameraData(position, up, forward, zoom)
    )
    proj = generate_orthographic_matrix(
        OrthographicProjectionData(
            projection[0], projection[1], projection[2], projection[3], near, far, viewport or (0, 0, 0, 0)), zoom
    )
    return _StaticCamera(view, proj, viewport, window)


def static_from_raw_perspective(
        aspect: float, fov: float,
        near: float = -100.0, far: float = 100.0,
        zoom: float = 1.0,
        position: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        up: Tuple[float, float, float] = (0.0, 1.0, 0.0),
        forward: Tuple[float, float, float] = (0.0, 0.0, -1.0),
        viewport: Optional[Tuple[int, int, int, int]] = None,
        *,
        window: Optional[Window] = None
) -> _StaticCamera:
    view = generate_view_matrix(
        CameraData(position, up, forward, zoom)
    )
    proj = generate_perspective_matrix(
        PerspectiveProjectionData(aspect, fov, near, far, viewport or (0, 0, 0, 0)), zoom
    )

    return _StaticCamera(view, proj, viewport, window)


def static_from_matrices(
        view: Mat4, projection: Mat4,
        viewport: Optional[Tuple[int, int, int, int]],
        *,
        window: Optional[Window] = None
) -> _StaticCamera:
    return _StaticCamera(view, projection, viewport, window)
