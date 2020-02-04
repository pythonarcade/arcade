import arcade

def test_isometric_grid_to_screen():
    tile_x = 0
    tile_y = 0
    width = 10
    height = 10
    tile_width = 64
    tile_height = 64
    x, y = arcade.isometric_grid_to_screen(tile_x, tile_y,
                                           width, height,
                                           tile_width, tile_height)
    assert x == 320
    assert y == 608

    tile_x = 2
    tile_y = 2
    width = 10
    height = 10
    tile_width = 64
    tile_height = 64
    x, y = arcade.isometric_grid_to_screen(tile_x, tile_y,
                                           width, height,
                                           tile_width, tile_height)
    assert x == 320
    assert y == 480


def test_screen_to_isometric_grid():
    screen_x = 0
    screen_y = 0
    width = 10
    height = 10
    tile_width = 64
    tile_height = 64
    x, y = arcade.screen_to_isometric_grid(screen_x, screen_y,
                                           width, height,
                                           tile_width, tile_height)
    print(x, y)
    assert x == 4
    assert y == 14

def test_create_isometric_grid_lines():
    width = 10
    height = 10
    tile_width = 64
    tile_height = 64
    window = arcade.open_window(800, 600, "Test")
    lines = arcade.create_isometric_grid_lines(width, height,
                                               tile_width, tile_height,
                                               arcade.color.BLACK, 2)

    assert lines
    arcade.close_window()
