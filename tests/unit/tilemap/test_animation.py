import arcade


def test_rotation_mirror():
    # Read in the tiled map
    tile_map = arcade.load_tilemap(":fixtures:tilemaps/animation.json")

    # --- Platforms ---
    assert "Blocking Sprites" in tile_map.sprite_lists
    wall_list = tile_map.sprite_lists["Blocking Sprites"]

    assert len(wall_list) == 1

    sprite = wall_list[0]
    assert isinstance(sprite, arcade.TextureAnimationSprite)
    assert len(sprite.animation) == 2
    assert sprite.animation.keyframes[0].duration == 500
    assert sprite.animation.keyframes[0].texture.file_path.name == "torch1.png"
    assert sprite.animation.keyframes[1].duration == 500
    assert sprite.animation.keyframes[1].texture.file_path.name == "torch2.png"

    sprite.update_animation(0.501)
    assert sprite.texture.file_path.name == "torch2.png"
    sprite.update_animation(0.501)
    assert sprite.texture.file_path.name == "torch1.png"
