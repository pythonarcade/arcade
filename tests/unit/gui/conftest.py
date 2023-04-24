from arcade.gui import UIManager
from pytest import fixture

from . import InteractionMixin


class InteractionUIManager(UIManager, InteractionMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.push_handlers(on_event=self._on_ui_event)



@fixture
def uimanager(window) -> InteractionUIManager:
    return InteractionUIManager()