"""
Low level tests for OpenGL 3.3 wrappers.
"""
from arcade.gl import geometry


def test_quad_2d_fs(ctx):
    geo = geometry.quad_2d_fs()
    assert geo.ctx == ctx
    assert geo.num_vertices == 4
    assert geo._mode == ctx.TRIANGLE_STRIP


def test_quad_2d(ctx):
    geo = geometry.quad_2d()
    assert geo.ctx == ctx
    assert geo.num_vertices == 4
    assert geo._mode == ctx.TRIANGLE_STRIP


def test_screen_rectangle(ctx):
    geo = geometry.screen_rectangle(0, 100, 0, 100)
    assert geo.ctx == ctx
    assert geo.num_vertices == 4
    assert geo._mode == ctx.TRIANGLE_STRIP
