import arcade
from arcade import LBWH
from arcade.gui import UIFlatButton


def test_ui_manager_respects_window_camera(uimanager, window):
    # GIVEN
    in_game_cam = arcade.Camera2D(
        viewport=LBWH(100, 100, window.width, window.height)
    )
    clicked = False

    button = uimanager.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))

    @button.event("on_click")
    def on_click(event):
        nonlocal clicked
        clicked = True
    
    # WHEN
    in_game_cam.use()
    uimanager.click(150, 150)
    
    # THEN
    assert clicked


def test_ui_manager_use_rotated_camera(uimanager, window):
    # GIVEN
    clicked = False

    button = uimanager.add(UIFlatButton(text="BottomLeftButton", width=100, height=100))

    @button.event("on_click")
    def on_click(event):
        nonlocal clicked
        clicked = True
        

    # WHEN
    uimanager.camera.angle = 90
    uimanager.click(150, 150)

    # THEN
    assert clicked
