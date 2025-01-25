import arcade
from arcade.isometric import (
    isometric_grid_to_screen,
    screen_to_isometric_grid,
    create_isometric_grid_lines,
)


def test_isometric_grid_to_screen(window):
    tile_x = 0
    tile_y = 0
    width = 10
    height = 10
    tile_width = 64
    tile_height = 64
    x, y = isometric_grid_to_screen(tile_x, tile_y,
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
    x, y = isometric_grid_to_screen(tile_x, tile_y,
                                    width, height,
                                    tile_width, tile_height)
    assert x == 320
    assert y == 480


def test_screen_to_isometric_grid(window):
    screen_x = 0
    screen_y = 0
    width = 10
    height = 10
    tile_width = 64
    tile_height = 64
    x, y = screen_to_isometric_grid(screen_x, screen_y,
                                    width, height,
                                    tile_width, tile_height)
    print(x, y)
    assert x == 4
    assert y == 14

def test_create_isometric_grid_lines(window):
    width = 10
    height = 10
    tile_width = 64
    tile_height = 64
    lines = create_isometric_grid_lines(width, height,
                                        tile_width, tile_height,
                                        arcade.color.BLACK, 2)

    assert lines
