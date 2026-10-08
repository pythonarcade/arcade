"""
Collision checks find hit boxes that reach beyond the sprites' drawn size,
with every collision method. The GPU method only knows the drawn sizes, and
used to miss them.
"""

import pytest

import arcade
from arcade import CollisionMethod
from arcade.hitbox import HitBox

# A 100 x 100 hit box on a 32 x 32 sprite, like a melee attack's reach
REACH = [(-50, -50), (50, -50), (50, 50), (-50, 50)]
METHODS = list(CollisionMethod)


def _sprites():
    """Two 32 px sprites 60 apart: only a 100 px hit box makes them touch"""
    near = arcade.SpriteSolidColor(32, 32, center_x=0, center_y=0)
    far = arcade.SpriteSolidColor(32, 32, center_x=60, center_y=0)
    return near, far


def _found(sprite, sprite_list, method):
    return arcade.check_for_collision_with_list(sprite, sprite_list, method=method)


@pytest.mark.parametrize("method", METHODS, ids=lambda method: method.name)
def test_checking_sprite_with_big_hit_box(window, method):
    near, far = _sprites()
    near.hit_box = HitBox(REACH)
    sprite_list = arcade.SpriteList()
    sprite_list.append(far)
    assert _found(near, sprite_list, method) == [far]


@pytest.mark.parametrize("method", METHODS, ids=lambda method: method.name)
def test_list_sprite_with_big_hit_box(window, method):
    near, far = _sprites()
    far.hit_box = HitBox(REACH)
    sprite_list = arcade.SpriteList()
    sprite_list.append(far)
    assert _found(near, sprite_list, method) == [far]


@pytest.mark.parametrize("method", METHODS, ids=lambda method: method.name)
def test_hit_box_set_after_adding_to_list(window, method):
    near, far = _sprites()
    sprite_list = arcade.SpriteList()
    sprite_list.append(far)
    assert _found(near, sprite_list, method) == []
    far.hit_box = HitBox(REACH)
    assert _found(near, sprite_list, method) == [far]


@pytest.mark.parametrize("method", METHODS, ids=lambda method: method.name)
def test_scaled_up_after_adding_to_list(window, method):
    """Scaling a sprite with a big hit box makes its reach bigger too"""
    near, far = _sprites()
    far.center_x = 110
    far.hit_box = HitBox(REACH)
    sprite_list = arcade.SpriteList()
    sprite_list.append(far)
    assert _found(near, sprite_list, method) == []
    far.scale = 2  # The hit box now reaches 100 from its center
    assert _found(near, sprite_list, method) == [far]


@pytest.mark.parametrize("method", METHODS, ids=lambda method: method.name)
def test_smaller_texture_after_adding_to_list(window, method):
    """A smaller texture shrinks the drawn size, but not a custom hit box"""
    near, far = _sprites()
    far.hit_box = HitBox(REACH)
    sprite_list = arcade.SpriteList()
    sprite_list.append(far)
    far.texture = arcade.make_soft_square_texture(4, arcade.color.RED, 255, 255)
    assert far.hit_box.points == HitBox(REACH).points
    assert _found(near, sprite_list, method) == [far]


@pytest.mark.parametrize("method", METHODS, ids=lambda method: method.name)
def test_ordinary_sprites_unchanged(window, method):
    """Without big hit boxes, the same sprites are found as before"""
    near, far = _sprites()
    sprite_list = arcade.SpriteList()
    sprite_list.append(far)
    assert _found(near, sprite_list, method) == []
    far.center_x = 30
    assert _found(near, sprite_list, method) == [far]


def test_hit_box_reach_resets_on_clear(window):
    near, far = _sprites()
    far.hit_box = HitBox(REACH)
    sprite_list = arcade.SpriteList()
    sprite_list.append(far)
    assert sprite_list._hit_box_reach > 0
    sprite_list.clear()
    assert sprite_list._hit_box_reach == 0
