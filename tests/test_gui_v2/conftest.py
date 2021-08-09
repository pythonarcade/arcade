from arcade.experimental.gui_v2 import UIManager
from pytest import fixture

from tests.test_gui_v2 import InteractionMixin


class InteractionUIManager(UIManager, InteractionMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.push_handlers(on_event=self._on_ui_event)



@fixture
def uimanager(window) -> InteractionUIManager:
    return InteractionUIManager()