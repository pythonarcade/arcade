from arcade.gui import UIClickable


def test_has_normal_state(mock_button):
    assert not mock_button.hovered
    assert not mock_button.pressed
    assert not mock_button.focused


def test_change_state_on_hover(mock_button):
    mock_button.on_hover()
    assert mock_button.hovered


def test_change_state_on_press(mock_button):
    mock_button.on_press()
    assert mock_button.pressed


def test_change_state_on_focus(mock_button):
    mock_button.on_focus()
    assert mock_button.focused


def test_uibutton_is_pressed(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click_and_hold(50, 50)

    assert mock_button.on_press_called
    assert not mock_button.on_click_called


def test_uibutton_clicked(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click(50, 50)

    assert mock_button.on_release
    assert mock_button.on_click_called


def test_uibutton_not_clicked_if_released_beside(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click_and_hold(50, 50)
    mock_mng.release(100, 100)

    assert not mock_button.on_click_called


def test_uibutton_send_custom_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.click(50, 50)

    assert mock_mng.last_event.type == UIClickable.CLICKED
    assert mock_mng.last_event.get('ui_element') == mock_button
