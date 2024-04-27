"""
The Cinematic Types, Classes, and Methods of Arcade.
Providing a multitude of camera's for any need.
"""

from arcade.camera.data_types import (
    Projection,
    Projector,
    CameraData,
    OrthographicProjectionData,
    PerspectiveProjectionData
)

from arcade.camera.orthographic import OrthographicProjector
from arcade.camera.perspective import PerspectiveProjector

from arcade.camera.camera_2d import Camera2D

import arcade.camera.grips as grips


__all__ = [
    'Projection',
    'Projector',
    'CameraData',
    'OrthographicProjectionData',
    'OrthographicProjector',
    'PerspectiveProjectionData',
    'PerspectiveProjector',
    'Camera2D',
    'grips'
]
