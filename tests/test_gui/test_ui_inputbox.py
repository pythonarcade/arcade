import pytest

from arcade.gui import UIEvent
from arcade.gui.elements.inputbox import UIInputBox
from arcade.gui.events import (
    TEXT_INPUT,
    TEXT_MOTION,
)
from arcade.key import *
from tests.test_gui import t


def test_set_cursor_behind_text_if_given_at_construction_time(mock_mng):
    inputbox = UIInputBox(text="arcade", center_x=30, center_y=30, width=40, height=40)

    # THEN
    assert inputbox.cursor_index == 6


def test_changes_text_on_text_input(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    inputbox.on_ui_event(UIEvent(TEXT_INPUT, text="a"))

    assert inputbox.text == "Best aGame Lib!"
    assert inputbox.cursor_index == 6


def test_ignores_newline(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    inputbox.on_ui_event(UIEvent(TEXT_INPUT, text="\r"))

    assert inputbox.text == "Best Game Lib!"
    assert inputbox.cursor_index == 5


def test_emits_event_on_enter(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    inputbox.on_ui_event(UIEvent(TEXT_INPUT, text="\r"))

    assert mock_mng.last_event.type == UIInputBox.ENTER
    assert mock_mng.last_event.get("ui_element") == inputbox


def test_invokes_callback_on_return(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    invoked = False

    def callback():
        nonlocal invoked
        invoked = True

    inputbox.on_enter = callback

    inputbox.on_ui_event(UIEvent(TEXT_INPUT, text="\r"))

    assert invoked is True


def test_invokes_decorator_on_return(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    invoked = False

    @inputbox.event("on_enter")
    def callback():
        nonlocal invoked
        invoked = True

    inputbox.on_ui_event(UIEvent(TEXT_INPUT, text="\r"))

    assert invoked is True


def test_ui_inputbox_has_on_enter_event_type():
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    assert "on_enter" in inputbox.event_types


def test_changes_text_on_backspace(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    inputbox.on_ui_event(UIEvent(TEXT_MOTION, motion=MOTION_BACKSPACE))

    assert inputbox.text == "BestGame Lib!"
    assert inputbox.cursor_index == 4


def test_cursor_can_not_be_negative(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 0
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    inputbox.on_ui_event(UIEvent(TEXT_MOTION, motion=MOTION_LEFT))

    assert inputbox.text == "Best Game Lib!"
    assert inputbox.cursor_index == 0


def test_changes_text_on_delete(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    inputbox.on_ui_event(UIEvent(TEXT_MOTION, motion=MOTION_DELETE))

    assert inputbox.text == "Best ame Lib!"
    assert inputbox.cursor_index == 5


@pytest.mark.parametrize(
    "motion,expected_index",
    [
        # Test against 'Best |Game Lib!'
        t("MOTION_UP", MOTION_UP, 0),
        t("MOTION_RIGHT", MOTION_RIGHT, 6),
        t("MOTION_DOWN", MOTION_DOWN, 14),
        t("MOTION_LEFT", MOTION_LEFT, 4),
        # T('MOTION_NEXT_WORD', MOTION_NEXT_WORD, 5),
        # T('MOTION_PREVIOUS_WORD', MOTION_PREVIOUS_WORD, 5),
        t("MOTION_BEGINNING_OF_LINE", MOTION_BEGINNING_OF_LINE, 0),
        t("MOTION_END_OF_LINE", MOTION_END_OF_LINE, 14),
        t("MOTION_NEXT_PAGE", MOTION_NEXT_PAGE, 14),
        t("MOTION_PREVIOUS_PAGE", MOTION_PREVIOUS_PAGE, 0),
        t("MOTION_BEGINNING_OF_FILE", MOTION_BEGINNING_OF_FILE, 0),
        t("MOTION_END_OF_FILE", MOTION_END_OF_FILE, 14),
        t("MOTION_BACKSPACE", MOTION_BACKSPACE, 4),
        t("MOTION_DELETE", MOTION_DELETE, 5),
    ],
)
def test_changes_cursor_on_text_motion(motion, expected_index, mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "Best Game Lib!"
    inputbox.cursor_index = 5
    inputbox.on_focus()
    mock_mng.add_ui_element(inputbox)

    inputbox.on_ui_event(UIEvent(TEXT_MOTION, motion=motion))

    assert inputbox.cursor_index == expected_index


def test_cursor_index_not_outside_text(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "love"
    inputbox.cursor_index = 5

    assert inputbox.cursor_index == 4


def test_cursor_index_always_greater_equals_0(mock_mng):
    inputbox = UIInputBox(center_x=30, center_y=30, width=40, height=40)
    inputbox.text = "love"
    inputbox.cursor_index = -1

    assert inputbox.cursor_index == 0
