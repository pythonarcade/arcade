import pytest
import arcade

def test_text_texture(window):
    texture = arcade.create_text_texture("Hello World")
    assert isinstance(texture, arcade.Texture)
    assert texture.width == pytest.approx(80, rel=10)
    assert texture.height == pytest.approx(20, rel=5)

def test_text_sprite(window):
    sprite = arcade.create_text_sprite("Hello World")
    assert isinstance(sprite, arcade.Sprite)
    assert sprite.width == pytest.approx(80, rel=10)
    assert sprite.height == pytest.approx(20, rel=5)
