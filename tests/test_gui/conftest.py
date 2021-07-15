import pytest
from pytest import fixture

import arcade
from . import MockButton, TestUIManager, TestUILayoutManager


@fixture()
def mock_mng(window):
    ui_manager = TestUIManager(window)
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
