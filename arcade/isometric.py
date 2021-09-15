
from arcade import ShapeElementList
from arcade.buffered_draw_commands import create_line
from typing import Tuple
from arcade import Color


def isometric_grid_to_screen(tile_x: int, tile_y: int, width: int, height: int, tile_width: int, tile_height: int)\
        -> Tuple[int, int]:
    screen_x = tile_width * tile_x // 2 + height * tile_width // 2 - tile_y * tile_width // 2
    screen_y = (height - tile_y - 1) * tile_height // 2 + width * tile_height // 2 - tile_x * tile_height // 2
    return screen_x, screen_y


def screen_to_isometric_grid(screen_x: int, screen_y: int, width: int, height: int, tile_width: int, tile_height: int)\
        -> Tuple[int, int]:
    x2 = (1 / tile_width * screen_x / 2 - 1 / tile_height * screen_y / 2 + width / 2) * 2 - (width / 2 + 0.5)
    y2 = (height - 1) - ((1 / tile_width * screen_x / 2 + 1 / tile_height * screen_y / 2) * 2 - (width / 2 + 0.5))
    x2 = round(x2)
    y2 = round(y2)
    return x2, y2


def create_isometric_grid_lines(width: int,
                                height: int,
                                tile_width: int,
                                tile_height: int,
                                color: Color,
                                line_width: int)\
        -> ShapeElementList:

    # Grid lines 1
    shape_list: ShapeElementList = ShapeElementList()

    for tile_row in range(-1, height):
        tile_x = 0
        start_x, start_y = isometric_grid_to_screen(tile_x, tile_row, width, height, tile_width, tile_height)
        tile_x = width - 1
        end_x, end_y = isometric_grid_to_screen(tile_x, tile_row, width, height, tile_width, tile_height)

        start_x -= tile_width // 2
        end_y -= tile_height // 2

        line = create_line(start_x, start_y, end_x, end_y, color, line_width=line_width)
        shape_list.append(line)

    # Grid lines 2
    for tile_column in range(-1, width):
        tile_y = 0
        start_x, start_y = isometric_grid_to_screen(tile_column, tile_y, width, height, tile_width, tile_height)
        tile_y = height - 1
        end_x, end_y = isometric_grid_to_screen(tile_column, tile_y, width, height, tile_width, tile_height)

        start_x += tile_width // 2
        end_y -= tile_height // 2

        line = create_line(start_x, start_y, end_x, end_y, color, line_width=line_width)
        shape_list.append(line)

    return shape_list
