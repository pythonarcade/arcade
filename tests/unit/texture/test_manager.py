"""Test the TextureCacheManager"""
import arcade
from arcade.types.rect import LBWH

SPRITESHEET_PATH = ":assets:images/spritesheets/codepage_437.png"
TEST_TEXTURE = ":assets:images/test_textures/test_texture.png"

def test_create():
    arcade.texture.TextureCacheManager()


def test_load_spritesheet():
    """Load spritesheet and test caching"""
    manager = arcade.texture.TextureCacheManager()
    spritesheet = manager.load_or_get_spritesheet(SPRITESHEET_PATH)
    assert spritesheet
    assert manager.load_or_get_spritesheet(SPRITESHEET_PATH) == spritesheet
    assert len(manager._sprite_sheets) == 1

    manager.flush()
    assert len(manager._sprite_sheets) == 0


def test_load_spritesheet_texture():
    """Load spritesheet and test caching"""
    manager = arcade.texture.TextureCacheManager()
    texture = manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, LBWH(0, 0, 8, 16))
    # This should have cached the spritesheet
    assert len(manager._sprite_sheets) == 1
    assert isinstance(list(manager._sprite_sheets.values())[0], arcade.SpriteSheet)
    # The same texture should be returned the second time
    assert manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, LBWH(0, 0, 8, 16)) == texture

    # Load a few more textures
    for i in range(10):
        texture = manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, LBWH(i * 9, 0, 8, 16))
        assert manager.load_or_get_spritesheet_texture(SPRITESHEET_PATH, LBWH(i * 9, 0, 8, 16)) == texture

    # We should still have 1 spritesheet
    assert len(manager._sprite_sheets) == 1
    # We loaded the texture 10 times with different crop values
    assert len(manager.texture_cache._file_entries) == 10
    assert len(manager.texture_cache._entries) == 10
    assert len(manager.image_data_cache) == 10

    # Flush the cache
    manager.flush()
    assert len(manager._sprite_sheets) == 0
    assert len(manager.texture_cache._file_entries) == 0
    assert len(manager.texture_cache._entries) == 0 
    assert len(manager.image_data_cache) == 0


def test_load_or_get_texture():
    """Load a texture and test caching"""
    manager = arcade.texture.TextureCacheManager()
    texture = manager.load_or_get_texture(TEST_TEXTURE)
    assert texture
    assert manager.load_or_get_texture(TEST_TEXTURE) == texture
    assert len(manager.texture_cache._file_entries) == 1
    assert len(manager.texture_cache._entries) == 1

    manager.flush()
    assert len(manager.texture_cache._file_entries) == 0
    assert len(manager.texture_cache._entries) == 0
