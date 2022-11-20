import pytest

import arcade
from arcade.gui import UIMouseReleaseEvent
from pyglet.math import Vec2


@pytest.mark.xfail
def test_ui_manager_respects_camera_viewport(uimanager, window):
    # GIVEN
    uimanager.use_super_mouse_adjustment = True
    camera = arcade.Camera(viewport=(0, 0, window.width, window.height), window=window)

    # WHEN
    camera.viewport = 0, 0, 300, 200
    camera.use()

    uimanager.click(100, 100)

    # THEN
    assert isinstance(uimanager.last_event, UIMouseReleaseEvent)
    assert uimanager.last_event.pos == (200, 200)

@pytest.mark.xfail
def test_ui_manager_respects_camera_pos(uimanager, window):
    # GIVEN
    uimanager.use_super_mouse_adjustment = True
    camera = arcade.Camera(viewport=(0, 0, window.width, window.height), window=window)

    # WHEN
    camera.position = Vec2(-100, -100)
    camera.update()
    camera.use()

    uimanager.click(100, 100)

    # THEN
    assert isinstance(uimanager.last_event, UIMouseReleaseEvent)
    assert uimanager.last_event.pos == (200, 200)
