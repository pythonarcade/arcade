from arcade.experimental.gui_v2 import UIManager
from pytest import fixture

from tests.test_gui_v2 import InteractionMixin


class InteractionUIManager(UIManager, InteractionMixin):
    pass


@fixture
def uimanager(window) -> InteractionUIManager:
    return InteractionUIManager()