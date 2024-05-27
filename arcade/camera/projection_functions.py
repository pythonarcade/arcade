from math import tan, pi
from typing import Optional, Union, Tuple

from pyglet.math import Vec2, Vec3, Vec4, Mat4
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
        ri.x, up.x, -fo.x, 0.0,
        ri.y, up.y, -fo.y, 0.0,
        ri.z, up.z, -fo.z, 0.0,
        -ri.dot(po), -up.dot(po), fo.dot(po), 1.0
    ))


def generate_orthographic_matrix(perspective_data: OrthographicProjectionData, zoom: float = 1.0):
    """
    Using the OrthographicProjectionData a projection matrix is generated where the size of an
    object is not affected by depth.

    Generally keep the scale value to integers or negative powers of integers (2^-1, 3^-1, 2^-2, etc.) to keep
    the pixels uniform in size. Avoid a zoom of 0.0.
    """

    # Scale the projection by the zoom value. Both the width and the height
    # share a zoom value to avoid ugly stretching.
    left = perspective_data.left / zoom
    right = perspective_data.right / zoom
    bottom = perspective_data.bottom / zoom
    top = perspective_data.top / zoom

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


def project_orthographic(world_coordinate: Vec3,
                         viewport: Tuple[int, int, int, int],
                         view_matrix: Mat4, projection_matrix: Mat4) -> Vec2:
    if len(world_coordinate) > 2:
        z = world_coordinate[2]
    else:
        z = 0.0
    x, y = world_coordinate[0], world_coordinate[1]

    world_position = Vec4(x, y, z, 1.0)

    projected_position = projection_matrix @ view_matrix @ world_position

    screen_coordinate_x = viewport[0] + (0.5 * projected_position.x + 0.5) * viewport[2]
    screen_coordinate_y = viewport[1] + (0.5 * projected_position.y + 0.5) * viewport[3]

    return Vec2(screen_coordinate_x, screen_coordinate_y)


def unproject_orthographic(screen_coordinate: Union[Vec2, Tuple[float, float]],
                           viewport: Tuple[int, int, int, int],
                           view_matrix: Mat4, projection_matrix: Mat4,
                           depth: Optional[float] = None) -> Vec3:
    screen_x = 2.0 * (screen_coordinate[0] - viewport[0]) / viewport[2] - 1
    screen_y = 2.0 * (screen_coordinate[1] - viewport[1]) / viewport[3] - 1

    _projection = ~projection_matrix
    _view = ~view_matrix

    _unprojected_position = _projection @ Vec4(screen_x, screen_y, 0.0, 1.0)
    _world_position = _view @ Vec4(_unprojected_position.x, _unprojected_position.y, depth or 0.0, 1.0)

    return Vec3(_world_position.x, _world_position.y, _world_position.z)


def project_perspective(world_coordinate: Vec3,
                        viewport: Tuple[int, int, int, int],
                        view_matrix: Mat4, projection_matrix: Mat4) -> Vec2:
    world_position = Vec4(world_coordinate.x, world_coordinate.y, world_coordinate.z, 1.0)

    semi_projected_position = projection_matrix @ view_matrix @ world_position
    div_val = semi_projected_position.w

    projected_x = semi_projected_position.x / div_val
    projected_y = semi_projected_position.y / div_val

    screen_coordinate_x = viewport[0] + (0.5 * projected_x + 0.5) * viewport[2]
    screen_coordinate_y = viewport[1] + (0.5 * projected_y + 0.5) * viewport[3]

    return Vec2(screen_coordinate_x, screen_coordinate_y)


def unproject_perspective(screen_coordinate: Union[Vec2, Tuple[float, float]],
                          viewport: Tuple[int, int, int, int],
                          view_matrix: Mat4, projection_matrix: Mat4,
                          depth: Optional[float] = None) -> Vec3:
    depth = depth or 1.0

    screen_x = 2.0 * (screen_coordinate[0] - viewport[0]) / viewport[2] - 1
    screen_y = 2.0 * (screen_coordinate[1] - viewport[1]) / viewport[3] - 1

    screen_x *= depth
    screen_y *= depth

    projected_position = Vec4(screen_x, screen_y, 1.0, 1.0)

    view_position = ~projection_matrix @ projected_position
    world_position = ~view_matrix @ Vec4(view_position.x, view_position.y, depth, 1.0)

    return Vec3(world_position.x, world_position.y, world_position.z)
