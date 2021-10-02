
import pytest
import arcade


def make_named_sprites(amount):
    spritelist = arcade.SpriteList()

    sprites = []
    for i in range(amount):
        sprite = arcade.Sprite()
        sprite.name = i
        sprites.append(sprite)

    spritelist.extend(sprites)
    return spritelist


def test_it_can_extend_a_spritelist():
    spritelist = arcade.SpriteList()
    sprites = []
    for i in range(10):
        sprites.append(arcade.Sprite())

    spritelist.extend(sprites)

    assert len(spritelist) == 10


def test_it_can_insert_in_a_spritelist():
    spritelist = make_named_sprites(2)

    sprite = arcade.Sprite()
    sprite.name = 2
    spritelist.insert(1, sprite)

    assert [s.name for s in spritelist] == [0, 2, 1]
    # New slot was added in position 2
    assert [spritelist.sprite_slot[s] for s in spritelist] == [0, 2, 1]
    # Index buffer should refer to the slots in the same order
    assert list(spritelist._sprite_index_data[:3]) == [0, 2, 1]


def test_it_can_reverse_a_spritelist():
    spritelist = make_named_sprites(3)
    spritelist.reverse()

    assert [s.name for s in spritelist] == [2, 1, 0]
    # The slot indices doesn't change, but the position in the spritelist do
    assert [spritelist.sprite_slot[s] for s in spritelist] == [2, 1, 0]
    assert list(spritelist._sprite_index_data[:3]) == [2, 1, 0]


def test_it_can_pop_at_a_given_index():
    spritelist = make_named_sprites(3)
    assert spritelist.pop(1).name == 1
    assert [s.name for s in spritelist] == [0, 2]
    # Indices will not change internally
    assert [spritelist.sprite_slot[s] for s in spritelist] == [0, 2]


def test_setitem():
    """Testing __setitem__"""
    num_sprites = 10
    spritelist = make_named_sprites(num_sprites)

    # Assign the same item to the same slot
    for i in range(num_sprites):
        spritelist[i] = spritelist[i]
        assert spritelist[i] == spritelist[i]

    # Try to duplicate a sprite
    with pytest.raises(Exception):
        spritelist[0] = spritelist[1]

    # Assign new sprite
    spritelist[0] = arcade.Sprite()


def test_can_shuffle():
    num_sprites = 10
    spritelist = make_named_sprites(num_sprites)

    # Shuffle multiple times
    for _ in range(10):
        spritelist.shuffle()
        # Ensure the index buffer is referring to the correct slots
        slots = [spritelist.sprite_slot[s] for s in spritelist]
        assert list(spritelist._sprite_index_data[:num_sprites]) == slots
        assert spritelist._sprite_buffer_slots == 10
        assert spritelist._sprite_index_slots == 10
        assert len(spritelist) == 10


def test_spritelist_lazy():
    """Test lazy creation of spritelist"""
    spritelist = arcade.SpriteList(lazy=True, use_spatial_hash=True)
    assert spritelist._sprite_pos_buf == None
    assert spritelist._geometry == None
    for x in range(100):
        spritelist.append(
            arcade.Sprite(":resources:images/items/coinGold.png", center_x=x * 64)
        )
    assert len(spritelist) == 100
    assert spritelist.spatial_hash
