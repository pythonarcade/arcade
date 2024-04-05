import pytest

import arcade
from arcade.gui import UIMouseReleaseEvent
from pyglet.math import Vec2


@pytest.mark.xfail
def test_ui_manager_respects_camera_viewport(uimanager, window):
    # GIVEN
    uimanager.use_super_mouse_adjustment = True
    camera = arcade.camera.Camera2D(position=(0.0, 0.0), projection=(0.0, window.width, 0.0, window.height),
                                    window=window)

    # WHEN
    camera.viewport = 0, 0, 400, 200
    camera.use()

    uimanager.click(100, 100)

    # THEN
    assert isinstance(uimanager.last_event, UIMouseReleaseEvent)
    assert uimanager.last_event.pos == (pytest.approx(200), pytest.approx(300))


@pytest.mark.xfail
def test_ui_manager_respects_camera_pos(uimanager, window):
    # GIVEN
    uimanager.use_super_mouse_adjustment = True
    camera = arcade.camera.Camera2D(position=(0.0, 0.0), projection=(0.0, window.width, 0.0, window.height),
                                    window=window)

    # WHEN
    camera.position = (100, 100)
    camera.use()

    uimanager.click(100, 100)

    # THEN
    assert isinstance(uimanager.last_event, UIMouseReleaseEvent)
    assert uimanager.last_event.pos == (pytest.approx(200), pytest.approx(200))
