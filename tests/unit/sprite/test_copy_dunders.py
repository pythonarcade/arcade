import copy
import pytest

import arcade


def test_copy_dunders_raise_notimplementederror():
    """Make sure our sprite types raise NotImplentedError for copy dunders.

    See the following GitHub issue for more context:
    https://github.com/pythonarcade/arcade/issues/2074
    """

    # Make sure BasicSprite raises NotImplementedError
    texture = arcade.load_texture(":resources:images/animated_characters/female_person/femalePerson_idle.png")
    basic_sprite = arcade.BasicSprite(texture)

    with pytest.raises(NotImplementedError):
        copy.copy(basic_sprite)

    with pytest.raises(NotImplementedError):
        copy.deepcopy(basic_sprite)

    sprite = arcade.Sprite(texture)
    with pytest.raises(NotImplementedError):
        copy.copy(sprite)

    with pytest.raises(NotImplementedError):
        copy.deepcopy(sprite)

    circle = arcade.SpriteCircle(5, arcade.color.RED)
    with pytest.raises(NotImplementedError):
        copy.copy(circle)

    with pytest.raises(NotImplementedError):
        copy.deepcopy(circle)

    solid = arcade.SpriteSolidColor(10, 10, color=arcade.color.RED)
    with pytest.raises(NotImplementedError):
        copy.copy(solid)

    with pytest.raises(NotImplementedError):
        copy.deepcopy(solid)
