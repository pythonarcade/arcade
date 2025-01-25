from array import array
import struct
import pytest
import arcade
from arcade import gl


def make_named_sprites(amount):
    spritelist = arcade.SpriteList()

    sprites = []
    for i in range(amount):
        c = min(255, i + 1)
        sprite = arcade.SpriteSolidColor(16, 16, color=(c, c, c, 1))
        sprite.name = i
        sprites.append(sprite)

    spritelist.extend(sprites)
    return spritelist


def test_filter(window):
    atlas = arcade.DefaultTextureAtlas((256, 256))
    spritelist = arcade.SpriteList(atlas=atlas)
    spritelist.append(arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE))

    assert atlas.texture.filter == (gl.LINEAR, gl.LINEAR)
    spritelist.draw(filter=(gl.NEAREST, gl.NEAREST))
    assert atlas.texture.filter == (gl.NEAREST, gl.NEAREST)
    spritelist.draw()
    assert atlas.texture.filter == (gl.LINEAR, gl.LINEAR)
    spritelist.draw(pixelated=True)
    assert atlas.texture.filter == (gl.NEAREST, gl.NEAREST)


def test_default_texture_filter(window):
    arcade.SpriteList.DEFAULT_TEXTURE_FILTER = gl.NEAREST, gl.NEAREST
    spritelist = arcade.SpriteList()
    spritelist.append(arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE))
    spritelist.draw()
    assert spritelist.atlas.texture.filter == (gl.NEAREST, gl.NEAREST)


# Temp fix for  https://github.com/pythonarcade/arcade/issues/2074
def test_copy_dunder_stubs_raise_notimplementederror():
    spritelist = arcade.SpriteList()
    import copy

    with pytest.raises(NotImplementedError):
       _ = copy.copy(spritelist)

    with pytest.raises(NotImplementedError):
       _ = copy.deepcopy(spritelist)


def test_it_can_extend_a_spritelist_from_a_list():
    spritelist = arcade.SpriteList()
    sprites = []
    for i in range(10):
        sprites.append(arcade.SpriteSolidColor(width=16, height=16, color=arcade.color.RED))

    spritelist.extend(sprites)

    assert len(spritelist) == 10


def test_it_can_extend_a_spritelist_from_a_generator_expression():
    sprite_list = arcade.SpriteList()
    sprite_list.extend(
        (
            arcade.SpriteSolidColor(
                width=32,
                height=32,
                center_x=coord,
                center_y=coord,
                color=arcade.color.RED,
            )
            for coord in range(5)
        )
    )
    for coord, sprite in enumerate(sprite_list):
        assert sprite.position == (coord, coord)


def test_it_can_extend_a_spritelist_from_a_generator_function():
    sprite_list = arcade.SpriteList()

    def sprite_grid_generator(cols: int, rows: int, cell_size: float):
        for row in range(rows):
            for col in range(cols):
                yield arcade.SpriteSolidColor(
                    width=32,
                    height=32,
                    color=arcade.color.RED,
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

    sprite = arcade.SpriteSolidColor(16, 16, color=arcade.color.RED)
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


def test_it_raises_indexerror_when_popping_from_empty_spritelist():
    spritelist = make_named_sprites(0)

    # With default index
    with pytest.raises(IndexError):
        spritelist.pop()

    # With positional argument
    with pytest.raises(IndexError):
        spritelist.pop(0)

    # With keyword argument
    with pytest.raises(IndexError):
        spritelist.pop(index=1)


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
    spritelist[0] = arcade.SpriteSolidColor(16, 16, color=arcade.color.RED)
    spritelist.insert(0, arcade.SpriteSolidColor(16, 16, color=arcade.color.BLUE))

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


def test_sort(ctx):
    s1 = arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE)
    s1.position = 100, 100

    s2 = arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE)
    s2.position = 110, 100

    s3 = arcade.SpriteSolidColor(10, 10, color=arcade.color.WHITE)
    s3.position = 120, 100

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


@pytest.mark.parametrize('capacity', (128, 512, 1024))
def test_clear(ctx, capacity):
    sp = arcade.SpriteList(capacity=capacity)
    sp.clear(capacity=None)
    assert len(sp._sprite_index_data) == capacity
    assert len(sp._sprite_pos_data) == capacity * 3
    assert sp._sprite_index_buf.size == capacity * 4
    assert sp._sprite_pos_buf.size == capacity * 4 * 3

    sp.extend(make_named_sprites(capacity))
    sp.clear(capacity=capacity)
    assert len(sp) == 0
    assert sp._sprite_index_slots == 0
    assert sp._sprite_buffer_slots == 0
    assert sp.atlas is not None
    assert len(sp._sprite_index_data) == capacity
    assert len(sp._sprite_pos_data) == capacity * 3
    assert sp._sprite_index_buf.size == capacity * 4
    assert sp._sprite_pos_buf.size == capacity * 4 * 3


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

    # Setting float RGBA works
    sp.color_normalized = 0.1, 0.2, 0.3, 0.4
    assert sp.color_normalized == pytest.approx((0.1, 0.2, 0.3, 0.4), rel=0.1)

    # Setting float RGB works
    sp.color_normalized = 0.5, 0.6, 0.7
    assert sp.color_normalized == pytest.approx((0.5, 0.6, 0.7, 1.0), rel=0.1)

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


def test_swap(window):
    """Test swapping sprites including drawing order"""
    window.clear()

    sprites = [
        arcade.SpriteSolidColor(10, 10, color=arcade.color.RED),
        arcade.SpriteSolidColor(10, 10, color=arcade.color.GREEN)
    ]
    sl = arcade.SpriteList()
    sl.extend(sprites)

    # Green sprite is last in list and drawn last
    sl.draw()
    assert arcade.get_pixel(x=0, y=0, components=4) == arcade.color.GREEN
    assert sl.sprite_list == sprites

    # Swap the order
    sl.swap(0, 1)

    # Red sprite is last in list and drawn last
    sl.draw()
    assert arcade.get_pixel(x=0, y=0, components=4) == arcade.color.RED
    assert sl.sprite_list == sprites[::-1]
