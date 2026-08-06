from unittest.mock import Mock, call

from pyglet.math import Vec2

from arcade.input.inputs import ControllerButtons
from arcade.input.manager import ActionState, InputDevice, InputManager


def make_input_manager() -> tuple[InputManager, Mock]:
    manager = object.__new__(InputManager)
    manager.active_device = None
    manager._dpad_state = Vec2()
    manager.controller_buttons_to_actions = {
        ControllerButtons.DPAD_LEFT.value: {"left"},
        ControllerButtons.DPAD_RIGHT.value: {"right"},
        ControllerButtons.DPAD_UP.value: {"up"},
        ControllerButtons.DPAD_DOWN.value: {"down"},
    }
    dispatch_action = Mock()
    manager.dispatch_action = dispatch_action
    return manager, dispatch_action


def test_dpad_motion_dispatches_pressed_actions():
    manager, dispatch_action = make_input_manager()

    manager.on_dpad_motion(Mock(), Vec2(-1, 1))

    assert manager.active_device == InputDevice.CONTROLLER
    assert dispatch_action.call_args_list == [
        call("left", ActionState.PRESSED),
        call("up", ActionState.PRESSED),
    ]


def test_dpad_motion_dispatches_direction_changes():
    manager, dispatch_action = make_input_manager()
    manager._dpad_state = Vec2(-1, 1)

    manager.on_dpad_motion(Mock(), Vec2(1, 0))

    assert dispatch_action.call_args_list == [
        call("left", ActionState.RELEASED),
        call("right", ActionState.PRESSED),
        call("up", ActionState.RELEASED),
    ]


def test_dpad_motion_ignores_unchanged_directions():
    manager, dispatch_action = make_input_manager()
    manager._dpad_state = Vec2(0, -1)

    manager.on_dpad_motion(Mock(), Vec2(0, -1))

    dispatch_action.assert_not_called()
