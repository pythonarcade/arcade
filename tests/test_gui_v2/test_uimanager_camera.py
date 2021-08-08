import pytest

import arcade
from arcade.experimental.gui_v2 import UIMouseReleaseEvent
from arcade.math import Vec2


@pytest.mark.xfail
def test_ui_manager_respects_camera_viewport(uimanager, window):
    # GIVEN
    uimanager.use_super_mouse_adjustment = True
    camera = arcade.Camera(window=window, viewport_width=window.width, viewport_height=window.height)

    # WHEN
    window.set_size(width=600, height=400)
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
    camera = arcade.Camera(window=window, viewport_width=window.width, viewport_height=window.height)

    # WHEN
    window.set_size(width=600, height=400)
    camera.position = Vec2(-100,-100)
    camera.update()
    camera.use()

    uimanager.click(100, 100)

    # THEN
    assert isinstance(uimanager.last_event, UIMouseReleaseEvent)
    assert uimanager.last_event.pos == (200, 200)
