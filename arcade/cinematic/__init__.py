"""
The Cinematic Types, Classes, and Methods of Arcade.
Providing a multitude of camera's for any need.
"""

from arcade.cinematic.data import CameraData, OrthographicProjectionData, PerspectiveProjectionData
from arcade.cinematic.types import Projection, Projector, Camera

from arcade.cinematic.orthographic import OrthographicProjector
from arcade.cinematic.perspective import PerspectiveProjector

from arcade.cinematic.simple_camera import SimpleCamera
from arcade.cinematic.camera_2d import Camera2D

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
    'Camera2D'
]
