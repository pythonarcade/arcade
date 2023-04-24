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
    del scene["Player"]

    with pytest.raises(KeyError):
        scene["Player"]

    del scene[scene._sprite_lists[0]]

    with pytest.raises(KeyError):
        scene["Walls"]
