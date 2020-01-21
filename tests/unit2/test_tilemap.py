import arcade


def test_one():
    tmx_map = arcade.tilemap.read_tmx(":resources:/tmx_maps/test_map_1.tmx")

    assert tmx_map.map_size.width == 10
    assert tmx_map.map_size.height == 5
    assert not tmx_map.infinite
    assert tmx_map.orientation == "orthogonal"
    assert tmx_map.render_order == 'right-down'
    assert len(tmx_map.layers) == 2
    assert tmx_map.background_color == (0, 160, 229)

    platforms_list = arcade.tilemap.process_layer(tmx_map, "Platforms", base_directory="test_data")

    assert platforms_list is not None
    assert len(platforms_list) == 10

    background_list = arcade.tilemap.process_layer(tmx_map, "Background", base_directory="test_data")
    assert len(background_list) == 2

    first_sprite = platforms_list[0]
    assert first_sprite.center_x == 64
    assert first_sprite.center_y == 64
    assert first_sprite.width == 128
    assert first_sprite.height == 128


def test_two():
    tmx_map = arcade.tilemap.read_tmx(":resources:tmx_maps/test_map_2.tmx")

    assert tmx_map.map_size.width == 10
    assert tmx_map.map_size.height == 5
    assert not tmx_map.infinite
    assert tmx_map.orientation == "orthogonal"
    assert tmx_map.render_order == 'left-up'
    assert len(tmx_map.layers) == 3

    platforms_list = arcade.tilemap.process_layer(tmx_map, "Platforms", base_directory="test_data")

    assert platforms_list is not None

    first_sprite = platforms_list[0]
    assert first_sprite is not None
    assert first_sprite.center_x == 64
    assert first_sprite.center_y == 64
    # print(first_sprite.center_x, first_sprite.center_y)
    # print(first_sprite.points)

    assert first_sprite.center_x == 64
    assert first_sprite.center_y == 64
    assert first_sprite.width == 128
    assert first_sprite.height == 128

    dirt_list = arcade.tilemap.process_layer(tmx_map, "Dirt", base_directory="test_data")

    first_sprite = dirt_list[0]
    assert first_sprite is not None

    # print(first_sprite.center_x, first_sprite.center_y)
    # print(first_sprite.points)

    first_sprite = dirt_list[1]
    assert first_sprite is not None
    # print(first_sprite.center_x, first_sprite.center_y)
    # print(first_sprite.points)

    first_sprite = dirt_list[2]
    assert first_sprite is not None
    # print(first_sprite.center_x, first_sprite.center_y)
    # print(first_sprite.points)

    coin_list = arcade.tilemap.process_layer(tmx_map, "Coins", base_directory="test_data")
    first_sprite = coin_list[0]
    assert first_sprite is not None
    # print(first_sprite.center_x, first_sprite.center_y)
    # print(first_sprite.points)

    # assert 'Points' in first_sprite.properties
    # assert first_sprite.properties['Points'] == '10'


def test_three():
    tmx_map = arcade.tilemap.read_tmx(":resources:tmx_maps/test_map_3.tmx")
    assert tmx_map is not None

    sprite_list = arcade.tilemap.process_layer(tmx_map, "Moving Platforms", base_directory="test_data")
    assert sprite_list is not None

    assert len(sprite_list) == 1
    sprite = sprite_list[0]
    assert sprite.properties is not None
    assert 'change_x' in sprite.properties
    assert 'change_y' in sprite.properties
    assert sprite.properties['change_x'] == 1
    assert sprite.properties['change_y'] == 1


def test_five():
    tmx_map = arcade.tilemap.read_tmx(":resources:tmx_maps/test_map_5.tmx")
    assert tmx_map is not None

    arcade.tilemap.process_layer(tmx_map, 'object_layer')

def test_sprite_sheet():
    tmx_map = arcade.tilemap.read_tmx(":resources:tmx_maps/test_map_6.tmx")
    assert tmx_map is not None

    sprite_list = arcade.tilemap.process_layer(tmx_map, 'Tile Layer 1')
    assert sprite_list is not None
    assert len(sprite_list) == 14

    first_sprite = sprite_list[0]
    assert first_sprite is not None
    assert first_sprite.height == 16
    assert first_sprite.width == 16

