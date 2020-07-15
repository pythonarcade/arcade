from arcade.gui import UIEvent, MOUSE_PRESS
from . import MockButton


def test_mng_starts_without_focused_element(mock_mng):
    assert mock_mng.focused_element is None


def test_setting_focused_element_handles_focus(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.focused_element = mock_button

    assert mock_mng.focused_element == mock_button
    assert mock_button.on_focus_called


def test_setting_focused_element_to_none_handles_unfocus(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.focused_element = mock_button
    mock_mng.focused_element = None

    assert mock_mng.focused_element is None
    assert mock_button.on_unfocus_called


def test_setting_focus_to_other_element_handles_refocus(mock_mng, mock_button, mock_button2: MockButton):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button2)
    mock_mng.focused_element = mock_button

    # WHEN
    mock_mng.focused_element = mock_button2

    # THEN
    # old element unfocused
    assert mock_button.on_unfocus_called

    # New element focused
    assert mock_mng.focused_element == mock_button2
    assert mock_button2.on_focus_called
    assert not mock_button2.on_unfocus_called


def test_click_on_element_makes_it_active(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.dispatch_ui_event(UIEvent(MOUSE_PRESS, x=50, y=50, button=1, modifier=0))

    assert mock_mng.focused_element is mock_button
    assert mock_button.on_focus_called


def test_click_beside_element_unfocuses(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.focused_element = mock_button

    mock_mng.dispatch_ui_event(UIEvent(MOUSE_PRESS, x=100, y=100, button=1, modifier=0))

    assert mock_mng.focused_element is None
    assert mock_button.on_unfocus_called


def test_change_focus_to_different_element(mock_mng, mock_button: MockButton, mock_button2: MockButton):
    mock_button.center_x += 100

    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button2)
    mock_mng.focused_element = mock_button

    # WHEN
    mock_mng.dispatch_ui_event(UIEvent(MOUSE_PRESS, x=50, y=50, button=1, modifier=0))

    # THEN
    assert mock_mng.focused_element is mock_button2
    assert mock_button.on_unfocus_called
    assert mock_button2.on_focus_called
