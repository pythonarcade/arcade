from array import array
import struct
import pytest
import arcade


def make_named_sprites(amount):
    spritelist = arcade.SpriteList()

    sprites = []
    for i in range(amount):
        c = i + 1
        sprite = arcade.SpriteSolidColor(16, 16, (c, c, c, 1))
        sprite.name = i
        sprites.append(sprite)

    spritelist.extend(sprites)
    return spritelist


def test_it_can_extend_a_spritelist_from_a_list():
    spritelist = arcade.SpriteList()
    sprites = []
    for i in range(10):
        sprites.append(arcade.Sprite())

    spritelist.extend(sprites)

    assert len(spritelist) == 10


def test_it_can_extend_a_spritelist_from_a_generator_expression():
    sprite_list = arcade.SpriteList()
    sprite_list.extend(
        (arcade.Sprite(center_x=coord, center_y=coord) for coord in range(5))
    )
    for coord, sprite in enumerate(sprite_list):
        assert sprite.position == (coord, coord)


def test_it_can_extend_a_spritelist_from_a_generator_function():
    sprite_list = arcade.SpriteList()

    def sprite_grid_generator(cols: int, rows: int, cell_size: float):
        for row in range(rows):
            for col in range(cols):
                yield arcade.Sprite(
                    center_x=col * cell_size,
                    center_y=row * cell_size
                )

    sprite_list.extend(sprite_grid_generator(3, 5, 1.0))
    index = 0
    for y in range(5):
        for x in range(3):
            assert sprite_list[index].position == (x, y)
            index += 1


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


def test_setitem(ctx):
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
    spritelist[0] = arcade.SpriteSolidColor(16, 16, arcade.color.RED)
    spritelist.insert(0, arcade.SpriteSolidColor(16, 16, arcade.color.BLUE))

    spritelist.draw()


def test_can_shuffle(ctx):
    num_sprites = 10
    spritelist = make_named_sprites(num_sprites)

    # Shuffle multiple times
    for _ in range(100):
        spritelist.shuffle()
        spritelist.draw()
        # Ensure the index buffer is referring to the correct slots
        # Raw buffer from OpenGL
        index_data = struct.unpack(f"{num_sprites}i", spritelist._sprite_index_buf.read()[:num_sprites * 4])
        for i, sprite in enumerate(spritelist):
            # Check if slots are updated
            slot = spritelist.sprite_slot[sprite]
            assert slot == spritelist._sprite_index_data[i]
            assert slot == index_data[i]


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


def test_sort(ctx):
    s1 = arcade.SpriteSolidColor(10, 10, arcade.color.WHITE)
    s1.set_position(100, 100)

    s2 = arcade.SpriteSolidColor(10, 10, arcade.color.WHITE)
    s2.set_position(110, 100)

    s3 = arcade.SpriteSolidColor(10, 10, arcade.color.WHITE)
    s3.set_position(120, 100)

    sprites_v1 = [s1, s2, s3]
    sprites_v2 = [s3, s2, s1]

    spritelist = arcade.SpriteList()
    spritelist.extend(sprites_v1)
    spritelist.draw()

    assert spritelist.sprite_list == sprites_v1

    spritelist.sort(key=lambda x: x.position[0], reverse=True)
    assert spritelist.sprite_list == sprites_v2
    assert spritelist._sprite_index_data[0:3] == array("f", [2, 1, 0])

    spritelist.sort(key=lambda x: x.position[0])
    assert spritelist.sprite_list == sprites_v1
    assert spritelist._sprite_index_data[0:3] == array("f", [0, 1, 2])


def test_clear(ctx):
    sp = arcade.SpriteList()
    sp.clear()
    sp.extend(make_named_sprites(100))
    sp.clear()
    assert len(sp) == 0
    assert sp._sprite_index_slots == 0
    assert sp._sprite_buffer_slots == 0
    assert sp.atlas is not None
    assert len(sp._sprite_index_data) == 100
    assert len(sp._sprite_pos_data) == 100 * 2
    assert sp._sprite_index_buf.size == 100 * 4
    assert sp._sprite_pos_buf.size == 100 * 4 * 2

def test_color():
    """Spritelist color"""
    sp = arcade.SpriteList()
    # Check default values
    assert sp.color == (255, 255, 255, 255)
    assert sp.color_normalized == (1.0, 1.0, 1.0, 1.0)
    assert sp.alpha == 255
    assert sp.alpha_normalized == 1.0

    # Change color and test
    sp.color = 16, 32, 64, 128
    assert sp.color == (16, 32, 64, 128)
    assert sp.color_normalized == pytest.approx((16 / 255, 32 / 255, 64 / 255, 128 / 255), rel=0.01)
    assert sp.alpha == 128
    assert sp.alpha_normalized == pytest.approx(128 / 256, rel=0.01)

    # Alpha
    sp.alpha = 172
    assert sp.alpha == 172
    assert sp.alpha_normalized == pytest.approx(172/255, rel=0.01)
    sp.alpha_normalized == 1.0

    # Alpha Normalized
    sp.alpha_normalized = 0.5
    assert sp.alpha == 127
    assert sp.alpha_normalized == 0.5

    # overflow
    # sp.alpha = 1000
    # assert sp.alpha == 255
    # assert sp.alpha_normalized == 1.0
    # sp.alpha_normalized = 20.0
    # assert sp.alpha_normalized == 1.0
    # assert sp.alpha == 255
    # sp.alpha = -1000
    # assert sp.alpha == 0
    # assert sp.alpha_normalized == 0.0
    # sp.alpha_normalized = -1000
    # assert sp.alpha == 0
    # assert sp.alpha_normalized == 0.0
