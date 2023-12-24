import pytest as pytest

from arcade import camera, Window
import arcade.camera.controllers as controllers


def test_strafe(window: Window):
    # Given
    camera_data = camera.CameraData()
    directions = ((1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0), (0.5, 0.5))

    # When
    camera_data.forward = (0.0 ,0.0, -1.0)
    camera_data.up = (0.0, 0.0, 1.0)

    # Then
    for dirs in directions:
        controllers.strafe(camera_data, dirs)
        assert (
            camera_data.position == (dirs[0], dirs[1], 0.0),
            f"Strafe failed to move the camera data correctly, {dirs}"
        )
        camera_data.position = (0.0, 0.0, 0.0)

    # Given
    camera_data.forward = (0.0, 0.0, -1.0)
    camera_data.up = (0.0, 0.0, 1.0)

    for dirs in directions:
        controllers.strafe(camera_data, dirs)
        assert (
            camera_data.position == (0.0, dirs[1], dirs[0]),
            f"Strafe failed to move the camera data correctly, {dirs}"
        )
        camera_data.position = (0.0, 0.0, 0.0)


def test_rotate_around_forward(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_rotate_around_up(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_rotate_around_right(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_interpolate(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_simple_follow(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When

    # Then


def test_simple_easing(window: Window):
    # Given
    camera_data = camera.CameraData()

    # When

    # Then
