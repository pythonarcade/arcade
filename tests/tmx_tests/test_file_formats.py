import arcade

TILE_SCALING = 1.0


def test_csv_left_up():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/cvs_left_up_embedded.tmx")

    assert my_map.tile_size == (128, 128)
    assert my_map.orientation == "orthogonal"
    assert my_map.render_order == "left-up"
    assert my_map.infinite == 0
    assert my_map.map_size == (10, 10)

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)

    assert wall_list[0].position == (64, 1216)
    assert "dirtCenter" in wall_list[0].texture.name

    assert wall_list[1].position == (1216, 1216)
    assert "grassCenter" in wall_list[1].texture.name

    assert wall_list[2].position == (64, 64)
    assert "boxCrate" in wall_list[2].texture.name

def test_csv_right_down():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/cvs_right_down_external.tmx")

    assert my_map.tile_size == (128, 128)
    assert my_map.orientation == "orthogonal"
    assert my_map.render_order == "right-down"
    assert my_map.infinite == 0
    assert my_map.map_size == (10, 10)

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)

    assert wall_list[0].position == (64, 1216)
    assert "dirtCenter" in wall_list[0].texture.name

    assert wall_list[1].position == (1216, 1216)
    assert "grassCenter" in wall_list[1].texture.name

    assert wall_list[2].position == (64, 64)
    assert "boxCrate" in wall_list[2].texture.name

def test_base_64_zlib():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/base_64_zlib.tmx")

    assert my_map.tile_size == (128, 128)
    assert my_map.orientation == "orthogonal"
    assert my_map.render_order == "left-down"
    assert my_map.infinite == 0
    assert my_map.map_size == (10, 10)

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)
    #
    # for wall in wall_list:
    #     print()
    #     print(wall.position)
    #     print(wall.texture.name)

    assert wall_list[0].position == (64, 1216)
    assert "dirtCenter" in wall_list[0].texture.name

    assert wall_list[1].position == (1216, 1216)
    assert "grassCenter" in wall_list[1].texture.name

    assert wall_list[2].position == (64, 64)
    assert "boxCrate" in wall_list[2].texture.name

def test_base_64_zstandard():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/base_64_zstandard.tmx")

    assert my_map.tile_size == (128, 128)
    assert my_map.orientation == "orthogonal"
    assert my_map.render_order == "right-up"
    assert my_map.infinite == 0
    assert my_map.map_size == (10, 10)

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)
    #
    # for wall in wall_list:
    #     print()
    #     print(wall.position)
    #     print(wall.texture.name)

    assert wall_list[0].position == (64, 1216)
    assert "dirtCenter" in wall_list[0].texture.name

    assert wall_list[1].position == (1216, 1216)
    assert "grassCenter" in wall_list[1].texture.name

    assert wall_list[2].position == (64, 64)
    assert "boxCrate" in wall_list[2].texture.name

def test_base_64_gzip():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/base_64_gzip.tmx")

    assert my_map.tile_size == (128, 128)
    assert my_map.orientation == "orthogonal"
    assert my_map.render_order == "right-up"
    assert my_map.infinite == 0
    assert my_map.map_size == (10, 10)

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites', TILE_SCALING)

    assert wall_list[0].position == (64, 1216)
    assert "dirtCenter" in wall_list[0].texture.name

    assert wall_list[1].position == (1216, 1216)
    assert "grassCenter" in wall_list[1].texture.name

    assert wall_list[2].position == (64, 64)
    assert "boxCrate" in wall_list[2].texture.name

