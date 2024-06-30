"""
The Camera Types, Classes, and Methods of Arcade.
Providing a multitude of camera's for any need.
"""

from arcade.camera.data_types import (
    Projection,
    Projector,
    CameraData,
    OrthographicProjectionData,
    PerspectiveProjectionData,
)

from arcade.camera.projection_functions import (
    generate_view_matrix,
    generate_orthographic_matrix,
    generate_perspective_matrix,
    project_orthographic,
    project_perspective,
    unproject_orthographic,
    unproject_perspective,
)

from arcade.camera.orthographic import OrthographicProjector
from arcade.camera.perspective import PerspectiveProjector

from arcade.camera.camera_2d import Camera2D

import arcade.camera.grips as grips


__all__ = [
    "Projection",
    "Projector",
    "CameraData",
    "generate_view_matrix",
    "OrthographicProjectionData",
    "generate_orthographic_matrix",
    "project_orthographic",
    "unproject_orthographic",
    "OrthographicProjector",
    "PerspectiveProjectionData",
    "generate_perspective_matrix",
    "project_perspective",
    "unproject_perspective",
    "PerspectiveProjector",
    "Camera2D",
    "grips",
]
