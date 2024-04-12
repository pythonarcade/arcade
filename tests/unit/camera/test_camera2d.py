from typing import Tuple

import pytest as pytest

from arcade import Window
from arcade.camera import Camera2D
from arcade.camera.data_types import ZeroProjectionDimension


class Camera2DSub1(Camera2D):
    ...

class Camera2DSub2(Camera2DSub1):
    ...


CAMERA2D_SUBS = [Camera2DSub1, Camera2DSub2]
ALL_CAMERA2D_TYPES = [Camera2D] + CAMERA2D_SUBS


AT_LEAST_ONE_EQUAL_VIEWPORT_DIMENSION = [
    (-100., -100., -1., 1.),
    (100., 100., -1., 1.),
    (0., 0., 1., 2.),
    (0., 1., -100., -100.),
    (-1., 1., 0., 0.),
    (1., 2., 100., 100.),
    (5., 5., 5., 5.)
]


@pytest.mark.parametrize("bad_projection", AT_LEAST_ONE_EQUAL_VIEWPORT_DIMENSION)
@pytest.mark.parametrize("camera_class", ALL_CAMERA2D_TYPES)
def test_camera2d_from_raw_data_bound_validation(
    window: Window,
    bad_projection: Tuple[float, float, float, float],  # Clarify type for PyCharm
    camera_class
):
    with pytest.raises(ZeroProjectionDimension):
        camera_class.from_raw_data(projection=bad_projection)


@pytest.mark.parametrize("camera_class", CAMERA2D_SUBS)
def test_camera2d_from_raw_data_inheritance_safety(
    window: Window,
    camera_class
):
    subclassed = camera_class.from_raw_data(zoom=10.0)
    assert isinstance(subclassed, Camera2DSub1)


RENDER_TARGET_SIZES = [
    (800, 600),  # Normal window size
    (1280, 720), # Bigger
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
def test_camera2d_from_raw_data_uses_render_target_size(window: Window, width, height):

    size = (width, height)
    texture = window.ctx.texture(size, components=4)
    framebuffer = window.ctx.framebuffer(color_attachments=[texture])

    ortho_camera = Camera2D.from_raw_data(render_target=framebuffer)
    assert ortho_camera.viewport_width == width
    assert ortho_camera.viewport_height == height

    assert ortho_camera.viewport == (0, 0, width, height)
    assert ortho_camera.viewport_left == 0
    assert ortho_camera.viewport_right == width
    assert ortho_camera.viewport_bottom == 0
    assert ortho_camera.viewport_top == height
