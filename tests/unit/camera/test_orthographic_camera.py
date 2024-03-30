import pytest as pytest

from arcade import camera, Window


def test_orthographic_projector_use(window: Window):
    # Given
    from pyglet.math import Mat4
    ortho_camera = camera.OrthographicProjector()

    view_matrix = ortho_camera._generate_view_matrix()
    proj_matrix = ortho_camera._generate_projection_matrix()

    # When
    ortho_camera.use()

    # Then
    assert window.current_camera is ortho_camera
    assert window.ctx.view_matrix == view_matrix
    assert window.ctx.projection_matrix == proj_matrix

    # Reset the window for later tests
    window.default_camera.use()


def test_orthographic_projector_activate(window: Window):
    # Given
    ortho_camera: camera.OrthographicProjector = camera.OrthographicProjector()

    view_matrix = ortho_camera._generate_view_matrix()
    proj_matrix = ortho_camera._generate_projection_matrix()

    # When
    with ortho_camera.activate() as cam:
        # Initially
        assert window.current_camera is cam is ortho_camera
        assert window.ctx.view_matrix == view_matrix
        assert window.ctx.projection_matrix == proj_matrix

    # Finally
    assert window.current_camera is window.default_camera

    # Reset the window for later tests
    window.default_camera.use()


def test_orthographic_projector_map_coordinates(window: Window):
    # Given
    ortho_camera = camera.OrthographicProjector()

    # When
    mouse_pos_a = (100.0, 100.0)
    mouse_pos_b = (100.0, 0.0)
    mouse_pos_c = (230.0, 800.0)

    # Then
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_a) == pytest.approx((100.0, 100.0, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_b) == pytest.approx((100.0, 0.0, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_c) == pytest.approx((230.0, 800.0, 0.0))


def test_orthographic_projector_map_coordinates_move(window: Window):
    window.set_size(800, 600)

    # Given
    ortho_camera = camera.OrthographicProjector()
    default_view = ortho_camera.view

    mouse_pos_a = (window.width//2, window.height//2)
    mouse_pos_b = (100.0, 100.0)

    # When
    default_view.position = (0.0, 0.0, 0.0)

    # Then
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_a) == pytest.approx((0.0, 0.0, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_b) == pytest.approx((-300.0, -200.0, 0.0))

    # And

    # When
    default_view.position = (100.0, 100.0, 0.0)

    # Then
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_a) == pytest.approx((100.0, 100.0, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_b) == pytest.approx((-200.0, -100.0, 0.0))


def test_orthographic_projector_map_coordinates_rotate(window: Window):
    window.set_size(800, 600)

    # Given
    ortho_camera = camera.OrthographicProjector()
    default_view = ortho_camera.view

    mouse_pos_a = (window.width//2, window.height//2)
    mouse_pos_b = (100.0, 100.0)

    # When
    default_view.up = (1.0, 0.0, 0.0)
    default_view.position = (0.0, 0.0, 0.0)

    # Then
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_a) == pytest.approx((0.0, 0.0, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_b) == pytest.approx((-200.0, 300.0, 0.0))

    # And

    # When
    default_view.up = (2.0**-0.5, 2.0**-0.5, 0.0)
    default_view.position = (100.0, 100.0, 0.0)

    # Then
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_a) == pytest.approx((100.0, 100.0, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_b) == pytest.approx((-253.553390, 170.710678, 0.0))


def test_orthographic_projector_map_coordinates_zoom(window: Window):
    window.set_size(800, 600)

    # Given
    ortho_camera = camera.OrthographicProjector()
    default_view = ortho_camera.view

    mouse_pos_a = (window.width, window.height)
    mouse_pos_b = (100.0, 100.0)

    # When
    default_view.zoom = 2.0

    # Then
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_a) == pytest.approx((window.width*0.75, window.height*0.75, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_b) == pytest.approx((250.0, 200.0, 0.0))

    # And

    # When
    default_view.position = (0.0, 0.0, 0.0)
    default_view.zoom = 0.25

    # Then
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_a) == pytest.approx((window.width*2.0, window.height*2.0, 0.0))
    assert ortho_camera.map_screen_to_world_coordinate(mouse_pos_b) == pytest.approx((-1200.0, -800.0, 0.0))