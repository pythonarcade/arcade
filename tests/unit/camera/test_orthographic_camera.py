import pytest as pytest

from arcade import camera, Window


def test_orthographic_camera(window: Window):
    default_camera = window.default_camera

    cam_default = camera.OrthographicProjector()
    default_view = cam_default.view_data
    default_projection = cam_default.projection_data

    # test that the camera correctly generated the default view and projection PoDs.
    assert default_view == camera.CameraData(
        (0, 0, window.width, window.height),  # Viewport
        (window.width/2, window.height/2, 0),  # Position
        (0.0, 1.0, 0.0),  # Up
        (0.0, 0.0, -1.0),  # Forward
        1.0,  # Zoom
    )
    assert default_projection == camera.OrthographicProjectionData(
        -0.5 * window.width, 0.5 * window.width,  # Left, Right
        -0.5 * window.height, 0.5 * window.height,  # Bottom, Top
        -100, 100  # Near, Far
    )

    # test that the camera properties work
    assert cam_default.view_data.position == default_view.position
    assert cam_default.view_data.viewport == default_view.viewport

    # Test that the camera is being used.
    cam_default.use()
    assert window.current_camera == cam_default
    default_camera.use()
    assert window.current_camera == default_camera

    # Test that the camera is actually recognised by the camera as being activated
    assert window.current_camera == default_camera
    with cam_default.activate() as cam:
        assert window.current_camera == cam and cam == cam_default
    assert window.current_camera == default_camera

    set_view = camera.CameraData(
        (0, 0, 1, 1),  # Viewport
        (0.0, 0.0, 0.0),  # Position
        (0.0, 1.0, 0.0),  # Up
        (0.0, 0.0, 1.0),  # Forward
        1.0  # Zoom
    )
    set_projection = camera.OrthographicProjectionData(
        0.0, 1.0,  # Left, Right
        0.0, 1.0,  # Bottom, Top
        -1.0, 1.0  # Near, Far
    )
    cam_set = camera.OrthographicProjector(
        view=set_view,
        projection=set_projection
    )

    # test that the camera correctly used the provided Pods.
    assert cam_set.view_data == set_view
    assert cam_set.projection_data == set_projection

    # test that the camera properties work
    assert cam_set.view_data.position == set_view.position
    assert cam_set.view_data.viewport == set_view.viewport

    # Test that the camera is actually recognised by the camera as being activated
    assert window.current_camera == default_camera
    with cam_set.activate() as cam:
        assert window.current_camera == cam and cam == cam_set
    assert window.current_camera == default_camera

    # Test that the camera is being used.
    cam_set.use()
    assert window.current_camera == cam_set
    default_camera.use()
    assert window.current_camera == default_camera


def test_orthographic_projection_matrix(window: Window):
    cam_default = camera.OrthographicProjector()
    default_view = cam_default.view_data
    default_projection = cam_default.projection_data


def test_orthographic_view_matrix(window: Window):
    cam_default = camera.OrthographicProjector()
    default_view = cam_default.view_data
    default_projection = cam_default.projection_data


def test_orthographic_map_coordinates(window: Window):
    cam_default = camera.OrthographicProjector()
    default_view = cam_default.view_data
    default_projection = cam_default.projection_data

    # Test that the camera maps coordinates properly when no values have been adjusted
    assert cam_default.map_coordinate((100.0, 100.0)) == (pytest.approx(100.0), pytest.approx(100.0))

    # Test that the camera maps coordinates properly when 0.0, 0.0 is in the center of the screen
    default_view.position = (0.0, 0.0, 0.0)
    assert (cam_default.map_coordinate((window.width//2, window.height//2)) == (0.0, 0.0))

    # Test that the camera maps coordinates properly when the position has changed.
    default_view.position = (100.0, 100.0, 0.0)
    assert (cam_default.map_coordinate((100.0, 100.0)) ==
            (pytest.approx(200.0 - window.width//2), pytest.approx(200.0 - window.height//2)))

    # Test that the camera maps coordinates properly when the rotation has changed.
    default_view.position = (0.0, 0.0, 0.0)
    default_view.up = (1.0, 0.0, 0.0)
    assert (cam_default.map_coordinate((window.width//2, window.height//2 + 100.0)) ==
            (pytest.approx(100.0), pytest.approx(00.0)))

    # Test that the camera maps coordinates properly when the rotation and position has changed.
    default_view.position = (100.0, 100.0, 0.0)
    default_view.up = (0.7071067812, 0.7071067812, 0.0)
    assert (cam_default.map_coordinate((window.width//2, window.height//2)) ==
            (pytest.approx(100.0), pytest.approx(100.0)))

    # Test that the camera maps coordinates properly when zoomed in.
    default_view.position = (0.0, 0.0, 0.0)
    default_view.up = (0.0, 1.0, 0.0)
    default_view.zoom = 2.0
    assert (cam_default.map_coordinate((window.width, window.height)) ==
            (pytest.approx(window.width//4), pytest.approx(window.height//4)))

    # Test that the camera maps coordinates properly when the viewport is not the default
    default_view.zoom = 1.0
    default_view.viewport = window.width//2, window.height//2, window.width//2, window.height//2
