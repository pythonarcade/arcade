from pytest import fixture

from arcade.gui import UIManager
from . import InteractionMixin


class InteractionUIManager(UIManager, InteractionMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.push_handlers(on_event=self._on_ui_event)


@fixture
def ui(window) -> InteractionUIManager:
    return InteractionUIManager()
