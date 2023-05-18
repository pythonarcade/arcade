import arcade
import pytest


def test_len():
    scene = arcade.Scene()
    scene.add_sprite_list("Player")

    assert len(scene) == 1

    scene.add_sprite_list("Walls")
    scene.add_sprite_list("Coins")

    assert len(scene) == 3


def test_delitem():
    scene = arcade.Scene()
    scene.add_sprite_list("Walls")
    scene.add_sprite_list("Player")
    scene.add_sprite_list("Coins")
    del scene["Player"]

    with pytest.raises(KeyError):
        scene["Player"]

    del scene[scene._sprite_lists[0]]

    with pytest.raises(KeyError):
        scene["Walls"]

    del scene[0]

    with pytest.raises(KeyError):
        scene["Coins"]


def test_bool():
    scene = arcade.Scene()
    assert not scene

    scene.add_sprite_list("Walls")
    assert scene


def test_contains():
    scene = arcade.Scene()
    assert "Walls" not in scene
    assert None not in scene
    
    walls_spriteList = arcade.SpriteList()
    scene.add_sprite_list("Walls", use_spatial_hash=True, sprite_list=walls_spriteList)
    assert "Walls" in scene

    test_sprite = arcade.Sprite()
    walls_spriteList.append(test_sprite)
    assert walls_spriteList in scene

    coins_spriteList = arcade.SpriteList()
    scene.add_sprite_list("Coins", use_spatial_hash=True, sprite_list=coins_spriteList)
    assert "Coins" in scene

    test_sprite = arcade.Sprite()
    coins_spriteList.append(test_sprite)
    assert coins_spriteList in scene

    assert None not in scene
