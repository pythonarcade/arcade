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
    assert spritelist._vao1 is None


def test_it_can_insert_in_a_spritelist():
    spritelist = make_named_sprites(2)

    sprite = arcade.Sprite()
    sprite.name = 2
    spritelist.insert(1, sprite)

    assert [s.name for s in spritelist] == [0, 2, 1]
    assert [spritelist.sprite_idx[s] for s in spritelist] == [0, 1, 2]
    assert spritelist._vao1 is None


def test_it_can_reverse_a_spritelist():
    spritelist = make_named_sprites(3)

    spritelist.reverse()

    assert [s.name for s in spritelist] == [2, 1, 0]
    assert [spritelist.sprite_idx[s] for s in spritelist] == [0, 1, 2]
    assert spritelist._vao1 is None


def test_it_can_pop_at_a_given_index():
    spritelist = make_named_sprites(3)
    assert spritelist.pop(1).name == 1
    assert [s.name for s in spritelist] == [0, 2]
    assert [spritelist.sprite_idx[s] for s in spritelist] == [0, 1]
    assert spritelist._vao1 is None


