"""
The Cinematic Types, Classes, and Methods of Arcade.
Providing a multitude of camera's for any need.
"""

from arcade.camera.data import CameraData, OrthographicProjectionData, PerspectiveProjectionData
from arcade.camera.types import Projection, Projector, Camera

from arcade.camera.orthographic import OrthographicProjector
from arcade.camera.perspective import PerspectiveProjector

from arcade.camera.simple_camera import SimpleCamera
from arcade.camera.camera_2d import Camera2D

import arcade.camera.controllers as controllers

__all__ = [
    'Projection',
    'Projector',
    'Camera',
    'CameraData',
    'OrthographicProjectionData',
    'OrthographicProjector',
    'PerspectiveProjectionData',
    'PerspectiveProjector',
    'SimpleCamera',
    'Camera2D',
    'controllers'
]
