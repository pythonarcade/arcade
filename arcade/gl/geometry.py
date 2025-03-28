"""
A module providing commonly used geometry
"""

import math
from array import array

from arcade.gl import BufferDescription, Context
from arcade.gl.vertex_array import Geometry


def _get_active_context() -> Context:
    """
    Get the global active context.

    The gl module is forbidden to reach outside of its own module.
    so we can't use ``arcade.get_window().ctx`` here.
    """
    ctx = Context.active
    if not ctx:
        raise RuntimeError("No context is currently activated")
    return ctx


def quad_2d_fs() -> Geometry:
    """Creates a screen aligned quad using normalized device coordinates"""
    return quad_2d(size=(2.0, 2.0))


def quad_2d(
    size: tuple[float, float] = (1.0, 1.0), pos: tuple[float, float] = (0.0, 0.0)
) -> Geometry:
    """
    Creates 2D quad Geometry using 2 triangle strip with texture coordinates.

    By default a unit quad is created with the center at (0, 0).

    Args:
        size:
            width and height of the quad
        pos:
            Center position x and y
    """
    ctx = _get_active_context()
    width, height = size
    x_pos, y_pos = pos

    # fmt: off
    data = array('f', [
        x_pos - width / 2.0, y_pos + height / 2.0, 0.0, 1.0,
        x_pos - width / 2.0, y_pos - height / 2.0, 0.0, 0.0,
        x_pos + width / 2.0, y_pos + height / 2.0, 1.0, 1.0,
        x_pos + width / 2.0, y_pos - height / 2.0, 1.0, 0.0,
    ])
    # fmt: on

    return ctx.geometry(
        [
            BufferDescription(
                ctx.buffer(data=data),
                "2f 2f",
                ["in_vert", "in_uv"],
            )
        ],
        mode=ctx.TRIANGLE_STRIP,
    )


def screen_rectangle(
    bottom_left_x: float, bottom_left_y: float, width: float, height: float
) -> Geometry:
    """
    Creates screen rectangle using 2 triangle strip with texture coordinates.

    This can create a rectangle in normalized device coordinates or projection space.

    Args:
        bottom_left_x:
            Bottom left x position
        bottom_left_y:
            Bottom left y position
        width:
            Width of the rectangle
        height:
            Height of the rectangle
    """
    ctx = _get_active_context()
    # fmt: off
    data = array('f', [
        bottom_left_x, bottom_left_y + height, 0.0, 1.0,
        bottom_left_x, bottom_left_y, 0.0, 0.0,
        bottom_left_x + width, bottom_left_y + height, 1.0, 1.0,
        bottom_left_x + width, bottom_left_y, 1.0, 0.0,
    ])
    # fmt: on
    return ctx.geometry(
        [
            BufferDescription(
                ctx.buffer(data=data),
                "2f 2f",
                ["in_vert", "in_uv"],
            )
        ],
        mode=ctx.TRIANGLE_STRIP,
    )


def cube(
    size: tuple[float, float, float] = (1.0, 1.0, 1.0),
    center: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Geometry:
    """
    Creates a cube with normals and texture coordinates.

    By default a unit cube is created with the center at (0, 0, 0).

    Args:
        size:
            Size of the cube as a 3-component tuple
        center:
            Center of the cube as a 3-component tuple
    Returns:
        A Geometry instance containing a cube
    """
    ctx = _get_active_context()
    width, height, depth = size
    width, height, depth = width / 2.0, height / 2.0, depth / 2.0

    # fmt: off
    pos = array('f', [
        center[0] + width, center[1] - height, center[2] + depth,
        center[0] + width, center[1] + height, center[2] + depth,
        center[0] - width, center[1] - height, center[2] + depth,
        center[0] + width, center[1] + height, center[2] + depth,
        center[0] - width, center[1] + height, center[2] + depth,
        center[0] - width, center[1] - height, center[2] + depth,
        center[0] + width, center[1] - height, center[2] - depth,
        center[0] + width, center[1] + height, center[2] - depth,
        center[0] + width, center[1] - height, center[2] + depth,
        center[0] + width, center[1] + height, center[2] - depth,
        center[0] + width, center[1] + height, center[2] + depth,
        center[0] + width, center[1] - height, center[2] + depth,
        center[0] + width, center[1] - height, center[2] - depth,
        center[0] + width, center[1] - height, center[2] + depth,
        center[0] - width, center[1] - height, center[2] + depth,
        center[0] + width, center[1] - height, center[2] - depth,
        center[0] - width, center[1] - height, center[2] + depth,
        center[0] - width, center[1] - height, center[2] - depth,
        center[0] - width, center[1] - height, center[2] + depth,
        center[0] - width, center[1] + height, center[2] + depth,
        center[0] - width, center[1] + height, center[2] - depth,
        center[0] - width, center[1] - height, center[2] + depth,
        center[0] - width, center[1] + height, center[2] - depth,
        center[0] - width, center[1] - height, center[2] - depth,
        center[0] + width, center[1] + height, center[2] - depth,
        center[0] + width, center[1] - height, center[2] - depth,
        center[0] - width, center[1] - height, center[2] - depth,
        center[0] + width, center[1] + height, center[2] - depth,
        center[0] - width, center[1] - height, center[2] - depth,
        center[0] - width, center[1] + height, center[2] - depth,
        center[0] + width, center[1] + height, center[2] - depth,
        center[0] - width, center[1] + height, center[2] - depth,
        center[0] + width, center[1] + height, center[2] + depth,
        center[0] - width, center[1] + height, center[2] - depth,
        center[0] - width, center[1] + height, center[2] + depth,
        center[0] + width, center[1] + height, center[2] + depth,
    ])
    normal = array('f', [
        -0, 0, 1,
        -0, 0, 1,
        -0, 0, 1,
        0, 0, 1,
        0, 0, 1,
        0, 0, 1,
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        1, 0, 0,
        0, -1, 0,
        0, -1, 0,
        0, -1, 0,
        0, -1, 0,
        0, -1, 0,
        0, -1, 0,
        -1, -0, 0,
        -1, -0, 0,
        -1, -0, 0,
        -1, -0, 0,
        -1, -0, 0,
        -1, -0, 0,
        0, 0, -1,
        0, 0, -1,
        0, 0, -1,
        0, 0, -1,
        0, 0, -1,
        0, 0, -1,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
        0, 1, 0,
    ])

    uv = array('f', [
        1, 0,
        1, 1,
        0, 0,
        1, 1,
        0, 1,
        0, 0,
        1, 0,
        1, 1,
        0, 0,
        1, 1,
        0, 1,
        0, 0,
        1, 1,
        0, 1,
        0, 0,
        1, 1,
        0, 0,
        1, 0,
        0, 1,
        0, 0,
        1, 0,
        0, 1,
        1, 0,
        1, 1,
        1, 0,
        1, 1,
        0, 1,
        1, 0,
        0, 1,
        0, 0,
        1, 1,
        0, 1,
        1, 0,
        0, 1,
        0, 0,
        1, 0
    ])
    # fmt: on

    return ctx.geometry(
        [
            BufferDescription(ctx.buffer(data=pos), "3f", ["in_position"]),
            BufferDescription(ctx.buffer(data=normal), "3f", ["in_normal"]),
            BufferDescription(ctx.buffer(data=uv), "2f", ["in_uv"]),
        ]
    )


def sphere(
    radius=0.5,
    sectors=32,
    rings=16,
    normals=True,
    uvs=True,
) -> Geometry:
    """
    Creates a 3D sphere.

    Args:
        radius:
            Radius or the sphere
        rings:
            number or horizontal rings
        sectors:
            number of vertical segments
        normals:
            Include normals
        uvs:
            Include texture coordinates
    Returns:
        A Geometry instance containing a sphere
    """
    ctx = _get_active_context()

    R = 1.0 / (rings - 1)
    S = 1.0 / (sectors - 1)

    vertices = [0.0] * (rings * sectors * 3)
    normals = [0.0] * (rings * sectors * 3)
    uvs = [0.0] * (rings * sectors * 2)

    v, n, t = 0, 0, 0
    for r in range(rings):
        for s in range(sectors):
            y = math.sin(-math.pi / 2 + math.pi * r * R)
            x = math.cos(2 * math.pi * s * S) * math.sin(math.pi * r * R)
            z = math.sin(2 * math.pi * s * S) * math.sin(math.pi * r * R)

            uvs[t] = s * S
            uvs[t + 1] = r * R

            vertices[v] = x * radius
            vertices[v + 1] = y * radius
            vertices[v + 2] = z * radius

            normals[n] = x
            normals[n + 1] = y
            normals[n + 2] = z

            t += 2
            v += 3
            n += 3

    indices = [0] * rings * sectors * 6
    i = 0
    for r in range(rings - 1):
        for s in range(sectors - 1):
            indices[i] = r * sectors + s
            indices[i + 1] = (r + 1) * sectors + (s + 1)
            indices[i + 2] = r * sectors + (s + 1)

            indices[i + 3] = r * sectors + s
            indices[i + 4] = (r + 1) * sectors + s
            indices[i + 5] = (r + 1) * sectors + (s + 1)
            i += 6

    content = [
        BufferDescription(ctx.buffer(data=array("f", vertices)), "3f", ["in_position"]),
    ]
    if normals:
        content.append(BufferDescription(ctx.buffer(data=array("f", normals)), "3f", ["in_normal"]))
    if uvs:
        content.append(BufferDescription(ctx.buffer(data=array("f", uvs)), "2f", ["in_uv"]))

    return ctx.geometry(
        content,
        index_buffer=ctx.buffer(data=array("I", indices)),
        mode=ctx.TRIANGLES,
    )
