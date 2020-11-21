from unittest.mock import Mock

import pytest

import arcade
from arcade import SpriteSolidColor
from arcade.gui import UIEvent
from arcade.gui.layouts.manager import UILayoutManager
from tests.test_gui import dummy_element


@pytest.fixture()
def layout_manager(window) -> UILayoutManager:
    mng = UILayoutManager(window)
    yield mng
    mng.unregister_handlers()


def test_update_triggers_refresh(layout_manager):
    layout_manager.root_layout.refresh = Mock()

    layout_manager.on_update(0)

    assert layout_manager.root_layout.refresh.called


def test_delegate_pack_method_to_root_layout(layout_manager):
    layout_manager.root_layout.pack = Mock()

    layout_manager.pack(dummy_element())

    assert layout_manager.root_layout.pack.called


def test_passes_ui_events(layout_manager):
    # GIVEN
    element = dummy_element()
    element.on_ui_event = Mock()
    layout_manager.pack(element)

    sprite = SpriteSolidColor(100, 50, arcade.color.GREEN)
    layout_manager.pack(sprite)

    test_event = UIEvent('ANY EVENT')

    # WHEN
    layout_manager.on_ui_event(test_event)

    # THEN
    element.on_ui_event.assert_called_once_with(test_event)
