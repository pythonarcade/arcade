import pytest as pytest

from pyglet.math import Vec3, Vec2

from arcade import camera, Window
from arcade.types import Point, LBWH, Rect

@pytest.mark.parametrize("wrld_pos", [Vec2(100, 150), Vec2(1280, 720), Vec3(500, 500, -10)])
def test_viewport_projector_project(window: Window, wrld_pos: Point):
    cam = camera.default.ViewportProjector()
    assert cam.project(wrld_pos) == wrld_pos.xy

@pytest.mark.parametrize("wrld_pos", [Vec2(100, 150), Vec2(1280, 720), Vec3(500, 500, -10)])
def test_viewport_projector_unproject(window: Window, wrld_pos: Point):
    cam = camera.default.ViewportProjector()
    x, y, *z = wrld_pos

    assert cam.unproject(wrld_pos) == Vec3(x, y, 0.0 if not z else z[0])

@pytest.mark.parametrize("viewport", [LBWH(0.0, 0.0, 100, 200), LBWH(100, 100, 20, 40), LBWH(300, 20, 20, 700)])
def test_viewport_projector_viewport(window: Window, viewport: Rect):
    cam = camera.default.ViewportProjector()
    assert cam.viewport.lbwh_int == window.ctx.viewport
    cam.viewport = viewport
    assert cam.viewport == viewport
