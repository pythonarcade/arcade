import sys

import pytest


class MockWindow:
    """ Replace the pyglet base class with something we control """

    def __init__(self, *args, **kwargs):
        self.height = kwargs['height']
        self.width = kwargs['width']
        self.caption = kwargs['caption']
        self.resizable = kwargs['resizable']
        self._fullscreen = False

    def set_fullscreen(self, value: bool):
        self._fullscreen = value


@pytest.fixture(autouse=True)
def mock_window(monkeypatch):
    sys.is_pyglet_docgen = True
    monkeypatch.setattr('pyglet.window.Window', MockWindow)
    from arcade import Window
    return Window


@pytest.fixture
def pyglet_clock(mocker):
    yield mocker.patch('pyglet.clock')
