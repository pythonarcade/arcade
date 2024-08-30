from unittest.mock import Mock

import arcade
from arcade import LBWH
from arcade.gui import UIFlatButton


def test_ui_manager_respects_window_camera(ui, window):
    # GIVEN
    in_game_cam = arcade.Camera2D(viewport=LBWH(100, 100, window.width, window.height))

    button = ui.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    in_game_cam.use()
    ui.click(50, 50)

    # THEN
    assert button.on_click.called


def test_ui_manager_use_positioned_camera(ui, window):
    # GIVEN
    button = ui.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    # this moves the camera bottom left and UI elements are shown more to the top right
    ui.camera.bottom_left = (-100, -100)
    ui.click(150, 150)

    # THEN
    assert button.on_click.called


def test_ui_manager_use_rotated_camera(ui, window):
    # GIVEN
    button = ui.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    ui.camera.angle = 90
    x, y = ui.camera.project((50, 50))
    ui.click(x, y)

    # THEN
    assert button.on_click.called, (ui.camera.project((50, 50)), window.size)


def test_ui_manager_use_zoom_camera(ui, window):
    # GIVEN
    button = ui.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))
    button.on_click = Mock()

    # WHEN
    ui.camera.zoom = 0.9
    x, y = ui.camera.project((50, 50))
    ui.click(x, y)

    # THEN
    assert button.on_click.called
