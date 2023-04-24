import pytest
import arcade


def test_create(window):
    sprite = arcade.create_text_sprite("Hello World")
    assert isinstance(sprite, arcade.Sprite)
    assert sprite.width == pytest.approx(75, rel=10)
    assert sprite.height == pytest.approx(20, rel=5)
