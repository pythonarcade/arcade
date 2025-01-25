"""
Area grips act similarly to position constrains used by physics engines. Much like
rotations the order of operations can have large impacts on the behavior of the
camera, so try and keep the number of area grips low.

The methods don't update the camera data directly incase you want to smoothly
interpolate towards the target position
"""

from arcade.camera.data_types import CameraData
from arcade.math import clamp
from arcade.types import Box, Point2, Point3, Rect


def constrain_x(data: CameraData, minimum: float, maximum: float) -> Point3:
    """
    Prevent the provided CameraData from leaving the provided bounds along the x-axis.
    assumed minimum < maximum
    """
    x, y, z = data.position
    if minimum <= x <= maximum:
        return data.position

    n_x = clamp(x, minimum, maximum)
    return n_x, y, z


def constrain_y(data: CameraData, minimum: float, maximum: float) -> Point3:
    """
    Prevent the provided CameraData from leaving the provided bounds along the y-axis.
    assumed minimum < maximum
    """
    x, y, z = data.position
    if minimum <= y <= maximum:
        return data.position

    n_y = clamp(y, minimum, maximum)
    return x, n_y, z


def constrain_z(data: CameraData, minimum: float, maximum: float) -> Point3:
    """
    Prevent the provided CameraData from leaving the provided bounds along the z-axis.
    assumed minimum < maximum
    """
    x, y, z = data.position
    if minimum <= z <= maximum:
        return data.position

    n_z = clamp(z, minimum, maximum)
    return x, y, n_z


def constrain_xy(data: CameraData, area: Rect) -> Point3:
    """
    Prevent the provided CameraData from leaving the provided Rect along the x and y-axis.
    Assumes area.left < area.right and area.bottom < area.top
    """
    x, y, z = data.position
    if area.point_in_rect((x, y)):
        return data.position

    n_x = clamp(x, area.left, area.right)
    n_y = clamp(y, area.bottom, area.top)

    return n_x, n_y, z


def constrain_yz(data: CameraData, area: Rect) -> Point3:
    """
    Prevent the provided CameraData from leaving the provided Rect along the y and z-axis.
    Assumes area.left < area.right and area.bottom < area.top
    """
    x, y, z = data.position
    if area.point_in_rect((y, z)):
        return data.position

    n_y = clamp(y, area.left, area.right)
    n_z = clamp(z, area.bottom, area.top)

    return x, n_y, n_z


def constrain_xz(data: CameraData, area: Rect) -> Point3:
    """
    Prevent the provided CameraData from leaving the provided Rect along the x and z-axis.
    Assumes area.left < area.right and area.bottom < area.top
    """
    x, y, z = data.position
    if area.point_in_rect((x, z)):
        return data.position

    n_x = clamp(x, area.left, area.right)
    n_z = clamp(z, area.bottom, area.top)

    return n_x, y, n_z


def constrain_xyz(data: CameraData, volume: Box) -> Point3:
    """
    Prevent the provided CameraData from leaving the provided Box along the x, y, and z-axis.
    assumes volume.left < volume.right, volume.bottom < volume.top, and volume.near < volume.far
    """
    x, y, z = data.position
    if volume.point_in_box((x, y, z)):
        return data.position

    n_x = clamp(x, volume.left, volume.right)
    n_y = clamp(y, volume.bottom, volume.top)
    n_z = clamp(z, volume.near, volume.far)

    return n_x, n_y, n_z


def constrain_boundary_x(data: CameraData, left: float, right: float, target_x: float) -> Point3:
    """
    Ensure that the target point is within the boundary values along the x-axis

    Assumes left < right
    """
    x, y, z = data.position
    dx = target_x - x
    if left <= dx <= right:
        return data.position

    n_x = target_x - clamp(dx, left, right)
    return n_x, y, z


def constrain_boundary_y(data: CameraData, bottom: float, top: float, target_y: float) -> Point3:
    """
    Ensure that the target point is within the boundary values along the y-axis

    Assumes bottom < top
    """
    x, y, z = data.position
    dy = target_y - y
    if bottom <= dy <= top:
        return data.position

    n_y = target_y - clamp(dy, bottom, top)
    return x, n_y, z


def constrain_boundary_z(data: CameraData, left: float, right: float, target_z: float) -> Point3:
    """
    Ensure that the target point is within the boundary values along the z-axis

    Assumes near < far
    """
    x, y, z = data.position
    dz = target_z - z
    if left <= dz <= right:
        return data.position

    n_z = target_z - clamp(dz, left, right)
    return x, y, n_z


def constrain_boundary_xy(data: CameraData, bounds: Rect, target: Point2) -> Point3:
    """
    Ensure that  the target point is within the boundary Rect along the x and y-axis

    Assumes bounds.left < bounds.right and bounds.bottom < bounds.top
    """
    x, y, z = data.position
    t_x, t_y = target
    dx = t_x - x
    dy = t_y - y
    if bounds.point_in_rect((dx, dy)):
        return data.position

    n_x = t_x - clamp(dx, bounds.left, bounds.right)
    n_y = t_y - clamp(dy, bounds.bottom, bounds.top)

    return n_x, n_y, z


def constrain_boundary_yz(data: CameraData, bounds: Rect, target: Point2) -> Point3:
    """
    Ensure that the target point is within the boundary Rect along the y and z-axis

    Assumes bounds.left < bounds.right and bounds.bottom < bounds.top
    """
    x, y, z = data.position
    t_y, t_z = target
    dy = t_y - y
    dz = t_z - z
    if bounds.point_in_rect((dy, dz)):
        return data.position

    n_y = t_y - clamp(dy, bounds.left, bounds.right)
    n_z = t_z - clamp(dz, bounds.bottom, bounds.top)

    return x, n_y, n_z


def constrain_boundary_xz(data: CameraData, bounds: Rect, target: Point2) -> Point3:
    """
    Ensure that the target point is within the boundary Rect along the x and z-axis

    Assumes bounds.left < bounds.right and bounds.bottom < bounds.top
    """
    x, y, z = data.position
    t_x, t_z = target
    dx = t_x - x
    dz = t_z - z
    if bounds.point_in_rect((dx, dz)):
        return data.position

    n_x = t_x - clamp(dx, bounds.left, bounds.right)
    n_z = t_z - clamp(dz, bounds.bottom, bounds.top)

    return n_x, y, n_z


def constrain_boundary_xyz(data: CameraData, bounds: Box, target: Point3) -> Point3:
    """
    Ensure that the target point is within the boundary Box along the x, y, and z-axis

    Assumes bounds.left < bounds.right, bounds.bottom < bounds.top, and bounds.near < bounds.right
    """
    x, y, z = data.position
    t_x, t_y, t_z = target
    dx = t_x - x
    dy = t_y - y
    dz = t_z - z
    if bounds.point_in_box((dx, dy, dz)):
        return data.position

    n_x = t_x - clamp(dx, bounds.left, bounds.right)
    n_y = t_y - clamp(dy, bounds.bottom, bounds.top)
    n_z = t_z - clamp(dz, bounds.near, bounds.far)

    return n_x, n_y, n_z
