import pytest as pytest

from arcade import camera, Window
import arcade.camera.controllers as controllers


def test_strafe():
    # Given
    camera_data = camera.CameraData()
    directions = ((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0), (0.5, 0.5))

    # When
    camera_data.forward = (0.0 ,0.0, -1.0)
    camera_data.up = (0.0, 1.0, 0.0)

    # Then
    for dirs in directions:
        controllers.strafe(camera_data, dirs)
        assert camera_data.position == (dirs[0], dirs[1], 0.0), f"Strafe failed to move the camera data correctly, {dirs}"
        camera_data.position = (0.0, 0.0, 0.0)

    # Given
    camera_data.forward = (1.0, 0.0, 0.0)
    camera_data.up = (0.0, 1.0, 0.0)

    for dirs in directions:
        controllers.strafe(camera_data, dirs)
        assert camera_data.position == (0.0, dirs[1], dirs[0]), f"Strafe failed to move the camera data correctly, {dirs}"
        camera_data.position = (0.0, 0.0, 0.0)


def test_rotate_around_forward():
    # TODO

    # Given
    camera_data = camera.CameraData()

    # When
    controllers.rotate_around_forward(camera_data, 90)

    # Then
    assert camera_data.up == pytest.approx((-1.0, 0.0, 0.0))


def test_rotate_around_up(window: Window):
    # TODO

    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_rotate_around_right(window: Window):
    # TODO

    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_interpolate(window: Window):
    # TODO

    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_simple_follow(window: Window):
    # TODO

    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_simple_easing(window: Window):
    # TODO

    # Given
    camera_data = camera.CameraData()

    # When

    # Then
