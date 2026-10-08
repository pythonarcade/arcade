"""Sprites raise TypeError for keyword arguments they don't accept."""

import pytest

import arcade

COIN = ":resources:images/items/coinGold.png"


@pytest.mark.parametrize(
    "make",
    [
        lambda: arcade.Sprite(COIN, hit_box_algorithm="None"),
        lambda: arcade.BasicSprite(arcade.load_texture(COIN), scaling=2.0),
        lambda: arcade.SpriteSolidColor(10, 10, colour=(255, 0, 0)),
        lambda: arcade.SpriteCircle(5, arcade.color.RED, bogus=1),
        lambda: arcade.TextureAnimationSprite(bogus=1),
        lambda: arcade.AnimatedWalkingSprite(bogus=1),
    ],
    ids=[
        "Sprite",
        "BasicSprite",
        "SpriteSolidColor",
        "SpriteCircle",
        "TextureAnimationSprite",
        "AnimatedWalkingSprite",
    ],
)
def test_unknown_keyword_argument_raises(make):
    with pytest.raises(TypeError, match="unexpected keyword argument"):
        make()


def test_subclass_init_with_unknown_argument_raises():
    class Card(arcade.Sprite):
        def __init__(self):
            super().__init__(COIN, 1.0, hit_box_algorithm="None")

    with pytest.raises(TypeError, match="hit_box_algorithm"):
        Card()


def test_visible_argument():
    assert arcade.Sprite(COIN, visible=False).visible is False
    assert arcade.BasicSprite(arcade.load_texture(COIN), visible=False).visible is False


def test_subclasses_pass_sprite_arguments_on():
    # These used to be accepted and silently ignored
    assert arcade.SpriteCircle(5, arcade.color.RED, angle=30).angle == 30
    assert arcade.SpriteSolidColor(10, 10, visible=False).visible is False
    assert arcade.TextureAnimationSprite(angle=45).angle == 45
    assert arcade.AnimatedWalkingSprite(angle=90, visible=False).angle == 90
