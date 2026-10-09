"""
Tests shared by the camera types. Each test runs for every camera type it
applies to, instead of being copied into a file for each type.
"""

from math import radians, tan

import pytest
from pyglet.math import Vec3

from arcade import Window, camera
from arcade.camera.default import DefaultProjector

PROJECTORS = [
    camera.OrthographicProjector,
    camera.PerspectiveProjector,
    camera.Camera2D,
    camera.ViewportProjector,
    DefaultProjector,
]
SIZES = [(800, 600), (1280, 720), (500, 500)]


def _has_matrices(projector) -> bool:
    return hasattr(projector, "generate_view_matrix") and hasattr(
        projector, "generate_projection_matrix"
    )


@pytest.mark.parametrize("projector_class", PROJECTORS)
def test_use(window: Window, projector_class):
    projector = projector_class()
    projector.use()

    assert window.current_camera is projector
    if _has_matrices(projector):
        assert window.ctx.view_matrix == projector.generate_view_matrix()
        assert window.ctx.projection_matrix == projector.generate_projection_matrix()

    # Reset the window for later tests
    window.default_camera.use()


@pytest.mark.parametrize("projector_class", PROJECTORS)
def test_activate_restores_previous_camera(window: Window, projector_class):
    previous = camera.Camera2D()
    previous.use()
    projector = projector_class()

    with projector.activate() as active:
        assert window.current_camera is active is projector
        if _has_matrices(projector):
            assert window.ctx.view_matrix == projector.generate_view_matrix()
            assert window.ctx.projection_matrix == projector.generate_projection_matrix()

    assert window.current_camera is previous

    # Reset the window for later tests
    window.default_camera.use()


# --- Mapping screen positions to the world, for the 3D projectors


def _depth(projector) -> float:
    """The z of the world positions unproject() gives at the default distance."""
    if isinstance(projector, camera.PerspectiveProjector):
        return 0.5 * projector.viewport.height / tan(radians(0.5 * projector._projection.fov))
    return 0.0


PROJECTORS_3D = [camera.OrthographicProjector, camera.PerspectiveProjector]


@pytest.mark.parametrize("projector_class", PROJECTORS_3D)
@pytest.mark.parametrize("width, height", SIZES)
def test_map_coordinates(window: Window, projector_class, width, height):
    window.set_size(width, height)
    projector = projector_class()
    depth = _depth(projector)

    for x, y in [(100.0, 100.0), (100.0, 0.0), (230.0, 800.0)]:
        assert tuple(projector.unproject((x, y))) == pytest.approx((x, y, depth))


@pytest.mark.parametrize("projector_class", PROJECTORS_3D)
@pytest.mark.parametrize("width, height", SIZES)
def test_map_coordinates_move(window: Window, projector_class, width, height):
    window.set_size(width, height)
    projector = projector_class()
    view = projector.view
    depth = _depth(projector)
    half_width, half_height = window.width // 2, window.height // 2
    center, corner = (half_width, half_height), (100.0, 100.0)

    view.position = (0.0, 0.0, 0.0)
    assert tuple(projector.unproject(center)) == pytest.approx((0.0, 0.0, depth))
    assert tuple(projector.unproject(corner)) == pytest.approx(
        (-half_width + 100.0, -half_height + 100.0, depth)
    )

    view.position = (100.0, 100.0, 0.0)
    assert tuple(projector.unproject(center)) == pytest.approx((100.0, 100.0, depth))
    assert tuple(projector.unproject(corner)) == pytest.approx(
        (-half_width + 200.0, -half_height + 200.0, depth)
    )


@pytest.mark.parametrize("projector_class", PROJECTORS_3D)
@pytest.mark.parametrize("width, height", SIZES)
def test_map_coordinates_rotate(window: Window, projector_class, width, height):
    window.set_size(width, height)
    projector = projector_class()
    view = projector.view
    depth = _depth(projector)
    half_width, half_height = window.width // 2, window.height // 2
    center, corner = (half_width, half_height), (100.0, 100.0)

    # Up pointing along x: a quarter turn
    view.up = (1.0, 0.0, 0.0)
    view.position = (0.0, 0.0, 0.0)
    assert tuple(projector.unproject(center)) == pytest.approx((0.0, 0.0, depth))
    assert tuple(projector.unproject(corner)) == pytest.approx(
        (-half_height + 100.0, half_width - 100.0, depth)
    )

    # Up pointing diagonally: an eighth of a turn
    view.up = (2.0**-0.5, 2.0**-0.5, 0.0)
    view.position = (100.0, 100.0, 0.0)
    shift_x = -half_width + 100.0
    shift_y = -half_height + 100.0
    rotated_x = shift_x / (2.0**0.5) + shift_y / (2.0**0.5) + 100
    rotated_y = -shift_x / (2.0**0.5) + shift_y / (2.0**0.5) + 100
    assert tuple(projector.unproject(center)) == pytest.approx((100.0, 100.0, depth))
    assert tuple(projector.unproject(corner)) == pytest.approx((rotated_x, rotated_y, depth))


@pytest.mark.parametrize("width, height", SIZES)
def test_orthographic_map_coordinates_zoom(window: Window, width, height):
    window.set_size(width, height)
    projector = camera.OrthographicProjector()
    view = projector.view
    half_width, half_height = window.width // 2, window.height // 2
    top_right, corner = (window.width, window.height), (100.0, 100.0)

    view.zoom = 2.0
    assert tuple(projector.unproject(top_right)) == pytest.approx(
        Vec3(window.width * 0.75, window.height * 0.75, 0.0)
    )
    assert tuple(projector.unproject(corner)) == pytest.approx(
        (half_width + (100 - half_width) * 0.5, half_height + (100 - half_height) * 0.5, 0.0)
    )

    view.position = (0.0, 0.0, 0.0)
    view.zoom = 0.25
    assert tuple(projector.unproject(top_right)) == pytest.approx(
        (window.width * 2.0, window.height * 2.0, 0.0)
    )
    assert tuple(projector.unproject(corner)) == pytest.approx(
        ((100 - half_width) * 4.0, (100 - half_height) * 4.0, 0.0)
    )
