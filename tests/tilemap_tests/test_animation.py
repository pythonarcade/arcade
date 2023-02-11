import os

import arcade


def test_rotation_mirror():

    # Change to current directory
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path)

    # Read in the tiled map
    tile_map = arcade.load_tilemap("../tiled_maps/animation.json")

    # --- Platforms ---
    assert "Blocking Sprites" in tile_map.sprite_lists
    wall_list = tile_map.sprite_lists["Blocking Sprites"]

    assert len(wall_list) == 1

    sprite = wall_list[0]
    assert isinstance(sprite, arcade.AnimatedTimeBasedSprite)
    assert len(sprite.frames) == 2
    assert sprite.frames[0].duration == 500
    assert "torch1" in sprite.frames[0].texture.file_name
    assert sprite.frames[1].duration == 500
    assert "torch2" in sprite.frames[1].texture.file_name

    sprite.update_animation(0.501)
    assert "torch2" in sprite.texture.file_name
    sprite.update_animation(0.501)
    assert "torch1" in sprite.texture.file_name
