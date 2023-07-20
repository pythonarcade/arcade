import pytest as pytest

from arcade import cinematic, Window


def test_orthographic_camera(window: Window):
    default_camera = window.current_camera

    cam_default = cinematic.OrthographicProjector()
    default_view = cam_default.view
    default_projection = cam_default.projection

    # test that the camera correctly generated the default view and projection PoDs.
    assert default_view == cinematic.CameraData(
        (0, 0, window.width, window.height),  # Viewport
        (window.width/2, window.height/2, 0),  # Position
        (0.0, 1.0, 0.0),  # Up
        (0.0, 0.0, 1.0),  # Forward
        1.0,  # Zoom
    )
    assert default_projection == cinematic.OrthographicProjectionData(
        -0.5 * window.width, 0.5 * window.width,  # Left, Right
        -0.5 * window.height, 0.5 * window.height,  # Bottom, Top
        -100, 100  # Near, Far
    )

    # test that the camera properties work
    assert cam_default.position == default_view.position
    assert cam_default.viewport == default_view.viewport

    # Test that the camera is actually recognised by the camera as being activated
    assert window.current_camera == default_camera
    with cam_default.activate() as cam:
        assert window.current_camera == cam and cam == cam_default
    assert window.current_camera == default_camera

    # Test that the camera is being used.
    cam_default.use()
    assert window.current_camera == cam_default
    default_camera.use()
    assert window.current_camera == default_camera

    set_view = cinematic.CameraData(
        (0, 0, 1, 1),  # Viewport
        (0.0, 0.0, 0.0),  # Position
        (0.0, 1.0, 0.0),  # Up
        (0.0, 0.0, 1.0),  # Forward
        1.0  # Zoom
    )
    set_projection = cinematic.OrthographicProjectionData(
        0.0, 1.0,  # Left, Right
        0.0, 1.0,  # Bottom, Top
        -1.0, 1.0  # Near, Far
    )
    cam_set = cinematic.OrthographicProjector(
        view=set_view,
        projection=set_projection
    )

    # test that the camera correctly used the provided Pods.
    assert cam_set.view == set_view
    assert cam_set.projection == set_projection

    # test that the camera properties work
    assert cam_set.position == set_view.position
    assert cam_set.viewport == set_view.viewport

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


def test_orthographic_projection_matrix():
    pass


def test_orthographic_view_matrix():
    pass


def test_orthographic_map_coordinates():
    pass
