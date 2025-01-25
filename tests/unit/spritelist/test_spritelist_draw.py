import pytest
import arcade
from arcade.gl import Geometry


def test_visible(window, monkeypatch):
    """Ensure invisible spritelists are not drawn"""
    sp = arcade.SpriteList()
    # Monkeypatch Geometry.render to raise an error if called
    def mock_draw(*args, **kwargs):
        raise AssertionError("Should not be called")
    monkeypatch.setattr(Geometry, "render", mock_draw)

    # Empty spritelist should not be rendered
    sp.draw()

    # It will draw if it has sprites
    sp.append(arcade.SpriteSolidColor(10, 10, color=arcade.color.RED))
    # Geometry.render should be called
    with pytest.raises(AssertionError):
        sp.draw()

    # Invisible should not be rendered
    sp.visible = False
    sp.draw()
    sp.visible = True

    # Alpha 0 should not be rendered
    sp.alpha = 0
    sp.draw()
