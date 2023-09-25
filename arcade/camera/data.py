from typing import Tuple
from dataclasses import dataclass


__all__ = [
    'CameraData',
    'OrthographicProjectionData',
    'PerspectiveProjectionData'
]


@dataclass
class CameraData:
    """
    A PoD (Packet of Data) which holds the necessary data for a functional camera excluding the projection data.

    :param viewport: The pixel bounds which will be drawn onto. (left, bottom, width, height)

    :param position: A 3D vector which describes where the camera is located.
    :param up: A 3D vector which describes which direction is up (+y).
    :param forward: a 3D vector which describes which direction is forwards (+z).
    :param zoom: A scaler that records the zoom of the camera. While this most often affects the projection matrix
                 it allows camera controllers access to the zoom functionality
                 without interacting with the projection data.
    """
    # Viewport data
    viewport: Tuple[int, int, int, int]

    # View matrix data
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    up: Tuple[float, float, float] = (0.0, 1.0, 0.0)
    forward: Tuple[float, float, float] = (0.0, 0.0, -1.0)

    # Zoom
    zoom: float = 1.0


@dataclass
class OrthographicProjectionData:
    """
    A PoD (Packet of Data) which holds the necessary data for a functional Orthographic Projection matrix.

    This is by default a Left-handed system. with the X axis going from left to right, The Y axis going from
    bottom to top, and the Z axis going from towards the screen to away from the screen. This can be made
    right-handed by making the near value greater than the far value.

    :param left: The left most value, which gets mapped to x = -1.0 (anything below this value is not visible).
    :param right: The right most value, which gets mapped to x = 1.0 (anything above this value is not visible).
    :param bottom: The bottom most value, which gets mapped to y = -1.0 (anything below this value is not visible).
    :param top: The top most value, which gets mapped to y = 1.0 (anything above this value is not visible).
    :param near: The 'closest' value, which gets mapped to z = -1.0 (anything below this value is not visible).
    :param far: The 'furthest' value, Which gets mapped to z = 1.0 (anything above this value is not visible).
    """
    left: float
    right: float
    bottom: float
    top: float
    near: float
    far: float


@dataclass
class PerspectiveProjectionData:
    """
    A PoD (Packet of Data) which holds the necessary data for a functional Perspective matrix.

    :param aspect: The aspect ratio of the screen (width over height).
    :param fov: The field of view in degrees. With the aspect ratio defines
                the size of the projection at any given depth.
    :param near: The 'closest' value, which gets mapped to z = -1.0 (anything below this value is not visible).
    :param far: The 'furthest' value, Which gets mapped to z = 1.0 (anything above this value is not visible).
    """
    aspect: float
    fov: float
    near: float
    far: float
