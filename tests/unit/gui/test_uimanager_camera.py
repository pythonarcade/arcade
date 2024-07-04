from unittest.mock import Mock

import arcade
from arcade import LBWH
from arcade.gui import UIFlatButton


def test_ui_manager_respects_window_camera(uimanager, window):
    # GIVEN
    in_game_cam = arcade.Camera2D(viewport=LBWH(100, 100, window.width, window.height))

    button = uimanager.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    in_game_cam.use()
    uimanager.click(50, 50)

    # THEN
    assert button.on_click.called


def test_ui_manager_use_positioned_camera(uimanager, window):
    # GIVEN
    button = uimanager.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    # this moves the camera bottom left and UI elements are shown more to the top right
    uimanager.camera.bottom_left = (-100, -100)
    uimanager.click(150, 150)

    # THEN
    assert button.on_click.called


def test_ui_manager_use_rotated_camera(uimanager, window):
    # GIVEN
    button = uimanager.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    uimanager.camera.angle = 90
    x, y = uimanager.camera.project((50, 50))
    uimanager.click(x, y)

    # THEN
    assert button.on_click.called, (uimanager.camera.project((50, 50)), window.size)


def test_ui_manager_use_zoom_camera(uimanager, window):
    # GIVEN
    button = uimanager.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    uimanager.camera.zoom = 0.9
    x, y = uimanager.camera.project((50, 50))
    uimanager.click(x, y)

    # THEN
    assert button.on_click.called
