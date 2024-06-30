"""
SpriteCircle and SpriteSolidColor
"""
import arcade


def test_sprite_circle_props():
    """Test basic properties of SpriteCircle"""
    sprite = arcade.SpriteCircle(50, arcade.color.RED)
    assert sprite.color == arcade.color.RED
    assert sprite.size == (100, 100)


def test_sprite_circle_texture_cache():
    """SpriteCircle should reuse cached textures"""
    sprite_1 = arcade.SpriteCircle(50, arcade.color.RED)
    sprite_2 = arcade.SpriteCircle(50, arcade.color.RED)
    assert sprite_1.texture == sprite_2.texture


def test_sprite_solid_color_props():
    """Test basic properties of SpriteSolidColor"""
    sprite = arcade.SpriteSolidColor(50, 100, color=arcade.color.RED)
    assert sprite.color == arcade.color.RED
    assert sprite.size == (50, 100)


def test_sprite_solid_color_texture_cache():
    """SpriteSolidColor should reuse cached textures and images"""
    # Cached textures
    sprite_1 = arcade.SpriteSolidColor(50, 100, color=arcade.color.RED)
    sprite_2 = arcade.SpriteSolidColor(50, 100, color=arcade.color.RED)
    assert sprite_1.texture == sprite_2.texture

    # Cached image (single one eternally reused)
    sprite_3 = arcade.SpriteSolidColor(10, 10, color=arcade.color.RED)
    assert sprite_3.texture.image_data == sprite_1.texture.image_data
