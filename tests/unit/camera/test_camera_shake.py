from arcade import camera, Window
from arcade.camera.grips import ScreenShake2D


def test_reset(window: Window):
    # Given
    camera_view = camera.CameraData()
    screen_shaker = ScreenShake2D(camera_view)

    # When
    screen_shaker.start()
    screen_shaker.update(1.0)
    screen_shaker.update_camera()
    screen_shaker.readjust_camera()
    screen_shaker.reset()

    # Then
    assert screen_shaker._current_dir == 0.0, "ScreenShakeController failed to reset properly [current_dir]"
    assert screen_shaker._last_vector == (0.0, 0.0, 0.0), "ScreenShakeController failed to reset properly [last_vector]"
    assert screen_shaker._length_shaking == 0.0, "ScreenShakeController failed to reset properly [length_shaking]"
    assert screen_shaker._last_update_time == 0.0, "ScreenShakeController failed to reset properly [last_update_time]"


def test_update(window: Window):
    # Given
    camera_view = camera.CameraData()
    screen_shaker = ScreenShake2D(camera_view)

    # When
    screen_shaker.update(1/60)

    # Then
    assert screen_shaker._length_shaking == 0.0, "ScreenShakeController updated when it had not started"

    # When
    screen_shaker.start()
    screen_shaker.update(1/60)

    # Then
    assert screen_shaker._length_shaking == 1/60, "ScreenShakeController failed to update by the correct dt"

    # When
    screen_shaker.stop()
    screen_shaker.update(1/60)

    # Then
    assert screen_shaker._length_shaking == 0.0, "ScreenShakeController failed to stop updating"

    # When
    screen_shaker.start()
    screen_shaker.update(2.0)

    # Then
    assert not screen_shaker.shaking, "ScreenShakeController failed to stop when shaking for too long"


def test_update_camera(window: Window):
    # Given
    camera_view = camera.CameraData()
    screen_shaker = ScreenShake2D(camera_view)

    cam_pos = camera_view.position

    # When
    screen_shaker.start()
    screen_shaker.update(1/60)
    screen_shaker.update_camera()

    # Then
    assert camera_view.position != cam_pos, "ScreenShakeController failed to change the camera's position"
    assert screen_shaker._last_vector != (0.0, 0.0, 0.0), "ScreenShakeController failed to store the last vector"
    _adjust_test = (
        camera_view.position[0] - screen_shaker._last_vector[0],
        camera_view.position[1] - screen_shaker._last_vector[1],
        camera_view.position[2] - screen_shaker._last_vector[2],
    )
    assert _adjust_test == cam_pos, "ScreenShakeController failed to store the correct last vector"


def test_readjust_camera(window: Window):
    camera_view = camera.CameraData()
    screen_shaker = ScreenShake2D(camera_view)

    cam_pos = camera_view.position

    # When
    screen_shaker.start()
    screen_shaker.update(1 / 60)
    screen_shaker.update_camera()
    screen_shaker.readjust_camera()

    # Then
    assert camera_view.position == cam_pos, "ScreenShakeController failed to readjust the camera position"
    assert screen_shaker._last_vector == (0.0, 0.0, 0.0), "ScreenShakeController failed to reset the last vector"
