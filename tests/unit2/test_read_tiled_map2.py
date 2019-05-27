import arcade

def test_one():
    map = arcade.read_tiled_map2("test_data/test_map_1.tmx")

    assert map.map_size.width == 10
    assert map.map_size.height == 5
    assert not map.infinite
    assert map.orientation == "orthogonal"
    assert map.render_order == 'right-down'
    assert len(map.layers) == 2
    assert map.background_color == (0, 160, 229)

    platforms_list = arcade.generate_sprites(map, "Platforms", base_directory="test_data")
    background_list = arcade.generate_sprites(map, "Background", base_directory="test_data")

    assert len(platforms_list) == 10
    assert len(background_list) == 2

    first_sprite = platforms_list[0]
    assert first_sprite.center_x == -64
    assert first_sprite.center_y == -64
    assert first_sprite.width == 128
    assert first_sprite.height == 128

def test_two():
    map = arcade.read_tiled_map2("test_data/test_map_2.tmx")

    assert map.map_size.width == 10
    assert map.map_size.height == 5
    assert not map.infinite
    assert map.orientation == "orthogonal"
    assert map.render_order == 'left-up'
    assert len(map.layers) == 2

    platforms_list = arcade.generate_sprites(map, "Platforms", base_directory="test_data")

    first_sprite = platforms_list[0]
    assert first_sprite.center_x == -64
    assert first_sprite.center_y == -64
    assert first_sprite.width == 128
    assert first_sprite.height == 128

    dirt_list = arcade.generate_sprites(map, "Dirt", base_directory="test_data")
    first_sprite = dirt_list[0]
    print(first_sprite)
