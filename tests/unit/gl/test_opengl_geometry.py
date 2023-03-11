"""
Low level tests for OpenGL 3.3 wrappers.
"""
from arcade.gl import geometry


def test_quad_2d_fs(ctx):
    geometry.quad_2d_fs()


def test_quad_2d(ctx):
    geometry.quad_2d()


def test_screen_rectangle(ctx):
    geometry.screen_rectangle(0, 100, 0, 100)
