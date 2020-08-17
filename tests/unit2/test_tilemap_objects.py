import arcade

#
# Test size, rotation, alpha of tiles from a Tiled object layer
# Also tests path traversal to get a layer within a layer group
#

def test_one():
    tmx_map = arcade.tilemap.read_tmx(":resources:/tmx_maps/test_objects.tmx")

    assert tmx_map.map_size.width == 20
    assert tmx_map.map_size.height == 20
    assert not tmx_map.infinite
    assert tmx_map.orientation == "orthogonal"
    assert tmx_map.render_order == 'right-down'
    assert len(tmx_map.layers) == 4
    assert tmx_map.background_color == (85, 170, 127)

    tile_list = arcade.tilemap.process_layer(tmx_map, "Tiles", base_directory="test_data")
    assert tile_list is not None
    assert len(tile_list) == 2

    sprite_1 = tile_list[0]
    assert sprite_1 is not None
    #
    # Test width, height and angle
    #
    assert sprite_1.width == 400
    assert sprite_1.height == 1000
    assert sprite_1.angle == 45

    # 
    # Test type and name properties
    #
    assert sprite_1.properties['type'] == 'crate'
    assert sprite_1.properties['name'] == 'crate1'
    #
    # Test getting layer in group
    #
    tile_list_2 = arcade.tilemap.process_layer(tmx_map, "Group/Tiles", base_directory="test_data")

    assert tile_list_2 is not None
    assert len(tile_list_2) == 2

    sprite_2 = tile_list_2[0]
    assert sprite_2 is not None
    #
    # Test width, height and angle
    #
    assert sprite_2.width == 600
    assert sprite_2.height == 400
    assert sprite_2.angle == -45
    #
    # Test alpha inherited from layer
    #
    assert sprite_2.alpha == int(255*.5)

    #
    # Test edge case with only group name.  Should return empty sprite list
    #
    tile_list_3 = arcade.tilemap.process_layer(tmx_map, "Group", base_directory="test_data")
    assert tile_list_3 is not None
    assert len(tile_list_3) == 0

    #
    # Future tests?
    #
    '''
    shape_list = arcade.tilemap.process_layer(tmx_map, "Shapes", base_directory="test_data")
    assert shape_list is not None
    assert len(shape_list) == 4

    text_list = arcade.tilemap.process_layer(tmx_map, "Text", base_directory="test_data")
    assert text_list is not None
    assert len(text_list) == 1
    '''
