from math import tan, radians

import pytest as pytest

from arcade import camera, Window


def test_perspective_projector_use(window: Window):
    # Given
    persp_camera = camera.PerspectiveProjector()

    view_matrix = persp_camera.generate_view_matrix()
    proj_matrix = persp_camera.generate_projection_matrix()

    # When
    persp_camera.use()

    # Then
    assert window.current_camera is persp_camera
    assert window.ctx.view_matrix == view_matrix
    assert window.ctx.projection_matrix == proj_matrix

    # Reset the window for later tests
    window.default_camera.use()


def test_perspective_projector_activate(window: Window):
    # Given
    persp_camera: camera.PerspectiveProjector = camera.PerspectiveProjector()

    view_matrix = persp_camera.generate_view_matrix()
    proj_matrix = persp_camera.generate_projection_matrix()

    # When
    with persp_camera.activate() as cam:
        # Initially
        assert window.current_camera is cam is persp_camera
        assert window.ctx.view_matrix == view_matrix
        assert window.ctx.projection_matrix == proj_matrix

    # Finally
    assert window.current_camera is window.default_camera

    # Reset the window for later tests
    window.default_camera.use()


@pytest.mark.parametrize("width, height", [(800, 600), (1280, 720), (500, 500)])
def test_perspective_projector_map_coordinates(window: Window, width, height):
    # Given
    window.set_size(width, height)
    persp_camera = camera.PerspectiveProjector()

    depth = (0.5 * persp_camera.viewport.height / tan(radians(0.5 * persp_camera._projection.fov)))

    # When
    mouse_pos_a = (100.0, 100.0)
    mouse_pos_b = (100.0, 0.0)
    mouse_pos_c = (230.0, 800.0)

    # Then
    assert tuple(persp_camera.unproject(mouse_pos_a)) == pytest.approx((100.0, 100.0, depth))
    assert tuple(persp_camera.unproject(mouse_pos_b)) == pytest.approx((100.0, 0.0, depth))
    assert tuple(persp_camera.unproject(mouse_pos_c)) == pytest.approx((230.0, 800.0, depth))


@pytest.mark.parametrize("width, height", [(800, 600), (1280, 720), (500, 500)])
def test_perspective_projector_map_coordinates_move(window: Window, width, height):
    # Given
    window.set_size(width, height)
    persp_camera = camera.PerspectiveProjector()
    default_view = persp_camera.view

    depth = (0.5 * persp_camera.viewport.height / tan(radians(0.5 * persp_camera._projection.fov)))

    half_width, half_height = window.width//2, window.height//2

    mouse_pos_a = (half_width, half_height)
    mouse_pos_b = (100.0, 100.0)

    # When
    default_view.position = (0.0, 0.0, 0.0)

    # Then
    assert tuple(persp_camera.unproject(mouse_pos_a)) == pytest.approx((0.0, 0.0, depth))
    assert (
            tuple(persp_camera.unproject(mouse_pos_b))
            ==
            pytest.approx((-half_width+100.0, -half_height+100, depth))
    )

    # And

    # When
    default_view.position = (100.0, 100.0, 0.0)

    # Then
    assert tuple(persp_camera.unproject(mouse_pos_a)) == pytest.approx((100.0, 100.0, depth))
    assert (
            tuple(persp_camera.unproject(mouse_pos_b))
            ==
            pytest.approx((-half_width+200.0, -half_height+200.0, depth))
    )


@pytest.mark.parametrize("width, height", [(800, 600), (1280, 720), (500, 500)])
def test_perspective_projector_map_coordinates_rotate(window: Window, width, height):
    # Given
    window.set_size(width, height)
    persp_camera = camera.PerspectiveProjector()
    default_view = persp_camera.view

    depth = (0.5 * persp_camera.viewport.height / tan(radians(0.5 * persp_camera._projection.fov)))

    half_width, half_height = window.width//2, window.height//2

    mouse_pos_a = (half_width, half_height)
    mouse_pos_b = (100.0, 100.0)

    # When
    default_view.up = (1.0, 0.0, 0.0)
    default_view.position = (0.0, 0.0, 0.0)

    # Then
    assert tuple(persp_camera.unproject(mouse_pos_a)) == pytest.approx((0.0, 0.0, depth))
    assert (
            tuple(persp_camera.unproject(mouse_pos_b))
            ==
            pytest.approx((-half_height+100.0, half_width-100.0, depth))
    )

    # And

    # When
    default_view.up = (2.0**-0.5, 2.0**-0.5, 0.0)
    default_view.position = (100.0, 100.0, 0.0)

    b_shift_x = -half_width + 100.0
    b_shift_y = -half_height + 100.0
    b_rotated_x = b_shift_x / (2.0**0.5) + b_shift_y / (2.0**0.5) + 100
    b_rotated_y = -b_shift_x / (2.0**0.5) + b_shift_y / (2.0**0.5) + 100
    # Then
    assert tuple(persp_camera.unproject(mouse_pos_a)) == pytest.approx((100.0, 100.0, depth))
    assert (
            tuple(persp_camera.unproject(mouse_pos_b))
            ==
            pytest.approx((b_rotated_x, b_rotated_y, depth))
    )

