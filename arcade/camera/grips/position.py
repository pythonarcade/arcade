from pyglet.math import Vec3

from arcade.camera import CameraData
from arcade.math import quaternion_rotation
from arcade.types import Point3


def look_at(camera: CameraData, target: Point3, up: Point3 | None = None) -> tuple[Point3, Point3]:
    """
    Calculate the neccisary forward and up vectors to have the camera look towards
    the target point.

    Uses the camera's up if none is provided.
    Args:
        camera: The CameraData to work from
        target: The point in 3D world space to look at
        up: An optional up axis to refer to when calculating the true up vector.
    """
    px, py, pz = camera.position
    tx, ty, tz = target
    dx, dy, dz = tx - px, ty - py, tz - pz

    up = up or camera.up

    f = Vec3(dx, dy, dz).normalize()
    r = f.cross(up)
    u = r.cross(f).normalize()

    return f, u


def orbit(camera: CameraData, origin: Point3, axis: Point3, angle: float) -> Point3:
    """
    Find the new position for the camera when rotated around the origin

    Args:
        camera: The CameraData to work from
        origin: The point around which to orbit
        axis: The axis to rotate around, like the stick on a spinning top.
        angle: The angle in degrees to rotate by
    """
    px, py, pz = camera.position
    tx, ty, tz = origin

    rx, ry, rz = quaternion_rotation(axis, (px - tx, py - ty, pz - tz), angle)
    return tx + rx, ty + ry, tz + rz
