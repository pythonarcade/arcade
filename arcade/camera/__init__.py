"""
The Camera Types, Classes, and Methods of Arcade.
Providing a multitude of camera's for any need.
"""

from .data_types import (
    Projection,
    Projector,
    CameraData,
    OrthographicProjectionData,
    PerspectiveProjectionData,
)

from .projection_functions import (
    generate_view_matrix,
    generate_orthographic_matrix,
    generate_perspective_matrix,
    project_orthographic,
    project_perspective,
    unproject_orthographic,
    unproject_perspective,
)

from .viewport import ViewportProjector
from .orthographic import OrthographicProjector
from .perspective import PerspectiveProjector
from .camera_2d import Camera2D

import arcade.camera.grips as grips


__all__ = [
    "Projection",
    "Projector",
    "ViewportProjector",
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
