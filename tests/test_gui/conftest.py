from contextlib import ExitStack
from unittest.mock import patch

import pytest
from pyglet.event import EventDispatcher
from pytest import fixture

from . import MockHolder, MockButton, TestUIManager


class MockWindow(EventDispatcher):
    def __init__(self):
        self.register_event_type('on_draw')
        self.register_event_type('on_mouse_press')
        self.register_event_type('on_mouse_release')
        self.register_event_type('on_mouse_scroll')
        self.register_event_type('on_mouse_motion')
        self.register_event_type('on_key_press')
        self.register_event_type('on_key_release')
        self.register_event_type('on_update')
        self.register_event_type('on_resize')
        self.register_event_type('on_text')
        self.register_event_type('on_text_motion')
        self.register_event_type('on_text_motion_select')


@fixture()
def draw_commands():
    """
    Decorator

    Mocks all 'arcade.draw_...' methods and injects a holder with mocks
    """
    import arcade
    to_patch = [attr for attr in dir(arcade) if attr.startswith('draw_')]
    holder = MockHolder()

    with ExitStack() as stack:
        for method in to_patch:
            holder[method] = stack.enter_context(patch(f'arcade.{method}'))

        yield holder


@pytest.fixture
def mock_window():
    return MockWindow()

@fixture
def mock_mng(mock_window):
    ui_manager = TestUIManager(mock_window)
    yield ui_manager
    ui_manager.unregister_handlers()


@pytest.fixture()
def mock_button() -> MockButton:
    return MockButton(center_x=50, center_y=50, width=40, height=40)


# provide same fixture twice, in case we need a second button
mock_button2 = mock_button
