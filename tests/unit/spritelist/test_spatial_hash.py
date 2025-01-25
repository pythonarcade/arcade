import pytest
import arcade
from arcade.sprite_list.spatial_hash import SpatialHash


def test_create():
    sh = SpatialHash(cell_size=10)
    assert sh.cell_size == 10
    assert sh.contents == {}
    assert sh.buckets_for_sprite == {}
    assert sh.count == 0

def test_incorrect_str_input():
    with pytest.raises(TypeError):
        sh = SpatialHash(cell_size="10")
    
def test_incorrect_inf_input():
    with pytest.raises(TypeError):
        sh = SpatialHash(cell_size=float("inf"))

def test_reset():
    sh = SpatialHash(cell_size=10)
    sh.add(arcade.SpriteSolidColor(10, 10, color=arcade.color.RED))
    assert sh.count == 1
    sh.reset()
    assert sh.count == 0


def test_add():
    """Test adding a sprite"""
    sh = SpatialHash(cell_size=10)
    sh.add(arcade.SpriteSolidColor(10, 10, color=arcade.color.RED))
    sh.add(arcade.SpriteSolidColor(10, 10, color=arcade.color.RED))
    sh.add(arcade.SpriteSolidColor(10, 10, color=arcade.color.RED))
    sh.add(arcade.SpriteSolidColor(10, 10, color=arcade.color.RED))
    assert sh.count == 4
    assert len(sh.contents) == 4
    assert len(sh.buckets_for_sprite) == 4


def test_add_twice():
    """Test adding the same sprite twice"""
    sh = SpatialHash(cell_size=10)
    sprite = arcade.SpriteSolidColor(10, 10, color=arcade.color.RED)
    for i in range(2):
        sh.add(sprite)
        assert sh.count == 1
        assert len(sh.contents) == 4
        assert len(sh.buckets_for_sprite) == 1


def test_add_remove():
    """Test adding and removing a sprite"""
    sh = SpatialHash(cell_size=10)
    sprite = arcade.SpriteSolidColor(10, 10)
    sh.add(sprite)
    assert sh.count == 1
    assert len(sh.contents) == 4  # 4 buckets
    for cn in sh.contents.values():
        assert len(cn) == 1
    assert len(sh.buckets_for_sprite) == 1
    sh.remove(sprite)
    assert sh.count == 0
    assert len(sh.contents) == 4
    for cn in sh.contents.values():
        assert len(cn) == 0
    assert len(sh.buckets_for_sprite) == 0


def test_remove_twice():
    """Test removing a sprite twice"""
    sh = SpatialHash(cell_size=10)
    sprite = arcade.SpriteSolidColor(10, 10)
    sh.add(sprite)
    sh.remove(sprite)
    with pytest.raises(KeyError):
        sh.remove(sprite)


def get_nearby_sprites():
    """Test getting nearby sprites"""
    sh = SpatialHash(cell_size=10)
    sprite_1 = arcade.SpriteSolidColor(10, 10, center_x=0)
    sprite_2 = arcade.SpriteSolidColor(10, 10, center_x=5)
    sh.add(sprite_1)
    sh.add(sprite_2)

    nearby_sprites = sh.get_sprites_near_sprite(
        arcade.SpriteSolidColor(10, 10, center_x=-5)
    )
    assert isinstance(nearby_sprites, set)
    assert len(nearby_sprites) == 1
    assert nearby_sprites[0] == sprite_1

    nearby_sprites = sh.get_sprites_near_sprite(
        arcade.SpriteSolidColor(10, 10, center_x=0)
    )
    assert isinstance(nearby_sprites, set)
    assert len(nearby_sprites) == 2
    assert nearby_sprites == set([sprite_1, sprite_2])


def test_get_near_point():
    """Test getting nearby sprites"""
    sh = SpatialHash(cell_size=10)
    sprite_1 = arcade.SpriteSolidColor(10, 10, center_x=0)
    sprite_2 = arcade.SpriteSolidColor(10, 10, center_x=5)
    sh.add(sprite_1)
    sh.add(sprite_2)

    nearby_sprites = sh.get_sprites_near_point((0, 0))
    assert isinstance(nearby_sprites, set)
    assert len(nearby_sprites) == 2
    assert nearby_sprites == set([sprite_1, sprite_2])

    nearby_sprites = sh.get_sprites_near_point((20, 0))
    assert isinstance(nearby_sprites, set)
    assert len(nearby_sprites) == 0


# Around for running debugger on the module directly
# if __name__ == "__main__":
#     test_reset()
