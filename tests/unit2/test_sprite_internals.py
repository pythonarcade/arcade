import arcade
import pytest


def test_it_can_correctly_set_left_after_width_change_with_texture():
    sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_walk0.png")
    assert sprite.get_adjusted_hit_box() == [[a,b] for (a, b) in sprite._points]
    sprite.width *= 2
    sprite.height *= 2
    assert sprite.get_adjusted_hit_box() == [[a*2,b*2] for (a, b) in sprite._points]


@pytest.mark.parametrize('orientation, dimension', [
    ('top', 'height'),
    ('bottom', 'height'),
    ('left', 'width'),
    ('right', 'width')
])
def test_it_has_correct_orientation_after_dimension_change(orientation, dimension):
    sprite = arcade.Sprite()
    sprite.texture = arcade.make_soft_square_texture(100, arcade.color.RED, 255, 255)
    sprite.position = (50, 50)
    original_orientation_value = getattr(sprite, orientation)
    assert getattr(sprite, orientation) == original_orientation_value
    setattr(sprite, dimension, 50)
    assert getattr(sprite, orientation) != original_orientation_value
