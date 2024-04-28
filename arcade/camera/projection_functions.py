from math import tan, pi

from pyglet.math import Vec3, Mat4
from arcade.camera.data_types import CameraData, PerspectiveProjectionData, OrthographicProjectionData


def generate_view_matrix(camera_data: CameraData) -> Mat4:
    """
    Using the ViewData it generates a view matrix from the pyglet Mat4 look at function
    """
    # Even if forward and up are normalised floating point error means every vector must be normalised.
    fo = Vec3(*camera_data.forward).normalize()  # Forward Vector
    up = Vec3(*camera_data.up)  # Initial Up Vector (Not necessarily perpendicular to forward vector)
    ri = fo.cross(up).normalize()  # Right Vector
    up = ri.cross(fo).normalize()  # Up Vector
    po = Vec3(*camera_data.position)
    return Mat4((
        ri.x, up.x, -fo.x, 0,
        ri.y, up.y, -fo.y, 0,
        ri.z, up.z, -fo.z, 0,
        -ri.dot(po), -up.dot(po), fo.dot(po), 1
    ))


def generate_orthographic_matrix(perspective_data: OrthographicProjectionData, zoom: float = 1.0):
    """
    Using the OrthographicProjectionData a projection matrix is generated where the size of the
    objects is not affected by depth.

    Generally keep the scale value to integers or negative powers of integers (2^-1, 3^-1, 2^-2, etc.) to keep
    the pixels uniform in size. Avoid a zoom of 0.0.
    """

    # Find the center of the projection values (often 0,0 or the center of the screen)
    projection_x, projection_y = (
        (perspective_data.left + perspective_data.right) / 2.0,
        (perspective_data.bottom + perspective_data.top) / 2.0
    )

    # Find half the width of the projection
    half_width, half_height = (
        (perspective_data.right - perspective_data.left) / 2.0,
        (perspective_data.top - perspective_data.bottom) / 2.0
    )

    # Scale the projection by the zoom value. Both the width and the height
    # share a zoom value to avoid ugly stretching.
    left = projection_x - half_width / zoom
    right = projection_x + half_width / zoom
    bottom = projection_y - half_height / zoom
    top = projection_y + half_height / zoom

    z_near, z_far = perspective_data.near, perspective_data.far

    width = right - left
    height = top - bottom
    depth = z_far - z_near

    sx = 2.0 / width
    sy = 2.0 / height
    sz = 2.0 / -depth

    tx = -(right + left) / width
    ty = -(top + bottom) / height
    tz = -(z_far + z_near) / depth

    return Mat4((
         sx, 0.0, 0.0, 0.0,
        0.0,  sy, 0.0, 0.0,
        0.0, 0.0,  sz, 0.0,
         tx,  ty,  tz, 1.0
    ))


def generate_perspective_matrix(perspective_data: PerspectiveProjectionData, zoom: float = 1.0):
    """
    Using the OrthographicProjectionData a projection matrix is generated where the size of the
    objects is not affected by depth.

    Generally keep the scale value to integers or negative powers of integers (2^-1, 3^-1, 2^-2, etc.) to keep
    the pixels uniform in size. Avoid a zoom of 0.0.
    """
    fov = perspective_data.fov / zoom
    z_near, z_far, aspect = perspective_data.near, perspective_data.far, perspective_data.aspect

    xy_max = z_near * tan(fov * pi / 360)
    y_min = -xy_max
    x_min = -xy_max

    width = xy_max - x_min
    height = xy_max - y_min
    depth = z_far - z_near
    q = -(z_far + z_near) / depth
    qn = -2 * z_far * z_near / depth

    w = 2 * z_near / width
    w = w / aspect
    h = 2 * z_near / height

    return Mat4((
        w, 0, 0, 0,
        0, h, 0, 0,
        0, 0, q, -1,
        0, 0, qn, 0
    ))
