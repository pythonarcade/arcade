import arcade
import pytest

def test_remove_sprite_list_by_index():
    scene = arcade.Scene()
    scene.add_sprite_list("Player")

    scene.remove_sprite_list_by_index(0)

    with pytest.raises(KeyError):
        scene["Player"]

def test_remove_sprite_list_by_name():
    scene = arcade.Scene()
    scene.add_sprite_list("Walls")

    scene.remove_sprite_list_by_name("Walls")

    with pytest.raises(KeyError):
        scene["Walls"]

def test_remove_sprite_list_by_object():
    scene = arcade.Scene()
    scene.add_sprite_list("Coins")

    scene.remove_sprite_list_by_object(scene.get_sprite_list("Coins"))

    with pytest.raises(KeyError):
        scene["Coins"]
