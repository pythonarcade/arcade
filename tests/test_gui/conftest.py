import pytest
from pyglet.event import EventDispatcher
from pytest import fixture

from arcade import Window
from . import MockButton, TestUIManager, TestUILayoutManager


class MockWindow(EventDispatcher):
    def __init__(self):
        self.register_event_type("on_draw")
        self.register_event_type("on_mouse_drag")
        self.register_event_type("on_mouse_motion")
        self.register_event_type("on_mouse_press")
        self.register_event_type("on_mouse_release")
        self.register_event_type("on_mouse_scroll")
        self.register_event_type("on_key_press")
        self.register_event_type("on_key_release")
        self.register_event_type("on_update")
        self.register_event_type("on_resize")
        self.register_event_type("on_text")
        self.register_event_type("on_text_motion")
        self.register_event_type("on_text_motion_select")


@pytest.fixture
def window():
    window = Window(title="ARCADE_GUI")
    yield window
    window.close()


@pytest.fixture
def mock_window():
    return MockWindow()


@fixture
def mock_mng(mock_window):
    ui_manager = TestUIManager(mock_window)
    yield ui_manager


@pytest.fixture()
def mock_layout_mng(window):
    ui_manager = TestUILayoutManager(window)
    ui_manager.enable()
    yield ui_manager
    ui_manager.disable()


@pytest.fixture()
def mock_button() -> MockButton:
    return MockButton(center_x=50, center_y=50, width=40, height=40)


# provide same fixture twice, in case we need a second button
mock_button2 = mock_button
