from arcade.gui import UIEvent, UIManager
from arcade.gui.core import MOUSE_MOTION
from . import MockButton


def test_view_starts_without_hovered_element(window, mock_mng):
    assert mock_mng.hovered_element is None


def test_setting_hovered_element_to_none_handles_unhover(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.hovered_element = mock_button
    mock_mng.hovered_element = None

    assert mock_mng.hovered_element is None
    assert mock_button.on_unhover_called


def test_setting_hovered_element_calls_on_hover(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.hovered_element = mock_button

    assert mock_mng.hovered_element == mock_button
    assert mock_button.on_hover_called


def test_setting_hover_to_other_element_handles_rehover(mock_mng, mock_button, mock_button2: MockButton):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button2)
    mock_mng.hovered_element = mock_button

    # WHEN
    mock_mng.hovered_element = mock_button2

    # THEN
    # old element unhovered
    assert mock_button.on_unhover_called

    # New element hovered
    assert mock_mng.hovered_element == mock_button2
    assert mock_button2.on_hover_called
    assert not mock_button2.on_unhover_called


def test_mouse_motion_over_element_makes_it_hovered(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_ui_event(UIEvent(MOUSE_MOTION, x=50, y=50, dx=1, dy=1))

    assert mock_mng.hovered_element is mock_button
    assert mock_button.on_hover_called


def test_motion_out_of_element_unhoveres(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.hovered_element = mock_button

    mock_mng.on_ui_event(UIEvent(MOUSE_MOTION, x=100, y=100, button=1, modifier=0))

    assert mock_mng.hovered_element is None
    assert mock_button.on_unhover_called


def test_change_hover_over_different_element(mock_mng, mock_button, mock_button2: MockButton):
    mock_button.center_x += 100

    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button2)
    mock_mng.hovered_element = mock_button

    # WHEN
    mock_mng.on_ui_event(UIEvent(MOUSE_MOTION, x=50, y=50, button=1, modifier=0))

    # THEN
    assert mock_mng.hovered_element is mock_button2
    assert mock_button.on_unhover_called
    assert mock_button2.on_hover_called
