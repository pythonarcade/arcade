import os

import arcade

GRID_PIXEL_SIZE = 128
TILE_SCALING = 0.5

def test_one():
    file_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(file_path + "/../../arcade/resources/tmx_maps")

    my_map = arcade.read_tiled_map(":resources:/tmx_maps/test_map_1.tmx")


    # Grab the layer of items we can't move through
    map_array = my_map.layers_int_data['Platforms']

    # Calculate the right edge of the my_map in pixels
    end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE
    print(end_of_map)

    # -- Platforms
    wall_list = arcade.generate_sprites(my_map, 'Platforms', TILE_SCALING)

    assert wall_list[0].center_x == -32
    assert wall_list[0].center_y == 32

    # --- Other stuff
    # Set the background color
    # if my_map.backgroundcolor:
