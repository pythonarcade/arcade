import arcade

def test_rotation_mirror():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/animation.tmx")

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites')

    assert len(wall_list) == 1

    sprite = wall_list[0]
    assert isinstance(sprite, arcade.AnimatedTimeBasedSprite)
    assert len(sprite.frames) == 2
    assert sprite.frames[0].duration == 500
    assert "torch1" in sprite.frames[0].texture.name
    assert sprite.frames[1].duration == 500
    assert "torch2" in sprite.frames[1].texture.name

    assert "torch1" in sprite.texture.name
    sprite.update_animation(.501)
    assert "torch2" in sprite.texture.name
    sprite.update_animation(.501)
    assert "torch1" in sprite.texture.name
