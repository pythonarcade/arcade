import arcade

def test_rotation_mirror():
    # Read in the tiled map
    my_map = arcade.tilemap.read_tmx("../tmx_maps/rotation.tmx")

    assert my_map.tile_size == (128, 128)
    assert my_map.orientation == "orthogonal"
    assert my_map.render_order == "left-up"
    assert my_map.infinite == 0
    assert my_map.map_size == (11, 10)

    # --- Platforms ---
    wall_list = arcade.tilemap.process_layer(my_map, 'Blocking Sprites')
    #
    # for wall in wall_list:
    #     print()
    #     print(wall.position)
    #     print(wall.texture.name)
    #     pos = 0, 0
    #     print(wall.texture.image.getpixel(pos))
    #     pos = 127, 0
    #     print(wall.texture.image.getpixel(pos))
    #     pos = 127, 127
    #     print(wall.texture.image.getpixel(pos))

    wall = wall_list[0]
    assert wall.position == (64, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 0, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (0, 255, 0, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (255, 0, 255, 255)

    wall = wall_list[1]
    assert wall.position == (192, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (0, 255, 0, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 0, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (0, 0, 255, 255)

    wall = wall_list[2]
    assert wall.position == (448, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (0, 0, 255, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 0, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (0, 255, 0, 255)


    wall = wall_list[3]
    assert wall.position == (576, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 255, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (0, 255, 0, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (255, 0, 0, 255)

    wall = wall_list[4]
    assert wall.position == (832, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 255, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (0, 0, 255, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (255, 0, 0, 255)

    wall = wall_list[5]
    assert wall.position == (960, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (0, 0, 255, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 255, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (0, 255, 0, 255)

    wall = wall_list[6]
    assert wall.position == (1216, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (0, 255, 0, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 255, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (0, 0, 255, 255)

    wall = wall_list[7]
    assert wall.position == (1344, 64)
    pos = 0, 0
    assert wall.texture.image.getpixel(pos) == (255, 0, 0, 255)
    pos = 127, 0
    assert wall.texture.image.getpixel(pos) == (0, 0, 255, 255)
    pos = 127, 127
    assert wall.texture.image.getpixel(pos) == (255, 0, 255, 255)
