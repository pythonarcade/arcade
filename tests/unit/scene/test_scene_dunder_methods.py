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
    assert bool(scene) == False

    scene.add_sprite_list("Walls")
    assert bool(scene) == True

def test_contains():
    scene = arcade.Scene()
    "Walls" not in scene
    None not in scene
    
    Walls_SpriteList = arcade.SpriteList()
    scene.add_sprite_list("Walls", sprite_list = Walls_SpriteList)
    assert "Walls" in scene

    test_sprite = arcade.Sprite()
    Walls_SpriteList.append(test_sprite)
    assert Walls_SpriteList in scene


    Coins_SpriteList = arcade.SpriteList()
    scene.add_sprite_list("Coins", sprite_list = Coins_SpriteList)
    assert "Coins" in scene

    test_sprite = arcade.Sprite()
    Coins_SpriteList.append(test_sprite)
    assert Coins_SpriteList in scene

    assert None not in scene
