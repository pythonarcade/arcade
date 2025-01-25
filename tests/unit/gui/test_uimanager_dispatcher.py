from unittest.mock import call, create_autospec

import pytest

import arcade
from arcade.gui import UIManager


@pytest.mark.usefixtures("window")
def test_handler_pushed():
    window = create_autospec(arcade.Window)

    msg = UIManager(window)
    msg.enable()

    window.assert_has_calls(
        [
            call.push_handlers(
                msg.on_resize,
                msg.on_update,
                msg.on_mouse_drag,
                msg.on_mouse_motion,
                msg.on_mouse_press,
                msg.on_mouse_release,
                msg.on_mouse_scroll,
                msg.on_key_press,
                msg.on_key_release,
                msg.on_text,
                msg.on_text_motion,
                msg.on_text_motion_select,
            )
        ]
    )


def test_handler_not_pushed():
    window = create_autospec(arcade.Window)

    _ = UIManager(window)

    assert not window.push_handlers.called


def test_handler_removed():
    window = create_autospec(arcade.Window)
    msg = UIManager(window)
    msg.enable()  # UIManager has to be enabled before it can be disabled

    msg.disable()

    window.assert_has_calls(
        [
            call.remove_handlers(
                msg.on_resize,
                msg.on_update,
                msg.on_mouse_drag,
                msg.on_mouse_motion,
                msg.on_mouse_press,
                msg.on_mouse_release,
                msg.on_mouse_scroll,
                msg.on_key_press,
                msg.on_key_release,
                msg.on_text,
                msg.on_text_motion,
                msg.on_text_motion_select,
            )
        ]
    )
