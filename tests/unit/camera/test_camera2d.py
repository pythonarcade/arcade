import pytest as pytest

from arcade import Window
from arcade.camera import Camera2D


def test_camera2d_from_raw_data_inheritance_safety(window: Window):
    class MyCamera2D(Camera2D):
        ...

    subclassed = MyCamera2D.from_raw_data(zoom=10.0)
    assert isinstance(subclassed, MyCamera2D)


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
