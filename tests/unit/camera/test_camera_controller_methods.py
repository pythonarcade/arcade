import pytest as pytest

from arcade import camera, Window
import arcade.camera.grips as grips


def test_strafe():
    # Given
    camera_data = camera.CameraData()
    directions = ((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0), (0.5, 0.5))

    # When
    camera_data.forward = (0.0, 0.0, -1.0)
    camera_data.up = (0.0, 1.0, 0.0)

    # Then
    for dirs in directions:
        camera_data.position = grips.strafe(camera_data, dirs)
        assert camera_data.position == (dirs[0], dirs[1], 0.0), f"Strafe failed to move the camera data correctly, {dirs}"
        camera_data.position = (0.0, 0.0, 0.0)

    # Given
    camera_data.forward = (1.0, 0.0, 0.0)
    camera_data.up = (0.0, 1.0, 0.0)

    for dirs in directions:
        camera_data.position = grips.strafe(camera_data, dirs)
        assert camera_data.position == (0.0, dirs[1], dirs[0]), f"Strafe failed to move the camera data correctly, {dirs}"
        camera_data.position = (0.0, 0.0, 0.0)


def test_rotate_around_forward():
    # Given
    camera_data = camera.CameraData()

    # When
    camera_data.up = grips.rotate_around_forward(camera_data, 90)

    # Then
    assert camera_data.up == pytest.approx((-1.0, 0.0, 0.0))


def test_rotate_around_up(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When
    camera_data.forward = grips.rotate_around_up(camera_data, 90)

    # Then
    assert camera_data.forward == pytest.approx((1.0, 0.0, 0.0))


def test_rotate_around_right(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When
    camera_data.up, camera_data.forward = grips.rotate_around_right(camera_data, 90)

    # Then
    assert camera_data.up == pytest.approx((0.0, 0.0, -1.0))
    assert camera_data.forward == pytest.approx((0.0, -1.0, 0.0))
