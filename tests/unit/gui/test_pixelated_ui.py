import pyglet
import pyglet.font.base
from pyglet.enums import TextureFilter

from arcade.gui import UIManager
from arcade.gui.experimental import pixelated_ui


def test_pixelated_ui_sets_nearest_font_filtering(monkeypatch):
    # Let monkeypatch put the global settings back afterwards
    monkeypatch.setattr(pyglet.options, "text_antialiasing", True)
    monkeypatch.setattr(pyglet.font.base.Font, "filters", TextureFilter.LINEAR)
    monkeypatch.setattr(UIManager, "_pixelated", False)

    pixelated_ui()

    assert pyglet.options.text_antialiasing is False
    assert pyglet.font.base.Font.filters == TextureFilter.NEAREST
    assert UIManager._pixelated is True
