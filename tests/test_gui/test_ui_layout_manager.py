from unittest.mock import Mock

import pytest

from arcade.gui.layouts.manager import UILayoutManager


@pytest.fixture()
def layout_manager(window) -> UILayoutManager:
    mng = UILayoutManager(window)
    yield mng
    mng.unregister_handlers()


def test_update_triggers_refresh(layout_manager):
    layout_manager.root_layout.refresh = Mock()

    layout_manager.on_update(0)

    assert layout_manager.root_layout.refresh.called
