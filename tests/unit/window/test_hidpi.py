"""
Drawing on scaled (HiDPI) displays.

CI runs at a pixel ratio of 1, so these tests make the window report a
framebuffer twice its size, like a scaled display in pyglet's "stretch"
mode, which Arcade uses by default.
"""

from ctypes import c_int

import pytest
from pyglet.graphics.api.gl import GL_SCISSOR_BOX, GL_VIEWPORT, glGetIntegerv

import arcade


def _gl_box(name) -> tuple[int, int, int, int]:
    box = (c_int * 4)()
    glGetIntegerv(name, box)
    return tuple(box)


@pytest.fixture
def scaled_window(window, monkeypatch):
    """The window, reporting a framebuffer twice its size"""
    width, height = window.get_size()
    monkeypatch.setattr(window, "get_framebuffer_size", lambda: (width * 2, height * 2))
    window.ctx.viewport = 0, 0, width, height
    window.default_camera.use()
    yield window
    monkeypatch.undo()
    window.ctx.viewport = 0, 0, width, height
    window.default_camera.use()


def test_pixel_ratio_is_framebuffer_over_window(scaled_window):
    assert scaled_window.get_pixel_ratio() == 2.0


def test_pixel_ratio_ignores_display_scale(window, monkeypatch):
    """
    pyglet's own ratio is the display scale, which isn't the framebuffer
    ratio when the framebuffer is the same size as the window
    """
    monkeypatch.setattr(type(window), "scale", property(lambda self: 1.25))
    assert window.get_framebuffer_size() == window.get_size()
    assert window.get_pixel_ratio() == 1.0


def test_viewport_is_in_pixels(scaled_window):
    width, height = scaled_window.get_size()
    assert scaled_window.ctx.viewport == (0, 0, width, height)
    assert _gl_box(GL_VIEWPORT) == (0, 0, width * 2, height * 2)


def test_text_keeps_the_scaled_viewport(scaled_window):
    """
    pyglet sets the window camera's viewport and scissor when it draws
    text. They used to be in window units, so text was drawn too small,
    and everything drawn after it in the same viewport as well.
    """
    width, height = scaled_window.get_size()
    pixels = (0, 0, width * 2, height * 2)
    sprites = arcade.SpriteList()
    sprites.append(arcade.SpriteSolidColor(10, 10, 50, 50))

    arcade.Text("Hello", 10, 10).draw()
    assert _gl_box(GL_VIEWPORT) == pixels
    assert _gl_box(GL_SCISSOR_BOX) == pixels

    sprites.draw()
    arcade.Text("Again", 10, 30).draw()
    assert _gl_box(GL_VIEWPORT) == pixels
    assert _gl_box(GL_SCISSOR_BOX) == pixels


def test_text_with_camera_keeps_the_scaled_viewport(scaled_window):
    width, height = scaled_window.get_size()
    camera = arcade.Camera2D()
    camera.use()
    arcade.Text("Hello", 10, 10).draw()
    assert _gl_box(GL_VIEWPORT) == (0, 0, width * 2, height * 2)


def test_default_camera_reports_pixels(scaled_window):
    """pyglet reads the window camera's viewport and scissor in framebuffer pixels"""
    width, height = scaled_window.get_size()
    camera = scaled_window.default_camera
    assert camera.viewport == (0, 0, width * 2, height * 2)
    scissor = camera.get_group_scissor_area()
    assert (scissor.x, scissor.y, scissor.width, scissor.height) == (0, 0, width * 2, height * 2)
    # Arcade's own idea of the viewport stays in window units
    assert camera.get_current_viewport() == (0, 0, width, height)
    assert (camera.width, camera.height) == (width, height)


def test_offscreen_framebuffer_is_not_scaled(scaled_window):
    """Framebuffers you create have their own pixel size, whatever the display"""
    ctx = scaled_window.ctx
    fbo = ctx.framebuffer(color_attachments=[ctx.texture((64, 32), components=4)])
    with fbo.activate():
        arcade.Text("Hello", 1, 1).draw()
        assert _gl_box(GL_VIEWPORT) == (0, 0, 64, 32)
        assert scaled_window.default_camera.viewport == (0, 0, 64, 32)
