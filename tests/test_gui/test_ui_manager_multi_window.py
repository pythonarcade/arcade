from arcade.gui.layouts.box import UIBoxLayout
from . import MockButton


def test_ui_manager_dispatch_ui_event_to_top_frame(mock_layout_mng):
    # GIVEN

    box_1 = UIBoxLayout()
    box_1.top = 100
    box_1.left = 100
    button_1 = box_1.pack(MockButton())

    box_2 = UIBoxLayout()
    box_2.top = 100
    box_2.left = 100
    button_2 = box_2.pack(MockButton())

    mock_layout_mng.push(box_1)
    mock_layout_mng.push(box_2)
    mock_layout_mng.do_layout()
    assert button_1.center_x == button_2.center_x
    assert button_1.center_y == button_2.center_y

    # WHEN
    mock_layout_mng.click(button_2.center_x, button_2.center_y)

    # THEN
    assert not button_1.on_press_called
    assert button_2.on_press_called
