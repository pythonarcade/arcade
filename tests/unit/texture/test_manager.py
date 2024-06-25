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
    # The same texture should be returned the second time
    assert manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, 0, 0, 8, 16) == texture

    # Load a few more textures
    for i in range(10):
        texture = manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, i * 9, 0, 8, 16)
        assert manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, i * 9, 0, 8, 16) == texture

    # We should still have 1 spritesheet
    assert len(manager._sprite_sheets) == 1
    # We loaded the texture 10 times with different crop values
    assert len(manager.texture_cache._file_entries) == 10
    assert len(manager.texture_cache._entries) == 10
