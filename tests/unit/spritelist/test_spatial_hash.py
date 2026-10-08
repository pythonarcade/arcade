import pytest

import arcade
from arcade.sprite_list.spatial_hash import SpatialHash
from arcade.types.rect import LRBT


def test_create():
    sh = SpatialHash(cell_size=10)
    assert sh.cell_size == 10
    assert sh.contents == {}
    assert sh.buckets_for_sprite == {}
    assert sh.count == 0


def test_incorrect_str_input():
    with pytest.raises(TypeError):
        SpatialHash(cell_size="10")


def test_incorrect_inf_input():
    with pytest.raises(TypeError):
        SpatialHash(cell_size=float("inf"))


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


def test_get_near_sprite():
    """Test getting nearby sprites"""
    sh = SpatialHash(cell_size=10)
    # Covers x from -25 to -15, cells -3 to -2
    sprite_1 = arcade.SpriteSolidColor(10, 10, center_x=-20)
    # Covers x from 15 to 25, cells 1 to 2
    sprite_2 = arcade.SpriteSolidColor(10, 10, center_x=20)
    sh.add(sprite_1)
    sh.add(sprite_2)

    nearby_sprites = sh.get_sprites_near_sprite(arcade.SpriteSolidColor(10, 10, center_x=-20))
    assert isinstance(nearby_sprites, set)
    assert nearby_sprites == {sprite_1}

    nearby_sprites = sh.get_sprites_near_sprite(arcade.SpriteSolidColor(10, 10, center_x=20))
    assert nearby_sprites == {sprite_2}

    nearby_sprites = sh.get_sprites_near_sprite(arcade.SpriteSolidColor(60, 10, center_x=0))
    assert nearby_sprites == {sprite_1, sprite_2}

    nearby_sprites = sh.get_sprites_near_sprite(arcade.SpriteSolidColor(10, 10, center_y=100))
    assert nearby_sprites == set()


@pytest.mark.parametrize("angle", [0, 30, 45, 90])
def test_cell_bounds_match_sprite_bounds(angle):
    """Cell bounds should match those from the sprite's left/right/bottom/top."""
    sh = SpatialHash(cell_size=10)
    sprite = arcade.SpriteSolidColor(40, 10, center_x=3, center_y=-7)
    sprite.angle = angle

    expected_min = sh.hash((int(sprite.left), int(sprite.bottom)))
    expected_max = sh.hash((int(sprite.right), int(sprite.top)))
    assert sh._get_cell_bounds(sprite) == (expected_min, expected_max)


def test_queries_do_not_add_buckets():
    """Querying empty areas must not create new buckets."""
    sh = SpatialHash(cell_size=10)
    sh.add(arcade.SpriteSolidColor(10, 10))
    bucket_count = len(sh.contents)

    far_sprite = arcade.SpriteSolidColor(50, 50, center_x=1000, center_y=1000)
    assert sh.get_sprites_near_sprite(far_sprite) == set()
    assert sh.get_sprites_near_point((1000, 1000)) == set()
    assert sh.get_sprites_near_rect(LRBT(1000, 1100, 1000, 1100)) == set()

    assert len(sh.contents) == bucket_count


def test_get_near_point_returns_copy():
    """Modifying the returned set must not change the spatial hash."""
    sh = SpatialHash(cell_size=10)
    sprite = arcade.SpriteSolidColor(10, 10)
    sh.add(sprite)

    nearby_sprites = sh.get_sprites_near_point((0, 0))
    nearby_sprites.clear()
    assert sh.get_sprites_near_point((0, 0)) == {sprite}


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
