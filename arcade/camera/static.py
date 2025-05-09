from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING

from pyglet.math import Mat4, Vec2, Vec3

from arcade.camera.data_types import (
    CameraData,
    OrthographicProjectionData,
    PerspectiveProjectionData,
)
from arcade.camera.projection_functions import (
    generate_orthographic_matrix,
    generate_perspective_matrix,
    generate_view_matrix,
    project_orthographic,
    project_perspective,
    unproject_orthographic,
    unproject_perspective,
)
from arcade.types import Point, Point3
from arcade.window_commands import get_window

if TYPE_CHECKING:
    from arcade.application import Window


class _StaticCamera:
    def __init__(
        self,
        view_matrix: Mat4,
        projection_matrix: Mat4,
        viewport: tuple[int, int, int, int] | None = None,
        *,
        project_method: (
            Callable[[Point, tuple[int, int, int, int], Mat4, Mat4], Vec2] | None
        ) = None,
        unproject_method: (
            Callable[[Point, tuple[int, int, int, int], Mat4, Mat4], Vec3] | None
        ) = None,
        window: Window | None = None,
    ):
        self._win: Window = window or get_window()
        self._viewport: tuple[int, int, int, int] = viewport or self._win.ctx.viewport
        self._view = view_matrix
        self._projection = projection_matrix

        self._project_method: Callable[[Point, tuple, Mat4, Mat4], Vec2] | None = project_method
        self._unproject_method: Callable[[Point, tuple, Mat4, Mat4], Vec3] | None = unproject_method

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

    def project(self, world_coordinate: Point) -> Vec2:
        """
        Take a Vec2 or Vec3 of coordinates and return the related screen coordinate
        """
        if self._project_method is None:
            raise ValueError("This Static Camera was not provided a project method at creation")

        pos = self._project_method(world_coordinate, self._viewport, self._view, self._projection)
        return pos

    def unproject(self, screen_coordinate: Point) -> Vec3:
        """
        Take in a pixel coordinate from within
        the range of the window size and returns
        the world space coordinates.

        Essentially reverses the effects of the projector.

        Args:
            screen_coordinate: A 2D position in pixels from the bottom left of the screen.
                               This should ALWAYS be in the range of 0.0 - screen size.
        Returns:
            A 3D vector in world space.
        """
        if self._unproject_method is None:
            raise ValueError("This Static Camera was not provided an unproject method at creation")

        return self._unproject_method(
            screen_coordinate, self._viewport, self._view, self._projection
        )


def static_from_orthographic(
    view: CameraData,
    orthographic: OrthographicProjectionData,
    viewport: tuple[int, int, int, int] | None = None,
    *,
    window: Window | None = None,
) -> _StaticCamera:
    """
    Create a static camera from a CameraData and OrthographicProjectionData

    Args:
        view: The view matrix to use
        orthographic: The orthographic projection to use
        viewport: The viewport to use
        window: The window to use
    """
    return _StaticCamera(
        generate_view_matrix(view),
        generate_orthographic_matrix(orthographic, view.zoom),
        viewport,
        window=window,
        project_method=project_orthographic,
        unproject_method=unproject_orthographic,
    )


def static_from_perspective(
    view: CameraData,
    perspective: OrthographicProjectionData,
    viewport: tuple[int, int, int, int] | None = None,
    *,
    window: Window | None = None,
) -> _StaticCamera:
    """
    Create a static camera from a CameraData and PerspectiveProjectionData

    Args:
        view: The view matrix to use
        perspective: The perspective projection to use
        viewport: The viewport to use
        window: The window
    """
    return _StaticCamera(
        generate_view_matrix(view),
        generate_orthographic_matrix(perspective, view.zoom),
        viewport,
        window=window,
        project_method=project_perspective,
        unproject_method=unproject_perspective,
    )


def static_from_raw_orthographic(
    projection: tuple[float, float, float, float],
    near: float = -100.0,
    far: float = 100.0,
    zoom: float = 1.0,
    position: Point3 = (0.0, 0.0, 0.0),
    up: Point3 = (0.0, 1.0, 0.0),
    forward: Point3 = (0.0, 0.0, -1.0),
    viewport: tuple[int, int, int, int] | None = None,
    *,
    window: Window | None = None,
) -> _StaticCamera:
    """
    Create a static camera from raw orthographic data.

    Args:
        projection: The orthographic projection to use
        near: The near plane
        far: The far plane
        zoom: The zoom level
        position: The position of the camera
        up: The up vector
        forward: The forward vector
        viewport: The viewport
        window: The window
    """
    view = generate_view_matrix(CameraData(position, up, forward, zoom))
    proj = generate_orthographic_matrix(
        OrthographicProjectionData(
            projection[0], projection[1], projection[2], projection[3], near, far
        ),
        zoom,
    )
    return _StaticCamera(
        view,
        proj,
        viewport,
        window=window,
        project_method=project_orthographic,
        unproject_method=unproject_orthographic,
    )


def static_from_raw_perspective(
    aspect: float,
    fov: float,
    near: float = -100.0,
    far: float = 100.0,
    zoom: float = 1.0,
    position: Point3 = (0.0, 0.0, 0.0),
    up: Point3 = (0.0, 1.0, 0.0),
    forward: Point3 = (0.0, 0.0, -1.0),
    viewport: tuple[int, int, int, int] | None = None,
    *,
    window: Window | None = None,
) -> _StaticCamera:
    """
    Create a static camera from raw perspective data.

    Args:
        aspect: The aspect ratio
        fov: The field of view
        near: The near plane
        far: The far plane
        zoom: The zoom level
        position: The position of the camera
        up: The up vector
        forward: The forward vector
        viewport: The viewport
        window: The window
    """
    view = generate_view_matrix(CameraData(position, up, forward, zoom))
    proj = generate_perspective_matrix(PerspectiveProjectionData(aspect, fov, near, far), zoom)

    return _StaticCamera(
        view,
        proj,
        viewport,
        window=window,
        project_method=project_perspective,
        unproject_method=unproject_perspective,
    )


def static_from_matrices(
    view: Mat4,
    projection: Mat4,
    viewport: tuple[int, int, int, int] | None,
    *,
    window: Window | None = None,
    project_method: Callable[[Point, tuple[int, int, int, int], Mat4, Mat4], Vec2] | None = None,
    unproject_method: Callable[[Point, tuple[int, int, int, int], Mat4, Mat4], Vec3] | None = None,
) -> _StaticCamera:
    """
    Create a static camera from raw matrices.

    Args:
        view: The view matrix
        projection: The projection matrix
        viewport: The viewport
        window: The window
        project_method: The project method
        unproject_method: The unproject method
    """
    return _StaticCamera(
        view,
        projection,
        viewport,
        window=window,
        project_method=project_method,
        unproject_method=unproject_method,
    )
