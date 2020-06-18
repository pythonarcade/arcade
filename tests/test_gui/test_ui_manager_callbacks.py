import arcade
from arcade.key import MOTION_UP

from arcade.gui import MOUSE_PRESS, MOUSE_RELEASE, MOUSE_SCROLL, KEY_PRESS, KEY_RELEASE, TEXT_MOTION_SELECTION
from arcade.gui import TEXT_INPUT, TEXT_MOTION
from arcade.gui.core import MOUSE_MOTION


def test_on_mouse_press_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_mouse_press(1, 2, 3, 4)

    event = mock_button.last_event
    assert event.type == MOUSE_PRESS
    assert event.get('x') == 1
    assert event.get('y') == 2
    assert event.get('button') == 3
    assert event.get('modifiers') == 4


def test_on_mouse_release_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_mouse_release(1, 2, 3, 4)

    event = mock_button.last_event
    assert event.type == MOUSE_RELEASE
    assert event.get('x') == 1
    assert event.get('y') == 2
    assert event.get('button') == 3
    assert event.get('modifiers') == 4


def test_on_mouse_scroll_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_mouse_scroll(1, 2, 3, 4)

    event = mock_button.last_event
    assert event.type == MOUSE_SCROLL
    assert event.get('x') == 1
    assert event.get('y') == 2
    assert event.get('scroll_x') == 3
    assert event.get('scroll_y') == 4


def test_on_mouse_motion_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_mouse_motion(1, 2, 3, 4)

    event = mock_button.last_event
    assert event.type == MOUSE_MOTION
    assert event.get('x') == 1
    assert event.get('y') == 2
    assert event.get('dx') == 3
    assert event.get('dy') == 4


def test_on_key_press_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_key_press(arcade.key.ENTER, 0)

    event = mock_button.last_event
    assert event.type == KEY_PRESS
    assert event.get('symbol') == arcade.key.ENTER


def test_on_key_release_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_key_release(arcade.key.ENTER, 0)

    event = mock_button.last_event
    assert event.type == KEY_RELEASE
    assert event.get('symbol') == arcade.key.ENTER


def test_on_text_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_text('a')

    event = mock_button.last_event
    assert event.type == TEXT_INPUT
    assert event.get('text') == 'a'


def test_on_text_motion_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_text_motion(MOTION_UP)

    event = mock_button.last_event
    assert event.type == TEXT_MOTION
    assert event.get('motion') == MOTION_UP


def test_on_text_motion_selection_passes_an_event(mock_mng, mock_button):
    mock_mng.add_ui_element(mock_button)
    mock_mng.add_ui_element(mock_button)

    mock_mng.on_text_motion_select(MOTION_UP)

    event = mock_button.last_event
    assert event.type == TEXT_MOTION_SELECTION
    assert event.get('selection') == MOTION_UP
