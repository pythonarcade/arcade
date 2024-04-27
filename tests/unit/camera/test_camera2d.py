from typing import Tuple

import pytest as pytest

from arcade import Window
from arcade.camera import Camera2D
from arcade.camera.data_types import ZeroProjectionDimension, OrthographicProjectionData


class Camera2DSub1(Camera2D):
    ...

class Camera2DSub2(Camera2DSub1):
    ...


CAMERA2D_SUBS = [Camera2DSub1, Camera2DSub2]
ALL_CAMERA2D_TYPES = [Camera2D] + CAMERA2D_SUBS


@pytest.fixture(params=ALL_CAMERA2D_TYPES)
def camera_class(request):
    return request.param


AT_LEAST_ONE_EQUAL_VIEWPORT_DIMENSION = [
    (-100., -100., -1., 1.),
    (100., 100., -1., 1.),
    (0., 0., 1., 2.),
    (0., 1., -100., -100.),
    (-1., 1., 0., 0.),
    (1., 2., 100., 100.),
    (5., 5., 5., 5.)
]

NEAR_FAR_VALUES = [-50.,0.,50.]


@pytest.fixture(params=AT_LEAST_ONE_EQUAL_VIEWPORT_DIMENSION)
def bad_projection(request):
    return request.param


@pytest.fixture(params=NEAR_FAR_VALUES)
def same_near_far(request):
    return request.param


def test_camera2d_from_camera_data_projection_xy_pairs_equal_raises_zeroprojectiondimension(
    window: Window,
    bad_projection: Tuple[float, float, float, float],  # Clarify type for PyCharm
    camera_class
):
    data = OrthographicProjectionData(
        *bad_projection, -100.0, 100.0,
        viewport=(0, 0, 800, 600)
    )

    with pytest.raises(ZeroProjectionDimension):
        _ = camera_class.from_camera_data(projection_data=data)


def test_camera2d_init_xy_pairs_equal_raises_zeroprojectiondimension(
    window: Window,
    bad_projection: Tuple[float, float, float, float],
    camera_class
):

    with pytest.raises(ZeroProjectionDimension):
        _ = camera_class(projection=bad_projection)


def test_camera2d_init_equal_near_far_raises_zeroprojectiondimension(
        window: Window,
        same_near_far: float,
        camera_class
):
    near_far = same_near_far
    with pytest.raises(ZeroProjectionDimension):
        camera_class(near=near_far, far=near_far)


@pytest.mark.parametrize("camera_class", CAMERA2D_SUBS)
def test_camera2d_init_inheritance_safety(
    window: Window,
    camera_class
):
    subclassed = camera_class(zoom=10.0)
    assert isinstance(subclassed, Camera2DSub1)


RENDER_TARGET_SIZES = [
    (800, 600),  # Normal window size
    (1280, 720),  # Bigger
    (16, 16)  # Tiny
]


@pytest.mark.parametrize("width, height", RENDER_TARGET_SIZES)
def test_camera2d_init_uses_render_target_size(window: Window, width, height):

    size = (width, height)
    texture = window.ctx.texture(size, components=4)
    framebuffer = window.ctx.framebuffer(color_attachments=[texture])

    ortho_camera = Camera2D(render_target=framebuffer)
    assert ortho_camera.viewport_width == width
    assert ortho_camera.viewport_height == height

    assert ortho_camera.viewport == (0, 0, width, height)
    assert ortho_camera.viewport_left == 0
    assert ortho_camera.viewport_right == width
    assert ortho_camera.viewport_bottom == 0
    assert ortho_camera.viewport_top == height


@pytest.mark.parametrize("width, height", RENDER_TARGET_SIZES)
def test_camera2d_from_camera_data_uses_render_target_size(window: Window, width, height):

    size = (width, height)
    texture = window.ctx.texture(size, components=4)
    framebuffer = window.ctx.framebuffer(color_attachments=[texture])

    ortho_camera = Camera2D.from_camera_data(render_target=framebuffer)
    assert ortho_camera.viewport_width == width
    assert ortho_camera.viewport_height == height

    assert ortho_camera.viewport == (0, 0, width, height)
    assert ortho_camera.viewport_left == 0
    assert ortho_camera.viewport_right == width
    assert ortho_camera.viewport_bottom == 0
    assert ortho_camera.viewport_top == height
