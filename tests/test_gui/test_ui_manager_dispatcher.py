from unittest.mock import Mock, call

from arcade.gui import UIManager


def test_handler_pushed():
    window = Mock()

    msg = UIManager(window)

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
    window = Mock()

    _ = UIManager(window, attach_callbacks=False)

    assert not window.push_handlers.called


def test_handler_removed():
    window = Mock()
    msg = UIManager(window)

    msg.unregister_handlers()

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
