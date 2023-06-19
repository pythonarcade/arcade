"""
The Cinematic Types, Classes, and Methods of Arcade.
Providing a multitude of camera's for any need.
"""

from arcade.cinematic.data import ViewData, OrthographicProjectionData, PerspectiveProjectionData
from arcade.cinematic.types import Projection, Projector, Camera

from arcade.cinematic.orthographic import OrthographicCamera
from arcade.cinematic.perspective import PerspectiveCamera

from arcade.cinematic.simple_camera import SimpleCamera
from arcade.cinematic.camera_2D import Camera2D

__all__ = [
    'Projection',
    'Projector',
    'Camera',
    'ViewData',
    'OrthographicProjectionData',
    'OrthographicCamera',
    'PerspectiveProjectionData',
    'PerspectiveCamera',
    'SimpleCamera',
    'Camera2D'
]
