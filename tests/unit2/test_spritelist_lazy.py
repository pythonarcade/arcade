import pytest
import arcade


def test_create():
    """Test lazy creation of spritelist"""
    spritelist = arcade.SpriteList(lazy=True, use_spatial_hash=True)
    assert spritelist._sprite_pos_buf == None
    assert spritelist._geometry == None
    for x in range(100):
        spritelist.append(
            arcade.Sprite(":resources:images/items/coinGold.png", center_x=x * 64)
        )
    assert len(spritelist) == 100
    assert spritelist.spatial_hash is not None
    assert spritelist._initialized is False

    arcade.set_window(None)
    with pytest.raises(RuntimeError):
        spritelist.initialize()


def test_create_2(window):
    spritelist = arcade.SpriteList(lazy=True)
    sprite = arcade.SpriteSolidColor(10, 10, color=(255, 255, 255, 255))
    spritelist.append(sprite)
    spritelist.remove(sprite)

    spritelist.initialize()  
    assert spritelist._initialized
    assert spritelist._sprite_pos_buf
    assert spritelist._geometry
    spritelist.draw()
