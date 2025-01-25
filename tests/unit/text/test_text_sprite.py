import pytest
import arcade


@pytest.mark.parametrize(
    'color', (arcade.color.WHITE, (255, 255, 255), (255, 255, 255, 255))
)
def test_create(window, color):
    sprite = arcade.create_text_sprite("Hello World", color)
    assert isinstance(sprite, arcade.Sprite)
    assert sprite.width == pytest.approx(75, rel=10)
    assert sprite.height == pytest.approx(20, rel=5)
