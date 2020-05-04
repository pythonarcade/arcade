"""
Low level tests for OpenGL 3.3 wrappers.
"""
import pytest
import arcade
from arcade.gl import geometry

from pyglet import gl

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


@pytest.fixture(scope="module")
def ctx():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Test OpenGL")
    yield window.ctx
    window.close()


def test_quad_2d_fs(ctx):
    geometry.quad_2d_fs()


def test_quad_2d(ctx):
    geometry.quad_2d()


def test_screen_rectangle(ctx):
    geometry.screen_rectangle(0, 100, 0, 100)
