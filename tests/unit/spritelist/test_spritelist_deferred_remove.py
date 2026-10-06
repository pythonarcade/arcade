"""
SpriteList.remove() takes sprites out of the list's storage later, when the
list is next used, so many removals are applied in one pass. These tests
check the list behaves as if each removal happened right away.
"""

import random
import struct

import pytest

import arcade
from arcade.sprite_list import sprite_list as sprite_list_module

# Fewer than this many removals are applied one at a time, more in one pass
ONE_PASS = getattr(sprite_list_module, "_REMOVE_IN_ONE_PASS", 8)
COUNTS = [1, ONE_PASS - 1, ONE_PASS, 40]


def _make(count, use_spatial_hash=False):
    sprites = arcade.SpriteList(use_spatial_hash=use_spatial_hash)
    for i in range(count):
        sprite = arcade.SpriteSolidColor(4, 4, center_x=i * 5, center_y=10)
        sprite.name = i
        sprites.append(sprite)
    return sprites


def _drawn_sprites(spritelist):
    """The sprites the GPU will draw, in order, read back from the GPU index buffer"""
    spritelist.draw()
    count = spritelist._sprite_index_slots
    gpu_slots = struct.unpack(f"{count}I", spritelist.data.storage_index.read()[: count * 4])
    sprite_for_slot = {slot: sprite for sprite, slot in spritelist.sprite_slot.items()}
    return [sprite_for_slot.get(slot) for slot in gpu_slots]


def _check(spritelist, expected):
    """The list, its bookkeeping, and the GPU draw order all match ``expected``"""
    assert list(spritelist) == expected
    assert len(spritelist) == len(expected)
    assert [spritelist[i] for i in range(len(expected))] == expected
    assert all(spritelist.index(sprite) == i for i, sprite in enumerate(expected))
    assert set(spritelist.sprite_slot) == set(expected)
    slots = [spritelist.sprite_slot[sprite] for sprite in expected]
    assert len(set(slots)) == len(slots)
    assert not set(slots) & set(spritelist._sprite_buffer_free_slots)
    assert _drawn_sprites(spritelist) == expected


@pytest.mark.parametrize("count", COUNTS)
def test_remove_keeps_order(ctx, count):
    spritelist = _make(60)
    spritelist.draw()
    sprites = list(spritelist)
    removed = random.Random(count).sample(sprites, count)
    for sprite in removed:
        sprite.remove_from_sprite_lists()
    _check(spritelist, [sprite for sprite in sprites if sprite not in removed])


@pytest.mark.parametrize("count", COUNTS)
def test_removed_sprite_is_gone_right_away(ctx, count):
    spritelist = _make(60, use_spatial_hash=True)
    removed = list(spritelist)[:count]
    for sprite in removed:
        spritelist.remove(sprite)
        assert sprite not in spritelist
        assert sprite.sprite_lists == []
        # Collisions don't find it, even before the list is used again
        assert sprite not in arcade.check_for_collision_with_list(sprite, spritelist)
    with pytest.raises(ValueError):
        spritelist.remove(removed[0])


@pytest.mark.parametrize("count", COUNTS)
def test_new_sprites_reuse_slots(ctx, count):
    """Sprites added after removals can get the removed sprites' buffer slots"""
    spritelist = _make(60)
    spritelist.draw()
    sprites = list(spritelist)
    for sprite in sprites[:count]:
        sprite.remove_from_sprite_lists()
    added = list(_make(count))
    for sprite in added:
        sprite.remove_from_sprite_lists()
        spritelist.append(sprite)
    _check(spritelist, sprites[count:] + added)


@pytest.mark.parametrize("count", COUNTS)
def test_remove_and_add_back(ctx, count):
    """A removed sprite added back before the list is used again moves to the end"""
    spritelist = _make(60)
    sprites = list(spritelist)
    removed = sprites[10 : 10 + count]
    for sprite in removed:
        spritelist.remove(sprite)
    expected = [sprite for sprite in sprites if sprite not in removed]
    spritelist.append(removed[0])
    expected.append(removed[0])
    if count > 1:
        spritelist.insert(0, removed[-1])
        expected.insert(0, removed[-1])
    _check(spritelist, expected)


@pytest.mark.parametrize("count", COUNTS)
@pytest.mark.parametrize(
    "operation",
    ["pop", "pop_first", "insert", "swap", "setitem", "reverse", "sort", "shuffle", "clear"],
)
def test_operations_after_removals(ctx, count, operation):
    """Every list operation sees the removals"""
    spritelist = _make(60)
    spritelist.draw()
    sprites = list(spritelist)
    for sprite in sprites[5 : 5 + count]:
        sprite.remove_from_sprite_lists()
    expected = sprites[:5] + sprites[5 + count :]

    if operation == "pop":
        assert spritelist.pop() is expected.pop()
    elif operation == "pop_first":
        assert spritelist.pop(0) is expected.pop(0)
    elif operation == "insert":
        new = arcade.SpriteSolidColor(4, 4)
        spritelist.insert(3, new)
        expected.insert(3, new)
    elif operation == "swap":
        spritelist.swap(1, -1)
        expected[1], expected[-1] = expected[-1], expected[1]
    elif operation == "setitem":
        new = arcade.SpriteSolidColor(4, 4)
        spritelist[2] = new
        expected[2] = new
    elif operation == "reverse":
        spritelist.reverse()
        expected.reverse()
    elif operation == "sort":
        spritelist.sort(key=lambda sprite: -sprite.name)
        expected.sort(key=lambda sprite: -sprite.name)
    elif operation == "shuffle":
        spritelist.shuffle()
        # Any order of the same sprites, as long as the GPU draws that order
        assert sorted(spritelist, key=lambda sprite: sprite.name) == expected
        expected = list(spritelist)
    elif operation == "clear":
        spritelist.clear()
        expected = []
    _check(spritelist, expected)


def test_many_rounds_of_removing_and_adding(ctx):
    """Random removals and additions over many frames stay consistent"""
    rng = random.Random(7)
    spritelist = _make(200)
    expected = list(spritelist)
    for frame in range(30):
        for sprite in rng.sample(expected, rng.randrange(0, 25)):
            sprite.remove_from_sprite_lists()
            expected.remove(sprite)
        for _ in range(rng.randrange(0, 25)):
            sprite = arcade.SpriteSolidColor(4, 4)
            sprite.name = frame
            spritelist.append(sprite)
            expected.append(sprite)
        if frame % 3 == 0:
            _check(spritelist, expected)
    _check(spritelist, expected)


def test_removed_sprites_are_not_drawn(window):
    """Only the sprites left are drawn"""
    spritelist = arcade.SpriteList()
    red = arcade.SpriteSolidColor(20, 20, center_x=15, center_y=15, color=arcade.color.RED)
    blues = [
        arcade.SpriteSolidColor(20, 20, center_x=15, center_y=15, color=arcade.color.BLUE)
        for _ in range(ONE_PASS + 2)
    ]
    spritelist.append(red)
    spritelist.extend(blues)
    window.clear()
    spritelist.draw()
    assert arcade.get_pixel(15, 15) == arcade.color.BLUE[:3]

    for blue in blues:
        blue.remove_from_sprite_lists()
    window.clear()
    spritelist.draw()
    assert arcade.get_pixel(15, 15) == arcade.color.RED[:3]


class _CountingList(list):
    """A list that counts searches, which cost O(N) each"""

    searches = 0

    def index(self, *args):
        type(self).searches += 1
        return super().index(*args)


@pytest.mark.parametrize(("count", "searches"), [(ONE_PASS - 1, ONE_PASS - 1), (40, 0)])
def test_many_removals_dont_search_for_each_sprite(ctx, count, searches):
    """A few removals find each sprite, but many are applied in one pass"""
    spritelist = _make(60)
    _CountingList.searches = 0
    spritelist.sprite_list = _CountingList(spritelist.sprite_list)
    sprites = list(spritelist)
    for sprite in sprites[:count]:
        sprite.remove_from_sprite_lists()
    assert len(spritelist) == 60 - count
    assert _CountingList.searches == searches
