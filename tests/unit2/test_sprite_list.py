from re import split
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


def test_can_assign_back_to_self():
    spritelist = make_named_sprites(3)
    spritelist[0] = spritelist[0]
    assert spritelist[0] == spritelist[0]

def test_can_shuffle():
    spritelist = make_named_sprites(3)
    spritelist.shuffle()

    # Ensure the index buffer is referring to the correct slots
    slots = [spritelist.sprite_slot[s] for s in spritelist]
    assert list(spritelist._sprite_index_data[:3]) == slots
