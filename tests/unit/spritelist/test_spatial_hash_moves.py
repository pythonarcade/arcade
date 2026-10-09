"""Moving a sprite in a spatial hash is applied at the next query."""

import arcade
from arcade.sprite_list.spatial_hash import SpatialHash
from arcade.types.rect import LRBT


def make_list(*positions):
    sprite_list = arcade.SpriteList(use_spatial_hash=True, spatial_hash_cell_size=32)
    sprites = []
    for position in positions:
        sprite = arcade.SpriteSolidColor(8, 8, color=arcade.color.RED)
        sprite.position = position
        sprite_list.append(sprite)
        sprites.append(sprite)
    return sprite_list, sprites


def count_adds(spatial_hash: SpatialHash | None):
    """Count calls to add() on one spatial hash."""
    assert spatial_hash is not None
    calls = []
    original = spatial_hash.add

    def add(sprite):
        calls.append(sprite)
        original(sprite)

    spatial_hash.add = add
    return calls


def test_query_finds_moved_sprite():
    sprite_list, (sprite,) = make_list((10, 10))
    spatial_hash = sprite_list.spatial_hash

    sprite.position = 500, 500

    assert spatial_hash.get_sprites_near_point((10, 10)) == set()
    assert spatial_hash.get_sprites_near_point((500, 500)) == {sprite}
    assert spatial_hash.get_sprites_near_rect(LRBT(480, 520, 480, 520)) == {sprite}

    sprite.position = 10, 10
    other = arcade.SpriteSolidColor(8, 8)
    other.position = 12, 12
    assert spatial_hash.get_sprites_near_sprite(other) == {sprite}


def test_collision_check_sees_moved_sprite():
    sprite_list, (sprite,) = make_list((10, 10))
    player = arcade.SpriteSolidColor(16, 16)
    player.position = 300, 300
    assert arcade.check_for_collision_with_list(player, sprite_list) == []

    sprite.position = 302, 298
    assert arcade.check_for_collision_with_list(player, sprite_list) == [sprite]


def test_several_moves_update_once():
    sprite_list, (sprite,) = make_list((10, 10))
    adds = count_adds(sprite_list.spatial_hash)

    # Moving the x and y separately, then rotating, used to re-add the
    # sprite three times
    sprite.center_x = 200
    sprite.center_y = 200
    sprite.angle = 45
    assert adds == []

    sprite_list.spatial_hash.get_sprites_near_point((200, 200))
    assert adds == [sprite]


def test_move_within_same_cells_is_skipped():
    sprite_list, (sprite,) = make_list((10, 10))
    adds = count_adds(sprite_list.spatial_hash)

    sprite.center_x += 1
    assert sprite_list.spatial_hash.get_sprites_near_point((11, 10)) == {sprite}
    assert adds == []


def test_remove_after_move():
    sprite_list, (sprite, _other) = make_list((10, 10), (100, 100))
    sprite.position = 500, 500
    sprite_list.remove(sprite)

    spatial_hash = sprite_list.spatial_hash
    assert spatial_hash.get_sprites_near_point((500, 500)) == set()
    assert spatial_hash.get_sprites_near_point((10, 10)) == set()
    assert spatial_hash.count == 1


def test_contents_include_moves():
    sprite_list, (sprite,) = make_list((10, 10))
    sprite.position = 500, 500

    spatial_hash = sprite_list.spatial_hash
    occupied = {cell for cell, bucket in spatial_hash.contents.items() if bucket}
    assert occupied == {(15, 15)}
    assert spatial_hash.buckets_for_sprite[sprite] == [{sprite}]


def test_reset_forgets_moves():
    sprite_list, (sprite,) = make_list((10, 10))
    sprite.position = 500, 500
    sprite_list.spatial_hash.reset()
    assert sprite_list.spatial_hash.get_sprites_near_point((500, 500)) == set()
