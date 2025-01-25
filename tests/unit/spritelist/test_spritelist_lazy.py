import pytest
import arcade
from arcade import DefaultTextureAtlas


def test_create_lazy_equals_true():
    """Test lazy creation of spritelist"""
    spritelist = arcade.SpriteList(lazy=True, use_spatial_hash=True)

    # Make sure OpenGL abstractions are not created
    assert spritelist._sprite_pos_buf == None
    assert spritelist._geometry == None
    assert spritelist.atlas is None

    # Make sure CPU-only behavior still works correctly
    for x in range(100):
        spritelist.append(
            arcade.Sprite(":resources:images/items/coinGold.png", center_x=x * 64)
        )
    assert len(spritelist) == 100
    assert spritelist.spatial_hash is not None
    assert spritelist._initialized is False

    # Verify that initialization will fail without a window
    arcade.set_window(None)
    with pytest.raises(RuntimeError):
        spritelist.initialize()


def test_manual_initialization_after_lazy_equals_true(window):
    """Test manual initialization of lazy sprite lists."""
    spritelist = arcade.SpriteList(lazy=True)

    # CPU-only actions which shouldn't affect initializing OpenGL resources
    sprite = arcade.SpriteSolidColor(10, 10, color=(255, 255, 255, 255))
    spritelist.append(sprite)
    spritelist.remove(sprite)

    # Make sure initialization still worked correctly.
    spritelist.initialize()  
    assert spritelist._initialized
    assert spritelist._sprite_pos_buf
    assert spritelist._geometry
    assert isinstance(spritelist.atlas, DefaultTextureAtlas)

    # Uncomment the next line and set a breakpoint on it to
    # spot-check the number of sprites drawn (it should be zero).
    spritelist.draw()
    # pass
