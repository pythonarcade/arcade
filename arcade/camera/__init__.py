"""
The Cinematic Types, Classes, and Methods of Arcade.
Providing a multitude of camera's for any need.
"""

from arcade.camera.data_types import Projection, Projector, CameraData, OrthographicProjectionData

from arcade.camera.orthographic import OrthographicProjector

from arcade.camera.simple_camera import SimpleCamera
from arcade.camera.camera_2d import Camera2D

import arcade.camera.controllers as controllers

__all__ = [
    'Projection',
    'Projector',
    'CameraData',
    'OrthographicProjectionData',
    'OrthographicProjector',
    'SimpleCamera',
    'Camera2D',
    'controllers'
]
