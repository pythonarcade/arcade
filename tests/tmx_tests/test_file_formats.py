import arcade

TILE_SCALING = 1.0


def test_csv_left_up():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/t2.tmx")

    assert my_map.tile_size == (128, 128)
    assert my_map.orientation == "orthogonal"
    assert my_map.render_order == "left-up"
    assert my_map.infinite == 0
    assert my_map.map_size == (10, 10)

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)

    print()
    print(wall_list[0].texture.name)
    # print(wall_list[1].texture.name)

    assert wall_list[0].position == (64, 64)
    assert "boxCrate" in wall_list[0].texture.name




