"""Test the TextureCacheManager"""
import arcade

SPRITESHEET_PATH = ":assets:images/spritesheets/codepage_437.png"

def test_create():
    arcade.texture.TextureCacheManager()


def test_load_spritesheet():
    """Load spritesheet and test caching"""
    manager = arcade.texture.TextureCacheManager()
    spritesheet = manager.load_or_get_spritesheet(SPRITESHEET_PATH)
    assert spritesheet
    assert manager.load_or_get_spritesheet(SPRITESHEET_PATH) == spritesheet


def test_load_spritesheet_texture():
    """Load spritesheet and test caching"""
    manager = arcade.texture.TextureCacheManager()
    texture = manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, 0, 0, 8, 16)
    # This should have cached the spritesheet
    assert len(manager._sprite_sheets) == 1
    assert isinstance(list(manager._sprite_sheets.values())[0], arcade.SpriteSheet)
